version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/control_FE_sensitivity_post4"
capture log close
log using "`out'/candidate_audit.log", text replace
tempname rr ll
postfile `rr' long model_id str20 contrast double(b se p p_wild) long rc using "`out'/candidate_wild.dta", replace
postfile `ll' long model_id long removed_province str20 contrast double(b se p N) long rc using "`out'/candidate_leave_one_province.dta", replace
use "`out'/fixed_panel.dta", clear
egen py=group(anchor_province year)
egen ct=group(city_code)
gen double d_m4=(k==-4)*C0
gen double all_d_m4=(k==-4)
gen double d_m3=(k==-3)*C0
gen double all_d_m3=(k==-3)
gen double d_m2=(k==-2)*C0
gen double all_d_m2=(k==-2)
gen double d_p0=(k==0)*C0
gen double all_d_p0=(k==0)
gen double d_p1=(k==1)*C0
gen double all_d_p1=(k==1)
gen double d_p2=(k==2)*C0
gen double all_d_p2=(k==2)
gen double d_p3=(k==3)*C0
gen double all_d_p3=(k==3)
gen double d_p4=(k==4)*C0
gen double all_d_p4=(k==4)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id year) vce(cluster anchor_province)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id year) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (9) ("post_average") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id year) vce(cluster anchor_province)
quietly lincom d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (9) ("post4") (`bb') (`ss') (`pp') (`pw') (`rc')
use "`out'/fixed_panel.dta", clear
egen py=group(anchor_province year)
egen ct=group(city_code)
gen double d_m4=(k==-4)*C0
gen double all_d_m4=(k==-4)
gen double d_m3=(k==-3)*C0
gen double all_d_m3=(k==-3)
gen double d_m2=(k==-2)*C0
gen double all_d_m2=(k==-2)
gen double d_p0=(k==0)*C0
gen double all_d_p0=(k==0)
gen double d_p1=(k==1)*C0
gen double all_d_p1=(k==1)
gen double d_p2=(k==2)*C0
gen double all_d_p2=(k==2)
gen double d_p3=(k==3)*C0
gen double all_d_p3=(k==3)
gen double d_p4=(k==4)*C0
gen double all_d_p4=(k==4)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id py) vce(cluster anchor_province)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id py) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, absorb(person_id) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (18) ("post_average") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id py) vce(cluster anchor_province)
quietly lincom d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, absorb(person_id) vce(cluster anchor_province)
quietly lincom d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (18) ("post4") (`bb') (`ss') (`pp') (`pw') (`rc')
use "`out'/fixed_panel.dta", clear
egen py=group(anchor_province year)
egen ct=group(city_code)
gen double d_m4=(k==-4)*C0
gen double all_d_m4=(k==-4)
gen double d_m3=(k==-3)*C0
gen double all_d_m3=(k==-3)
gen double d_m2=(k==-2)*C0
gen double all_d_m2=(k==-2)
gen double d_p0=(k==0)*C0
gen double all_d_p0=(k==0)
gen double d_p1=(k==1)*C0
gen double all_d_p1=(k==1)
gen double d_p2=(k==2)*C0
gen double all_d_p2=(k==2)
gen double d_p3=(k==3)*C0
gen double all_d_p3=(k==3)
gen double d_p4=(k==4)*C0
gen double all_d_p4=(k==4)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.ct i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (21) ("post_average") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly lincom d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.ct i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (21) ("post4") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly levelsof anchor_province, local(provinces)
foreach p of local provinces {
preserve
drop if anchor_province==`p'
capture quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
local rc=_rc
if `rc'==0 {
local nn=e(N)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
post `ll' (21) (`p') ("post_average") (r(estimate)) (r(se)) (r(p)) (`nn') (0)
quietly lincom d_p4
post `ll' (21) (`p') ("post4") (r(estimate)) (r(se)) (r(p)) (`nn') (0)
}
else {
post `ll' (21) (`p') ("failed") (.) (.) (.) (.) (`rc')
}
restore
}
use "`out'/fixed_panel.dta", clear
egen py=group(anchor_province year)
egen ct=group(city_code)
gen double d_m4=(k==-4)*C0
gen double all_d_m4=(k==-4)
gen double d_m3=(k==-3)*C0
gen double all_d_m3=(k==-3)
gen double d_m2=(k==-2)*C0
gen double all_d_m2=(k==-2)
gen double d_p0=(k==0)*C0
gen double all_d_p0=(k==0)
gen double d_p1=(k==1)*C0
gen double all_d_p1=(k==1)
gen double d_p2=(k==2)*C0
gen double all_d_p2=(k==2)
gen double d_p3=(k==3)*C0
gen double all_d_p3=(k==3)
gen double d_p4=(k==4)*C0
gen double all_d_p4=(k==4)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.ct i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (27) ("post_average") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
quietly lincom d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4 i.ct i.year, absorb(person_id) vce(cluster anchor_province)
quietly lincom d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (27) ("post4") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly levelsof anchor_province, local(provinces)
foreach p of local provinces {
preserve
drop if anchor_province==`p'
capture quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
local rc=_rc
if `rc'==0 {
local nn=e(N)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
post `ll' (27) (`p') ("post_average") (r(estimate)) (r(se)) (r(p)) (`nn') (0)
quietly lincom d_p4
post `ll' (27) (`p') ("post4") (r(estimate)) (r(se)) (r(p)) (`nn') (0)
}
else {
post `ll' (27) (`p') ("failed") (.) (.) (.) (.) (`rc')
}
restore
}
use "`out'/fixed_panel.dta", clear
egen py=group(anchor_province year)
egen ct=group(city_code)
gen double d_m4=(k==-4)*C0
gen double all_d_m4=(k==-4)
gen double d_m3=(k==-3)*C0
gen double all_d_m3=(k==-3)
gen double d_m2=(k==-2)*C0
gen double all_d_m2=(k==-2)
gen double d_p0=(k==0)*C0
gen double all_d_p0=(k==0)
gen double d_p1=(k==1)*C0
gen double all_d_p1=(k==1)
gen double d_p2=(k==2)*C0
gen double all_d_p2=(k==2)
gen double d_p3=(k==3)*C0
gen double all_d_p3=(k==3)
gen double d_p4=(k==4)*C0
gen double all_d_p4=(k==4)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id city_code py) vce(cluster anchor_province)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id city_code py) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.ct i.py, absorb(person_id) vce(cluster anchor_province)
quietly lincom 0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (0.25*d_p1 + 0.25*d_p2 + 0.25*d_p3 + 0.25*d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (36) ("post_average") (`bb') (`ss') (`pp') (`pw') (`rc')
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id city_code py) vce(cluster anchor_province)
quietly lincom d_p4
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
quietly reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.ct i.py, absorb(person_id) vce(cluster anchor_province)
quietly lincom d_p4
assert abs(r(estimate)-`bb')<0.000001
capture quietly boottest (d_p4=0), cluster(anchor_province) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
local pw=.
if `rc'==0 local pw=r(p)
post `rr' (36) ("post4") (`bb') (`ss') (`pp') (`pw') (`rc')
postclose `rr'
postclose `ll'
log close
exit, clear
