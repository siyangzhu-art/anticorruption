"""Prespecified full control/FE sensitivity; never retain only significant models."""
from pathlib import Path
import sys,hashlib,json,shutil,itertools
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'control_FE_sensitivity_post4';E=B/'with_officer_city_economics'
for p in [O,O/'code',O/'figures']:p.mkdir(exist_ok=True)
EC=['gdp_growth_lag','lngdppc_lag','lnpop_lag'];PERSONAL='age2 tenure tenure2 i.base_rank i.role_secretary'
configs=[dict(control_id='C00',label='FE only',personal=False,econ=[]),dict(control_id='C01',label='Personal',personal=True,econ=[]),dict(control_id='C02',label='Personal + growth',personal=True,econ=[EC[0]]),dict(control_id='C03',label='Personal + log GDPpc',personal=True,econ=[EC[1]]),dict(control_id='C04',label='Personal + log population',personal=True,econ=[EC[2]]),dict(control_id='C05',label='Personal + growth + log GDPpc',personal=True,econ=EC[:2]),dict(control_id='C06',label='Personal + growth + log population',personal=True,econ=[EC[0],EC[2]]),dict(control_id='C07',label='Personal + log GDPpc + log population',personal=True,econ=EC[1:]),dict(control_id='C08',label='Personal + all economics',personal=True,econ=EC)]
fes=[dict(fe='I_YEAR',absorb='person_id year',label='Individual + year'),dict(fe='I_PXY',absorb='person_id py',label='Individual + province x year'),dict(fe='I_CITY_YEAR',absorb='person_id city_code year',label='Individual + city + year'),dict(fe='I_CITY_PXY',absorb='person_id city_code py',label='Individual + city + province x year')]
pd.DataFrame([{**c,'econ':' '.join(c['econ'])} for c in configs]).to_csv(O/'prespecified_controls.csv',index=False,encoding='utf-8-sig');pd.DataFrame(fes).to_csv(O/'prespecified_FE.csv',index=False)
def core(a):
 dropped=[]
 for step in range(100):
  keep=pd.Series(True,index=a.index)
  for col in ['person_id','city_code','provyear']:keep&=a.groupby(col)[col].transform('size').gt(1)
  if keep.all():return a,pd.concat(dropped) if dropped else a.iloc[:0].copy()
  dropped.append(a[~keep].assign(drop_step=step));a=a[keep].copy()
 raise ValueError('singleton iteration')
fixed=pd.read_csv(E/'SA_TWFE_common_sample/analysis_panel.csv.gz')
dyn=pd.read_csv(B/'event_study_no_Xi/analysis_panel_2006_2017.csv.gz')
rematch=pd.read_csv(E/'annual_economics_rematched.csv.gz',usecols=['person_id','year']+EC)
dyn=dyn.drop(columns=EC).merge(rematch,on=['person_id','year'],validate='1:1').dropna(subset=EC);dyn=dyn[dyn.k.between(-4,4)].copy();dyn['anchor_province']=dyn.province_code
sample=[]
for name,a in [('fixed',fixed),('dynamic',dyn)]:
 d,drop=core(a);d.to_csv(O/(name+'_panel.csv.gz'),index=False);drop.to_csv(O/(name+'_singleton_exclusions.csv'),index=False)
 cols=['person_id','year','city_code','anchor_province','Y','k','age2','tenure','tenure2','base_rank','role_secretary']+EC+(['C0','G0','never','treated_cohort'] if name=='fixed' else ['C_any'])
 d[cols].to_stata(O/(name+'_panel.dta'),write_index=False,version=118);sample.append(dict(sample=name,N=len(d),people=d.person_id.nunique(),city=d.city_code.nunique(),G=d.anchor_province.nunique(),removed=len(drop)))
pd.DataFrame(sample).to_csv(O/'common_samples.csv',index=False)
ks=[-4,-3,-2,0,1,2,3,4];names=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in ks]
models=[];mid=0
for name in ['fixed','dynamic']:
 for f in fes:
  for c in configs:
   mid+=1;models.append(dict(model_id=mid,sample=name,fe=f['fe'],control_id=c['control_id'],control_label=c['label'],absorb=f['absorb'],controls=((PERSONAL+' ') if c['personal'] else '')+' '.join(c['econ'])))
