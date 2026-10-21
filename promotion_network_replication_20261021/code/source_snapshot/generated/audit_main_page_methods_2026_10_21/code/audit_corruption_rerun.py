from pathlib import Path
import pandas as pd
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'audit_main_page_methods_2026_10_21'
L=['version 18','clear all','set more off','set processors 2',f'local base "{B.as_posix()}"',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/corruption_rerun.log", text replace','tempname rr','postfile `rr\' str16 variant str20 method str20 fe double(b se p lo hi N G) using "`out\'/corruption_rerun.dta", replace']
terms=['d_m4','d_m3','d_m2','d_p0','d_p1','d_p2','d_p3','d_p4']
for fe,absorb in [('I_YEAR','person_id year'),('I_PXY','person_id py'),('I_CITY_YEAR','person_id city_code year'),('I_CITY_PXY','person_id city_code py')]:
 L+=['use "`base\'/control_FE_sensitivity_post4/fixed_panel.dta", clear','drop if inlist(anchor_province,130000,350000,310000,120000,500000)','egen py=group(anchor_province year)']
 for k,n in zip([-4,-3,-2,0,1,2,3,4],terms):L += [f'gen double {n}=(k=={k})*C0',f'gen double all_{n}=(k=={k})']
 cov='age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag'+(' '+' '.join('all_'+n for n in terms) if fe in ['I_YEAR','I_CITY_YEAR'] else '')
 for method in ['TWFE_fixed','Sun_Abraham']:
  cmd='reghdfe Y '+' '.join(terms)+' '+cov+f', absorb({absorb}) vce(cluster anchor_province)' if method=='TWFE_fixed' else 'eventstudyinteract Y '+' '.join(terms)+f', cohort(treated_cohort) control_cohort(never) absorb({absorb}) covariates({cov}) vce(cluster anchor_province)'
  L += [cmd,'local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)']
  if method=='Sun_Abraham':L += ['matrix BI=e(b_iw)','matrix VI=e(V_iw)','ereturn post BI VI, obs(`NN\') dof(`DD\')']
  L+=['quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)',f'post `rr\' ("Strict") ("{method}") ("{fe}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\')']
for variant,provs in [('Strict',[130000,350000,310000,120000,500000]),('Plus_discipline',[130000,350000,310000,120000,500000,510000]),('Plus_recent',[130000,350000,310000,120000,500000,510000,210000,620000])]:
 L += ['use "`base\'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta", clear','drop if inlist(anchor_province,'+','.join(map(str,provs))+')','reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)','local NN=e(N)','local GG=e(N_clust)','quietly lincom CP, level(95)',f'post `rr\' ("{variant}") ("cumulative24m") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\')']
L+=['postclose `rr\'','log close','exit, clear'];(O/'code/corruption_rerun.do').write_text('\n'.join(L)+'\n',encoding='utf-8')
f=pd.read_csv(B/'control_FE_sensitivity_post4/fixed_panel.csv.gz');c=pd.read_stata(B/'cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta')
d=[]
for name,q in [('Annual',f),('Cumulative24m',c)]:
 z=q[q.anchor_province.isin([130000,350000,310000,120000,500000])];d.append(dict(sample=name,removed_rows=len(z),removed_officials=z.person_id.nunique(),removed_connected_officials=z[z.C0.eq(1)].person_id.nunique()))
pd.DataFrame(d).to_csv(O/'data/strict_exclusion_which_group.csv',index=False,encoding='utf-8-sig');print(pd.DataFrame(d).to_string(index=False))
