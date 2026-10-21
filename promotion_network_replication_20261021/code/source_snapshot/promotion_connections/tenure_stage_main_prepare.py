"""Same-sample tenure specification: quadratic vs tenure-stage by official role."""
from pathlib import Path
import sys,shutil,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');S=B/'control_FE_sensitivity_post4';O=B/'tenure_stage_main_effect_all_methods'
for p in [O,O/'code',O/'figures',O/'data']:p.mkdir(exist_ok=True)
def save(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')
def stage(x):
 assert x.notna().all() and x.ge(0).all()
 return np.floor(x).clip(upper=5).astype(int)
annual=pd.read_csv(B/'annual_official_panel.csv.gz',low_memory=False)
actual=(pd.to_datetime(annual.baseline_date)-pd.to_datetime(annual.city_spell_start)).dt.days/365.2425
assert np.allclose(actual,annual.tenure,atol=1e-10)
save(annual[['person_id','name','year','baseline_date','city_spell_start','tenure','tenure2']].assign(recomputed_tenure=actual,tenure_stage=stage(annual.tenure)),'tenure_date_audit.csv')
EC='gdp_growth_lag lngdppc_lag lnpop_lag';BASEEC='base_growth base_lngdppc base_lnpop'
configs=[dict(tenure_spec='quadratic',annual_controls='age2 tenure tenure2 i.base_rank i.role_secretary '+EC,lp_controls='base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role '+BASEEC),dict(tenure_spec='stage_only',annual_controls='age2 i.tenure_stage i.role_secretary i.base_rank '+EC,lp_controls='base_age base_age2 i.base_stage i.base_role i.base_rank '+BASEEC)]
fes=[('I_YEAR','person_id year'),('I_PXY','person_id py'),('I_CITY_YEAR','person_id city_code year'),('I_CITY_PXY','person_id city_code py')]
models=[];mid=0;counts=[]
for sample in ['fixed','dynamic']:
 a=pd.read_stata(S/f'{sample}_panel.dta');a['tenure_stage']=stage(a.tenure);a.to_stata(O/f'data/{sample}_panel.dta',write_index=False,version=118)
 for (s,r),g in a.groupby(['tenure_stage','role_secretary']):counts.append(dict(sample=sample,tenure_stage=s,role=r,N=len(g),promotions=int(g.Y.gt(0).sum())))
 for fe,absorb in fes:
  for config in configs:
   mid+=1;models.append(dict(model_id=mid,sample=sample,fe=fe,absorb=absorb,N=len(a),G=a.anchor_province.nunique(),**config))
save(pd.DataFrame(models),'annual_model_design.csv');save(pd.DataFrame(counts),'annual_stage_role_counts.csv')
KS=[-4,-3,-2,0,1,2,3,4];NS=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in KS]
L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/annual.log", text replace','tempname rr jj mm vv ww cc ff',
'postfile `rr\' long model_id str16 estimator str24 term double(b se p lo hi) using "`out\'/annual_results.dta", replace',
'postfile `jj\' long model_id str16 estimator str24 test double(F df_num p) using "`out\'/annual_joint.dta", replace',
'postfile `mm\' long model_id str16 estimator double(N G df) using "`out\'/annual_stats.dta", replace',
'postfile `vv\' long model_id str16 estimator str16 term1 str16 term2 double value using "`out\'/annual_covariances.dta", replace',
'postfile `ww\' long model_id long cohort str16 term double weight using "`out\'/SA_weights.dta", replace',
'postfile `cc\' long model_id long cohort str16 term double b using "`out\'/SA_cohort_points.dta", replace',
'postfile `ff\' long model_id str16 estimator long rc using "`out\'/annual_failures.dta", replace']
def store(mid,est):
 z=[f'post `mm\' ({mid}) ("{est}") (`NN\') (`GG\') (`DD\')','matrix VV=e(V)']
 for n in NS:
  z += [f'quietly lincom {n}, level(95)',f'post `rr\' ({mid}) ("{est}") ("{n}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
 for name,expr in [('post_average','(d_p1+d_p2+d_p3+d_p4)/4'),('late_average','(d_p2+d_p3+d_p4)/3')]:
  z += [f'quietly lincom {expr}, level(95)',f'post `rr\' ({mid}) ("{est}") ("{name}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
 for name,expr in [('pretrend','d_m4 d_m3 d_m2'),('post_joint','d_p1 d_p2 d_p3 d_p4')]:
  z += [f'quietly test {expr}',f'post `jj\' ({mid}) ("{est}") ("{name}") (r(F)) (r(df)) (r(p))']
 for i,n1 in enumerate(NS,1):
  for j,n2 in enumerate(NS,1):z += [f'post `vv\' ({mid}) ("{est}") ("{n1}") ("{n2}") (VV[{i},{j}])']
 return z
for m in models:
 mid=m['model_id'];L += [f'use "`out\'/data/{m["sample"]}_panel.dta", clear','egen py=group(anchor_province year)','isid person_id year']
 for n,k in zip(NS,KS):L += [f'gen double all_{n}=(k=={k})',f'gen double {n}=(k=={k})*'+('C0' if m['sample']=='fixed' else 'C_any')]
 cov=m['annual_controls']+(' '+' '.join('all_'+n for n in NS) if m['fe'] in ['I_YEAR','I_CITY_YEAR'] else '')
 if m['sample']=='fixed':
  L += ['capture noisily eventstudyinteract Y '+' '.join(NS)+f', cohort(treated_cohort) control_cohort(never) absorb({m["absorb"]}) vce(cluster anchor_province) covariates({cov})','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) ("Sun_Abraham") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)',f'assert `NN\'=={m["N"]}','matrix BI=e(b_iw)','matrix VI=e(V_iw)','matrix WI=e(ff_w)','matrix CI=e(b_interact)']
  for i,n in enumerate(NS,1):
   for j,g in enumerate([2013,2014],1):L += [f'post `ww\' ({mid}) ({g}) ("{n}") (WI[{j},{i}])',f'post `cc\' ({mid}) ({g}) ("{n}") (CI[{j},{i}])']
  L += ['ereturn post BI VI, obs(`NN\') dof(`DD\')']+store(mid,'Sun_Abraham')+['}']
 est='TWFE_'+m['sample']
 L += ['capture noisily reghdfe Y '+' '.join(NS)+(' C_any' if m['sample']=='dynamic' else '')+' '+cov+f', absorb({m["absorb"]}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) ("{est}") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)',f'assert `NN\'=={m["N"]}','matrix BT=J(1,8,.)','matrix VT=J(8,8,.)']
 for i,n1 in enumerate(NS,1):
  L += [f'assert _se[{n1}]>0',f'matrix BT[1,{i}]=_b[{n1}]']
  for j,n2 in enumerate(NS,1):L += [f'matrix VT[{i},{j}]=e(V)[rownumb(e(V),"{n1}"),colnumb(e(V),"{n2}")]']
 L += ['matrix colnames BT='+' '.join(NS),'matrix colnames VT='+' '.join(NS),'matrix rownames VT='+' '.join(NS),'ereturn post BT VT, obs(`NN\') dof(`DD\')']+store(mid,est)+['}']
L += ['postclose `rr\'','postclose `jj\'','postclose `mm\'','postclose `vv\'','postclose `ww\'','postclose `cc\'','postclose `ff\'','log close','exit, clear'];(O/'code/run_annual.do').write_text('\n'.join(L)+'\n',encoding='utf8')

T=pd.read_stata(S/'lpdid_panel.dta');T['base_stage']=stage(T.base_tenure);T.to_stata(O/'data/lpdid_panel.dta',write_index=False,version=118)
Q=pd.read_csv(S/'horizon_pairs.csv.gz');Q['base_stage']=stage(Q.base_tenure);Q['base_stage_role']=Q.base_stage*2+Q.base_role.astype(int);Q.to_csv(O/'data/horizon_pairs.csv.gz',index=False)
lpmodels=[];manual=[];support=[];scores=[];mid=0
P=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/LPDID.log", text replace','tempname rr ff','postfile `rr\' long model_id str16 term double(b se p lo hi N) using "`out\'/LPDID_results.dta", replace','postfile `ff\' long model_id long rc using "`out\'/LPDID_failures.dta", replace']
for fe in ['cohort','province']:
 for config in configs:
  mid+=1;lpmodels.append(dict(model_id=mid,fe=fe,**config))
  for h,q in Q.groupby('h'):
   cat='anchor_province' if fe=='province' else 'G0';cc=['base_age','base_age2','base_growth','base_lngdppc','base_lnpop']+(['base_tenure','base_tenure2','base_role'] if config['tenure_spec']=='quadratic' else ['base_role'])
   z=np.column_stack([np.ones(len(q)),q[cc].to_numpy(),pd.get_dummies(q.base_rank0,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q[cat],drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q.base_stage,drop_first=True,dtype=float).to_numpy() if config['tenure_spec']=='stage_only' else np.empty((len(q),0))]);norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0];ctl=q.C0.eq(0).to_numpy();zr=z[ctl];bb=lstsq(zr,q.deltaY.to_numpy()[ctl],cond=1e-10)[0];u=q.deltaY.to_numpy()-z@bb;val=u[~ctl].mean();projection=z[~ctl]-z[~ctl]@np.linalg.pinv(zr,rcond=1e-10)@zr;err=float(np.max(np.abs(projection)));support.append(dict(model_id=mid,h=h,controls_rank=int(np.linalg.matrix_rank(zr)),columns=z.shape[1],max_treated_rowspace_error=err));assert err<1e-7,(mid,h,err)
   sc=np.zeros(len(q));sc[~ctl]=(u[~ctl]-val)/(~ctl).sum();sc[ctl]=-u[ctl]*(zr@np.linalg.pinv(zr.T@zr,rcond=1e-10)@z[~ctl].mean(axis=0));cs=pd.Series(sc).groupby(q.anchor_province.to_numpy()).sum()
   manual.append(dict(model_id=mid,h=h,b=val,se=np.sqrt((cs**2).sum()),N=len(q),G=q.anchor_province.nunique(),treated=int(q.C0.sum())))
   for p,ss in cs.items():scores.append(dict(model_id=mid,h=h,province=p,score=ss))
  P += ['use "`out\'/data/lpdid_panel.dta", clear','capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 '+config['lp_controls']+') cluster(anchor_province)'+(' absorb(anchor_province)' if fe=='province' else '')+' level(95) nograph','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) (`rc\')','if `rc\'==0 {','matrix RR=e(results)','local rn: rownames RR','forvalues i=1/9 {','local nm: word `i\' of `rn\'',f'post `rr\' ({mid}) ("`nm\'") (RR[`i\',1]) (RR[`i\',2]) (RR[`i\',4]) (RR[`i\',5]) (RR[`i\',6]) (RR[`i\',7])','}','}']
P += ['postclose `rr\'','postclose `ff\'','log close','exit, clear'];(O/'code/run_LPDID.do').write_text('\n'.join(P)+'\n',encoding='utf8')
save(pd.DataFrame(lpmodels),'LPDID_model_design.csv');save(pd.DataFrame(manual),'LPDID_independent.csv');save(pd.DataFrame(support),'LPDID_control_support.csv');save(pd.DataFrame(scores),'LPDID_cluster_scores.csv')
save(Q.groupby(['h','base_stage','base_role','C0']).size().rename('N').reset_index(),'baseline_stage_role_support.csv')
save(pd.DataFrame([dict(stage=i,lower_years=i,upper_years=i+1 if i<5 else np.nan,label=f'[{i},{i+1}) years' if i<5 else '5+ years') for i in range(6)]),'tenure_stage_dictionary.csv')
save(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [S/'fixed_panel.dta',S/'dynamic_panel.dta',S/'lpdid_panel.dta',S/'horizon_pairs.csv.gz',B/'annual_official_panel.csv.gz']]),'input_manifest.csv')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
print('Prepared 24 annual regressions, 4 LP-DiD models; tenure dates exactly verified for',len(annual),'rows.');print(pd.DataFrame(manual).to_string(index=False));print('Output',O)
