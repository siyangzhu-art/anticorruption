"""User-requested pooled event coefficients with individual/year FE first.
No Xi conditioning or inspection-cohort coefficient interactions. Includes
event-time main effects when these are not absorbed by province-year FE.
"""
from pathlib import Path
import sys,json,shutil,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t,f
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'event_study_individual_FE'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
A=pd.read_csv(BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz',low_memory=False)
assert len(A)==7249 and A.year.between(2006,2017).all()

def common_core(d):
 removed=[]
 for step in range(100):
  ni=d.groupby('person_id').person_id.transform('size');nt=d.groupby('provyear').provyear.transform('size')
  keep=ni.gt(1)&nt.gt(1)
  if keep.all():return d,pd.concat(removed,ignore_index=True) if removed else pd.DataFrame()
  z=d[~keep].copy();z['singleton_step']=step;z['singleton_person']=ni[~keep].eq(1);z['singleton_provyear']=nt[~keep].eq(1);removed.append(z);d=d[keep].copy()
 raise ValueError('Singleton removal did not converge')

def fe_project(M,groups):
 """Exact sparse dummy projection; ground one node per bipartite component."""
 n=len(M)
 if len(groups)==1:
  g=groups[0];cnt=np.bincount(g);sums=np.zeros((len(cnt),M.shape[1]));np.add.at(sums,g,M)
  return M-sums[g]/cnt[g,None],len(cnt),1
 a,b=groups;na=int(a.max()+1);nb=int(b.max()+1)
 graph=coo_matrix((np.ones(2*n),(np.r_[a,b+na],np.r_[b+na,a])),shape=(na+nb,na+nb)).tocsr()
 nc,labels=connected_components(graph,directed=False)
 _,ground=np.unique(labels,return_index=True);keep=np.ones(na+nb,dtype=bool);keep[ground]=False
 F=coo_matrix((np.ones(2*n),(np.r_[np.arange(n),np.arange(n)],np.r_[a,b+na])),shape=(n,na+nb)).tocsc()[:,keep]
 lu=splu((F.T@F).tocsc());res=M-F@lu.solve(np.asarray(F.T@M))
 return res,F.shape[1],int(nc)

def fit(d,fe,targets,events):
 if fe=='I_YEAR':groups=[pd.factorize(d.person_id)[0],pd.factorize(d.year)[0]]
 elif fe=='I_PXY':groups=[pd.factorize(d.person_id)[0],pd.factorize(d.provyear)[0]]
 else:groups=[pd.factorize(d.provyear)[0]]
 # Linear age is exactly in the individual+time FE span. Drop it explicitly
 # in those models, avoiding numerical pseudo-identification of this control.
 control_names=['age2','tenure','tenure2','role_secretary'] if fe.startswith('I_') else ['age','age2','tenure','tenure2','role_secretary']
 Z=np.column_stack([d[control_names].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),events])
 m=targets.shape[1];dm,frank,ncomp=fe_project(np.column_stack([d.Y.to_numpy(),targets,Z]),groups)
 YX=dm[:,:m+1];Z=dm[:,m+1:];norm=np.linalg.norm(Z,axis=0);Z=Z[:,norm>1e-8]/norm[norm>1e-8]
 cc,_,zr,_=lstsq(Z,YX,cond=1e-10,lapack_driver='gelsd');rr=YX-Z@cc;y=rr[:,0];x=rr[:,1:]
 sv=np.linalg.svd(x,compute_uv=False)
 if sv[-1]<max(1,sv[0])*1e-9:raise ValueError('Connection/event targets not identified')
 b,_,_,_=lstsq(x,y,cond=1e-10,lapack_driver='gelsd');err=y-x@b;bread=np.linalg.inv(x.T@x)
 gc=pd.factorize(d.province_code)[0];G=int(gc.max()+1);N=len(d);K=int(frank+zr+m)
 sc=np.zeros((G,m));np.add.at(sc,gc,x*err[:,None]);V=bread@sc.T@sc@bread*G/(G-1)*(N-1)/(N-K)
 orth=0.
 for g in groups:
  sums=np.zeros((g.max()+1,dm.shape[1]));np.add.at(sums,g,dm);orth=max(orth,float(np.abs(sums/np.bincount(g)[:,None]).max()))
 meta=dict(N=N,G=G,df=G-1,K=K,fe_rank=frank,fe_components=ncomp,nuisance_rank=int(zr),people=d.person_id.nunique(),cities=d.city_code.nunique(),promotions=int(d.promotion.sum()),C_changers=int(d.groupby('person_id').C_any.nunique().gt(1).sum()),crossprovince_people=int(d.groupby('person_id').province_code.nunique().gt(1).sum()),FE_group_mean_error=orth,min_target_singular_value=float(sv[-1]))
 return b,V,meta

