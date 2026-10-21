"""Audit identification and sample change from province-year to city-year FE."""
from pathlib import Path
import sys, json, shutil, hashlib, ast
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd, numpy as np
from scipy.linalg import lstsq
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu

B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'province_year_vs_city_year_audit'; O.mkdir(exist_ok=True)
for sub in ['code','figures','data']: (O/sub).mkdir(exist_ok=True)
EC=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
KS=[-4,-3,-2,0,1,2,3,4]
NS=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in KS]
def save(a,n):a.to_csv(O/n,index=False,encoding='utf-8-sig')
rawfixed=pd.read_csv(B/'with_officer_city_economics/SA_TWFE_common_sample/analysis_panel.csv.gz')
rawdynamic=pd.read_csv(B/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz')
eco=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz',usecols=['person_id','year']+EC)
rawdynamic=rawdynamic.drop(columns=EC).merge(eco,on=['person_id','year'],validate='1:1')
rawdynamic=rawdynamic[rawdynamic.k.between(-4,4)].dropna(subset=EC).copy()
rawdynamic['anchor_province']=rawdynamic.province_code
for a in [rawfixed,rawdynamic]:
 a['cy']=pd.factorize(pd.MultiIndex.from_frame(a[['city_code','year']]))[0]+1
 a['py']=pd.factorize(pd.MultiIndex.from_frame(a[['anchor_province','year']]))[0]+1
 assert not a.duplicated(['person_id','year']).any()
 assert a.groupby('cy').anchor_province.nunique().max()==1

def core(a,fe):
 dropped=[];a=a.copy()
 for step in range(100):
  si=a.groupby('person_id').person_id.transform('size').eq(1)
  sf=a.groupby(fe)[fe].transform('size').eq(1)
  bad=si|sf
  if not bad.any():return a,pd.concat(dropped,ignore_index=True) if dropped else a.iloc[:0]
  dropped.append(a[bad].assign(drop_step=step,singleton_person=si[bad],singleton_cell=sf[bad]));a=a[~bad].copy()
 raise RuntimeError('nonconvergent singleton removal')

ns=globals(); tree=ast.parse(Path(__file__).with_name('event_study_individual_FE.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='fe_project'],type_ignores=[]),'helper','exec'),ns)
stats=[]; cells=[];supports=[];idchecks=[];models=[];all_exclusions=[]; mid=0
for sample,raw in [('fixed',rawfixed),('dynamic',rawdynamic)]:
 c='C0' if sample=='fixed' else 'C_any'
 p,pdrop=core(raw,'py'); q,qdrop=core(raw,'cy')
 # cy is nested in py, so the city-year core is the common support.
 assert set(zip(q.person_id,q.year))<=set(zip(p.person_id,p.year))
 for stage,a in [('input',raw),('PXY_max',p),('CXY_max_common',q)]:
  g=a.groupby('cy'); cc=g.agg(n=('person_id','size'),people=('person_id','nunique'),cmin=(c,'min'),cmax=(c,'max'),roles=('role_secretary','nunique'),promotions=('Y',lambda x:(x>0).sum()),year=('year','first'),city_code=('city_code','first'),k=('k','first'),province=('anchor_province','first'))
  cc['discordant']=cc.cmin.ne(cc.cmax);cc['sample']=sample;cc['stage']=stage;cells.append(cc.reset_index())
  stats.append(dict(sample=sample,stage=stage,N=len(a),people=a.person_id.nunique(),cities=a.city_code.nunique(),G=a.anchor_province.nunique(),city_year_cells=len(cc),single_city_year_cells=int(cc.n.eq(1).sum()),two_city_year_cells=int(cc.n.eq(2).sum()),more_than_two_cells=int(cc.n.gt(2).sum()),discordant_city_year_cells=int(cc.discordant.sum()),rows_in_discordant_cells=int(cc.loc[cc.discordant,'n'].sum()),promotion_events=int(a.Y.gt(0).sum()),connected_observations=int(a[c].sum())))
  for k,d in a.groupby('k'):
   dc=cc[cc.k.eq(k)]
   supports.append(dict(sample=sample,stage=stage,k=k,N=len(d),G=d.anchor_province.nunique(),connected=int(d[c].sum()),discordant_cells=int(dc.discordant.sum()),discordant_provinces=int(dc.loc[dc.discordant,'province'].nunique()),promotions=int(d.Y.gt(0).sum())))
 for fe,ex in [('PXY',pdrop),('CXY',qdrop)]:
  ex=ex.assign(sample=sample,fe=fe);all_exclusions.append(ex)
 for label,a in [('PXY_max',p),('CXY_max',q),('common',q)]:
  use=['I_PXY'] if label=='PXY_max' else ['I_CXY'] if label=='CXY_max' else ['I_PXY','I_CXY']
  cols=['person_id','year','city_code','anchor_province','Y','k','age2','tenure','tenure2','base_rank','role_secretary','py','cy']+EC+([c,'G0','never','treated_cohort'] if sample=='fixed' else [c])
  a[cols].to_stata(O/f'data/{sample}_{label}.dta',write_index=False,version=118)
  for fe in use:
   for control in ['personal','full']:
    mid+=1;fcol='py' if fe=='I_PXY' else 'cy'
    models.append(dict(model_id=mid,sample=sample,comparison=label,fe=fe,control=control,N_expected=len(a),data=f'{sample}_{label}.dta',connection=c))
    target=np.column_stack([a[c].to_numpy()*a.k.eq(k).to_numpy() for k in KS])
    if sample=='dynamic':target=np.column_stack([target,a[c].to_numpy()])
    ctrl=['age2','tenure','tenure2','role_secretary']+(EC if control=='full' else [])
    z=np.column_stack([a[ctrl].to_numpy(),pd.get_dummies(a.base_rank,drop_first=True,dtype=float).to_numpy()])
    dm,rank,comp=fe_project(np.column_stack([target,z]),[pd.factorize(a.person_id)[0],pd.factorize(a[fcol])[0]])
    x=dm[:,:target.shape[1]];z=dm[:,target.shape[1]:]; zn=np.linalg.norm(z,axis=0);z=z[:,zn>1e-8]/zn[zn>1e-8]
    resid=x-z@lstsq(z,x,cond=1e-10)[0];sv=np.linalg.svd(resid,compute_uv=False)
    econspread={e:float(a.groupby('cy')[e].agg(lambda s:s.max()-s.min()).max()) for e in EC}
    idchecks.append(dict(model_id=mid,targets=target.shape[1],target_rank=int(np.linalg.matrix_rank(resid,tol=1e-8)),min_singular_value=float(sv.min()),max_singular_value=float(sv.max()),fe_rank=rank,fe_components=comp,**{e+'_within_city_year_max_range':v for e,v in econspread.items()}))
    # Save independent FWL points and residualized-design diagnostics.
    dy,_,_=fe_project(a.Y.to_numpy()[:,None],[pd.factorize(a.person_id)[0],pd.factorize(a[fcol])[0]])
    yr=dy[:,0]-z@lstsq(z,dy[:,0],cond=1e-10)[0]
    if np.linalg.matrix_rank(resid,tol=1e-8)==target.shape[1]:
     bb=lstsq(resid,yr,cond=1e-10)[0]
     save(pd.DataFrame({'term':NS+(['C_any'] if sample=='dynamic' else []),'b':bb,'residual_norm':np.linalg.norm(resid,axis=0)}),f'data/independent_points_{mid}.csv')

M=pd.DataFrame(models);save(M,'model_design.csv');save(pd.DataFrame(stats),'sample_comparison.csv');save(pd.concat(cells),'city_year_cell_audit.csv');save(pd.DataFrame(supports),'event_time_support.csv');save(pd.DataFrame(idchecks),'identification_rank.csv');save(pd.concat(all_exclusions),'singleton_exclusions.csv.gz')
L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/estimation.log", text replace','tempname rr mm jj ff oo','postfile `rr\' long model_id str16 estimator str24 term double(b se p lo hi) using "`out\'/results.dta", replace','postfile `mm\' long model_id str16 estimator double(N G df) using "`out\'/model_stats.dta", replace','postfile `jj\' long model_id str16 estimator str20 test double(F p) using "`out\'/joint_tests.dta", replace','postfile `ff\' long model_id str16 estimator long rc using "`out\'/failures.dta", replace','postfile `oo\' long model_id str16 estimator str40 term double(b se) using "`out\'/all_parameters.dta", replace']
def store(mid,est,sa=False):
 s=['local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)',f'post `mm\' ({mid}) ("{est}") (`NN\') (`GG\') (`DD\')']
 if sa:s+=['matrix BI=e(b_iw)','matrix VI=e(V_iw)','ereturn post BI VI, obs(`NN\') dof(`DD\')']
 else:
  s+=['local pars: colnames e(b)','foreach nm of local pars {',f'post `oo\' ({mid}) ("{est}") ("`nm\'") (_b[`nm\']) (_se[`nm\'])','}']
 for n in NS:
  s += [f'capture quietly lincom {n}, level(95)','if _rc==0 {',f'post `rr\' ({mid}) ("{est}") ("{n}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))','}']
 for label,expr in [('post_average','(d_p1+d_p2+d_p3+d_p4)/4')]:
  s += [f'capture quietly lincom {expr}, level(95)','if _rc==0 {',f'post `rr\' ({mid}) ("{est}") ("{label}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))','}']
 for label,terms in [('pretrend','d_m4 d_m3 d_m2'),('post_joint','d_p1 d_p2 d_p3 d_p4')]:
  s += [f'capture quietly test {terms}','if _rc==0 {',f'post `jj\' ({mid}) ("{est}") ("{label}") (r(F)) (r(p))','}']
 return s
for m in models:
 L+= [f'use "`out\'/data/{m["data"]}", clear','isid person_id year']
 for n,k in zip(NS,KS):L += [f'gen double {n}=(k=={k})*{m["connection"]}']
 cov='age2 tenure tenure2 i.base_rank i.role_secretary'+(' '+' '.join(EC) if m['control']=='full' else '')
 f='py' if m['fe']=='I_PXY' else 'cy';est='TWFE_'+m['sample']
 L += ['capture noisily reghdfe Y '+' '.join(NS)+(' C_any' if m['sample']=='dynamic' else '')+' '+cov+f', absorb(person_id {f}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({m["model_id"]}) ("{est}") (`rc\')','if `rc\'==0 {',f'assert e(N)=={m["N_expected"]}']+store(m['model_id'],est)+['}']
 if m['sample']=='fixed':
  L += ['capture noisily eventstudyinteract Y '+' '.join(NS)+f', cohort(treated_cohort) control_cohort(never) absorb(person_id {f}) vce(cluster anchor_province) covariates({cov})','local rc=_rc',f'if `rc\'!=0 post `ff\' ({m["model_id"]}) ("Sun_Abraham") (`rc\')','if `rc\'==0 {',f'assert e(N)=={m["N_expected"]}']+store(m['model_id'],'Sun_Abraham',True)+['}']
L += ['postclose `rr\'','postclose `mm\'','postclose `jj\'','postclose `ff\'','postclose `oo\'','log close','exit, clear']
(O/'code/run_audit.do').write_text('\n'.join(L)+'\n',encoding='utf8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
save(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [B/'with_officer_city_economics/SA_TWFE_common_sample/analysis_panel.csv.gz',B/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz',B/'with_officer_city_economics/annual_economics_rematched.csv.gz']]),'input_manifest.csv')
print(pd.DataFrame(stats).to_string(index=False));print('Target rank checks:');print(pd.DataFrame(idchecks)[['model_id','targets','target_rank','min_singular_value']].to_string(index=False));print('Ready:',O)
