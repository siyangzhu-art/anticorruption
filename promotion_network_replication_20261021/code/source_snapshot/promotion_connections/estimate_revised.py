"""Predefined rolling LPMs and pooled interaction tests; all failures retained."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
OUT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
REL=['cowork_6m','hometown_prefecture','classmate_6m','connected']
C1=['age','age2','tenure','tenure2'];ECON=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
CONTROLS={'C0':[],'C1':C1,'C2':C1+ECON}
FES=['PY','PXY','CITY_PXY']
results=[];status=[];idcounter=0;tasks=[];validation=[]
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
def say(*a):print(*a,flush=True)

def demean(mat,groups):
 a=np.array(mat,float,copy=True)
 for it in range(2000):
  before=a.copy()
  for g in groups:
   counts=np.bincount(g);sums=np.zeros((len(counts),a.shape[1]));np.add.at(sums,g,a);a-=sums[g]/counts[g,None]
  if np.max(abs(a-before),initial=0)<1e-10:return a,it+1
 raise ValueError('FE_DEMEANING_FAILED')

def ferank(groups):
 if len(groups)==1:return int(groups[0].max()+1)
 a,b=groups;na=a.max()+1;nb=b.max()+1
 g=coo_matrix((np.ones(2*len(a)),(np.r_[a,b+na],np.r_[b+na,a])),shape=(na+nb,na+nb)).tocsr()
 return int(na+nb-connected_components(g,directed=False,return_labels=False))

def fit(d,controls,fe,pooled=False):
 if fe=='PY':groups=[pd.factorize(d.province_code)[0],pd.factorize(d.year)[0]]
 elif fe=='PXY':groups=[pd.factorize(d.provyear)[0]]
 else:groups=[pd.factorize(d.city_code)[0],pd.factorize(d.provyear)[0]]
 X=np.column_stack([d.CS,d.CG,d.CS*d.post,d.CG*d.post]) if pooled else np.column_stack([d.CS,d.CG])
 terms=['CS','CG','CSPost','CGPost'] if pooled else ['CS','CG']
 Z=d[CONTROLS[controls]].to_numpy(float)
 if d.role.nunique()>1:Z=np.column_stack([Z,d.role_secretary.to_numpy(float)])
 if pooled:Z=np.column_stack([Z,d.post.to_numpy(float)])
 if controls!='C0':Z=np.column_stack([Z,pd.get_dummies(d.base_rank,drop_first=True).to_numpy(float)])
 mat=np.column_stack([d.Y.to_numpy(float)*100,X,Z]);dm,it=demean(mat,groups);m=len(terms)
 YX=dm[:,:1+m];Z=dm[:,1+m:]
 if Z.shape[1]:
  norm=np.linalg.norm(Z,axis=0);Z=Z[:,norm>1e-9]/norm[norm>1e-9]
  q,_,nr,_=lstsq(Z,YX,cond=1e-10,lapack_driver='gelsd');res=YX-Z@q
 else:nr=0;res=YX
 Y=res[:,0];X=res[:,1:];sv=np.linalg.svd(X,compute_uv=False)
 if len(sv)<m or sv[-1]<1e-8*max(1,sv[0]):raise ValueError('CONNECTION_COEFFICIENTS_NOT_SEPARATELY_IDENTIFIED')
 b,_,rank,_=lstsq(X,Y,cond=1e-10,lapack_driver='gelsd');bread=np.linalg.inv(X.T@X);err=Y-X@b
 Gcodes=pd.factorize(d.province_code)[0];G=int(Gcodes.max()+1);N=len(d);K=ferank(groups)+nr+m
 if N<=K:raise ValueError('NO_RESIDUAL_DF')
 scores=np.zeros((G,m));np.add.at(scores,Gcodes,X*err[:,None]);V=bread@(scores.T@scores)@bread*G/(G-1)*(N-1)/(N-K)
 if np.linalg.eigvalsh(V).min()<-1e-8:raise ValueError('INVALID_COVARIANCE')
 contrasts=[]
 for j,leader in enumerate(['S','G']):
  if pooled:
   pre=np.eye(m)[j];chg=np.eye(m)[j+2];contrasts += [(leader,'pre',pre),(leader,'post',pre+chg),(leader,'change',chg)]
  else:contrasts += [(leader,'window',np.eye(m)[j])]
 out=[]
 for leader,estimand,L in contrasts:
  bb=float(L@b);se=float(np.sqrt(max(0,L@V@L)));p=float(2*t.sf(abs(bb/se),G-1)) if se>0 else np.nan;crit=t.ppf(.975,G-1)
  out.append(dict(leader=leader,estimand=estimand,b=bb,se=se,p=p,lo=bb-crit*se,hi=bb+crit*se,N=N,K=int(K),G=G,df=G-1,iterations=it,actual_start=int(d.year.min()),actual_end=int(d.year.max()),people=d.person_id.nunique(),cities=d.city_code.nunique(),promotions=int(d.Y.sum()),CS_positive=int(d.CS.eq(1).sum()),CG_positive=int(d.CG.eq(1).sum())))
 return out

def support(d,pooled=False):
 out={'N':len(d),'G':d.province_code.nunique(),'promotions':int(d.Y.sum()),'CS1':int(d.CS.eq(1).sum()),'CS0':int(d.CS.eq(0).sum()),'CG1':int(d.CG.eq(1).sum()),'CG0':int(d.CG.eq(0).sum())}
 if pooled:
  for s in [0,1]:
   q=d[d.post.eq(s)];out.update({f'N_post{s}':len(q),f'promotions_post{s}':int(q.Y.sum()),f'CS1_post{s}':int(q.CS.sum()),f'CG1_post{s}':int(q.CG.sum())})
 return out

def reason(s):
 if s['G']<10:return 'LESS_THAN_10_PROVINCES'
 if s['promotions']<10:return 'LESS_THAN_10_PROMOTIONS'
 if min(s['CS1'],s['CS0'],s['CG1'],s['CG0'])<10:return 'LESS_THAN_10_CONNECTED_OR_UNCONNECTED_FOR_A_LEADER'
 return ''

def sample(base,outcome,rel,timing,controls,sampling):
 d=base.copy();d['Y']=d[outcome];d['CS']=d[timing+'_'+rel+'_S'];d['CG']=d[timing+'_'+rel+'_G']
 require=['Y','CS','CG']+(C1+ECON+['base_rank'] if sampling=='common' else CONTROLS[controls]+(['base_rank'] if controls!='C0' else []))
 d=d.dropna(subset=require)
 return d

def runfit(d,meta,pooled=False,primary=False):
 global idcounter
 if meta['kind']=='rolling':
  timecol='year' if meta['axis']=='calendar' else 'k';nt=int(d[timecol].nunique())
  bycohort=d.groupby('first_inspection_year')[timecol].nunique();minimum=int(bycohort.min()) if len(bycohort) else 0
  meta={**meta,'observed_time_points':nt,'observed_time_levels':'|'.join(map(str,sorted(d[timecol].dropna().astype(int).unique()))),'incomplete_window':bool(nt<meta['width'] or (meta['axis']=='inspection_relative' and (len(bycohort)<2 or minimum<meta['width']))),'inspection_cohorts':len(bycohort),'minimum_cohort_time_points':minimum}
 idcounter+=1;meta={**meta,'model_id':idcounter};sup=support(d,pooled);why=reason(sup)
 if why:status.append({**meta,**sup,'status':why});return
 try:
  rr=fit(d,meta['controls'],meta['fe'],pooled)
  for r in rr:results.append({**meta,**r,'primary_test':int(primary)})
  status.append({**meta,**sup,'status':'OK'})
  if primary:
   q=d[['person_id','year','province_code','city_code','Y','CS','CG','post','age','age2','tenure','tenure2','base_rank','role_secretary']].copy();q['task_id']=idcounter;q['CSPost']=q.CS*q.post;q['CGPost']=q.CG*q.post
   validation.append(q);tasks.append({**meta,'N':len(q)})
 except Exception as ex:status.append({**meta,**sup,'status':str(ex)})

def pooled_grid(base,unit):
 for role in ['all','mayor','secretary']:
  bb=base.copy() if role=='all' else base[base.role.eq(role)]
  for outcome in ['promotion','rank_promotion','executive_promotion']:
   combos=[('cowork_6m','legacy',c,fe,'common') for c in CONTROLS for fe in FES]
   combos += [('cowork_6m','legacy',c,fe,'maximal') for c in ['C0','C1'] for fe in FES]
   combos += [(rel,timing,'C1','PXY','common') for rel,timing in [('cowork_6m','preassignment'),('hometown_prefecture','legacy'),('classmate_6m','legacy'),('connected','legacy')]]
   for rel,timing,c,fe,sampling in combos:
    d=sample(bb,outcome,rel,timing,c,sampling)
    for cutoff in ['national_main','national_include2012','inspection_main','inspection_drop_entry']:
     q=d.copy()
     if cutoff=='national_main':q=q[q.year.ne(2012)].copy();q['post']=q.year.ge(2013).astype(float)
     elif cutoff=='national_include2012':q['post']=q.year.ge(2013).astype(float)
     else:
      q=q[q.first_inspection_year.notna()].copy()
      if cutoff=='inspection_drop_entry':q=q[q.k.ne(0)].copy()
      q['post']=q.year.ge(q.first_inspection_year).astype(float)
     meta=dict(kind='pooled',unit=unit,role=role,outcome=outcome,relation=rel,timing=timing,controls=c,fe=fe,sampling=sampling,axis=cutoff,width=0,center=np.nan,mixed=False)
     primary=unit=='annual' and outcome=='promotion' and rel=='cowork_6m' and timing=='legacy' and c=='C1' and fe=='PXY' and sampling=='maximal' and cutoff in ['national_main','inspection_main']
     runfit(q,meta,pooled=True,primary=primary)
  say('Pooled complete',unit,role,'models',idcounter)

def rolling_grid(base,unit):
 for role in ['all','mayor','secretary']:
  bb=base.copy() if role=='all' else base[base.role.eq(role)]
  combos=[]
  if unit=='annual':
   combos=[('promotion','cowork_6m','legacy',c,fe,'common',[3,5,7]) for c in CONTROLS for fe in FES]
   combos += [('promotion','cowork_6m','legacy',c,fe,'maximal',[3,5,7]) for c in ['C0','C1'] for fe in FES]
   combos += [('promotion',rel,timing,'C1','PXY','common',[0]) for rel,timing in [('cowork_6m','preassignment'),('hometown_prefecture','legacy'),('classmate_6m','legacy'),('connected','legacy')]]
  combos += [(outcome,'cowork_6m','legacy','C1','PXY','common',[0]) for outcome in (['rank_promotion','executive_promotion'] if unit=='annual' else ['promotion','rank_promotion','executive_promotion'])]
  for outcome,rel,timing,c,fe,sampling,widths in combos:
   d=sample(bb,outcome,rel,timing,c,sampling)
   for axis in ['calendar','inspection_relative']:
    # Common relative-year support for BOTH inspection cohorts in source risk period.
    min_k=int(max(2006-bb.first_inspection_year.dropna().unique()));max_k=int(min(2017-bb.first_inspection_year.dropna().unique()))
    lo,hi=(2006,2017) if axis=='calendar' else (min_k,max_k)
    for width0 in widths:
     width=(5 if axis=='calendar' else 3) if width0==0 else width0;h=width//2
     for center in range(lo+h,hi-h+1):
      q=d[d.year.between(center-h,center+h)].copy() if axis=='calendar' else d[d.k.between(center-h,center+h)].copy()
      mixed=(center-h<=2012<=center+h) if axis=='calendar' else (center-h<=0<=center+h)
      meta=dict(kind='rolling',unit=unit,role=role,outcome=outcome,relation=rel,timing=timing,controls=c,fe=fe,sampling=sampling,axis=axis,width=width,center=center,mixed=mixed,requested_lo=center-h,requested_hi=center+h)
      runfit(q,meta)
  say('Rolling complete',unit,role,'models',idcounter)

def holm(x):
 a=np.array(x,float);valid=np.isfinite(a);z=np.where(valid,a,1.);order=np.argsort(z);out=np.empty(len(z));last=0
 for j,i in enumerate(order):last=max(last,min(1,(len(z)-j)*z[i]));out[i]=last
 out[~valid]=np.nan;return out

if __name__=='__main__':
 for fname,unit in [('annual_official_panel.csv.gz','annual')]:
  d=pd.read_csv(OUT/fname,low_memory=False);pooled_grid(d,unit);rolling_grid(d,unit)
 r=pd.DataFrame(results);s=pd.DataFrame(status);r['holm_twelve_primary_changes']=np.nan
 primary=r.primary_test.eq(1)&r.estimand.eq('change')
 if primary.sum()==12:r.loc[primary,'holm_twelve_primary_changes']=holm(r.loc[primary,'p'])
 save(r,'all_estimates.csv');save(s,'model_status.csv');save(r[r.primary_test.eq(1)],'primary_pooled_estimates.csv');save(pd.DataFrame(tasks),'stata_tasks.csv')
 if validation:
  q=pd.concat(validation,ignore_index=True);q.to_stata(OUT/'stata_primary_panel.dta',write_index=False,version=118);pd.DataFrame(tasks)[['model_id','role','axis']].to_stata(OUT/'stata_primary_tasks.dta',write_index=False,version=118)
 summary={'models_requested':len(s),'models_ok':int(s.status.eq('OK').sum()),'status_counts':s.status.value_counts().to_dict(),'estimates':len(r),'primary_change_tests':int(primary.sum()),'wild_seed':20261015,'CI':'95% pointwise province clustered CR1, t(G-1)','ranking':'No selection by significance; all planned grid cells saved'}
 (OUT/'estimation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');say(json.dumps(summary,ensure_ascii=False,indent=2));shutil.copy2(__file__,OUT/'code/estimate.py')