results=[];joint=[];cons=[];jcons=[];metaall=[];panels=[];audits=[];dropped=[];mid=0
for range_name,lo,hi in [('short',-3,2),('long',-7,3),('full',-8,4)]:
 raw=A[A.k.between(lo,hi)].copy();d,removed=common_core(raw)
 if len(removed):removed['range']=range_name;dropped.append(removed)
 levels=sorted(map(int,d.k.unique()));eventks=[k for k in levels if k!=-1]
 for fe in ['I_YEAR','I_PXY','PXY']:
  mid+=1;termnames=['C_any']+[f'c_m{abs(k)}' if k<0 else f'c_p{k}' for k in eventks]
  eventnames=[f'd_m{abs(k)}' if k<0 else f'd_p{k}' for k in eventks]
  dd=np.column_stack([d.k.eq(k).to_numpy(float) for k in eventks]);XX=np.column_stack([d.C_any.to_numpy(),dd*d.C_any.to_numpy()[:,None]])
  b,V,meta=fit(d,fe,XX,dd);meta={**meta,'model_id':mid,'range':range_name,'fe':fe,'relative_min':lo,'relative_max':hi,'initial_N':len(raw),'removed_singleton_rows':len(raw)-len(d),'age_linear_absorbed':fe.startswith('I_')};metaall.append(meta)
  save(pd.DataFrame(V,index=termnames,columns=termnames),f'covariance_model_{mid}.csv')
  lookup={k:j+1 for j,k in enumerate(eventks)}
  def levelL(k):
   z=np.zeros(len(termnames));z[0]=1
   if k!=-1:z[lookup[k]]=1
   return z
  def deltaL(k):
   z=np.zeros(len(termnames))
   if k!=-1:z[lookup[k]]=1
   return z
  def add(label,estimand,k,L,reference=False):
   if reference:row=dict(b=0.,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan)
   else:
    bb=float(L@b);se=float(np.sqrt(max(0,L@V@L)));crit=t.ppf(.975,meta['df']);row=dict(b=bb,se=se,p=float(2*t.sf(abs(bb/se),meta['df'])),lo=bb-crit*se,hi=bb+crit*se)
   results.append({**meta,'contrast':label,'estimand':estimand,'relative_year':k,'reference':reference,**row})
   if not reference:
    for j,v in enumerate(L):
     if abs(v)>1e-15:cons.append(dict(model_id=mid,contrast=label,term=termnames[j],weight=float(v)))
  for k in levels:add('level_'+str(k),'level',k,levelL(k));add('change_'+str(k),'change',k,deltaL(k),k==-1)
  pp=np.mean([levelL(k) for k in levels if k<0],axis=0);aa=np.mean([levelL(k) for k in levels if k>=0],axis=0)
  add('pre_mean','pre_mean',np.nan,pp);add('post_mean','post_mean',np.nan,aa);add('post_minus_pre','post_minus_pre',np.nan,aa-pp)
  for label,ks in [('pretrend',[k for k in levels if k<-1]),('post_dynamics',[k for k in levels if k>=0])]:
   RR=np.vstack([deltaL(k) for k in ks]);vv=RR@V@RR.T;rank=int(np.linalg.matrix_rank(vv,tol=1e-9));bb=RR@b;F=float(bb@np.linalg.pinv(vv,rcond=1e-10)@bb/rank)
   joint.append({**meta,'test':label,'F':F,'df_num':rank,'restrictions':len(ks),'p':float(f.sf(F,rank,meta['df']))})
   for j,L in enumerate(RR):
    for ix,v in enumerate(L):
     if abs(v)>1e-15:jcons.append(dict(model_id=mid,test=label,equation=j,term=termnames[ix],weight=float(v)))
  q=d[['person_id','year','province_code','provyear','city_code','Y','C_any','age','age2','tenure','tenure2','base_rank','role_secretary','k']].copy();q['model_id']=mid
  for j,term in enumerate(termnames[1:]):q[term]=XX[:,j+1]
  for j,term in enumerate(eventnames):q[term]=dd[:,j]
  panels.append(q)
  audits.append(d.groupby('person_id').agg(rows=('person_id','size'),C_values=('C_any','nunique'),provinces=('province_code','nunique'),promotions=('promotion','sum')).reset_index().assign(range=range_name,fe=fe))
  print(range_name,fe,'N',len(d),'K',meta['K'],'switchers',meta['C_changers'],flush=True)

