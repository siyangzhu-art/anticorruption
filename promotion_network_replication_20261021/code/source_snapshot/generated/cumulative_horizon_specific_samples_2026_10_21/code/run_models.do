version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/cumulative_horizon_specific_samples_2026_10_21"
capture log close
log using "`out'/estimation.log", text replace
tempname rr ww ff
postfile `rr' long model_id double(b se p lo hi N G df) using "`out'/coefficients.dta", replace
postfile `ww' long model_id double(p_wild) long rc using "`out'/wild_tests.dta", replace
postfile `ff' long model_id long rc using "`out'/failures.dta", replace
use "`out'/data/panel_Original_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (1) (`rc')
if `rc'==0 {
assert e(N)==994
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (1) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (2) (`rc')
if `rc'==0 {
assert e(N)==994
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (2) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (3) (`rc')
if `rc'==0 {
assert e(N)==994
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (3) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_12m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (3) (r(p)) (`rc')
if `rc'!=0 post `ww' (3) (.) (`rc')
use "`out'/data/panel_Strict_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (4) (`rc')
if `rc'==0 {
assert e(N)==922
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (4) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Strict_12m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (4) (r(p)) (`rc')
if `rc'!=0 post `ww' (4) (.) (`rc')
use "`out'/data/panel_Plus_discipline_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (5) (`rc')
if `rc'==0 {
assert e(N)==862
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (5) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_discipline_12m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (5) (r(p)) (`rc')
if `rc'!=0 post `ww' (5) (.) (`rc')
use "`out'/data/panel_Plus_recent_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (6) (`rc')
if `rc'==0 {
assert e(N)==764
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (6) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_recent_12m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (6) (r(p)) (`rc')
if `rc'!=0 post `ww' (6) (.) (`rc')
use "`out'/data/panel_Original_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (7) (`rc')
if `rc'==0 {
assert e(N)==932
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (7) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (8) (`rc')
if `rc'==0 {
assert e(N)==932
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (8) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (9) (`rc')
if `rc'==0 {
assert e(N)==932
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (9) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_24m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (9) (r(p)) (`rc')
if `rc'!=0 post `ww' (9) (.) (`rc')
use "`out'/data/panel_Strict_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (10) (`rc')
if `rc'==0 {
assert e(N)==866
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (10) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Strict_24m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (10) (r(p)) (`rc')
if `rc'!=0 post `ww' (10) (.) (`rc')
use "`out'/data/panel_Plus_discipline_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (11) (`rc')
if `rc'==0 {
assert e(N)==810
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (11) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_discipline_24m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (11) (r(p)) (`rc')
if `rc'!=0 post `ww' (11) (.) (`rc')
use "`out'/data/panel_Plus_recent_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (12) (`rc')
if `rc'==0 {
assert e(N)==718
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (12) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_recent_24m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (12) (r(p)) (`rc')
if `rc'!=0 post `ww' (12) (.) (`rc')
use "`out'/data/panel_Original_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP , absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (13) (`rc')
if `rc'==0 {
assert e(N)==850
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (13) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (14) (`rc')
if `rc'==0 {
assert e(N)==850
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (14) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (15) (`rc')
if `rc'==0 {
assert e(N)==850
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (15) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Original_36m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (15) (r(p)) (`rc')
if `rc'!=0 post `ww' (15) (.) (`rc')
use "`out'/data/panel_Strict_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (16) (`rc')
if `rc'==0 {
assert e(N)==792
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (16) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Strict_36m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (16) (r(p)) (`rc')
if `rc'!=0 post `ww' (16) (.) (`rc')
use "`out'/data/panel_Plus_discipline_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (17) (`rc')
if `rc'==0 {
assert e(N)==740
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (17) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_discipline_36m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (17) (r(p)) (`rc')
if `rc'!=0 post `ww' (17) (.) (`rc')
use "`out'/data/panel_Plus_recent_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (18) (`rc')
if `rc'==0 {
assert e(N)==654
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (18) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD')
}
use "`out'/data/panel_Plus_recent_36m.dta", clear
keep person_id anchor_province post Y C0 age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0
reshape wide Y, i(person_id) j(post)
gen double deltaY=Y1-Y0
egen prov=group(anchor_province)
regress deltaY C0 age0 age20 tenure0 tenure20 i.rank0 role0 growth0 lngdppc0 lnpop0 i.prov, vce(cluster anchor_province)
capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph
local rc=_rc
if `rc'==0 post `ww' (18) (r(p)) (`rc')
if `rc'!=0 post `ww' (18) (.) (`rc')
postclose `rr'
postclose `ww'
postclose `ff'
log close
exit, clear
