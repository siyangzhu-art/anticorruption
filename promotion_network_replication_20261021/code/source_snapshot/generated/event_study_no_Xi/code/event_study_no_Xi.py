"""Inspection-aligned event study of the promotion return to either provincial tie.
Uses no Xi variable or Xi-based sample restriction. Dynamic ties imply conditional
association changes, not an automatically identified causal ATT.
"""
from pathlib import Path
import sys,json,shutil,importlib.util,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t,f

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'event_study_no_Xi'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
shutil.copy2(BASE/'code/estimate_revised.py',OUT/'code/regression_engine.py')
sp=importlib.util.spec_from_file_location('engine',OUT/'code/regression_engine.py');eng=importlib.util.module_from_spec(sp);sp.loader.exec_module(eng)
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))

A=pd.read_csv(BASE/'annual_official_panel.csv.gz',low_memory=False)
S=A.legacy_cowork_6m_S;G=A.legacy_cowork_6m_G
A['C_any']=np.where(S.eq(1)|G.eq(1),1.,np.where(S.eq(0)&G.eq(0),0.,np.nan))
cols=['promotion','C_any','age','age2','tenure','tenure2','base_rank','role_secretary','first_inspection_year']
D=A.dropna(subset=cols).copy()
D['cohort']=D.first_inspection_year.astype(int);D['k']=D.year-D.cohort
D['Y']=D.promotion*100
# Fixed weights use baseline officer counts, not selected estimates or post data.
bcounts=D[D.k.eq(-1)].groupby('cohort').size()
weights=(bcounts/bcounts.sum()).to_dict()
save(pd.DataFrame([dict(cohort=g,baseline_N=int(bcounts[g]),weight=float(w)) for g,w in weights.items()]),'cohort_weights.csv')
save(D,'analysis_panel_2006_2017.csv.gz')
support=D.groupby(['cohort','k']).agg(N=('person_id','size'),connected=('C_any','sum'),promotions=('promotion','sum'),provinces=('province_code','nunique')).reset_index()
support['unconnected']=support.N-support.connected;save(support,'support_by_cohort_relative_year.csv')

