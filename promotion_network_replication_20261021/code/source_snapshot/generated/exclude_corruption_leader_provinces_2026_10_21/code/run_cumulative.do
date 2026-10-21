version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/exclude_corruption_leader_provinces_2026_10_21"
capture log close
log using "`out'/cumulative.log", text replace
tempname rr ff ww vv
postfile `rr' long model_id double(b se p lo hi N G df K) using "`out'/cumulative_results.dta", replace
postfile `ff' long model_id long rc using "`out'/cumulative_failures.dta", replace
postfile `ww' long model_id double(p_wild) long rc using "`out'/cumulative_wild.dta", replace
postfile `vv' long model_id double b using "`out'/cumulative_FD_points.dta", replace
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (1) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (1) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (1) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (2) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (2) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (2) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (3) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (3) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (3) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (4) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (4) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (4) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (5) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (5) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (5) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (6) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (6) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (6) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (7) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (7) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (7) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (8) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (8) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (8) (_b[C0])
use "`out'/data/cumulative_Original_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (9) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (9) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (9) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (9) (r(p)) (`rc')
if `rc'!=0 post `ww' (9) (.) (`rc')
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (10) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (10) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (10) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (11) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (11) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (11) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (12) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (12) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (12) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (13) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (13) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (13) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (14) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (14) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (14) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (15) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (15) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (15) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (16) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (16) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (16) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (17) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (17) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (17) (_b[C0])
use "`out'/data/cumulative_Original_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (18) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (18) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (18) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (18) (r(p)) (`rc')
if `rc'!=0 post `ww' (18) (.) (`rc')
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (19) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (19) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (19) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (20) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (20) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (20) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (21) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (21) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (21) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (22) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (22) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (22) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (23) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (23) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (23) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (24) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (24) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (24) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (25) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (25) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (25) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (26) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (26) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (26) (_b[C0])
use "`out'/data/cumulative_Original_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (27) (`rc')
if `rc'==0 {
assert e(N)==844
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (27) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Original_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (27) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (27) (r(p)) (`rc')
if `rc'!=0 post `ww' (27) (.) (`rc')
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (28) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (28) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (28) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (29) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (29) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (29) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (30) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (30) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (30) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (31) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (31) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (31) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (32) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (32) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (32) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (33) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (33) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (33) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (34) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (34) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (34) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (35) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (35) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (35) (_b[C0])
use "`out'/data/cumulative_Strict_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (36) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (36) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (36) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (36) (r(p)) (`rc')
if `rc'!=0 post `ww' (36) (.) (`rc')
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (37) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (37) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (37) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (38) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (38) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (38) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (39) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (39) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (39) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (40) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (40) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (40) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (41) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (41) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (41) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (42) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (42) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (42) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (43) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (43) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (43) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (44) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (44) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (44) (_b[C0])
use "`out'/data/cumulative_Strict_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (45) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (45) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (45) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (45) (r(p)) (`rc')
if `rc'!=0 post `ww' (45) (.) (`rc')
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (46) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (46) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (46) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (47) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (47) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (47) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (48) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (48) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (48) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (49) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (49) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (49) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (50) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (50) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (50) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (51) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (51) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (51) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (52) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (52) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (52) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (53) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (53) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (53) (_b[C0])
use "`out'/data/cumulative_Strict_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (54) (`rc')
if `rc'==0 {
assert e(N)==786
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (54) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Strict_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (54) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (54) (r(p)) (`rc')
if `rc'!=0 post `ww' (54) (.) (`rc')
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (55) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (55) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (55) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (56) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (56) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (56) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (57) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (57) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (57) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (58) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (58) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (58) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (59) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (59) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (59) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (60) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (60) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (60) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (61) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (61) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (61) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (62) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (62) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (62) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (63) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (63) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (63) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (63) (r(p)) (`rc')
if `rc'!=0 post `ww' (63) (.) (`rc')
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (64) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (64) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (64) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (65) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (65) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (65) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (66) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (66) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (66) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (67) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (67) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (67) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (68) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (68) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (68) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (69) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (69) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (69) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (70) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (70) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (70) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (71) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (71) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (71) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (72) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (72) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (72) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (72) (r(p)) (`rc')
if `rc'!=0 post `ww' (72) (.) (`rc')
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (73) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (73) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (73) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (74) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (74) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (74) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (75) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (75) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (75) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (76) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (76) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (76) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (77) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (77) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (77) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (78) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (78) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (78) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (79) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (79) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (79) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (80) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (80) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (80) (_b[C0])
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (81) (`rc')
if `rc'==0 {
assert e(N)==734
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (81) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_discipline_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (81) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (81) (r(p)) (`rc')
if `rc'!=0 post `ww' (81) (.) (`rc')
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (82) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (82) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (82) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (83) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (83) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (83) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (84) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (84) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (84) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (85) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (85) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (85) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (86) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (86) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (86) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (87) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (87) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (87) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (88) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (88) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (88) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (89) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (89) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (89) (_b[C0])
use "`out'/data/cumulative_Plus_recent_12.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (90) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (90) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_12.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (90) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (90) (r(p)) (`rc')
if `rc'!=0 post `ww' (90) (.) (`rc')
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (91) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (91) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (91) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (92) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (92) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (92) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (93) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (93) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (93) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (94) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (94) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (94) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (95) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (95) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (95) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (96) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (96) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (96) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (97) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (97) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (97) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (98) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (98) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (98) (_b[C0])
use "`out'/data/cumulative_Plus_recent_24.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (99) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (99) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_24.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (99) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (99) (r(p)) (`rc')
if `rc'!=0 post `ww' (99) (.) (`rc')
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (100) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (100) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 , vce(cluster anchor_province)
post `vv' (100) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (101) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (101) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0, vce(cluster anchor_province)
post `vv' (101) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (102) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (102) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0, vce(cluster anchor_province)
post `vv' (102) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (103) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (103) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.end_year0, vce(cluster anchor_province)
post `vv' (103) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (104) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (104) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.end_year0, vce(cluster anchor_province)
post `vv' (104) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (105) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (105) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.end_year0, vce(cluster anchor_province)
post `vv' (105) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (106) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (106) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0  i.prov, vce(cluster anchor_province)
post `vv' (106) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (107) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (107) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 i.prov, vce(cluster anchor_province)
post `vv' (107) (_b[C0])
use "`out'/data/cumulative_Plus_recent_36.dta", clear
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (108) (`rc')
if `rc'==0 {
assert e(N)==648
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
local KK=e(df_m)+e(df_a)
quietly lincom CP, level(95)
post `rr' (108) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (`KK')
}
use "`out'/data/cumulative_Plus_recent_36.dta", clear
keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y end_year, i(person_id) j(post)
gen deltaY=Y1-Y0
egen prov=group(anchor_province)
quietly regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
post `vv' (108) (_b[C0])
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (108) (r(p)) (`rc')
if `rc'!=0 post `ww' (108) (.) (`rc')
postclose `rr'
postclose `ff'
postclose `ww'
postclose `vv'
log close
exit, clear
