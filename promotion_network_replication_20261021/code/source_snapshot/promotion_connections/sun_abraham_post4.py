"""Actual eventstudyinteract: fixed pre-inspection network exposure, four post years."""
from pathlib import Path
import sys,ast,shutil,hashlib,json
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu
BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'sun_abraham_fixed_connection_post4'
for p in [OUT,OUT/'code',OUT/'figures']:p.mkdir(exist_ok=True)
helper=Path(__file__).with_name('event_study_individual_FE.py')
tree=ast.parse(helper.read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['common_core','fe_project','fit']],type_ignores=[]),str(helper),'exec'))
A=pd.read_csv(BASE/'annual_official_panel.csv.gz',low_memory=False)
S=A.legacy_cowork_6m_S;G=A.legacy_cowork_6m_G
A['C_dynamic']=np.where(S.eq(1)|G.eq(1),1.,np.where(S.eq(0)&G.eq(0),0.,np.nan))
anchor=A[A.k.eq(-1)].copy()
assert not anchor.duplicated('person_id').any()
anchor['anchor_unknown']=anchor.C_dynamic.isna()
anchor.to_csv(OUT/'all_preinspection_anchor_records.csv',index=False,encoding='utf-8-sig')
keep=['person_id','province_code','first_inspection_year','C_dynamic','year','baseline_date','S_person_id','G_person_id']
rename={'province_code':'anchor_province','first_inspection_year':'G0','C_dynamic':'C0','year':'anchor_year','baseline_date':'anchor_snapshot','S_person_id':'anchor_S','G_person_id':'anchor_G'}
B=anchor[~anchor.anchor_unknown][keep].rename(columns=rename)
D=A.merge(B,on='person_id',validate='m:1')
offprovince=D[D.province_code.ne(D.anchor_province)].copy();offprovince.to_csv(OUT/'excluded_outside_anchor_province.csv',index=False)
D=D[D.province_code.eq(D.anchor_province)].copy();D['k']=D.year-D.G0
D=D[D.k.between(-4,4)].copy()
required=['promotion','age2','tenure','tenure2','base_rank','role_secretary']
incomplete=D[D[required].isna().any(axis=1)].copy();incomplete.to_csv(OUT/'excluded_incomplete.csv',index=False)
D=D.dropna(subset=required).copy();D['Y']=100*D.promotion
D['C_any']=D.C0;D['never']=D.C0.eq(0).astype(int);D['treated_cohort']=D.G0.where(D.C0.eq(1));D['provyear']=D.anchor_province*10000+D.year
D,removed=common_core(D);removed.to_csv(OUT/'singleton_exclusions.csv',index=False)
assert not D.duplicated(['person_id','year']).any() and D.groupby('person_id').C0.nunique().eq(1).all()
terms=[];values=[];termkeys=[]
ks=[-4,-3,-2,0,1,2,3,4];dnames=[]
for k in ks:
 nm=f'd_m{-k}' if k<0 else f'd_p{k}';dnames.append(nm);D[nm]=(D.k.eq(k)&D.C0.eq(1)).astype(float);D['all_'+nm]=D.k.eq(k).astype(float)
 for g in [2013,2014]:
  v=(D.G0.eq(g)&D.k.eq(k)&D.C0.eq(1)).to_numpy(float)
  if not v.any():continue
  terms.append(f'z{g}_{"m"+str(-k) if k<0 else "p"+str(k)}');values.append(v);termkeys.append((g,k))
D.to_csv(OUT/'analysis_panel.csv.gz',index=False)
D[['person_id','year','anchor_province','Y','C0','never','treated_cohort','G0','age2','tenure','tenure2','base_rank','role_secretary','k']+dnames+['all_'+n for n in dnames]].to_stata(OUT/'analysis_panel.dta',write_index=False,version=118)
D.groupby(['G0','C0','k']).agg(N=('person_id','size'),people=('person_id','nunique'),provinces=('anchor_province','nunique'),promotions=('promotion','sum')).reset_index().to_csv(OUT/'event_support.csv',index=False)
point_checks=[]
for mid,fe in [(1,'I_YEAR'),(2,'I_PXY')]:
 E=np.column_stack([(D.k.eq(k)).to_numpy(float) for k in ks])
 bb,V,meta=fit(D,fe,np.column_stack(values),E)
 for (g,k),v in zip(termkeys,bb):point_checks.append(dict(model_id=mid,cohort=g,k=k,b=v))
pd.DataFrame(point_checks).to_csv(OUT/'python_cohort_point_estimates.csv',index=False)

