version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/preinspection_fixed_C0_levels_2026_10_21"
capture log close
log using "`out'/estimation.log", text replace
tempname rr
postfile `rr' long model_id str12 term double(b se p lo hi N G df K df_a df_nested residual_sd dense_b dense_se) using "`out'/stata_results.dta", replace
use "`out'/preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 , absorb(py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
local b_C0=r(estimate)
local s_C0=r(se)
local p_C0=r(p)
local l_C0=r(lb)
local h_C0=r(ub)
quietly regress C0   i.py
predict double rr_C0, residuals
quietly summarize rr_C0
local rs_C0=r(sd)
quietly regress Y C0  i.py, vce(cluster anchor_province)
post `rr' (1) ("C0") (`b_C0') (`s_C0') (`p_C0') (`l_C0') (`h_C0') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_C0') (_b[C0]) (_se[C0])
use "`out'/preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
local b_C0=r(estimate)
local s_C0=r(se)
local p_C0=r(p)
local l_C0=r(lb)
local h_C0=r(ub)
quietly regress C0  age age2 tenure tenure2 i.base_rank i.role_secretary i.py
predict double rr_C0, residuals
quietly summarize rr_C0
local rs_C0=r(sd)
quietly regress Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary i.py, vce(cluster anchor_province)
post `rr' (2) ("C0") (`b_C0') (`s_C0') (`p_C0') (`l_C0') (`h_C0') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_C0') (_b[C0]) (_se[C0])
use "`out'/preinspection_panel.dta", clear
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
local b_C0=r(estimate)
local s_C0=r(se)
local p_C0=r(p)
local l_C0=r(lb)
local h_C0=r(ub)
quietly regress C0  age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_C0, residuals
quietly summarize rr_C0
local rs_C0=r(sd)
quietly regress Y C0 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, vce(cluster anchor_province)
post `rr' (3) ("C0") (`b_C0') (`s_C0') (`p_C0') (`l_C0') (`h_C0') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_C0') (_b[C0]) (_se[C0])
use "`out'/preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y C0 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom C0, level(95)
local b_C0=r(estimate)
local s_C0=r(se)
local p_C0=r(p)
local l_C0=r(lb)
local h_C0=r(ub)
quietly regress C0  age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_C0, residuals
quietly summarize rr_C0
local rs_C0=r(sd)
quietly regress Y C0 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, vce(cluster anchor_province)
post `rr' (4) ("C0") (`b_C0') (`s_C0') (`p_C0') (`l_C0') (`h_C0') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_C0') (_b[C0]) (_se[C0])
use "`out'/preinspection_panel.dta", clear
isid person_id year
local initialN=_N
reghdfe Y c_m4 c_m3 c_m2 c_m1 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(py) vce(cluster anchor_province)
assert e(N)==`initialN'
local nn=e(N)
local gg=e(N_clust)
local dd=e(df_r)
local da=e(df_a)
local dn=e(df_a_nested)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
quietly lincom c_m4, level(95)
local b_c_m4=r(estimate)
local s_c_m4=r(se)
local p_c_m4=r(p)
local l_c_m4=r(lb)
local h_c_m4=r(ub)
quietly lincom c_m3, level(95)
local b_c_m3=r(estimate)
local s_c_m3=r(se)
local p_c_m3=r(p)
local l_c_m3=r(lb)
local h_c_m3=r(ub)
quietly lincom c_m2, level(95)
local b_c_m2=r(estimate)
local s_c_m2=r(se)
local p_c_m2=r(p)
local l_c_m2=r(lb)
local h_c_m2=r(ub)
quietly lincom c_m1, level(95)
local b_c_m1=r(estimate)
local s_c_m1=r(se)
local p_c_m1=r(p)
local l_c_m1=r(lb)
local h_c_m1=r(ub)
quietly regress c_m4 c_m3 c_m2 c_m1 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_c_m4, residuals
quietly summarize rr_c_m4
local rs_c_m4=r(sd)
quietly regress c_m3 c_m4 c_m2 c_m1 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_c_m3, residuals
quietly summarize rr_c_m3
local rs_c_m3=r(sd)
quietly regress c_m2 c_m4 c_m3 c_m1 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_c_m2, residuals
quietly summarize rr_c_m2
local rs_c_m2=r(sd)
quietly regress c_m1 c_m4 c_m3 c_m2 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py
predict double rr_c_m1, residuals
quietly summarize rr_c_m1
local rs_c_m1=r(sd)
quietly regress Y c_m4 c_m3 c_m2 c_m1 age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, vce(cluster anchor_province)
post `rr' (5) ("c_m4") (`b_c_m4') (`s_c_m4') (`p_c_m4') (`l_c_m4') (`h_c_m4') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_c_m4') (_b[c_m4]) (_se[c_m4])
post `rr' (5) ("c_m3") (`b_c_m3') (`s_c_m3') (`p_c_m3') (`l_c_m3') (`h_c_m3') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_c_m3') (_b[c_m3]) (_se[c_m3])
post `rr' (5) ("c_m2") (`b_c_m2') (`s_c_m2') (`p_c_m2') (`l_c_m2') (`h_c_m2') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_c_m2') (_b[c_m2]) (_se[c_m2])
post `rr' (5) ("c_m1") (`b_c_m1') (`s_c_m1') (`p_c_m1') (`l_c_m1') (`h_c_m1') (`nn') (`gg') (`dd') (`kk') (`da') (`dn') (`rs_c_m1') (_b[c_m1]) (_se[c_m1])
postclose `rr'
log close
exit, clear
