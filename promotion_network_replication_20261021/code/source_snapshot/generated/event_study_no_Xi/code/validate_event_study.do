version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/event_study_no_Xi"
adopath ++ "C:/Users/siyang zhu/Desktop/hometown/project_organized/code/vendor/pz_boottest"
capture log close
log using "`out'/stata_event_validation.log", text replace
tempname res jres
postfile `res' long model_id str32 contrast double b se p lo hi N K G df p_wild boot_rc using "`out'/stata_event_validation.dta", replace
postfile `jres' long model_id str24 test double F df_num df_den p p_wild boot_rc using "`out'/stata_joint_validation.dta", replace
use "`out'/stata_event_panel.dta", clear
keep if model_id==1
isid person_id year
egen py=group(province_code year)
quietly areg Y z0 z1 z2 z3 z4 z5 z6 z7 z8 z9 z10 z11 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 0.41080196399345337*z0 + 0.58919803600654663*z6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z0 + -0.41080196399345337*z2 + 0.58919803600654663*z6 + -0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + 0.58919803600654663*z7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + -0.41080196399345337*z2 + 0.58919803600654663*z7 + -0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + 0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + 0.58919803600654663*z9, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z3 + -0.58919803600654663*z8 + 0.58919803600654663*z9, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + 0.58919803600654663*z10, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z4 + -0.58919803600654663*z8 + 0.58919803600654663*z10, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + 0.58919803600654663*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z5 + -0.58919803600654663*z8 + 0.58919803600654663*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (1) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.13693398799781778*z0 + 0.13693398799781778*z1 + 0.13693398799781778*z2 + 0.19639934533551553*z6 + 0.19639934533551553*z7 + 0.19639934533551553*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.13693398799781778*z0 + 0.13693398799781778*z1 + 0.13693398799781778*z2 + 0.19639934533551553*z6 + 0.19639934533551553*z7 + 0.19639934533551553*z8=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.13693398799781778*z0 + -0.13693398799781778*z1 + -0.13693398799781778*z2 + 0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + -0.19639934533551553*z6 + -0.19639934533551553*z7 + -0.19639934533551553*z8 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
capture quietly boottest (-0.13693398799781778*z0 + -0.13693398799781778*z1 + -0.13693398799781778*z2 + 0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + -0.19639934533551553*z6 + -0.19639934533551553*z7 + -0.19639934533551553*z8 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `res' (1) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (0.41080196399345337*z0 + -0.41080196399345337*z2 + 0.58919803600654663*z6 + -0.58919803600654663*z8=0) (0.41080196399345337*z1 + -0.41080196399345337*z2 + 0.58919803600654663*z7 + -0.58919803600654663*z8=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (0.41080196399345337*z0 + -0.41080196399345337*z2 + 0.58919803600654663*z6 + -0.58919803600654663*z8=0) (0.41080196399345337*z1 + -0.41080196399345337*z2 + 0.58919803600654663*z7 + -0.58919803600654663*z8=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jres' (1) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-0.41080196399345337*z2 + 0.41080196399345337*z3 + -0.58919803600654663*z8 + 0.58919803600654663*z9=0) (-0.41080196399345337*z2 + 0.41080196399345337*z4 + -0.58919803600654663*z8 + 0.58919803600654663*z10=0) (-0.41080196399345337*z2 + 0.41080196399345337*z5 + -0.58919803600654663*z8 + 0.58919803600654663*z11=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (1) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*z0 + -1*z2=0) (1*z1 + -1*z2=0) (1*z6 + -1*z8=0) (1*z7 + -1*z8=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
capture quietly boottest (1*z0 + -1*z2=0) (1*z1 + -1*z2=0) (1*z6 + -1*z8=0) (1*z7 + -1*z8=0), cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
local rc=_rc
if `rc'==0 local pw=r(p)
post `jres' (1) ("pretrend_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-1*z2 + 1*z3=0) (-1*z2 + 1*z4=0) (-1*z2 + 1*z5=0) (-1*z8 + 1*z9=0) (-1*z8 + 1*z10=0) (-1*z8 + 1*z11=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (1) ("post_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_event_panel.dta", clear
keep if model_id==2
isid person_id year
egen py=group(province_code year)
quietly areg Y z0 z1 z2 z3 z4 z5 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*z0 + 1*z1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z1, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 1*z2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 1*z3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z3, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 1*z4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z4, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 1*z5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 0.33333333333333331*z1 + 0.33333333333333331*z2, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z0 + 0.33333333333333331*z3 + 0.33333333333333331*z4 + 0.33333333333333331*z5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.33333333333333331*z1 + -0.33333333333333331*z2 + 0.33333333333333331*z3 + 0.33333333333333331*z4 + 0.33333333333333331*z5, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (2) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*z1=0) (1*z2=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (2) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*z3=0) (1*z4=0) (1*z5=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (2) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_event_panel.dta", clear
keep if model_id==3
isid person_id year
egen py=group(province_code year)
quietly areg Y z0 z1 z2 z3 z4 z5 z6 z7 z8 z9 z10 z11 z12 z13 z14 z15 z16 z17 z18 z19 z20 z21 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 0.41080196399345337*z0 + 0.58919803600654663*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z0 + -0.41080196399345337*z6 + 0.58919803600654663*z11 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + 0.58919803600654663*z12, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + -0.41080196399345337*z6 + 0.58919803600654663*z12 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + 0.58919803600654663*z13, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + -0.41080196399345337*z6 + 0.58919803600654663*z13 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + 0.58919803600654663*z14, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + -0.41080196399345337*z6 + 0.58919803600654663*z14 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + 0.58919803600654663*z15, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + -0.41080196399345337*z6 + 0.58919803600654663*z15 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + 0.58919803600654663*z16, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + -0.41080196399345337*z6 + 0.58919803600654663*z16 + -0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z6 + 0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z7 + 0.58919803600654663*z18, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z7 + -0.58919803600654663*z17 + 0.58919803600654663*z18, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z8 + 0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z8 + -0.58919803600654663*z17 + 0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z9 + 0.58919803600654663*z20, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z9 + -0.58919803600654663*z17 + 0.58919803600654663*z20, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z10 + 0.58919803600654663*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z10 + -0.58919803600654663*z17 + 0.58919803600654663*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.058685994856207624*z0 + 0.058685994856207624*z1 + 0.058685994856207624*z2 + 0.058685994856207624*z3 + 0.058685994856207624*z4 + 0.058685994856207624*z5 + 0.058685994856207624*z6 + 0.084171148000935239*z11 + 0.084171148000935239*z12 + 0.084171148000935239*z13 + 0.084171148000935239*z14 + 0.084171148000935239*z15 + 0.084171148000935239*z16 + 0.084171148000935239*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.10270049099836334*z7 + 0.10270049099836334*z8 + 0.10270049099836334*z9 + 0.10270049099836334*z10 + 0.14729950900163666*z18 + 0.14729950900163666*z19 + 0.14729950900163666*z20 + 0.14729950900163666*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.058685994856207624*z0 + -0.058685994856207624*z1 + -0.058685994856207624*z2 + -0.058685994856207624*z3 + -0.058685994856207624*z4 + -0.058685994856207624*z5 + -0.058685994856207624*z6 + 0.10270049099836334*z7 + 0.10270049099836334*z8 + 0.10270049099836334*z9 + 0.10270049099836334*z10 + -0.084171148000935239*z11 + -0.084171148000935239*z12 + -0.084171148000935239*z13 + -0.084171148000935239*z14 + -0.084171148000935239*z15 + -0.084171148000935239*z16 + -0.084171148000935239*z17 + 0.14729950900163666*z18 + 0.14729950900163666*z19 + 0.14729950900163666*z20 + 0.14729950900163666*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (3) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (0.41080196399345337*z0 + -0.41080196399345337*z6 + 0.58919803600654663*z11 + -0.58919803600654663*z17=0) (0.41080196399345337*z1 + -0.41080196399345337*z6 + 0.58919803600654663*z12 + -0.58919803600654663*z17=0) (0.41080196399345337*z2 + -0.41080196399345337*z6 + 0.58919803600654663*z13 + -0.58919803600654663*z17=0) (0.41080196399345337*z3 + -0.41080196399345337*z6 + 0.58919803600654663*z14 + -0.58919803600654663*z17=0) (0.41080196399345337*z4 + -0.41080196399345337*z6 + 0.58919803600654663*z15 + -0.58919803600654663*z17=0) (0.41080196399345337*z5 + -0.41080196399345337*z6 + 0.58919803600654663*z16 + -0.58919803600654663*z17=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-0.41080196399345337*z6 + 0.41080196399345337*z7 + -0.58919803600654663*z17 + 0.58919803600654663*z18=0) (-0.41080196399345337*z6 + 0.41080196399345337*z8 + -0.58919803600654663*z17 + 0.58919803600654663*z19=0) (-0.41080196399345337*z6 + 0.41080196399345337*z9 + -0.58919803600654663*z17 + 0.58919803600654663*z20=0) (-0.41080196399345337*z6 + 0.41080196399345337*z10 + -0.58919803600654663*z17 + 0.58919803600654663*z21=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*z0 + -1*z6=0) (1*z1 + -1*z6=0) (1*z2 + -1*z6=0) (1*z3 + -1*z6=0) (1*z4 + -1*z6=0) (1*z5 + -1*z6=0) (1*z11 + -1*z17=0) (1*z12 + -1*z17=0) (1*z13 + -1*z17=0) (1*z14 + -1*z17=0) (1*z15 + -1*z17=0) (1*z16 + -1*z17=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("pretrend_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-1*z6 + 1*z7=0) (-1*z6 + 1*z8=0) (-1*z6 + 1*z9=0) (-1*z6 + 1*z10=0) (-1*z17 + 1*z18=0) (-1*z17 + 1*z19=0) (-1*z17 + 1*z20=0) (-1*z17 + 1*z21=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (3) ("post_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_event_panel.dta", clear
keep if model_id==4
isid person_id year
egen py=group(province_code year)
quietly areg Y z0 z1 z2 z3 z4 z5 z6 z7 z8 z9 z10 z11 z12 z13 z14 z15 z16 z17 z18 z19 z20 z21 z22 z23 age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 1*z12, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z12 + -1*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-8") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z0 + 0.58919803600654663*z13, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z0 + -0.41080196399345337*z6 + 0.58919803600654663*z13 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-7") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + 0.58919803600654663*z14, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + -0.41080196399345337*z6 + 0.58919803600654663*z14 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-6") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + 0.58919803600654663*z15, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + -0.41080196399345337*z6 + 0.58919803600654663*z15 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-5") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + 0.58919803600654663*z16, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + -0.41080196399345337*z6 + 0.58919803600654663*z16 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + 0.58919803600654663*z17, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + -0.41080196399345337*z6 + 0.58919803600654663*z17 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + 0.58919803600654663*z18, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + -0.41080196399345337*z6 + 0.58919803600654663*z18 + -0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z6 + 0.58919803600654663*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z7 + 0.58919803600654663*z20, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z7 + -0.58919803600654663*z19 + 0.58919803600654663*z20, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z8 + 0.58919803600654663*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z8 + -0.58919803600654663*z19 + 0.58919803600654663*z21, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z9 + 0.58919803600654663*z22, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z9 + -0.58919803600654663*z19 + 0.58919803600654663*z22, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z10 + 0.58919803600654663*z23, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z6 + 0.41080196399345337*z10 + -0.58919803600654663*z19 + 0.58919803600654663*z23, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 1*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("level_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -1*z6 + 1*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("change_4") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.051350245499181671*z0 + 0.051350245499181671*z1 + 0.051350245499181671*z2 + 0.051350245499181671*z3 + 0.051350245499181671*z4 + 0.051350245499181671*z5 + 0.051350245499181671*z6 + 0.125*z12 + 0.073649754500818329*z13 + 0.073649754500818329*z14 + 0.073649754500818329*z15 + 0.073649754500818329*z16 + 0.073649754500818329*z17 + 0.073649754500818329*z18 + 0.073649754500818329*z19, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.082160392798690668*z7 + 0.082160392798690668*z8 + 0.082160392798690668*z9 + 0.082160392798690668*z10 + 0.20000000000000001*z11 + 0.11783960720130933*z20 + 0.11783960720130933*z21 + 0.11783960720130933*z22 + 0.11783960720130933*z23, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.051350245499181671*z0 + -0.051350245499181671*z1 + -0.051350245499181671*z2 + -0.051350245499181671*z3 + -0.051350245499181671*z4 + -0.051350245499181671*z5 + -0.051350245499181671*z6 + 0.082160392798690668*z7 + 0.082160392798690668*z8 + 0.082160392798690668*z9 + 0.082160392798690668*z10 + 0.20000000000000001*z11 + -0.125*z12 + -0.073649754500818329*z13 + -0.073649754500818329*z14 + -0.073649754500818329*z15 + -0.073649754500818329*z16 + -0.073649754500818329*z17 + -0.073649754500818329*z18 + -0.073649754500818329*z19 + 0.11783960720130933*z20 + 0.11783960720130933*z21 + 0.11783960720130933*z22 + 0.11783960720130933*z23, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (4) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (1*z12 + -1*z19=0) (0.41080196399345337*z0 + -0.41080196399345337*z6 + 0.58919803600654663*z13 + -0.58919803600654663*z19=0) (0.41080196399345337*z1 + -0.41080196399345337*z6 + 0.58919803600654663*z14 + -0.58919803600654663*z19=0) (0.41080196399345337*z2 + -0.41080196399345337*z6 + 0.58919803600654663*z15 + -0.58919803600654663*z19=0) (0.41080196399345337*z3 + -0.41080196399345337*z6 + 0.58919803600654663*z16 + -0.58919803600654663*z19=0) (0.41080196399345337*z4 + -0.41080196399345337*z6 + 0.58919803600654663*z17 + -0.58919803600654663*z19=0) (0.41080196399345337*z5 + -0.41080196399345337*z6 + 0.58919803600654663*z18 + -0.58919803600654663*z19=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-0.41080196399345337*z6 + 0.41080196399345337*z7 + -0.58919803600654663*z19 + 0.58919803600654663*z20=0) (-0.41080196399345337*z6 + 0.41080196399345337*z8 + -0.58919803600654663*z19 + 0.58919803600654663*z21=0) (-0.41080196399345337*z6 + 0.41080196399345337*z9 + -0.58919803600654663*z19 + 0.58919803600654663*z22=0) (-0.41080196399345337*z6 + 0.41080196399345337*z10 + -0.58919803600654663*z19 + 0.58919803600654663*z23=0) (-1*z6 + 1*z11=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*z0 + -1*z6=0) (1*z1 + -1*z6=0) (1*z2 + -1*z6=0) (1*z3 + -1*z6=0) (1*z4 + -1*z6=0) (1*z5 + -1*z6=0) (1*z12 + -1*z19=0) (1*z13 + -1*z19=0) (1*z14 + -1*z19=0) (1*z15 + -1*z19=0) (1*z16 + -1*z19=0) (1*z17 + -1*z19=0) (1*z18 + -1*z19=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("pretrend_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-1*z6 + 1*z7=0) (-1*z6 + 1*z8=0) (-1*z6 + 1*z9=0) (-1*z6 + 1*z10=0) (-1*z6 + 1*z11=0) (-1*z19 + 1*z20=0) (-1*z19 + 1*z21=0) (-1*z19 + 1*z22=0) (-1*z19 + 1*z23=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (4) ("post_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
use "`out'/stata_event_panel.dta", clear
keep if model_id==5
isid person_id year
egen py=group(province_code year)
quietly areg Y z0 z1 z2 z3 z4 z5 z6 z7 z8 z9 z10 z11 age age2 tenure tenure2 i.base_rank i.role_secretary i.city_code, absorb(py) vce(cluster province_code)
local nn=e(N)
quietly _ms_omit_info e(b)
local kk=e(df_a)+colsof(e(b))-r(k_omit)
local gg=e(N_clust)
local dfr=e(df_r)
quietly lincom 0.41080196399345337*z0 + 0.58919803600654663*z6, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z0 + -0.41080196399345337*z2 + 0.58919803600654663*z6 + -0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-3") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + 0.58919803600654663*z7, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z1 + -0.41080196399345337*z2 + 0.58919803600654663*z7 + -0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_-2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z2 + 0.58919803600654663*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_-1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z3 + 0.58919803600654663*z9, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z3 + -0.58919803600654663*z8 + 0.58919803600654663*z9, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_0") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z4 + 0.58919803600654663*z10, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z4 + -0.58919803600654663*z8 + 0.58919803600654663*z10, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_1") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.41080196399345337*z5 + 0.58919803600654663*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("level_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.41080196399345337*z2 + 0.41080196399345337*z5 + -0.58919803600654663*z8 + 0.58919803600654663*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("change_2") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.13693398799781778*z0 + 0.13693398799781778*z1 + 0.13693398799781778*z2 + 0.19639934533551553*z6 + 0.19639934533551553*z7 + 0.19639934533551553*z8, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("pre_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom 0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("post_mean") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly lincom -0.13693398799781778*z0 + -0.13693398799781778*z1 + -0.13693398799781778*z2 + 0.13693398799781778*z3 + 0.13693398799781778*z4 + 0.13693398799781778*z5 + -0.19639934533551553*z6 + -0.19639934533551553*z7 + -0.19639934533551553*z8 + 0.19639934533551553*z9 + 0.19639934533551553*z10 + 0.19639934533551553*z11, level(95)
local bb=r(estimate)
local ss=r(se)
local pp=r(p)
local ll=r(lb)
local hh=r(ub)
local pw=.
local rc=.
post `res' (5) ("post_minus_pre") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`dfr') (`pw') (`rc')
quietly test (0.41080196399345337*z0 + -0.41080196399345337*z2 + 0.58919803600654663*z6 + -0.58919803600654663*z8=0) (0.41080196399345337*z1 + -0.41080196399345337*z2 + 0.58919803600654663*z7 + -0.58919803600654663*z8=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("pretrend") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-0.41080196399345337*z2 + 0.41080196399345337*z3 + -0.58919803600654663*z8 + 0.58919803600654663*z9=0) (-0.41080196399345337*z2 + 0.41080196399345337*z4 + -0.58919803600654663*z8 + 0.58919803600654663*z10=0) (-0.41080196399345337*z2 + 0.41080196399345337*z5 + -0.58919803600654663*z8 + 0.58919803600654663*z11=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("post_dynamics") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (1*z0 + -1*z2=0) (1*z1 + -1*z2=0) (1*z6 + -1*z8=0) (1*z7 + -1*z8=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("pretrend_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
quietly test (-1*z2 + 1*z3=0) (-1*z2 + 1*z4=0) (-1*z2 + 1*z5=0) (-1*z8 + 1*z9=0) (-1*z8 + 1*z10=0) (-1*z8 + 1*z11=0)
local ff=r(F)
local dd=r(df)
local pp=r(p)
local pw=.
local rc=.
post `jres' (5) ("post_all_cohorts") (`ff') (`dd') (`dfr') (`pp') (`pw') (`rc')
postclose `res'
postclose `jres'
use "`out'/stata_event_validation.dta", clear
format b se p lo hi p_wild %24.16g
export delimited using "`out'/stata_event_validation.csv", replace
use "`out'/stata_joint_validation.dta", clear
format F p p_wild %24.16g
export delimited using "`out'/stata_joint_validation.csv", replace
log close
exit, clear
