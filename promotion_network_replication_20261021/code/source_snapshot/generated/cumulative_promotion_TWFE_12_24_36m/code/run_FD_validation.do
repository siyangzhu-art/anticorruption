version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/cumulative_promotion_TWFE_12_24_36m"
capture log close
log using "`out'/FD_validation.log", text replace
tempname rr ww
postfile `rr' long model_id double(b se p N G) using "`out'/FD_validation.dta", replace
postfile `ww' long model_id double(p_wild reps) long rc using "`out'/wild_cluster_tests.dta", replace
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (1) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (2) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (3) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (4) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (5) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (6) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (6) (r(p)) (9999) (`rc')
if `rc'!=0 post `ww' (6) (.) (9999) (`rc')
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (7) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (8) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (9) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (10) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (11) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (12) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (12) (r(p)) (9999) (`rc')
if `rc'!=0 post `ww' (12) (.) (9999) (`rc')
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (13) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (14) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (15) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (16) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (17) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (18) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (18) (r(p)) (9999) (`rc')
if `rc'!=0 post `ww' (18) (.) (9999) (`rc')
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (19) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (20) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (21) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (22) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (23) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (24) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (25) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (26) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (27) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (28) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (29) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (30) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `rr' (31) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `rr' (32) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `rr' (33) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `rr' (34) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `rr' (35) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `rr' (36) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (37) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (38) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (39) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (40) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (41) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (42) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (43) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (44) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_common_all_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (45) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (46) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (47) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_12m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (48) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (49) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (50) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_24m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (51) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `rr' (52) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `rr' (53) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
use "`out'/data/panel_maximum_each_H_36m.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `rr' (54) (_b[C0]) (_se[C0]) (2*ttail(e(df_r),abs(_b[C0]/_se[C0]))) (e(N)) (e(N_clust))
postclose `rr'
postclose `ww'
log close
exit, clear