lines=['version 18','clear all','set more off','set processors 2',f'local out "{OUT.as_posix()}"','capture log close','log using "`out\'/sun_abraham.log", text replace','which eventstudyinteract','which reghdfe','which avar','tempname res vv ww cc mm jj',
'postfile `res\' long model_id str16 method str16 term double b se p lo hi using "`out\'/coefficients.dta", replace',
'postfile `vv\' long model_id str16 method str16 term1 str16 term2 double value using "`out\'/covariances.dta", replace',
'postfile `ww\' long model_id long cohort str16 term double weight using "`out\'/weights.dta", replace',
'postfile `cc\' long model_id long cohort str16 term double b using "`out\'/cohort_coefficients.dta", replace',
'postfile `mm\' long model_id str16 method double N G df using "`out\'/models.dta", replace',
'postfile `jj\' long model_id str16 method str24 test double F df_num p using "`out\'/joint_tests.dta", replace']
for mid,fe in [(1,'I_YEAR'),(2,'I_PXY')]:
 lines+=['use "`out\'/analysis_panel.dta", clear','isid person_id year','egen py=group(anchor_province year)']
 absorb='person_id year' if fe=='I_YEAR' else 'person_id py'
 cov='age2 tenure tenure2 i.base_rank i.role_secretary'+(' '+' '.join('all_'+n for n in dnames) if fe=='I_YEAR' else '')
 lines += ['eventstudyinteract Y '+' '.join(dnames)+f', cohort(treated_cohort) control_cohort(never) absorb({absorb}) covariates({cov}) vce(cluster anchor_province)','matrix BI=e(b_iw)','matrix VI=e(V_iw)','matrix WI=e(ff_w)','matrix CI=e(b_interact)','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)']
 for i,nm in enumerate(dnames,1):
  for gi,g in enumerate([2013,2014],1):lines += [f'post `ww\' ({mid}) ({g}) ("{nm}") (WI[{gi},{i}])',f'post `cc\' ({mid}) ({g}) ("{nm}") (CI[{gi},{i}])']
 lines += ['ereturn post BI VI, obs(`NN\') dof(`DD\')']
 def results(method):
  q=[f'post `mm\' ({mid}) ("{method}") (`NN\') (`GG\') (`DD\')']
  for nm in dnames:
   q += [f'quietly lincom {nm}, level(95)',f'post `res\' ({mid}) ("{method}") ("{nm}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
  for label,ee in [('post_average','(d_p1+d_p2+d_p3+d_p4)/4'),('late_average','(d_p2+d_p3+d_p4)/3')]:q += [f'quietly lincom {ee}, level(95)',f'post `res\' ({mid}) ("{method}") ("{label}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
  for name,tt in [('pretrend','d_m4 d_m3 d_m2'),('post_joint','d_p1 d_p2 d_p3 d_p4')]:q += [f'quietly test {tt}',f'post `jj\' ({mid}) ("{method}") ("{name}") (r(F)) (r(df)) (r(p))']
  q += ['matrix VV=e(V)']
  for i,n1 in enumerate(dnames,1):
   for j,n2 in enumerate(dnames,1):q += [f'post `vv\' ({mid}) ("{method}") ("{n1}") ("{n2}") (VV[{i},{j}])']
  return q
 lines += results('Sun_Abraham')
 lines += ['reghdfe Y '+' '.join(dnames)+f' {cov}, absorb({absorb}) vce(cluster anchor_province)','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)']
 # Extract TWFE targets first to give a covariance matrix with the same ordering.
 lines += ['matrix BT=J(1,8,.)','matrix VT=J(8,8,.)']
 for i,n1 in enumerate(dnames,1):
  lines += [f'matrix BT[1,{i}]=_b[{n1}]']
  for j,n2 in enumerate(dnames,1):lines += [f'matrix VT[{i},{j}]=e(V)[rownumb(e(V),"{n1}"),colnumb(e(V),"{n2}")]']
 lines += ['matrix colnames BT='+' '.join(dnames),'matrix colnames VT='+' '.join(dnames),'matrix rownames VT='+' '.join(dnames),'ereturn post BT VT, obs(`NN\') dof(`DD\')']
 lines += results('TWFE_fixed')
lines += ['postclose `res\'','postclose `vv\'','postclose `ww\'','postclose `cc\'','postclose `mm\'','postclose `jj\'','log close','exit, clear']
(OUT/'code/run_sun_abraham.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name);shutil.copy2(helper,OUT/'code'/helper.name)
sources=[BASE/'annual_official_panel.csv.gz',Path(r'C:\Users\siyang zhu\ado\plus\e\eventstudyinteract.ado'),Path(r'C:\Users\siyang zhu\ado\plus\r\reghdfe.ado')]
pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources]).to_csv(OUT/'input_manifest.csv',index=False)
print('N',len(D),'people',D.person_id.nunique(),'connected',D[D.C0.eq(1)].person_id.nunique(),'provinces',D.anchor_province.nunique())
print(D.groupby(['G0','C0','k']).size().to_string())
