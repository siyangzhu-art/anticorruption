version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/cumulative_promotion_TWFE_12_24_36m"
capture log close
log using "`out'/TWFE.log", text replace
tempname rr ff
postfile `rr' long model_id double(b se p lo hi N G df K) using "`out'/TWFE_results.dta", replace
postfile `ff' long model_id long rc using "`out'/TWFE_failures.dta", replace
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (1) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (1) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (2) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (2) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (3) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (3) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (4) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (4) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (5) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (5) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (6) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (6) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (7) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (7) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (8) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (8) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (9) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (9) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (10) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (10) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (11) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (11) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (12) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (12) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (13) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (13) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (14) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (14) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (15) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (15) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (16) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (16) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (17) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (17) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (18) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (18) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (19) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (19) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (20) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (20) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (21) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (21) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (22) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (22) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (23) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (23) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (24) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (24) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (25) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (25) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (26) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (26) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (27) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (27) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (28) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (28) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (29) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (29) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (30) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (30) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (31) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (31) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (32) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (32) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (33) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (33) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (34) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (34) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (35) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (35) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (36) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (36) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (37) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (37) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (38) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (38) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (39) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (39) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (40) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (40) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (41) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (41) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (42) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (42) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (43) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (43) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (44) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (44) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_common_all_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (45) (`rc')
if `rc'==0 {
assert e(N)==844
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (45) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (46) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (46) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (47) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (47) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_12m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (48) (`rc')
if `rc'==0 {
assert e(N)==994
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (48) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (49) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (49) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (50) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (50) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_24m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (51) (`rc')
if `rc'==0 {
assert e(N)==932
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (51) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid post) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (52) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (52) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid end_year) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (53) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (53) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
use "`out'/data/panel_maximum_each_H_36m.dta", clear
isid person_id post
capture noisily reghdfe Y CP, absorb(pid pp) vce(cluster anchor_province)
local rc=_rc
if `rc'!=0 post `ff' (54) (`rc')
if `rc'==0 {
assert e(N)==850
assert _se[CP]>0
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom CP, level(95)
post `rr' (54) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG') (`DD') (e(df_m)+e(df_a))
}
postclose `rr'
postclose `ff'
log close
exit, clear