R=pd.DataFrame(results);JT=pd.DataFrame(joint);MM=pd.DataFrame(metaall);CL=pd.DataFrame(cons);JD=pd.DataFrame(jcons)
save(R,'event_coefficients.csv');save(JT,'joint_tests.csv');save(MM,'model_summary.csv');save(CL,'contrast_design.csv');save(JD,'joint_test_design.csv');save(pd.concat(audits,ignore_index=True),'individual_identification_audit.csv')
if dropped:save(pd.concat(dropped,ignore_index=True),'singleton_exclusions.csv.gz')
save(A,'source_analysis_panel.csv.gz')
pd.concat(panels,ignore_index=True).to_stata(OUT/'stata_model_panel.dta',write_index=False,version=118)
ck('All nine models estimated',len(MM)==9)
ck('Same observations across FE comparisons in each range',MM.groupby('range').N.nunique().eq(1).all())
ck('Short comparison sample is 3420 observations',MM[MM.range.eq('short')].N.eq(3420).all())
ck('One person per year in source',not A.duplicated(['person_id','year']).any())
ck('Individual-FE models retain within-person connection changes',MM[MM.fe.str.startswith('I_')].C_changers.gt(0).all())
ck('Sparse FE projection accurately orthogonal',MM.FE_group_mean_error.lt(1e-6).all(),MM.FE_group_mean_error.max())
ck('All estimated CIs finite',np.isfinite(R.loc[~R.reference,['b','se','lo','hi','p']]).all().all())
ck('Reference zero has no estimated CI',R[R.reference].b.eq(0).all() and R[R.reference].se.isna().all())
save(pd.DataFrame(checks),'pre_stata_validation.csv');assert all(x['passed'] for x in checks)
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
save(pd.DataFrame([dict(path=str(BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz'),sha256=hashlib.sha256((BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz').read_bytes()).hexdigest())]),'input_manifest.csv')

def expr(d):return ' + '.join(f'{r.weight:.17g}*{r.term}' for r in d.itertuples())
lines=['version 18','clear all','set more off','set processors 2',f'local out "{OUT.as_posix()}"',f'adopath ++ "{(BASE.parent.parent/"code/vendor/pz_boottest").as_posix()}"','capture log close','log using "`out\'/stata_validation.log", text replace','tempname res jres',
 'postfile `res\' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out\'/stata_validation.dta", replace',
 'postfile `jres\' long model_id str24 test double F df_num df_den p p_wild boot_rc using "`out\'/stata_joint_validation.dta", replace']
for m in MM.itertuples():
 terms=CL[CL.model_id.eq(m.model_id)].term.drop_duplicates().tolist();eventks=[k for k in range(m.relative_min,m.relative_max+1) if k!=-1];events=[f'd_m{abs(k)}' if k<0 else f'd_p{k}' for k in eventks]
 controls='age2 tenure tenure2 i.base_rank i.role_secretary'
 if m.fe=='I_YEAR':cmd='quietly areg Y '+' '.join(terms+events)+' '+controls+' i.year, absorb(person_id) vce(cluster province_code)'
 elif m.fe=='I_PXY':cmd='quietly areg Y '+' '.join(terms+events)+' '+controls+' i.py, absorb(person_id) vce(cluster province_code)'
 else:cmd='quietly areg Y '+' '.join(terms+events)+' age '+controls+', absorb(py) vce(cluster province_code)'
 lines += ['use "`out\'/stata_model_panel.dta", clear',f'keep if model_id=={m.model_id}','isid person_id year','egen py=group(province_code year)',cmd,'local nn=e(N)','quietly _ms_omit_info e(b)','local kk=e(df_a)+colsof(e(b))-r(k_omit)','local gg=e(N_clust)','local dfr=e(df_r)']
 for label,d in CL[CL.model_id.eq(m.model_id)].groupby('contrast',sort=False):
  ee=expr(d);lines += [f'quietly lincom {ee}, level(95)','local bb=r(estimate)','local ss=r(se)','local pp=r(p)','local ll=r(lb)','local hh=r(ub)','local pw=.','local rc=.']
  if m.model_id in [1,2] and label in ['pre_mean','post_mean','post_minus_pre']:lines += [f'capture quietly boottest ({ee}=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `res\' ({m.model_id}) ("{label}") (`bb\') (`ss\') (`pp\') (`ll\') (`hh\') (`nn\') (`kk\') (`gg\') (`dfr\') (`pw\') (`rc\')']
 for label,d in JD[JD.model_id.eq(m.model_id)].groupby('test',sort=False):
  ee=' '.join('('+expr(g)+'=0)' for _,g in d.groupby('equation'))
  lines += [f'quietly test {ee}','local ff=r(F)','local dd=r(df)','local pp=r(p)','local pw=.','local rc=.']
  if m.model_id in [1,2] and label=='pretrend':lines += [f'capture quietly boottest {ee}, cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `jres\' ({m.model_id}) ("{label}") (`ff\') (`dd\') (`dfr\') (`pp\') (`pw\') (`rc\')']
lines += ['postclose `res\'','postclose `jres\'','use "`out\'/stata_validation.dta", clear','format b se p lo hi p_wild %24.16g','export delimited using "`out\'/stata_validation.csv", replace','use "`out\'/stata_joint_validation.dta", clear','format F p p_wild %24.16g','export delimited using "`out\'/stata_joint_validation.csv", replace','log close','exit, clear']
(OUT/'code/validate_individual_FE.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(R[R.model_id.isin([1,2,3])&R.estimand.isin(['pre_mean','post_mean','post_minus_pre'])][['fe','estimand','b','p','lo','hi']].to_string(index=False),flush=True)
