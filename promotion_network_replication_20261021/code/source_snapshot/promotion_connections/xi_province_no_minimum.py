"""User-authorized all-identifiable-window version: remove minimum-province screen.
Province-year Xi definitions, promotion, covariates, and CR1/t CIs are unchanged.
"""
from pathlib import Path
import sys,json,shutil,importlib.util,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq

ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
BASE=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'
SOURCE=BASE/'Xi_province_union_rolling'
OUT=BASE/'Xi_province_union_no_min_provinces'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
shutil.copy2(BASE/'code/estimate_revised.py',OUT/'code/regression_engine.py')
spec=importlib.util.spec_from_file_location('regression_engine',OUT/'code/regression_engine.py');eng=importlib.util.module_from_spec(spec);spec.loader.exec_module(eng)
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))

A=pd.read_csv(SOURCE/'annual_panel_with_Xi_status.csv.gz',low_memory=False)
D=eng.sample(A,'promotion','cowork_6m','legacy','C1','maximal')
rows=[];status=[];dense=[];stata=[];mid=0
for xi in [0,1]:
 for center in range(-3,3):
  mid+=1;q=D[D.k.between(center-1,center+1)&D.Xi_province.eq(xi)].copy()
  sup=eng.support(q)
  meta=dict(model_id=mid,Xi_group=xi,center=center,width=3,requested_k_lo=center-1,requested_k_hi=center+1,CS_positive_provinces=int(q[q.CS.eq(1)].province_code.nunique()),CG_positive_provinces=int(q[q.CG.eq(1)].province_code.nunique()),CS_varying_provinces=int(q.groupby('province_code').CS.nunique().gt(1).sum()),CG_varying_provinces=int(q.groupby('province_code').CG.nunique().gt(1).sum()),low_connection_count=min(sup['CS1'],sup['CS0'],sup['CG1'],sup['CG0'])<10,**sup)
  # No arbitrary minimum-cluster or minimum-exposure-count screen. At least
  # two clusters are mathematically necessary for the existing CR1/t formula.
  if sup['G']<2:
   status.append({**meta,'status':'CLUSTER_CI_UNDEFINED_WITH_FEWER_THAN_TWO_PROVINCES'});continue
  try:
   rr=eng.fit(q,'C1','PXY',False)
   for r in rr:rows.append({**meta,**r})
   status.append({**meta,'status':'OK'})
  except Exception as ex:
   status.append({**meta,'status':str(ex)});continue
  qq=q[['person_id','year','province_code','city_code','Y','CS','CG','age','age2','tenure','tenure2','base_rank','role_secretary']].copy();qq['task_id']=mid;stata.append(qq)
  # Independent full-dummy regression, separately calculating cluster scores.
  chunks=[np.ones((len(q),1)),q[['CS','CG','age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(q.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q.provyear,drop_first=True,dtype=float).to_numpy()]
  X=np.column_stack(chunks);norm=np.linalg.norm(X,axis=0);Xn=X/norm
  b,_,rank,_=lstsq(Xn,q.Y.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');b=b/norm
  u=q.Y.to_numpy()*100-X@b;bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10)
  gc=pd.factorize(q.province_code)[0];G=int(gc.max()+1);score=np.zeros((G,X.shape[1]));np.add.at(score,gc,Xn*u[:,None]);V=bread@score.T@score@bread*G/(G-1)*(len(q)-1)/(len(q)-rank);V=V/norm[:,None]/norm[None,:]
  for r,col in zip(rr,[1,2]):
   se=float(np.sqrt(max(0,V[col,col])));dense.append(dict(model_id=mid,leader=r['leader'],b=r['b'],b_independent=b[col],se=r['se'],se_independent=se,K_saved=r['K'],K_independent=int(rank),passed=abs(r['b']-b[col])<1e-6 and abs(r['se']-se)<1e-6 and r['K']==rank))

R=pd.DataFrame(rows);ST=pd.DataFrame(status);V=pd.DataFrame(dense)
save(R,'all_window_coefficients.csv');save(ST,'window_support_and_status.csv');save(V,'independent_dummy_validation.csv')
pd.concat(stata,ignore_index=True).to_stata(OUT/'stata_window_panel.dta',write_index=False,version=118)
ST[ST.status.eq('OK')][['model_id','Xi_group','center']].to_stata(OUT/'stata_window_tasks.dta',write_index=False,version=118)
prior=pd.read_csv(SOURCE/'four_panel_estimates.csv')
old=R[R.Xi_group.eq(0)].merge(prior,on=['leader','center','Xi_group'],suffixes=('_new','_old'),validate='1:1')
ck('All 12 requested group/window models attempted',len(ST)==12)
ck('No province-count screening retained',all(ST.loc[ST.G.ge(2),'status'].ne('LESS_THAN_10_PROVINCES')))
ck('All 24 coefficients independently verified',len(V)==24 and V.passed.all(),len(V))
ck('No-Xi group coefficients and CIs unchanged',len(old)==12 and all(np.allclose(old[c+'_new'],old[c+'_old'],atol=1e-8) for c in ['b','se','p','lo','hi']))
ck('All saved CIs finite and contain point estimate',np.isfinite(R[['b','se','lo','hi']]).all().all() and R.lo.le(R.b).all() and R.hi.ge(R.b).all())
ck('Province group identical for both leader effects',R.groupby(['Xi_group','center']).apply(lambda g:g.N.nunique()==1 and g.G.nunique()==1,include_groups=False).all())
ck('All point estimates kept regardless of significance',len(R)==2*ST.status.eq('OK').sum())
save(pd.DataFrame(checks),'pre_stata_validation.csv');assert all(c['passed'] for c in checks)
for fn in ['province_Xi_group_by_year.csv','province_leader_Xi_status_by_year.csv','Xi_local_cowork_evidence.csv']:
 shutil.copy2(SOURCE/fn,OUT/fn)
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
postfile `res' long model_id str1 leader double b se p lo hi N K G df using "`out'/stata_window_validation.dta", replace
forvalues i=1/`n' {
 frame tasks: local tid=model_id[`i']
 frame change panel
 use "`out'/stata_window_panel.dta", clear
 quietly keep if task_id==`tid'
 isid person_id year
 quietly replace Y=Y*100
 quietly egen py=group(province_code year)
 quietly areg Y CS CG age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
 local nn=e(N)
 quietly _ms_omit_info e(b)
 local kk=e(df_a)+colsof(e(b))-r(k_omit)
 local gg=e(N_clust)
 local df=e(df_r)
 foreach lead in S G {
  quietly lincom C`lead', level(95)
  post `res' (`tid') ("`lead'") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`kk') (`gg') (`df')
 }
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
print(json.dumps({'models':len(ST),'supported':int(ST.status.eq('OK').sum()),'coefficients':len(R),'all_pre_stata_checks_passed':True,'out':str(OUT)},ensure_ascii=False),flush=True)