def estimate(d,X,fe):
 groups=[pd.factorize(d.provyear)[0]] if fe=='PXY' else [pd.factorize(d.city_code)[0],pd.factorize(d.provyear)[0]]
 Z=np.column_stack([d[['age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy()])
 m=X.shape[1];dm,it=eng.demean(np.column_stack([d.Y.to_numpy(),X,Z]),groups);YX=dm[:,:m+1];Z=dm[:,m+1:]
 norm=np.linalg.norm(Z,axis=0);Z=Z[:,norm>1e-9]/norm[norm>1e-9]
 cc,_,zr,_=lstsq(Z,YX,cond=1e-10,lapack_driver='gelsd');res=YX-Z@cc;y=res[:,0];x=res[:,1:]
 sv=np.linalg.svd(x,compute_uv=False)
 if sv[-1]<max(1,sv[0])*1e-9:raise ValueError('EVENT_INTERACTIONS_NOT_IDENTIFIED')
 b,_,rank,_=lstsq(x,y,cond=1e-10,lapack_driver='gelsd');u=y-x@b;bread=np.linalg.inv(x.T@x)
 codes=pd.factorize(d.province_code)[0];ng=int(codes.max()+1);n=len(d);K=int(eng.ferank(groups)+zr+m)
 scores=np.zeros((ng,m));np.add.at(scores,codes,x*u[:,None]);V=bread@scores.T@scores@bread*ng/(ng-1)*(n-1)/(n-K)
 assert np.linalg.eigvalsh(V).min()>-1e-8
 return b,V,dict(N=n,G=ng,df=ng-1,K=K,iterations=it,people=d.person_id.nunique(),cities=d.city_code.nunique(),promotions=int(d.promotion.sum()))

models=[('inspection_short_cohort',-3,2,'cohort','PXY'),('inspection_short_pooled',-3,2,'pooled','PXY'),('inspection_long_cohort',-7,3,'cohort','PXY'),('inspection_full_cohort',-8,4,'cohort','PXY'),('inspection_short_city_FE',-3,2,'cohort','CITY_PXY')]
allrows=[];joint=[];contrasts=[];data_stata=[];designs=[];allmeta=[];coefrows=[]
for mid,(name,lo,hi,kind,fe) in enumerate(models,1):
 d=D[D.k.between(lo,hi)].copy();levels=sorted(map(int,d.k.unique()));terms=[];values=[];lookup={}
 if kind=='cohort':
  for g in sorted(weights):
   for k in levels:
    if not ((d.cohort==g)&(d.k==k)).any():continue
    j=len(terms);terms.append(f'z{j}');values.append((d.C_any*d.cohort.eq(g)*d.k.eq(k)).to_numpy(float));lookup[g,k]=j
 else:
  terms=['z0'];values=[d.C_any.to_numpy(float)];lookup['base']=0
  for k in levels:
   if k==-1:continue
   j=len(terms);terms.append(f'z{j}');values.append((d.C_any*d.k.eq(k)).to_numpy(float));lookup[k]=j
 X=np.column_stack(values);b,V,meta=estimate(d,X,fe);meta={**meta,'model_id':mid,'model':name,'kind':kind,'fe':fe,'relative_min':lo,'relative_max':hi};allmeta.append(meta)
 pd.DataFrame(V,index=terms,columns=terms).to_csv(OUT/f'covariance_model_{mid}.csv',encoding='utf-8-sig')
 def Llevel(k):
  z=np.zeros(len(terms))
  if kind=='cohort':
   gs=[g for g in weights if (g,k) in lookup];den=sum(weights[g] for g in gs)
   for g in gs:z[lookup[g,k]]=weights[g]/den
  else:
   z[0]=1
   if k!=-1:z[lookup[k]]=1
  return z
 def Lchange(k):
  z=Llevel(k)
  if kind=='cohort':
   gs=[g for g in weights if (g,k) in lookup];den=sum(weights[g] for g in gs)
   for g in gs:z[lookup[g,-1]]-=weights[g]/den
  else:z-=Llevel(-1)
  return z
 def add(label,estimand,k,L,reference=False):
  if reference:r=dict(b=0.,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan)
  else:
   bb=float(L@b);se=float(np.sqrt(max(0,L@V@L)));crit=t.ppf(.975,meta['df']);r=dict(b=bb,se=se,p=float(2*t.sf(abs(bb/se),meta['df'])) if se else np.nan,lo=bb-crit*se,hi=bb+crit*se)
  row={**meta,'contrast':label,'estimand':estimand,'relative_year':k,'reference':reference,'single_cohort_endpoint':bool(k in levels and d[d.k.eq(k)].cohort.nunique()<2),**r}
  allrows.append(row)
  if not reference:
   for j,v in enumerate(L):
    if abs(v)>1e-15:contrasts.append(dict(model_id=mid,contrast=label,term=terms[j],weight=float(v)))
 for k in levels:
  add('level_'+str(k),'level',k,Llevel(k))
  add('change_'+str(k),'change',k,Lchange(k),k==-1)
 # The short-range contrasts are the prespecified average pre/post comparison.
 pre=[k for k in levels if k<0];post=[k for k in levels if k>=0]
 lp=np.mean([Llevel(k) for k in pre],axis=0);la=np.mean([Llevel(k) for k in post],axis=0)
 add('pre_mean','pre_mean',np.nan,lp);add('post_mean','post_mean',np.nan,la);add('post_minus_pre','post_minus_pre',np.nan,la-lp)
 for label,ks in [('pretrend',[k for k in levels if k<-1]),('post_dynamics',[k for k in levels if k>=0])]:
  RR=np.vstack([Lchange(k) for k in ks]);vv=RR@V@RR.T;rank=int(np.linalg.matrix_rank(vv,tol=1e-9));bb=RR@b;stat=float(bb@np.linalg.pinv(vv,rcond=1e-10)@bb/rank)
  joint.append({**meta,'test':label,'restrictions':len(ks),'covariance_rank':rank,'F':stat,'df_num':rank,'p':float(f.sf(stat,rank,meta['df']))})
  for ii,L in enumerate(RR):
   for j,v in enumerate(L):
    if abs(v)>1e-15:designs.append(dict(model_id=mid,test=label,equation=ii,term=terms[j],weight=float(v)))
 if kind=='cohort':
  for label,ks in [('pretrend_all_cohorts',[k for k in levels if k<-1]),('post_all_cohorts',[k for k in levels if k>=0])]:
   rr=[]
   for g in sorted(weights):
    for k in ks:
     if (g,k) not in lookup:continue
     z=np.zeros(len(terms));z[lookup[g,k]]=1;z[lookup[g,-1]]=-1;rr.append(z)
   RR=np.vstack(rr);vv=RR@V@RR.T;rank=int(np.linalg.matrix_rank(vv,tol=1e-9));bb=RR@b;stat=float(bb@np.linalg.pinv(vv,rcond=1e-10)@bb/rank)
   joint.append({**meta,'test':label,'restrictions':len(RR),'covariance_rank':rank,'F':stat,'df_num':rank,'p':float(f.sf(stat,rank,meta['df']))})
   for ii,L in enumerate(RR):
    for j,v in enumerate(L):
     if abs(v)>1e-15:designs.append(dict(model_id=mid,test=label,equation=ii,term=terms[j],weight=float(v)))
 reverse={v:key for key,v in lookup.items()} if kind=='cohort' else {}
 for j,term in enumerate(terms):coefrows.append({**meta,'term':term,'term_cohort':reverse[j][0] if j in reverse else np.nan,'term_relative_year':reverse[j][1] if j in reverse else np.nan,'b':float(b[j]),'se':float(np.sqrt(V[j,j]))})
 qq=d[['person_id','year','province_code','city_code','Y','C_any','age','age2','tenure','tenure2','base_rank','role_secretary','k','cohort']].copy();qq['model_id']=mid
 for j,term in enumerate(terms):qq[term]=X[:,j]
 data_stata.append(qq)
 print(name,'N',len(d),'terms',len(terms),flush=True)

R=pd.DataFrame(allrows);JT=pd.DataFrame(joint);CL=pd.DataFrame(contrasts);JD=pd.DataFrame(designs);MM=pd.DataFrame(allmeta)
save(R,'event_study_coefficients.csv');save(JT,'joint_tests.csv');save(CL,'contrast_design.csv');save(JD,'joint_test_design.csv');save(MM,'model_summary.csv');save(pd.DataFrame(coefrows),'underlying_slope_coefficients.csv')
pd.concat(data_stata,ignore_index=True).to_stata(OUT/'stata_event_panel.dta',write_index=False,version=118)
ck('Source years 2006-2017',A.year.between(2006,2017).all())
ck('Analysis person year unique',not D.duplicated(['person_id','year']).any())
ck('No Xi sample restriction',len(D)==7249 and not any('Xi' in c for c in cols),len(D))
ck('Both positive union preserved',(A.C_any.eq(1)==(S.eq(1)|G.eq(1))).all())
ck('Unknown relation not imputed zero',A.loc[(S.isna()&~G.eq(1))|(G.isna()&~S.eq(1)),'C_any'].isna().all())
ck('Reference period only normalized in change plot',R[R.reference].b.eq(0).all() and R[R.reference][['se','lo','hi']].isna().all().all())
ck('Level plot baseline retains uncertainty',R[R.estimand.eq('level')&R.relative_year.eq(-1)].se.gt(0).all())
ck('All estimated intervals finite',np.isfinite(R.loc[~R.reference,['b','se','p','lo','hi']]).all().all())
ck('Both cohorts in short and common long ranges',all(support[support.k.between(lo,hi)].groupby('k').cohort.nunique().eq(2).all() for lo,hi in [(-3,2),(-7,3)]))
save(pd.DataFrame(checks),'pre_stata_validation.csv');assert all(c['passed'] for c in checks)
save(pd.DataFrame([dict(path=str(BASE/'annual_official_panel.csv.gz'),bytes=(BASE/'annual_official_panel.csv.gz').stat().st_size,sha256=hashlib.sha256((BASE/'annual_official_panel.csv.gz').read_bytes()).hexdigest())]),'input_manifest.csv')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)

def expr(q):return ' + '.join(f'{float(r.weight):.17g}*{r.term}' for r in q.itertuples())
lines=['version 18','clear all','set more off','set processors 2',f'local out "{OUT.as_posix()}"',f'adopath ++ "{(BASE.parent.parent/"code/vendor/pz_boottest").as_posix()}"','capture log close','log using "`out\'/stata_event_validation.log", text replace',
 'tempname res jres',
 'postfile `res\' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out\'/stata_event_validation.dta", replace',
 'postfile `jres\' long model_id str24 test double F df_num df_den p p_wild boot_rc using "`out\'/stata_joint_validation.dta", replace']
for m in MM.itertuples():
 terms=pd.DataFrame(coefrows).query('model_id==@m.model_id').term.tolist()
 lines += ['use "`out\'/stata_event_panel.dta", clear',f'keep if model_id=={m.model_id}','isid person_id year','egen py=group(province_code year)']
 if m.fe=='PXY':cmd='quietly areg Y '+' '.join(terms)+' age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)'
 else:cmd='quietly areg Y '+' '.join(terms)+' age age2 tenure tenure2 i.base_rank i.role_secretary i.city_code, absorb(py) vce(cluster province_code)'
 lines += [cmd,'local nn=e(N)','quietly _ms_omit_info e(b)','local kk=e(df_a)+colsof(e(b))-r(k_omit)','local gg=e(N_clust)','local dfr=e(df_r)']
 for label,g in CL[CL.model_id.eq(m.model_id)].groupby('contrast',sort=False):
  ee=expr(g);lines += [f'quietly lincom {ee}, level(95)','local bb=r(estimate)','local ss=r(se)','local pp=r(p)','local ll=r(lb)','local hh=r(ub)','local pw=.','local rc=.']
  if m.model_id==1 and label in ['pre_mean','post_mean','post_minus_pre']:
   lines += [f'capture quietly boottest ({ee}=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `res\' ({m.model_id}) ("{label}") (`bb\') (`ss\') (`pp\') (`ll\') (`hh\') (`nn\') (`kk\') (`gg\') (`dfr\') (`pw\') (`rc\')']
 for label,jg in JD[JD.model_id.eq(m.model_id)].groupby('test',sort=False):
  ee=' '.join('('+expr(g)+'=0)' for _,g in jg.groupby('equation',sort=True))
  lines += [f'quietly test {ee}','local ff=r(F)','local dd=r(df)','local pp=r(p)','local pw=.','local rc=.']
  if m.model_id==1 and label in ['pretrend','pretrend_all_cohorts']:lines += [f'capture quietly boottest {ee}, cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `jres\' ({m.model_id}) ("{label}") (`ff\') (`dd\') (`dfr\') (`pp\') (`pw\') (`rc\')']
lines += ['postclose `res\'','postclose `jres\'','use "`out\'/stata_event_validation.dta", clear','format b se p lo hi p_wild %24.16g','export delimited using "`out\'/stata_event_validation.csv", replace','use "`out\'/stata_joint_validation.dta", clear','format F p p_wild %24.16g','export delimited using "`out\'/stata_joint_validation.csv", replace','log close','exit, clear']
(OUT/'code/validate_event_study.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(MM.to_string(index=False),flush=True)
print(R[(R.model_id==1)&R.estimand.isin(['change','pre_mean','post_mean','post_minus_pre'])][['estimand','relative_year','b','se','p','lo','hi']].to_string(index=False),flush=True)
print(JT[JT.model_id.eq(1)][['test','F','p']].to_string(index=False),flush=True)