pd.DataFrame(models).to_csv(O/'prespecified_models.csv',index=False)
lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/level_models.log", text replace','tempname rr jj ww cc mm vv ff',
'postfile `rr\' long model_id str16 estimator str20 term double(b se p lo hi) using "`out\'/level_results.dta", replace',
'postfile `jj\' long model_id str16 estimator str24 test double(F df_num p) using "`out\'/level_joint.dta", replace',
'postfile `ww\' long model_id long cohort str16 term double weight using "`out\'/SA_weights.dta", replace',
'postfile `cc\' long model_id long cohort str16 term double b using "`out\'/SA_cohort_points.dta", replace',
'postfile `mm\' long model_id str16 estimator double(N G df) using "`out\'/model_stats.dta", replace',
'postfile `vv\' long model_id str16 estimator str16 term1 str16 term2 double value using "`out\'/level_covariances.dta", replace',
'postfile `ff\' long model_id str16 estimator long rc using "`out\'/level_failures.dta", replace']
def store(mid,est):
 z=[f'post `mm\' ({mid}) ("{est}") (`NN\') (`GG\') (`DD\')','matrix VV=e(V)']
 for nm in names:
  z += [f'quietly lincom {nm}, level(95)',f'post `rr\' ({mid}) ("{est}") ("{nm}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
 for label,ee in [('post_average','(d_p1+d_p2+d_p3+d_p4)/4'),('late_average','(d_p2+d_p3+d_p4)/3')]:z += [f'quietly lincom {ee}, level(95)',f'post `rr\' ({mid}) ("{est}") ("{label}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
 for name,ee in [('pretrend','d_m4 d_m3 d_m2'),('post_joint','d_p1 d_p2 d_p3 d_p4')]:z += [f'quietly test {ee}',f'post `jj\' ({mid}) ("{est}") ("{name}") (r(F)) (r(df)) (r(p))']
 for i,n1 in enumerate(names,1):
  for j,n2 in enumerate(names,1):z += [f'post `vv\' ({mid}) ("{est}") ("{n1}") ("{n2}") (VV[{i},{j}])']
 return z
for m in models:
 lines += ['use "`out\'/'+m['sample']+'_panel.dta", clear','isid person_id year','egen py=group(anchor_province year)','local initialN=_N']
 for nm,k in zip(names,ks):
  lines += [f'gen double all_{nm}=(k=={k})',f'gen double {nm}=(k=={k})*'+('C0' if m['sample']=='fixed' else 'C_any')]
 # Event main effects are absorbed by province-year, otherwise explicitly controlled.
 cov=m['controls']+(' '+' '.join('all_'+n for n in names) if m['fe'] in ['I_YEAR','I_CITY_YEAR'] else '')
 if m['sample']=='fixed':
  cmd='eventstudyinteract Y '+' '.join(names)+f', cohort(treated_cohort) control_cohort(never) absorb({m["absorb"]}) vce(cluster anchor_province)'+(f' covariates({cov})' if cov.strip() else '')
  lines += ['capture noisily '+cmd,'local rc=_rc',f'if `rc\'!=0 post `ff\' ({m["model_id"]}) ("Sun_Abraham") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','assert `NN\'==`initialN\'','matrix BI=e(b_iw)','matrix VI=e(V_iw)','matrix WI=e(ff_w)','matrix CI=e(b_interact)']
  for i,nm in enumerate(names,1):
   for j,g in enumerate([2013,2014],1):lines += [f'post `ww\' ({m["model_id"]}) ({g}) ("{nm}") (WI[{j},{i}])',f'post `cc\' ({m["model_id"]}) ({g}) ("{nm}") (CI[{j},{i}])']
  lines += ['ereturn post BI VI, obs(`NN\') dof(`DD\')']+store(m['model_id'],'Sun_Abraham')+['}']
 cmd='reghdfe Y '+' '.join(names)+(' C_any' if m['sample']=='dynamic' else '')+' '+cov+f', absorb({m["absorb"]}) vce(cluster anchor_province)'
 est='TWFE_fixed' if m['sample']=='fixed' else 'TWFE_dynamic'
 lines += ['capture noisily '+cmd,'local rc=_rc',f'if `rc\'!=0 post `ff\' ({m["model_id"]}) ("{est}") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','assert `NN\'==`initialN\'','matrix BT=J(1,8,.)','matrix VT=J(8,8,.)']
 for i,n1 in enumerate(names,1):
  lines += [f'matrix BT[1,{i}]=_b[{n1}]']
  for j,n2 in enumerate(names,1):lines += [f'matrix VT[{i},{j}]=e(V)[rownumb(e(V),"{n1}"),colnumb(e(V),"{n2}")]']
 lines += ['matrix colnames BT='+' '.join(names),'matrix colnames VT='+' '.join(names),'matrix rownames VT='+' '.join(names),'ereturn post BT VT, obs(`NN\') dof(`DD\')']+store(m['model_id'],est)+['}']
lines += ['postclose `rr\'','postclose `jj\'','postclose `ww\'','postclose `cc\'','postclose `mm\'','postclose `vv\'','postclose `ff\'','log close','exit, clear']
(O/'code/run_level_models.do').write_text('\n'.join(lines)+'\n',encoding='utf8')

# LP-DiD: keep the baseline economic-complete, clean-province comparison sample.
lp_panel=pd.read_stata(E/'LPDID_DoubleML_common_sample/lpdid_panel.dta');lp_panel.to_stata(O/'lpdid_panel.dta',write_index=False,version=118)
q=pd.read_csv(E/'LPDID_DoubleML_common_sample/horizon_pairs.csv.gz');q.to_csv(O/'horizon_pairs.csv.gz',index=False)
ecmap=dict(zip(EC,['base_growth','base_lngdppc','base_lnpop']))
lp_models=[];manual=[];mid=0
lp_lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/LPDID_models.log", text replace','tempname rr ff','postfile `rr\' long model_id str16 term double(b se p lo hi N) using "`out\'/LPDID_results.dta", replace','postfile `ff\' long model_id long rc using "`out\'/LPDID_failures.dta", replace']
for fe in ['cohort','province']:
 for c in configs:
  mid+=1;econ=[ecmap[x] for x in c['econ']];ctrl=('base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role ' if c['personal'] else '')+' '.join(econ)
  lp_models.append(dict(model_id=mid,fe=fe,control_id=c['control_id'],control_label=c['label'],personal=c['personal'],economic_controls=' '.join(econ)))
  for h,g in q.groupby('h'):
   col=(['base_age','base_age2','base_tenure','base_tenure2','base_role'] if c['personal'] else [])+econ
   z=np.column_stack([np.ones(len(g)),g[col].to_numpy(),pd.get_dummies(g.base_rank0,drop_first=True,dtype=float).to_numpy() if c['personal'] else np.empty((len(g),0)),pd.get_dummies(g['anchor_province' if fe=='province' else 'G0'],drop_first=True,dtype=float).to_numpy()]);norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0];ctl=g.C0.eq(0).to_numpy();bb=lstsq(z[ctl],g.deltaY.to_numpy()[ctl],cond=1e-10)[0];u=g.deltaY.to_numpy()-z@bb;val=u[~ctl].mean();score=np.zeros(len(g));score[~ctl]=(u[~ctl]-val)/(~ctl).sum();score[ctl]=-u[ctl]*(z[ctl]@np.linalg.pinv(z[ctl].T@z[ctl],rcond=1e-10)@z[~ctl].mean(axis=0));cs=pd.Series(score).groupby(g.anchor_province.to_numpy()).sum()
   manual.append(dict(model_id=mid,h=h,b=val,se=float(np.sqrt((cs**2).sum())),N=len(g),G=g.anchor_province.nunique(),treated=int(g.C0.sum())))
  lp_lines += ['use "`out\'/lpdid_panel.dta", clear','capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 '+ctrl+') cluster(anchor_province)'+(' absorb(anchor_province)' if fe=='province' else '')+' level(95) nograph','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) (`rc\')','if `rc\'==0 {','matrix RR=e(results)','local rn: rownames RR','forvalues i=1/9 {','local nm: word `i\' of `rn\'',f'post `rr\' ({mid}) ("`nm\'") (RR[`i\',1]) (RR[`i\',2]) (RR[`i\',4]) (RR[`i\',5]) (RR[`i\',6]) (RR[`i\',7])','}','}']
lp_lines += ['postclose `rr\'','postclose `ff\'','log close','exit, clear'];(O/'code/run_LPDID_models.do').write_text('\n'.join(lp_lines)+'\n',encoding='utf8')
pd.DataFrame(lp_models).to_csv(O/'prespecified_LPDID_models.csv',index=False);pd.DataFrame(manual).to_csv(O/'LPDID_independent_points_SE.csv',index=False)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [E/'SA_TWFE_common_sample/analysis_panel.csv.gz',E/'annual_economics_rematched.csv.gz',E/'LPDID_DoubleML_common_sample/horizon_pairs.csv.gz']]).to_csv(O/'input_manifest.csv',index=False)
print(pd.DataFrame(sample).to_string(index=False));print('Level regressions planned:108; LP-DiD models planned:18')
