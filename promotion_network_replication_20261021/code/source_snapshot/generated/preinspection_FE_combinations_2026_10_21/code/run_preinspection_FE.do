version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/preinspection_FE_combinations_2026_10_21"
capture log close
log using "`out'/estimation.log", text replace
tempname rr jj vv
postfile `rr' long model_id str20 term double(b se p lo hi N G df K df_a df_nested) using "`out'/stata_results.dta", replace
postfile `jj' long model_id double(F df_num df_den p) using "`out'/joint_tests.dta", replace
postfile `vv' long model_id str12 term1 str12 term2 double value using "`out'/covariances.dta", replace
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
post `rr' (1) ("C0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
post `vv' (1) ("C0") ("C0") (e(V)[rownumb(e(V),"C0"),colnumb(e(V),"C0")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(city_code year) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
post `rr' (2) ("C0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
post `vv' (2) ("C0") ("C0") (e(V)[rownumb(e(V),"C0"),colnumb(e(V),"C0")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(city_code py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
post `rr' (3) ("C0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
post `vv' (3) ("C0") ("C0") (e(V)[rownumb(e(V),"C0"),colnumb(e(V),"C0")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y c_m4 c_m3 c_m2 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag d_m4 d_m3 d_m2, absorb(person_id year) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom c_m4, level(95)
post `rr' (4) ("c_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m3, level(95)
post `rr' (4) ("c_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m2, level(95)
post `rr' (4) ("c_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom (c_m4+c_m3+c_m2)/3, level(95)
post `rr' (4) ("pre_average_change") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly test c_m4 c_m3 c_m2
post `jj' (4) (r(F)) (r(df)) (r(df_r)) (r(p))
post `vv' (4) ("c_m4") ("c_m4") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m4")])
post `vv' (4) ("c_m4") ("c_m3") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m3")])
post `vv' (4) ("c_m4") ("c_m2") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m2")])
post `vv' (4) ("c_m3") ("c_m4") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m4")])
post `vv' (4) ("c_m3") ("c_m3") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m3")])
post `vv' (4) ("c_m3") ("c_m2") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m2")])
post `vv' (4) ("c_m2") ("c_m4") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m4")])
post `vv' (4) ("c_m2") ("c_m3") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m3")])
post `vv' (4) ("c_m2") ("c_m2") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m2")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y c_m4 c_m3 c_m2 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom c_m4, level(95)
post `rr' (5) ("c_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m3, level(95)
post `rr' (5) ("c_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m2, level(95)
post `rr' (5) ("c_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom (c_m4+c_m3+c_m2)/3, level(95)
post `rr' (5) ("pre_average_change") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly test c_m4 c_m3 c_m2
post `jj' (5) (r(F)) (r(df)) (r(df_r)) (r(p))
post `vv' (5) ("c_m4") ("c_m4") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m4")])
post `vv' (5) ("c_m4") ("c_m3") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m3")])
post `vv' (5) ("c_m4") ("c_m2") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m2")])
post `vv' (5) ("c_m3") ("c_m4") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m4")])
post `vv' (5) ("c_m3") ("c_m3") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m3")])
post `vv' (5) ("c_m3") ("c_m2") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m2")])
post `vv' (5) ("c_m2") ("c_m4") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m4")])
post `vv' (5) ("c_m2") ("c_m3") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m3")])
post `vv' (5) ("c_m2") ("c_m2") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m2")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y c_m4 c_m3 c_m2 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag d_m4 d_m3 d_m2, absorb(person_id city_code year) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom c_m4, level(95)
post `rr' (6) ("c_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m3, level(95)
post `rr' (6) ("c_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m2, level(95)
post `rr' (6) ("c_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom (c_m4+c_m3+c_m2)/3, level(95)
post `rr' (6) ("pre_average_change") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly test c_m4 c_m3 c_m2
post `jj' (6) (r(F)) (r(df)) (r(df_r)) (r(p))
post `vv' (6) ("c_m4") ("c_m4") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m4")])
post `vv' (6) ("c_m4") ("c_m3") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m3")])
post `vv' (6) ("c_m4") ("c_m2") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m2")])
post `vv' (6) ("c_m3") ("c_m4") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m4")])
post `vv' (6) ("c_m3") ("c_m3") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m3")])
post `vv' (6) ("c_m3") ("c_m2") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m2")])
post `vv' (6) ("c_m2") ("c_m4") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m4")])
post `vv' (6) ("c_m2") ("c_m3") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m3")])
post `vv' (6) ("c_m2") ("c_m2") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m2")])
use "`out'/common_preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y c_m4 c_m3 c_m2 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id city_code py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom c_m4, level(95)
post `rr' (7) ("c_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m3, level(95)
post `rr' (7) ("c_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom c_m2, level(95)
post `rr' (7) ("c_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly lincom (c_m4+c_m3+c_m2)/3, level(95)
post `rr' (7) ("pre_average_change") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn') (`gg') (`dd') (`kk') (`da') (`dn')
quietly test c_m4 c_m3 c_m2
post `jj' (7) (r(F)) (r(df)) (r(df_r)) (r(p))
post `vv' (7) ("c_m4") ("c_m4") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m4")])
post `vv' (7) ("c_m4") ("c_m3") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m3")])
post `vv' (7) ("c_m4") ("c_m2") (e(V)[rownumb(e(V),"c_m4"),colnumb(e(V),"c_m2")])
post `vv' (7) ("c_m3") ("c_m4") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m4")])
post `vv' (7) ("c_m3") ("c_m3") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m3")])
post `vv' (7) ("c_m3") ("c_m2") (e(V)[rownumb(e(V),"c_m3"),colnumb(e(V),"c_m2")])
post `vv' (7) ("c_m2") ("c_m4") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m4")])
post `vv' (7) ("c_m2") ("c_m3") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m3")])
post `vv' (7) ("c_m2") ("c_m2") (e(V)[rownumb(e(V),"c_m2"),colnumb(e(V),"c_m2")])
postclose `rr'
postclose `jj'
postclose `vv'
log close
exit, clear
