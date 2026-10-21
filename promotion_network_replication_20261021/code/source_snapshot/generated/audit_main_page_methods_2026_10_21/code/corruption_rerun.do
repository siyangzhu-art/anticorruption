version 18
clear all
set more off
set processors 2
local base "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20"
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/audit_main_page_methods_2026_10_21"
capture log close
log using "`out'/corruption_rerun.log", text replace
tempname rr
postfile `rr' str16 variant str20 method str20 fe double(b se p lo hi N G) using "`out'/corruption_rerun.dta", replace
use "`base'/control_FE_sensitivity_post4/fixed_panel.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000)
egen py=group(anchor_province year)
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
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id year) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("TWFE_fixed") ("I_YEAR") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id year) covariates(age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
ereturn post BI VI, obs(`NN') dof(`DD')
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("Sun_Abraham") ("I_YEAR") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/control_FE_sensitivity_post4/fixed_panel.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000)
egen py=group(anchor_province year)
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
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id py) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("TWFE_fixed") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id py) covariates(age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
ereturn post BI VI, obs(`NN') dof(`DD')
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("Sun_Abraham") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/control_FE_sensitivity_post4/fixed_panel.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000)
egen py=group(anchor_province year)
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
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id city_code year) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("TWFE_fixed") ("I_CITY_YEAR") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id city_code year) covariates(age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
ereturn post BI VI, obs(`NN') dof(`DD')
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("Sun_Abraham") ("I_CITY_YEAR") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/control_FE_sensitivity_post4/fixed_panel.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000)
egen py=group(anchor_province year)
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
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag, absorb(person_id city_code py) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("TWFE_fixed") ("I_CITY_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id city_code py) covariates(age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
ereturn post BI VI, obs(`NN') dof(`DD')
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `rr' ("Strict") ("Sun_Abraham") ("I_CITY_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000)
reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
quietly lincom CP, level(95)
post `rr' ("Strict") ("cumulative24m") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000,510000)
reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
quietly lincom CP, level(95)
post `rr' ("Plus_discipline") ("cumulative24m") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
use "`base'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_24m.dta", clear
drop if inlist(anchor_province,130000,350000,310000,120000,500000,510000,210000,620000)
reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
quietly lincom CP, level(95)
post `rr' ("Plus_recent") ("cumulative24m") ("I_PXY") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN') (`GG')
postclose `rr'
log close
exit, clear
