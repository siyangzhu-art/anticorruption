"""User-confirmed two-group plot: ONE city-to-either-provincial-leader regressor."""
from pathlib import Path
import sys,json,shutil,importlib.util,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
SOURCE=BASE/'Xi_province_union_rolling'
OUT=BASE/'Xi_two_groups_any_connection'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
shutil.copy2(BASE/'code/estimate_revised.py',OUT/'code/regression_engine.py')
spec=importlib.util.spec_from_file_location('regression_engine',OUT/'code/regression_engine.py');eng=importlib.util.module_from_spec(spec);spec.loader.exec_module(eng)
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))

A=pd.read_csv(SOURCE/'annual_panel_with_Xi_status.csv.gz',low_memory=False)
S=A.legacy_cowork_6m_S;G=A.legacy_cowork_6m_G
A['C_any']=np.where(S.eq(1)|G.eq(1),1.,np.where(S.eq(0)&G.eq(0),0.,np.nan))
A['either_relation_missing']=S.isna()|G.isna()
require=['promotion','C_any','Xi_province','age','age2','tenure','tenure2','base_rank','role_secretary']
D=A.dropna(subset=require).copy()
save(A,'annual_panel_one_connection.csv.gz')
rows=[];status=[];dense=[];stata=[];mid=0
for sampling in ['maximal_union','previous_both_relations_observed']:
 for xi in [0,1]:
  for center in range(-3,3):
   mid+=1;q=D[D.k.between(center-1,center+1)&D.Xi_province.eq(xi)].copy()
   if sampling=='previous_both_relations_observed':q=q[~q.either_relation_missing].copy()
   codes=pd.factorize(q.province_code)[0];n=len(q);ng=int(codes.max()+1) if n else 0
   meta=dict(model_id=mid,sampling=sampling,Xi_group=xi,center=center,width=3,requested_k_lo=center-1,requested_k_hi=center+1,N=n,G=ng,df=ng-1,promotions=int(q.promotion.sum()),C1=int(q.C_any.eq(1).sum()),C0=int(q.C_any.eq(0).sum()),low_exposure_count=min(q.C_any.eq(1).sum(),q.C_any.eq(0).sum())<10,cities=q.city_code.nunique(),people=q.person_id.nunique(),provinces_with_connection_variation=int(q.groupby('province_code').C_any.nunique().gt(1).sum()),actual_calendar_start=int(q.year.min()) if n else None,actual_calendar_end=int(q.year.max()) if n else None)
   if ng<2:status.append({**meta,'status':'CI_UNDEFINED_FEWER_THAN_TWO_PROVINCES'});continue
   try:
    groups=[pd.factorize(q.provyear)[0]]
    Z=np.column_stack([q[['age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(q.base_rank,drop_first=True,dtype=float).to_numpy()])
    mat=np.column_stack([q.promotion.to_numpy(float)*100,q.C_any.to_numpy(float),Z]);dm,it=eng.demean(mat,groups);YX=dm[:,:2];Z=dm[:,2:]
    norm=np.linalg.norm(Z,axis=0);Z=Z[:,norm>1e-9]/norm[norm>1e-9]
    coef,_,zr,_=lstsq(Z,YX,cond=1e-10,lapack_driver='gelsd');res=YX-Z@coef;y=res[:,0];x=res[:,1]
    xx=float(x@x)
    if xx<1e-12:raise ValueError('ANY_CONNECTION_NOT_IDENTIFIED')
    b=float(x@y/xx);u=y-x*b;K=int(eng.ferank(groups)+zr+1)
    if n<=K:raise ValueError('NO_RESIDUAL_DF')
    score=np.zeros(ng);np.add.at(score,codes,x*u)
    vv=float(score@score/(xx*xx)*ng/(ng-1)*(n-1)/(n-K));se=float(np.sqrt(max(0,vv)));crit=float(t.ppf(.975,ng-1));pv=float(2*t.sf(abs(b/se),ng-1)) if se else np.nan
    rr={**meta,'b':b,'se':se,'p':pv,'lo':b-crit*se,'hi':b+crit*se,'K':K,'iterations':it}
    rows.append(rr);status.append({**meta,'status':'OK'})
    # Independent dense full-FE solution and covariance calculation.
    X=np.column_stack([np.ones((n,1)),q[['C_any','age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(q.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q.provyear,drop_first=True,dtype=float).to_numpy()])
    norm=np.linalg.norm(X,axis=0);Xn=X/norm
    beta,_,rank,_=lstsq(Xn,q.promotion.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');beta=beta/norm;err=q.promotion.to_numpy()*100-X@beta
    bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10);scores=np.zeros((ng,X.shape[1]));np.add.at(scores,codes,Xn*err[:,None]);V=bread@scores.T@scores@bread*ng/(ng-1)*(n-1)/(n-rank);V=V/norm[:,None]/norm[None,:]
    sd=float(np.sqrt(max(0,V[1,1])));dense.append(dict(model_id=mid,b_saved=b,b_dense=beta[1],se_saved=se,se_dense=sd,K_saved=K,K_dense=int(rank),passed=abs(b-beta[1])<1e-6 and abs(se-sd)<1e-6 and K==rank))
    qq=q[['person_id','year','province_code','promotion','C_any','age','age2','tenure','tenure2','base_rank','role_secretary']].copy();qq['task_id']=mid;stata.append(qq)
   except Exception as ex:status.append({**meta,'status':str(ex)});raise

R=pd.DataFrame(rows);ST=pd.DataFrame(status);V=pd.DataFrame(dense)
save(R,'all_window_estimates.csv');save(ST,'all_window_support.csv');save(V,'independent_full_dummy_validation.csv')
pd.concat(stata,ignore_index=True).to_stata(OUT/'stata_window_panel.dta',write_index=False,version=118)
ST[ST.status.eq('OK')][['model_id','Xi_group','center']].to_stata(OUT/'stata_window_tasks.dta',write_index=False,version=118)
ck('Union relation 1 iff either known positive',A.C_any.eq(1).equals(S.eq(1)|G.eq(1)))
ck('Union zero requires both relations known zero',A.loc[A.C_any.eq(0),['legacy_cowork_6m_S','legacy_cowork_6m_G']].eq(0).all().all())
ck('One relation unknown and no positive remains unknown',A.loc[(S.isna()&~G.eq(1))|(G.isna()&~S.eq(1)),'C_any'].isna().all())
ck('Annual person-year unique',not A.duplicated(['person_id','year']).any())
ck('Province-year grouping unchanged',A.Xi_province.equals(pd.read_csv(SOURCE/'annual_panel_with_Xi_status.csv.gz',usecols=['Xi_province']).Xi_province))
ck('Exactly 12 main window coefficients',len(R[R.sampling.eq('maximal_union')])==12)
ck('All coefficients independently validated',len(V)==len(R) and V.passed.all(),len(V))
ck('All CIs finite and contain coefficient',np.isfinite(R[['b','se','p','lo','hi']]).all().all() and R.lo.le(R.b).all() and R.hi.ge(R.b).all())
save(pd.DataFrame(checks),'pre_stata_validation.csv');assert all(c['passed'] for c in checks)
shutil.copy2(SOURCE/'province_Xi_group_by_year.csv',OUT/'province_Xi_group_by_year.csv')
save(pd.DataFrame([dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [SOURCE/'annual_panel_with_Xi_status.csv.gz',SOURCE/'province_Xi_group_by_year.csv']]),'input_manifest.csv')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
do=r'''version 18
clear all
set more off
set processors 2
local out "__OUT__"
capture log close
log using "`out'/stata_window_validation.log", text replace
use "`out'/stata_window_tasks.dta", clear
local n=_N
frame rename default tasks
frame create panel
tempname res
postfile `res' long model_id double b se p lo hi N K G df using "`out'/stata_window_validation.dta", replace
forvalues i=1/`n' {
 frame tasks: local tid=model_id[`i']
 frame change panel
 use "`out'/stata_window_panel.dta", clear
 quietly keep if task_id==`tid'
 isid person_id year
 quietly replace promotion=promotion*100
 quietly egen py=group(province_code year)
 quietly areg promotion C_any age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
 local nn=e(N)
 quietly _ms_omit_info e(b)
 local kk=e(df_a)+colsof(e(b))-r(k_omit)
 local gg=e(N_clust)
 local df=e(df_r)
 quietly lincom C_any, level(95)
 post `res' (`tid') (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`kk') (`gg') (`df')
 frame change tasks
}
postclose `res'
use "`out'/stata_window_validation.dta", clear
format b se p lo hi %24.16g
export delimited using "`out'/stata_window_validation.csv", replace
log close
exit, clear
'''.replace('__OUT__',OUT.as_posix())
(OUT/'code/validate_windows.do').write_text(do,encoding='utf8')
print(json.dumps({'models':len(ST),'models_ok':int(ST.status.eq('OK').sum()),'main_coefficients':12,'validation_passed':True},ensure_ascii=False),flush=True)
print(R[R.sampling.eq('maximal_union')][['Xi_group','center','b','p','lo','hi','N','G']].to_string(index=False),flush=True)
