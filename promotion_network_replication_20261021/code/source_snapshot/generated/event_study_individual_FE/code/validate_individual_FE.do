version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/event_study_individual_FE"
adopath ++ "C:/Users/siyang zhu/Desktop/hometown/project_organized/code/vendor/pz_boottest"
capture log close
log using "`out'/stata_validation.log", text replace
tempname res jres
postfile `res' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out'/stata_validation.dta", replace
postfile `jres' long model_id str24 test double F df_num df_den p p_wild boot_rc using "`out'/stata_joint_validation.dta", replace
use "`out'/stata_model_panel.dta", clear
keep if model_id==1
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m3 c_m2 c_p0 c_p1 c_p2 d_m3 d_m2 d_p0 d_p1 d_p2 age2 tenure tenure2 i.base_rank i.role_secretary i.year, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_m3 + 0.33333333333333331*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (1*C_any + 0.33333333333333331*c_m3 + 0.33333333333333331*c_m2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (1*C_any + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.33333333333333331*c_m3 + -0.33333333333333331*c_m2 + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (-0.33333333333333331*c_m3 + -0.33333333333333331*c_m2 + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_m3=0) (1*c_m2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jres' (1) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (1) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==2
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m3 c_m2 c_p0 c_p1 c_p2 d_m3 d_m2 d_p0 d_p1 d_p2 age2 tenure tenure2 i.base_rank i.role_secretary i.py, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_m3 + 0.33333333333333331*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (1*C_any + 0.33333333333333331*c_m3 + 0.33333333333333331*c_m2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (2) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (1*C_any + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (2) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.33333333333333331*c_m3 + -0.33333333333333331*c_m2 + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (-0.33333333333333331*c_m3 + -0.33333333333333331*c_m2 + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (2) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*c_m3=0) (1*c_m2=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jres' (2) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (2) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==3
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m3 c_m2 c_p0 c_p1 c_p2 d_m3 d_m2 d_p0 d_p1 d_p2 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_m3 + 0.33333333333333331*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.33333333333333331*c_m3 + -0.33333333333333331*c_m2 + 0.33333333333333331*c_p0 + 0.33333333333333331*c_p1 + 0.33333333333333331*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==4
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 age2 tenure tenure2 i.base_rank i.role_secretary i.year, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.14285714285714285*c_m7 + 0.14285714285714285*c_m6 + 0.14285714285714285*c_m5 + 0.14285714285714285*c_m4 + 0.14285714285714285*c_m3 + 0.14285714285714285*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.14285714285714285*c_m7 + -0.14285714285714285*c_m6 + -0.14285714285714285*c_m5 + -0.14285714285714285*c_m4 + -0.14285714285714285*c_m3 + -0.14285714285714285*c_m2 + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==5
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 age2 tenure tenure2 i.base_rank i.role_secretary i.py, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.14285714285714285*c_m7 + 0.14285714285714285*c_m6 + 0.14285714285714285*c_m5 + 0.14285714285714285*c_m4 + 0.14285714285714285*c_m3 + 0.14285714285714285*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.14285714285714285*c_m7 + -0.14285714285714285*c_m6 + -0.14285714285714285*c_m5 + -0.14285714285714285*c_m4 + -0.14285714285714285*c_m3 + -0.14285714285714285*c_m2 + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==6
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.14285714285714285*c_m7 + 0.14285714285714285*c_m6 + 0.14285714285714285*c_m5 + 0.14285714285714285*c_m4 + 0.14285714285714285*c_m3 + 0.14285714285714285*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.14285714285714285*c_m7 + -0.14285714285714285*c_m6 + -0.14285714285714285*c_m5 + -0.14285714285714285*c_m4 + -0.14285714285714285*c_m3 + -0.14285714285714285*c_m2 + 0.25*c_p0 + 0.25*c_p1 + 0.25*c_p2 + 0.25*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (6) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (6) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (6) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==7
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m8 c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m8 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary i.year, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.125*c_m8 + 0.125*c_m7 + 0.125*c_m6 + 0.125*c_m5 + 0.125*c_m4 + 0.125*c_m3 + 0.125*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.125*c_m8 + -0.125*c_m7 + -0.125*c_m6 + -0.125*c_m5 + -0.125*c_m4 + -0.125*c_m3 + -0.125*c_m2 + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (7) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m8=0) (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (7) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (7) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==8
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m8 c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m8 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary i.py, absorb(person_id) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.125*c_m8 + 0.125*c_m7 + 0.125*c_m6 + 0.125*c_m5 + 0.125*c_m4 + 0.125*c_m3 + 0.125*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.125*c_m8 + -0.125*c_m7 + -0.125*c_m6 + -0.125*c_m5 + -0.125*c_m4 + -0.125*c_m3 + -0.125*c_m2 + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (8) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m8=0) (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (8) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (8) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_model_panel.dta", clear
keep if model_id==9
isid person_id year
egen py=group(province_code year)
quietly areg Y C_any c_m8 c_m7 c_m6 c_m5 c_m4 c_m3 c_m2 c_p0 c_p1 c_p2 c_p3 c_p4 d_m8 d_m7 d_m6 d_m5 d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*C_any + 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.125*c_m8 + 0.125*c_m7 + 0.125*c_m6 + 0.125*c_m5 + 0.125*c_m4 + 0.125*c_m3 + 0.125*c_m2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*C_any + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.125*c_m8 + -0.125*c_m7 + -0.125*c_m6 + -0.125*c_m5 + -0.125*c_m4 + -0.125*c_m3 + -0.125*c_m2 + 0.20000000000000001*c_p0 + 0.20000000000000001*c_p1 + 0.20000000000000001*c_p2 + 0.20000000000000001*c_p3 + 0.20000000000000001*c_p4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (9) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*c_m8=0) (1*c_m7=0) (1*c_m6=0) (1*c_m5=0) (1*c_m4=0) (1*c_m3=0) (1*c_m2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (9) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*c_p0=0) (1*c_p1=0) (1*c_p2=0) (1*c_p3=0) (1*c_p4=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (9) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
postclose `res'
postclose `jres'
use "`out'/stata_validation.dta", clear
format b se p lo hi p_wild %24.16g
export delimited using "`out'/stata_validation.csv", replace
use "`out'/stata_joint_validation.dta", clear
format F p p_wild %24.16g
export delimited using "`out'/stata_joint_validation.csv", replace
log close
exit, clear
