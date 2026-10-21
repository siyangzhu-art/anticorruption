from pathlib import Path
import pandas as pd,shutil
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'cumulative_promotion_TWFE_12_24_36m'
p=O/'code/run_TWFE.do';s=p.read_text(encoding='utf8');s=s.replace('pretrend_placeholder','K').replace("(`NN') (`GG') (`DD') (.)","(`NN') (`GG') (`DD') (e(df_m)+e(df_a))");p.write_text(s,encoding='utf8')
M=pd.read_csv(O/'model_design.csv');L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/FD_validation.log", text replace','tempname rr ww','postfile `rr\' long model_id double(b se p N G) using "`out\'/FD_validation.dta", replace','postfile `ww\' long model_id double(p_wild reps) long rc using "`out\'/wild_cluster_tests.dta", replace']
for m in M.itertuples():
 c='' if m.control=='none' else 'age0 age20 tenure0 tenure20 i.rank0 role0'+(' growth0 lngdppc0 lnpop0' if m.control=='full' else '')
 if m.fe=='I_CALENDAR':c+=' i.end_year0'
 if m.fe=='I_PXY':c+=' i.prov'
 L += [f'use "`out\'/data/{m.filename}", clear','keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0','reshape wide Y end_year, i(person_id) j(post)','gen deltaY=Y1-Y0','egen prov=group(anchor_province)','quietly regress deltaY C0 '+c+', vce(cluster anchor_province)',f'post `rr\' ({m.model_id}) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))']
 if m.sample=='common_all_H' and m.control=='full' and m.fe=='I_PXY':
  L += ['capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph','local rc=_rc',f'if `rc\'==0 post `ww\' ({m.model_id}) (r(p)) (9999) (`rc\')',f'if `rc\'!=0 post `ww\' ({m.model_id}) (.) (9999) (`rc\')']
L += ['postclose `rr\'','postclose `ww\'','log close','exit, clear'];(O/'code/run_FD_validation.do').write_text('\n'.join(L)+'\n',encoding='utf8');shutil.copy2(__file__,O/'code'/Path(__file__).name)
print(f'Prepared independent first-difference validation for all {len(M)} TWFE models; 3 main wild tests.')
