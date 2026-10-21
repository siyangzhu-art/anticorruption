from pathlib import Path
import sys,json,shutil,warnings
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd,sklearn,doubleml
from doubleml import DoubleMLDIDData,DoubleMLDID
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge,LogisticRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from scipy.stats import t
O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\with_officer_city_economics\LPDID_DoubleML_common_sample')
Q=pd.read_csv(O/'horizon_pairs.csv.gz');SEED=20261015;NREP=5;KFOLD=3
features=['base_age','base_age2','base_tenure','base_tenure2','base_role','inspection2014']
ranks=sorted(Q.base_rank0.unique())
for rank in ranks[1:]:
 nm='rank_'+str(int(rank));Q[nm]=Q.base_rank0.eq(rank).astype(float);features.append(nm)
def splits(q,h):
 all_s=[];all_c=[];audit=[];gc=q.anchor_province.to_numpy();cs=np.unique(gc)
 positive=q.groupby('anchor_province').C0.sum();pos=positive[positive.gt(0)].index.to_numpy();neg=np.setdiff1d(cs,pos)
 if len(pos)<2:raise ValueError('Province-disjoint cross-fitting requires treatment support in at least two provinces')
 for rep in range(NREP):
  rng=np.random.default_rng(SEED+100*(h+4)+rep);pp=rng.permutation(pos);nn=rng.permutation(neg)
  foldmap={int(c):i%KFOLD for i,c in enumerate(pp)};counts=np.bincount(list(foldmap.values()),minlength=KFOLD)
  for c in nn:
   pick=int(np.argmin(counts));foldmap[int(c)]=pick;counts[pick]+=1
  sr=[];cr=[]
  for fold in range(KFOLD):
   testc=np.array([c for c in cs if foldmap[int(c)]==fold]);trainc=np.setdiff1d(cs,testc)
   train=np.flatnonzero(np.isin(gc,trainc));test=np.flatnonzero(np.isin(gc,testc))
   assert len(np.intersect1d(trainc,testc))==0 and q.iloc[train].C0.nunique()==2
   sr.append((train,test));cr.append(([trainc],[testc]))
   for idx in test:audit.append(dict(h=h,rep=rep,fold=fold,person_id=int(q.iloc[idx].person_id),province=int(gc[idx])))
  all_s.append(sr);all_c.append(cr)
 return all_s,all_c,audit
rows=[];preds=[];reps=[];audits=[];failures=[];warns=[]
for h in [-4,-3,-2,0,1,2,3,4]:
 q=Q[Q.h.eq(h)].copy().reset_index(drop=True);sm,sc,fa=splits(q,h);audits.extend(fa)
 for base_learner,use_econ in [('Ridge_Logit',False),('RandomForest',False),('Ridge_Logit',True),('RandomForest',True)]:
  learner=base_learner+('_econ' if use_econ else '_base')
  used_features=features+(['base_growth','base_lngdppc','base_lnpop'] if use_econ else [])
  try:
   if base_learner=='Ridge_Logit':
    mg=make_pipeline(StandardScaler(),Ridge(alpha=10))
    mm=make_pipeline(StandardScaler(),LogisticRegression(C=.5,max_iter=3000,random_state=SEED))
   else:
    mg=RandomForestRegressor(n_estimators=200,max_depth=3,min_samples_leaf=5,max_features=1.,random_state=SEED,n_jobs=2)
    mm=RandomForestClassifier(n_estimators=200,max_depth=3,min_samples_leaf=5,max_features=1.,random_state=SEED,n_jobs=2)
   with warnings.catch_warnings(record=True) as ww:
    warnings.simplefilter('always')
    data=DoubleMLDIDData(q,y_col='deltaY',d_cols='C0',x_cols=used_features,cluster_cols='anchor_province')
    model=DoubleMLDID(data,mg,mm,n_folds=KFOLD,n_rep=NREP,score='observational',clipping_threshold=.01,draw_sample_splitting=False)
    model.set_sample_splitting(sm,all_smpls_cluster=sc)
    model.fit(n_jobs_cv=1,store_predictions=True)
    for w in ww:warns.append(dict(h=h,learner=learner,category=w.category.__name__,message=str(w.message)))
   b=float(model.coef[0]);se=float(model.se[0]);G=q.anchor_province.nunique();df=G-1;crit=t.ppf(.975,df)
   mhat=np.asarray(model.predictions['ml_m'])[:,:,0];g0=np.asarray(model.predictions['ml_g0'])[:,:,0]
   row=dict(method='DoubleML_DID',learner=learner,economic_controls=use_econ,h=h,b=b,se=se,p=float(2*t.sf(abs(b/se),df)),lo=b-crit*se,hi=b+crit*se,p_normal=float(model.pval[0]),N=len(q),treated=int(q.C0.sum()),controls=int(q.C0.eq(0).sum()),G=G,df=df,n_folds=KFOLD,n_rep=NREP,propensity_min=float(mhat.min()),propensity_max=float(mhat.max()),clipped_fraction=float(((mhat<=.01000001)|(mhat>=.98999999)).mean()))
   rows.append(row)
   for r in range(NREP):
    reps.append(dict(h=h,learner=learner,rep=r,b=float(model.all_coef[0,r]),se=float(model.all_se[0,r])))
    for i in range(len(q)):preds.append(dict(h=h,learner=learner,rep=r,person_id=int(q.iloc[i].person_id),province=int(q.iloc[i].anchor_province),C0=q.iloc[i].C0,deltaY=q.iloc[i].deltaY,m_hat=mhat[i,r],g0_hat=g0[i,r],psi_a=float(model.psi_elements['psi_a'][i,r,0]),psi_b=float(model.psi_elements['psi_b'][i,r,0])))
   print(learner,'h',h,'N',len(q),'treated',int(q.C0.sum()),'b',round(b,3),'p',round(row['p'],4),flush=True)
  except Exception as e:
   failures.append(dict(h=h,learner=learner,reason=repr(e)));print('FAILED',h,learner,repr(e),flush=True)
pd.DataFrame(rows).to_csv(O/'doubleml_results.csv',index=False,encoding='utf-8-sig');pd.DataFrame(preds).to_csv(O/'doubleml_predictions_scores.csv.gz',index=False)
pd.DataFrame(reps).to_csv(O/'doubleml_repetitions.csv',index=False);pd.DataFrame(audits).to_csv(O/'province_fold_assignments.csv',index=False)
pd.DataFrame(failures,columns=['h','learner','reason']).to_csv(O/'doubleml_failures.csv',index=False);pd.DataFrame(warns).to_csv(O/'doubleml_warnings.csv',index=False)
(O/'doubleml_configuration.json').write_text(json.dumps(dict(DoubleML=doubleml.__version__,sklearn=sklearn.__version__,seed=SEED,folds=KFOLD,repetitions=NREP,features=features,economic_features=['base_growth','base_lngdppc','base_lnpop'],cluster='anchor_province',score='observational',clip=.01,DoubleML_class='DoubleMLDID (supported deprecated API in installed 0.11.4)',learners={'Ridge_Logit':{'Ridge_alpha':10,'Logit_C':.5},'RandomForest':{'trees':200,'depth':3,'min_leaf':5}},FE='No province dummies: cluster-held-out provinces have no estimable province intercept; covariates plus cohort only',inference='DoubleML province-clustered SE; display t(G-1) CIs; original normal p retained'),ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
assert len(rows)==32 and not failures,failures
