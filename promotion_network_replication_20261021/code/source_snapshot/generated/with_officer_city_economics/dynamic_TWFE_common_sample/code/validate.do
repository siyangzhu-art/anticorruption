version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/with_officer_city_economics/dynamic_TWFE_common_sample"
adopath ++ "C:/Users/siyang zhu/Desktop/hometown/project_organized/code/vendor/pz_boottest"
capture log close
log using "`out'/validation.log", text replace
tempname res jr
postfile `res' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out'/stata_validation.dta", replace
postfile `jr' long model_id str32 test double F df_num p p_wild boot_rc using "`out'/stata_joint.dta", replace
use "`out'/stata_panel.dta", clear
keep if model_id==1
isid person_id year
egen py=group(province_code year)
quietly areg Y c_m4 C_any c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary i.year, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local df=e(df_r)
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_m4 + 0.25*c_m3 + 0.25*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("pre_level") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("post_level_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("post_change_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("post_change_1_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.33333333333333331*c_p2 + 0.33333333333333331*c_p3 + 0.33333333333333331*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("late_change_2_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom -0.25*c_m4 + -0.25*c_m3 + -0.25*c_m2 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly test (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (1) ("pretrend") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (1) ("post_joint_0_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jr' (1) ("post_joint_1_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (1) ("late_joint_2_4") (`ff') (`dn') (`pp') (`pw') (`rc')
use "`out'/stata_panel.dta", clear
keep if model_id==2
isid person_id year
egen py=group(province_code year)
quietly areg Y c_m4 C_any c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary i.py, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local df=e(df_r)
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_m4 + 0.25*c_m3 + 0.25*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("pre_level") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("post_level_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("post_change_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (2) ("post_change_1_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.33333333333333331*c_p2 + 0.33333333333333331*c_p3 + 0.33333333333333331*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("late_change_2_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom -0.25*c_m4 + -0.25*c_m3 + -0.25*c_m2 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly test (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (2) ("pretrend") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (2) ("post_joint_0_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jr' (2) ("post_joint_1_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (2) ("late_joint_2_4") (`ff') (`dn') (`pp') (`pw') (`rc')
use "`out'/stata_panel.dta", clear
keep if model_id==3
isid person_id year
egen py=group(province_code year)
quietly areg Y c_m4 C_any c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.year, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local df=e(df_r)
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_m4 + 0.25*c_m3 + 0.25*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("pre_level") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_level_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_change_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (3) ("post_change_1_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.33333333333333331*c_p2 + 0.33333333333333331*c_p3 + 0.33333333333333331*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("late_change_2_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom -0.25*c_m4 + -0.25*c_m3 + -0.25*c_m2 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly test (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (3) ("pretrend") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (3) ("post_joint_0_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jr' (3) ("post_joint_1_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (3) ("late_joint_2_4") (`ff') (`dn') (`pp') (`pw') (`rc')
use "`out'/stata_panel.dta", clear
keep if model_id==4
isid person_id year
egen py=group(province_code year)
quietly areg Y c_m4 C_any c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag i.py, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local df=e(df_r)
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_m4 + 0.25*c_m3 + 0.25*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("pre_level") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_level_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_change_0_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (4) ("post_change_1_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom 0.33333333333333331*c_p2 + 0.33333333333333331*c_p3 + 0.33333333333333331*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("late_change_2_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly lincom -0.25*c_m4 + -0.25*c_m3 + -0.25*c_m2 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3 + 0.25*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
quietly test (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (4) ("pretrend") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (4) ("post_joint_0_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jr' (4) ("post_joint_1_4") (`ff') (`dn') (`pp') (`pw') (`rc')
quietly test (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dn=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jr' (4) ("late_joint_2_4") (`ff') (`dn') (`pp') (`pw') (`rc')
postclose `res'
postclose `jr'
log close
exit, clear
