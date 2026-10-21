from pathlib import Path
import pandas as pd,shutil
O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\control_FE_sensitivity_post4')
M=pd.read_csv(O/'prespecified_models.csv').fillna('')
C=M[M['sample'].eq('fixed')&((M.control_id.eq('C08'))|(M.control_id.eq('C02')&M.fe.eq('I_CITY_YEAR')))]
C.to_csv(O/'post_search_audit_specs.csv',index=False)
names=['d_m4','d_m3','d_m2','d_p0','d_p1','d_p2','d_p3','d_p4'];ks=[-4,-3,-2,0,1,2,3,4]
lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/candidate_audit.log", text replace','tempname rr ll','postfile `rr\' long model_id str20 contrast double(b se p p_wild) long rc using "`out\'/candidate_wild.dta", replace','postfile `ll\' long model_id long removed_province str20 contrast double(b se p N) long rc using "`out\'/candidate_leave_one_province.dta", replace']
for m in C.itertuples():
 lines+=['use "`out\'/fixed_panel.dta", clear','egen py=group(anchor_province year)','egen ct=group(city_code)']
 for nm,k in zip(names,ks):lines += [f'gen double {nm}=(k=={k})*C0',f'gen double all_{nm}=(k=={k})']
 cov=m.controls+(' '+' '.join('all_'+n for n in names) if m.fe in ['I_YEAR','I_CITY_YEAR'] else '')
 cmd='quietly reghdfe Y '+' '.join(names)+' '+cov+f', absorb({m.absorb}) vce(cluster anchor_province)'
 explicit={'I_YEAR':'i.year','I_PXY':'i.py','I_CITY_YEAR':'i.ct i.year','I_CITY_PXY':'i.ct i.py'}[m.fe]
 bootcmd='quietly reghdfe Y '+' '.join(names)+' '+cov+' '+explicit+', absorb(person_id) vce(cluster anchor_province)'
 lines += [cmd]
 for label,expr in [('post_average','0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4'),('post4','d_p4')]:
  lines += [cmd,f'quietly lincom {expr}','local bb=r(estimate)','local ss=r(se)','local pp=r(p)',bootcmd,f'quietly lincom {expr}','assert abs(r(estimate)-`bb\')<0.000001',f'capture quietly boottest ({expr}=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph','local rc=_rc','local pw=.','if `rc\'==0 local pw=r(p)',f'post `rr\' ({m.model_id}) ("{label}") (`bb\') (`ss\') (`pp\') (`pw\') (`rc\')']
 if m.fe=='I_CITY_YEAR':
  lines += ['quietly levelsof anchor_province, local(provinces)','foreach p of local provinces {','preserve','drop if anchor_province==`p\'', 'capture '+cmd,'local rc=_rc','if `rc\'==0 {','local nn=e(N)']
  for label,expr in [('post_average','0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4'),('post4','d_p4')]:
   lines += [f'quietly lincom {expr}',f'post `ll\' ({m.model_id}) (`p\') ("{label}") (r(estimate)) (r(se)) (r(p)) (`nn\') (0)']
  lines += ['}','else {',f'post `ll\' ({m.model_id}) (`p\') ("failed") (.) (.) (.) (.) (`rc\')','}','restore','}']
lines+=['postclose `rr\'','postclose `ll\'','log close','exit, clear'];(O/'code/audit_candidates.do').write_text('\n'.join(lines)+'\n',encoding='utf8');shutil.copy2(__file__,O/'code'/Path(__file__).name)
print(C[['model_id','fe','control_id']].to_string(index=False))
