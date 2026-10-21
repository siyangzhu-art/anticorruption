"""Exhaustive pre-window sensitivity; post horizon fixed through k=+4."""
from pathlib import Path
import ast,sys,shutil,json,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t,f
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'with_officer_city_economics/dynamic_TWFE_common_sample'
for p in [OUT,OUT/'code',OUT/'figures']:p.mkdir(exist_ok=True)
helper=Path(__file__).with_name('event_study_individual_FE.py')
tree=ast.parse(helper.read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['common_core','fe_project','fit']],type_ignores=[]),str(helper),'exec'))
A=pd.read_csv(BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz',low_memory=False)
assert len(A)==7249 and not A.duplicated(['person_id','year']).any()
econ=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
rematched=pd.read_csv(BASE/'with_officer_city_economics/annual_economics_rematched.csv.gz',usecols=['person_id','year']+econ)
A=A.drop(columns=econ).merge(rematched,on=['person_id','year'],how='left',validate='1:1').dropna(subset=econ).copy()
rows=[];jrows=[];models=[];panels=[];cons=[];jointcons=[];support=[];excluded=[];fails=[]
for L in [4]:
 raw=A[A.k.between(-L,4)].copy();d,drop=common_core(raw)
 if len(drop):excluded.append(drop.assign(window=f'[-{L},4]'))
 for k,g in d.groupby('k'):
  support.append(dict(window=f'[-{L},4]',relative_year=k,N=len(g),people=g.person_id.nunique(),provinces=g.province_code.nunique(),connected=int(g.C_any.sum()),unconnected=int(g.C_any.eq(0).sum()),promotions=int(g.promotion.sum()),cohort_2013=int((g.year-g.k).eq(2013).sum()),cohort_2014=int((g.year-g.k).eq(2014).sum())))
 for mid,(fe,use_econ) in enumerate([('I_YEAR',False),('I_PXY',False),('I_YEAR',True),('I_PXY',True)],1):
  ks=list(range(-L,5));events=[k for k in ks if k!=-1]
  cn=['C_any']+[f'c_m{-k}' if k<0 else f'c_p{k}' for k in events]
  dn=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in events]
  dd=np.column_stack([d.k.eq(k).to_numpy(float) for k in events]);XX=np.column_stack([d.C_any.to_numpy(),dd*d.C_any.to_numpy()[:,None]])
  try:b,V,meta=fit(d,fe,XX,np.column_stack([dd,d[econ].to_numpy()]) if use_econ else dd)
  except Exception as e:fails.append(dict(model_id=mid,L=L,fe=fe,reason=str(e)));continue
  meta.update(model_id=mid,L=L,fe=fe,economic_controls=use_econ,window=f'[-{L},4]',initial_N=len(raw),singleton_rows=len(raw)-len(d))
  models.append(meta)
  pd.DataFrame(V,index=cn,columns=cn).to_csv(OUT/f'covariance_{mid}.csv')
  lookup={k:i+1 for i,k in enumerate(events)}
  def delta(k):
   z=np.zeros(len(cn))
   if k!=-1:z[lookup[k]]=1
   return z
  def level(k):
   z=delta(k);z[0]=1;return z
  def add(name,est,k,v,ref=False):
   if ref:bb=0.;se=p=ll=hh=np.nan
   else:
    bb=float(v@b);se=float(np.sqrt(v@V@v));p=float(2*t.sf(abs(bb/se),meta['df']));crit=t.ppf(.975,meta['df']);ll=bb-crit*se;hh=bb+crit*se
    for nm,weight in zip(cn,v):
     if weight:cons.append(dict(model_id=mid,contrast=name,term=nm,weight=weight))
   rows.append({**meta,'contrast':name,'estimand':est,'k':k,'reference':ref,'b':bb,'se':se,'p':p,'lo':ll,'hi':hh})
  for k in ks:
   add(f'change_{k}','change',k,delta(k),k==-1)
   add(f'level_{k}','level',k,level(k))
  pre=np.mean([level(k) for k in ks if k<0],axis=0)
  for name,v in [('pre_level',pre),('post_level_0_4',np.mean([level(k) for k in range(5)],axis=0)),('post_change_0_4',np.mean([delta(k) for k in range(5)],axis=0)),('post_change_1_4',np.mean([delta(k) for k in range(1,5)],axis=0)),('late_change_2_4',np.mean([delta(k) for k in range(2,5)],axis=0)),('post_minus_pre',np.mean([level(k) for k in range(1,5)],axis=0)-pre)]:add(name,name,np.nan,v)
  for name,kk in [('pretrend',[k for k in ks if k<-1]),('post_joint_0_4',list(range(5))),('post_joint_1_4',list(range(1,5))),('late_joint_2_4',list(range(2,5)))]:
   R=np.vstack([delta(k) for k in kk]);vv=R@V@R.T;rr=int(np.linalg.matrix_rank(vv,tol=1e-9));bb=R@b;FF=float(bb@np.linalg.pinv(vv,rcond=1e-10)@bb/rr)
   jrows.append({**meta,'test':name,'F':FF,'df_num':rr,'p':float(f.sf(FF,rr,meta['df']))})
   for j,v in enumerate(R):
    for nm,w in zip(cn,v):
     if w:jointcons.append(dict(model_id=mid,test=name,equation=j,term=nm,weight=w))
  q=d[['person_id','year','province_code','provyear','Y','C_any','age2','tenure','tenure2','base_rank','role_secretary','k']+econ].copy();q['model_id']=mid
  for i,nm in enumerate(cn[1:]):q[nm]=XX[:,i+1]
  for i,nm in enumerate(dn):q[nm]=dd[:,i]
  panels.append(q)
  print(mid,meta['window'],fe,'N',len(d),flush=True)

