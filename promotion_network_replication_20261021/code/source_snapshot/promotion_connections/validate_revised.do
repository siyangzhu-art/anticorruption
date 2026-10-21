version 18
clear all
set more off
set processors 2
local root "C:/Users/siyang zhu/Desktop/hometown/project_organized"
local out "`root'/result/promotion_connections_revised_2006_2017_2026_10_20"
adopath ++ "`root'/code/vendor/pz_boottest"
capture log close
log using "`out'/stata_primary_validation.log", text replace
use "`out'/stata_primary_tasks.dta", clear
local n=_N
frame rename default tasks
frame create panel
tempname res
postfile `res' long model_id str2 leader str8 estimand double b se p lo hi N K G df p_wild boot_rc using "`out'/stata_primary_validation.dta", replace
forvalues i=1/`n' {
 frame tasks: local tid=model_id[`i']
 frame change panel
 use "`out'/stata_primary_panel.dta", clear
 quietly keep if task_id==`tid'
 isid person_id year
 quietly replace Y=Y*100
 quietly egen py=group(province_code year)
 quietly areg Y CS CG CSPost CGPost age age2 tenure tenure2 i.base_rank i.role_secretary, absorb(py) vce(cluster province_code)
 local nn=e(N)
 quietly _ms_omit_info e(b)
 local kk=e(df_a)+colsof(e(b))-r(k_omit)
 local gg=e(N_clust)
 local df=e(df_r)
 foreach lead in S G {
  foreach est in pre post change {
   if "`est'"=="pre" local term "C`lead'"
   if "`est'"=="post" local term "C`lead'+C`lead'Post"
   if "`est'"=="change" local term "C`lead'Post"
   quietly lincom `term', level(95)
   local bb=r(estimate)
   local ss=r(se)
   local pp=r(p)
   local ll=r(lb)
   local hh=r(ub)
   local pw=.
   local rc=.
   if "`est'"=="change" {
    capture quietly boottest `term'=0, cluster(province_code) reps(9999) weight(webb) seed(20261015) noci nograph
    local rc=_rc
    if `rc'==0 local pw=r(p)
   }
   post `res' (`tid') ("`lead'") ("`est'") (`bb') (`ss') (`pp') (`ll') (`hh') (`nn') (`kk') (`gg') (`df') (`pw') (`rc')
   display "VALIDATED model `tid' `lead' `est' wild=`pw' rc=`rc'"
  }
 }
 frame change tasks
}
postclose `res'
use "`out'/stata_primary_validation.dta", clear
format b se p lo hi p_wild %24.16g
export delimited using "`out'/stata_primary_validation.csv", replace
log close
exit, clear
