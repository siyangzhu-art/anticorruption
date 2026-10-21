from pathlib import Path
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'audit_main_page_methods_2026_10_21'
L=['version 18','clear all','set more off','set processors 2',f'local base "{B.as_posix()}"',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/wild24_rerun.log", text replace','which boottest','tempname ww','postfile `ww\' str12 variant double(b p_wild) long rc using "`out\'/wild24_rerun.dta", replace']
for variant in ['Original','Strict']:
 L+=['use "`base\'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta", clear']
 if variant=='Strict':L+=['drop if inlist(anchor_province,130000,350000,310000,120000,500000)']
 L+=['keep person_id anchor_province C0 post Y age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0','reshape wide Y, i(person_id) j(post)','gen double deltaY=Y1-Y0','egen prov=group(anchor_province)','regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)','local bb=_b[C0]','capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph','local rc=_rc',f'if `rc\'==0 post `ww\' ("{variant}") (`bb\') (r(p)) (`rc\')',f'if `rc\'!=0 post `ww\' ("{variant}") (`bb\') (.) (`rc\')']
L+=['postclose `ww\'','log close','exit, clear'];(O/'code/wild24_rerun.do').write_text('\n'.join(L)+'\n',encoding='utf-8')