R=pd.DataFrame(rows);J=pd.DataFrame(jrows);M=pd.DataFrame(models);C=pd.DataFrame(cons);JC=pd.DataFrame(jointcons)
for name,d in [('coefficients.csv',R),('joint_tests.csv',J),('models.csv',M),('contrast_design.csv',C),('joint_design.csv',JC),('support.csv',pd.DataFrame(support)),('failures.csv',pd.DataFrame(fails,columns=['model_id','L','fe','reason']))]:d.to_csv(OUT/name,index=False,encoding='utf-8-sig')
if excluded:pd.concat(excluded).to_csv(OUT/'singleton_exclusions.csv.gz',index=False)
pd.concat(panels).to_stata(OUT/'stata_panel.dta',write_index=False,version=118)
def expression(d):return ' + '.join(f'{r.weight:.17g}*{r.term}' for r in d.itertuples())
lines=['version 18','clear all','set more off','set processors 2',f'local out "{OUT.as_posix()}"',f'adopath ++ "{(BASE.parent.parent/"code/vendor/pz_boottest").as_posix()}"','capture log close','log using "`out\'/validation.log", text replace','tempname res jr','postfile `res\' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out\'/stata_validation.dta", replace','postfile `jr\' long model_id str32 test double F df_num p p_wild boot_rc using "`out\'/stata_joint.dta", replace']
for m in M.itertuples():
 tt=C[C.model_id.eq(m.model_id)].term.drop_duplicates().tolist();ev=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in range(-m.L,5) if k!=-1]
 cmd='quietly areg Y '+' '.join(tt+ev)+' age2 tenure tenure2 i.base_rank i.role_secretary '+(' '.join(econ)+' ' if m.economic_controls else '')+('i.year' if m.fe=='I_YEAR' else 'i.py')+', absorb(person_id) vce(cluster province_code)'
 lines+=['use "`out\'/stata_panel.dta", clear',f'keep if model_id=={m.model_id}','isid person_id year','egen py=group(province_code year)',cmd,'local nn=e(N)','quietly _ms_omit_info e(b)','local kk=e(df_a)+colsof(e(b))-r(k_omit)','local gg=e(N_clust)','local df=e(df_r)']
 for name,d in C[C.model_id.eq(m.model_id)].groupby('contrast',sort=False):
  ee=expression(d)
  lines += [f'quietly lincom {ee}, level(95)','local bb=r(estimate)','local ss=r(se)','local pp=r(p)','local ll=r(lb)','local hh=r(ub)','local pw=.','local rc=.']
  if name=='post_change_1_4':lines += [f'capture quietly boottest ({ee}=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `res\' ({m.model_id}) ("{name}") (`bb\') (`ss\') (`pp\') (`ll\') (`hh\') (`nn\') (`kk\') (`gg\') (`df\') (`pw\') (`rc\')']
 for name,d in JC[JC.model_id.eq(m.model_id)].groupby('test',sort=False):
  ee=' '.join('('+expression(g)+'=0)' for _,g in d.groupby('equation'))
  lines += [f'quietly test {ee}','local ff=r(F)','local dn=r(df)','local pp=r(p)','local pw=.','local rc=.']
  if name=='post_joint_1_4':lines += [f'capture quietly boottest {ee}, cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','if `rc\'==0 local pw=r(p)']
  lines += [f'post `jr\' ({m.model_id}) ("{name}") (`ff\') (`dn\') (`pp\') (`pw\') (`rc\')']
lines+=['postclose `res\'','postclose `jr\'','log close','exit, clear']
(OUT/'code/validate.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name);shutil.copy2(helper,OUT/'code'/helper.name)
pd.DataFrame([dict(path=str(BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz'),sha256=hashlib.sha256((BASE/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz').read_bytes()).hexdigest())]).to_csv(OUT/'input_manifest.csv',index=False)
assert len(M)==4 and M.groupby('L').N.nunique().eq(1).all() and not fails
assert M.FE_group_mean_error.lt(1e-6).all()
print(R[R.estimand.eq('post_change_1_4')][['window','fe','N','b','p','lo','hi']].to_string(index=False))
