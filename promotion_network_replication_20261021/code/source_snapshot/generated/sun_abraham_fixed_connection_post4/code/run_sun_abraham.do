version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/sun_abraham_fixed_connection_post4"
capture log close
log using "`out'/sun_abraham.log", text replace
which eventstudyinteract
which reghdfe
which avar
tempname res vv ww cc mm jj
postfile `res' long model_id str16 method str16 term double b se p lo hi using "`out'/coefficients.dta", replace
postfile `vv' long model_id str16 method str16 term1 str16 term2 double value using "`out'/covariances.dta", replace
postfile `ww' long model_id long cohort str16 term double weight using "`out'/weights.dta", replace
postfile `cc' long model_id long cohort str16 term double b using "`out'/cohort_coefficients.dta", replace
postfile `mm' long model_id str16 method double N G df using "`out'/models.dta", replace
postfile `jj' long model_id str16 method str24 test double F df_num p using "`out'/joint_tests.dta", replace
use "`out'/analysis_panel.dta", clear
isid person_id year
egen py=group(anchor_province year)
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id year) covariates(age2 tenure tenure2 i.base_rank i.role_secretary all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4) vce(cluster anchor_province)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
matrix WI=e(ff_w)
matrix CI=e(b_interact)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
post `ww' (1) (2013) ("d_m4") (WI[1,1])
post `cc' (1) (2013) ("d_m4") (CI[1,1])
post `ww' (1) (2014) ("d_m4") (WI[2,1])
post `cc' (1) (2014) ("d_m4") (CI[2,1])
post `ww' (1) (2013) ("d_m3") (WI[1,2])
post `cc' (1) (2013) ("d_m3") (CI[1,2])
post `ww' (1) (2014) ("d_m3") (WI[2,2])
post `cc' (1) (2014) ("d_m3") (CI[2,2])
post `ww' (1) (2013) ("d_m2") (WI[1,3])
post `cc' (1) (2013) ("d_m2") (CI[1,3])
post `ww' (1) (2014) ("d_m2") (WI[2,3])
post `cc' (1) (2014) ("d_m2") (CI[2,3])
post `ww' (1) (2013) ("d_p0") (WI[1,4])
post `cc' (1) (2013) ("d_p0") (CI[1,4])
post `ww' (1) (2014) ("d_p0") (WI[2,4])
post `cc' (1) (2014) ("d_p0") (CI[2,4])
post `ww' (1) (2013) ("d_p1") (WI[1,5])
post `cc' (1) (2013) ("d_p1") (CI[1,5])
post `ww' (1) (2014) ("d_p1") (WI[2,5])
post `cc' (1) (2014) ("d_p1") (CI[2,5])
post `ww' (1) (2013) ("d_p2") (WI[1,6])
post `cc' (1) (2013) ("d_p2") (CI[1,6])
post `ww' (1) (2014) ("d_p2") (WI[2,6])
post `cc' (1) (2014) ("d_p2") (CI[2,6])
post `ww' (1) (2013) ("d_p3") (WI[1,7])
post `cc' (1) (2013) ("d_p3") (CI[1,7])
post `ww' (1) (2014) ("d_p3") (WI[2,7])
post `cc' (1) (2014) ("d_p3") (CI[2,7])
post `ww' (1) (2013) ("d_p4") (WI[1,8])
post `cc' (1) (2013) ("d_p4") (CI[1,8])
post `ww' (1) (2014) ("d_p4") (WI[2,8])
post `cc' (1) (2014) ("d_p4") (CI[2,8])
ereturn post BI VI, obs(`NN') dof(`DD')
post `mm' (1) ("Sun_Abraham") (`NN') (`GG') (`DD')
quietly lincom d_m4, level(95)
post `res' (1) ("Sun_Abraham") ("d_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m3, level(95)
post `res' (1) ("Sun_Abraham") ("d_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m2, level(95)
post `res' (1) ("Sun_Abraham") ("d_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p0, level(95)
post `res' (1) ("Sun_Abraham") ("d_p0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p1, level(95)
post `res' (1) ("Sun_Abraham") ("d_p1") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p2, level(95)
post `res' (1) ("Sun_Abraham") ("d_p2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p3, level(95)
post `res' (1) ("Sun_Abraham") ("d_p3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p4, level(95)
post `res' (1) ("Sun_Abraham") ("d_p4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `res' (1) ("Sun_Abraham") ("post_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p2+d_p3+d_p4)/3, level(95)
post `res' (1) ("Sun_Abraham") ("late_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly test d_m4 d_m3 d_m2
post `jj' (1) ("Sun_Abraham") ("pretrend") (r(F)) (r(df)) (r(p))
quietly test d_p1 d_p2 d_p3 d_p4
post `jj' (1) ("Sun_Abraham") ("post_joint") (r(F)) (r(df)) (r(p))
matrix VV=e(V)
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_m4") (VV[1,1])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_m3") (VV[1,2])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_m2") (VV[1,3])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_p0") (VV[1,4])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_p1") (VV[1,5])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_p2") (VV[1,6])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_p3") (VV[1,7])
post `vv' (1) ("Sun_Abraham") ("d_m4") ("d_p4") (VV[1,8])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_m4") (VV[2,1])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_m3") (VV[2,2])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_m2") (VV[2,3])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_p0") (VV[2,4])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_p1") (VV[2,5])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_p2") (VV[2,6])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_p3") (VV[2,7])
post `vv' (1) ("Sun_Abraham") ("d_m3") ("d_p4") (VV[2,8])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_m4") (VV[3,1])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_m3") (VV[3,2])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_m2") (VV[3,3])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_p0") (VV[3,4])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_p1") (VV[3,5])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_p2") (VV[3,6])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_p3") (VV[3,7])
post `vv' (1) ("Sun_Abraham") ("d_m2") ("d_p4") (VV[3,8])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_m4") (VV[4,1])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_m3") (VV[4,2])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_m2") (VV[4,3])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_p0") (VV[4,4])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_p1") (VV[4,5])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_p2") (VV[4,6])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_p3") (VV[4,7])
post `vv' (1) ("Sun_Abraham") ("d_p0") ("d_p4") (VV[4,8])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_m4") (VV[5,1])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_m3") (VV[5,2])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_m2") (VV[5,3])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_p0") (VV[5,4])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_p1") (VV[5,5])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_p2") (VV[5,6])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_p3") (VV[5,7])
post `vv' (1) ("Sun_Abraham") ("d_p1") ("d_p4") (VV[5,8])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_m4") (VV[6,1])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_m3") (VV[6,2])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_m2") (VV[6,3])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_p0") (VV[6,4])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_p1") (VV[6,5])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_p2") (VV[6,6])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_p3") (VV[6,7])
post `vv' (1) ("Sun_Abraham") ("d_p2") ("d_p4") (VV[6,8])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_m4") (VV[7,1])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_m3") (VV[7,2])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_m2") (VV[7,3])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_p0") (VV[7,4])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_p1") (VV[7,5])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_p2") (VV[7,6])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_p3") (VV[7,7])
post `vv' (1) ("Sun_Abraham") ("d_p3") ("d_p4") (VV[7,8])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_m4") (VV[8,1])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_m3") (VV[8,2])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_m2") (VV[8,3])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_p0") (VV[8,4])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_p1") (VV[8,5])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_p2") (VV[8,6])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_p3") (VV[8,7])
post `vv' (1) ("Sun_Abraham") ("d_p4") ("d_p4") (VV[8,8])
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary all_d_m4 all_d_m3 all_d_m2 all_d_p0 all_d_p1 all_d_p2 all_d_p3 all_d_p4, absorb(person_id year) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BT=J(1,8,.)
matrix VT=J(8,8,.)
matrix BT[1,1]=_b[d_m4]
matrix VT[1,1]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m4")]
matrix VT[1,2]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m3")]
matrix VT[1,3]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m2")]
matrix VT[1,4]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p0")]
matrix VT[1,5]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p1")]
matrix VT[1,6]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p2")]
matrix VT[1,7]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p3")]
matrix VT[1,8]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p4")]
matrix BT[1,2]=_b[d_m3]
matrix VT[2,1]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m4")]
matrix VT[2,2]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m3")]
matrix VT[2,3]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m2")]
matrix VT[2,4]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p0")]
matrix VT[2,5]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p1")]
matrix VT[2,6]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p2")]
matrix VT[2,7]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p3")]
matrix VT[2,8]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p4")]
matrix BT[1,3]=_b[d_m2]
matrix VT[3,1]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m4")]
matrix VT[3,2]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m3")]
matrix VT[3,3]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m2")]
matrix VT[3,4]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p0")]
matrix VT[3,5]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p1")]
matrix VT[3,6]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p2")]
matrix VT[3,7]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p3")]
matrix VT[3,8]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p4")]
matrix BT[1,4]=_b[d_p0]
matrix VT[4,1]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m4")]
matrix VT[4,2]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m3")]
matrix VT[4,3]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m2")]
matrix VT[4,4]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p0")]
matrix VT[4,5]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p1")]
matrix VT[4,6]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p2")]
matrix VT[4,7]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p3")]
matrix VT[4,8]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p4")]
matrix BT[1,5]=_b[d_p1]
matrix VT[5,1]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m4")]
matrix VT[5,2]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m3")]
matrix VT[5,3]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m2")]
matrix VT[5,4]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p0")]
matrix VT[5,5]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p1")]
matrix VT[5,6]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p2")]
matrix VT[5,7]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p3")]
matrix VT[5,8]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p4")]
matrix BT[1,6]=_b[d_p2]
matrix VT[6,1]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m4")]
matrix VT[6,2]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m3")]
matrix VT[6,3]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m2")]
matrix VT[6,4]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p0")]
matrix VT[6,5]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p1")]
matrix VT[6,6]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p2")]
matrix VT[6,7]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p3")]
matrix VT[6,8]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p4")]
matrix BT[1,7]=_b[d_p3]
matrix VT[7,1]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m4")]
matrix VT[7,2]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m3")]
matrix VT[7,3]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m2")]
matrix VT[7,4]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p0")]
matrix VT[7,5]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p1")]
matrix VT[7,6]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p2")]
matrix VT[7,7]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p3")]
matrix VT[7,8]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p4")]
matrix BT[1,8]=_b[d_p4]
matrix VT[8,1]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m4")]
matrix VT[8,2]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m3")]
matrix VT[8,3]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m2")]
matrix VT[8,4]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p0")]
matrix VT[8,5]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p1")]
matrix VT[8,6]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p2")]
matrix VT[8,7]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p3")]
matrix VT[8,8]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p4")]
matrix colnames BT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
matrix colnames VT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
matrix rownames VT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
ereturn post BT VT, obs(`NN') dof(`DD')
post `mm' (1) ("TWFE_fixed") (`NN') (`GG') (`DD')
quietly lincom d_m4, level(95)
post `res' (1) ("TWFE_fixed") ("d_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m3, level(95)
post `res' (1) ("TWFE_fixed") ("d_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m2, level(95)
post `res' (1) ("TWFE_fixed") ("d_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p0, level(95)
post `res' (1) ("TWFE_fixed") ("d_p0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p1, level(95)
post `res' (1) ("TWFE_fixed") ("d_p1") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p2, level(95)
post `res' (1) ("TWFE_fixed") ("d_p2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p3, level(95)
post `res' (1) ("TWFE_fixed") ("d_p3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p4, level(95)
post `res' (1) ("TWFE_fixed") ("d_p4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `res' (1) ("TWFE_fixed") ("post_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p2+d_p3+d_p4)/3, level(95)
post `res' (1) ("TWFE_fixed") ("late_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly test d_m4 d_m3 d_m2
post `jj' (1) ("TWFE_fixed") ("pretrend") (r(F)) (r(df)) (r(p))
quietly test d_p1 d_p2 d_p3 d_p4
post `jj' (1) ("TWFE_fixed") ("post_joint") (r(F)) (r(df)) (r(p))
matrix VV=e(V)
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_m4") (VV[1,1])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_m3") (VV[1,2])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_m2") (VV[1,3])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_p0") (VV[1,4])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_p1") (VV[1,5])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_p2") (VV[1,6])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_p3") (VV[1,7])
post `vv' (1) ("TWFE_fixed") ("d_m4") ("d_p4") (VV[1,8])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_m4") (VV[2,1])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_m3") (VV[2,2])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_m2") (VV[2,3])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_p0") (VV[2,4])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_p1") (VV[2,5])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_p2") (VV[2,6])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_p3") (VV[2,7])
post `vv' (1) ("TWFE_fixed") ("d_m3") ("d_p4") (VV[2,8])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_m4") (VV[3,1])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_m3") (VV[3,2])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_m2") (VV[3,3])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_p0") (VV[3,4])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_p1") (VV[3,5])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_p2") (VV[3,6])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_p3") (VV[3,7])
post `vv' (1) ("TWFE_fixed") ("d_m2") ("d_p4") (VV[3,8])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_m4") (VV[4,1])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_m3") (VV[4,2])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_m2") (VV[4,3])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_p0") (VV[4,4])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_p1") (VV[4,5])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_p2") (VV[4,6])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_p3") (VV[4,7])
post `vv' (1) ("TWFE_fixed") ("d_p0") ("d_p4") (VV[4,8])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_m4") (VV[5,1])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_m3") (VV[5,2])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_m2") (VV[5,3])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_p0") (VV[5,4])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_p1") (VV[5,5])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_p2") (VV[5,6])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_p3") (VV[5,7])
post `vv' (1) ("TWFE_fixed") ("d_p1") ("d_p4") (VV[5,8])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_m4") (VV[6,1])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_m3") (VV[6,2])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_m2") (VV[6,3])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_p0") (VV[6,4])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_p1") (VV[6,5])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_p2") (VV[6,6])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_p3") (VV[6,7])
post `vv' (1) ("TWFE_fixed") ("d_p2") ("d_p4") (VV[6,8])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_m4") (VV[7,1])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_m3") (VV[7,2])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_m2") (VV[7,3])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_p0") (VV[7,4])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_p1") (VV[7,5])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_p2") (VV[7,6])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_p3") (VV[7,7])
post `vv' (1) ("TWFE_fixed") ("d_p3") ("d_p4") (VV[7,8])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_m4") (VV[8,1])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_m3") (VV[8,2])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_m2") (VV[8,3])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_p0") (VV[8,4])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_p1") (VV[8,5])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_p2") (VV[8,6])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_p3") (VV[8,7])
post `vv' (1) ("TWFE_fixed") ("d_p4") ("d_p4") (VV[8,8])
use "`out'/analysis_panel.dta", clear
isid person_id year
egen py=group(anchor_province year)
eventstudyinteract Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4, cohort(treated_cohort) control_cohort(never) absorb(person_id py) covariates(age2 tenure tenure2 i.base_rank i.role_secretary) vce(cluster anchor_province)
matrix BI=e(b_iw)
matrix VI=e(V_iw)
matrix WI=e(ff_w)
matrix CI=e(b_interact)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
post `ww' (2) (2013) ("d_m4") (WI[1,1])
post `cc' (2) (2013) ("d_m4") (CI[1,1])
post `ww' (2) (2014) ("d_m4") (WI[2,1])
post `cc' (2) (2014) ("d_m4") (CI[2,1])
post `ww' (2) (2013) ("d_m3") (WI[1,2])
post `cc' (2) (2013) ("d_m3") (CI[1,2])
post `ww' (2) (2014) ("d_m3") (WI[2,2])
post `cc' (2) (2014) ("d_m3") (CI[2,2])
post `ww' (2) (2013) ("d_m2") (WI[1,3])
post `cc' (2) (2013) ("d_m2") (CI[1,3])
post `ww' (2) (2014) ("d_m2") (WI[2,3])
post `cc' (2) (2014) ("d_m2") (CI[2,3])
post `ww' (2) (2013) ("d_p0") (WI[1,4])
post `cc' (2) (2013) ("d_p0") (CI[1,4])
post `ww' (2) (2014) ("d_p0") (WI[2,4])
post `cc' (2) (2014) ("d_p0") (CI[2,4])
post `ww' (2) (2013) ("d_p1") (WI[1,5])
post `cc' (2) (2013) ("d_p1") (CI[1,5])
post `ww' (2) (2014) ("d_p1") (WI[2,5])
post `cc' (2) (2014) ("d_p1") (CI[2,5])
post `ww' (2) (2013) ("d_p2") (WI[1,6])
post `cc' (2) (2013) ("d_p2") (CI[1,6])
post `ww' (2) (2014) ("d_p2") (WI[2,6])
post `cc' (2) (2014) ("d_p2") (CI[2,6])
post `ww' (2) (2013) ("d_p3") (WI[1,7])
post `cc' (2) (2013) ("d_p3") (CI[1,7])
post `ww' (2) (2014) ("d_p3") (WI[2,7])
post `cc' (2) (2014) ("d_p3") (CI[2,7])
post `ww' (2) (2013) ("d_p4") (WI[1,8])
post `cc' (2) (2013) ("d_p4") (CI[1,8])
post `ww' (2) (2014) ("d_p4") (WI[2,8])
post `cc' (2) (2014) ("d_p4") (CI[2,8])
ereturn post BI VI, obs(`NN') dof(`DD')
post `mm' (2) ("Sun_Abraham") (`NN') (`GG') (`DD')
quietly lincom d_m4, level(95)
post `res' (2) ("Sun_Abraham") ("d_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m3, level(95)
post `res' (2) ("Sun_Abraham") ("d_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m2, level(95)
post `res' (2) ("Sun_Abraham") ("d_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p0, level(95)
post `res' (2) ("Sun_Abraham") ("d_p0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p1, level(95)
post `res' (2) ("Sun_Abraham") ("d_p1") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p2, level(95)
post `res' (2) ("Sun_Abraham") ("d_p2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p3, level(95)
post `res' (2) ("Sun_Abraham") ("d_p3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p4, level(95)
post `res' (2) ("Sun_Abraham") ("d_p4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `res' (2) ("Sun_Abraham") ("post_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p2+d_p3+d_p4)/3, level(95)
post `res' (2) ("Sun_Abraham") ("late_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly test d_m4 d_m3 d_m2
post `jj' (2) ("Sun_Abraham") ("pretrend") (r(F)) (r(df)) (r(p))
quietly test d_p1 d_p2 d_p3 d_p4
post `jj' (2) ("Sun_Abraham") ("post_joint") (r(F)) (r(df)) (r(p))
matrix VV=e(V)
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_m4") (VV[1,1])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_m3") (VV[1,2])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_m2") (VV[1,3])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_p0") (VV[1,4])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_p1") (VV[1,5])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_p2") (VV[1,6])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_p3") (VV[1,7])
post `vv' (2) ("Sun_Abraham") ("d_m4") ("d_p4") (VV[1,8])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_m4") (VV[2,1])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_m3") (VV[2,2])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_m2") (VV[2,3])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_p0") (VV[2,4])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_p1") (VV[2,5])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_p2") (VV[2,6])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_p3") (VV[2,7])
post `vv' (2) ("Sun_Abraham") ("d_m3") ("d_p4") (VV[2,8])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_m4") (VV[3,1])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_m3") (VV[3,2])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_m2") (VV[3,3])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_p0") (VV[3,4])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_p1") (VV[3,5])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_p2") (VV[3,6])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_p3") (VV[3,7])
post `vv' (2) ("Sun_Abraham") ("d_m2") ("d_p4") (VV[3,8])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_m4") (VV[4,1])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_m3") (VV[4,2])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_m2") (VV[4,3])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_p0") (VV[4,4])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_p1") (VV[4,5])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_p2") (VV[4,6])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_p3") (VV[4,7])
post `vv' (2) ("Sun_Abraham") ("d_p0") ("d_p4") (VV[4,8])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_m4") (VV[5,1])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_m3") (VV[5,2])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_m2") (VV[5,3])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_p0") (VV[5,4])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_p1") (VV[5,5])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_p2") (VV[5,6])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_p3") (VV[5,7])
post `vv' (2) ("Sun_Abraham") ("d_p1") ("d_p4") (VV[5,8])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_m4") (VV[6,1])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_m3") (VV[6,2])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_m2") (VV[6,3])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_p0") (VV[6,4])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_p1") (VV[6,5])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_p2") (VV[6,6])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_p3") (VV[6,7])
post `vv' (2) ("Sun_Abraham") ("d_p2") ("d_p4") (VV[6,8])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_m4") (VV[7,1])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_m3") (VV[7,2])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_m2") (VV[7,3])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_p0") (VV[7,4])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_p1") (VV[7,5])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_p2") (VV[7,6])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_p3") (VV[7,7])
post `vv' (2) ("Sun_Abraham") ("d_p3") ("d_p4") (VV[7,8])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_m4") (VV[8,1])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_m3") (VV[8,2])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_m2") (VV[8,3])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_p0") (VV[8,4])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_p1") (VV[8,5])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_p2") (VV[8,6])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_p3") (VV[8,7])
post `vv' (2) ("Sun_Abraham") ("d_p4") ("d_p4") (VV[8,8])
reghdfe Y d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4 age2 tenure tenure2 i.base_rank i.role_secretary, absorb(person_id py) vce(cluster anchor_province)
local NN=e(N)
local GG=e(N_clust)
local DD=e(df_r)
matrix BT=J(1,8,.)
matrix VT=J(8,8,.)
matrix BT[1,1]=_b[d_m4]
matrix VT[1,1]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m4")]
matrix VT[1,2]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m3")]
matrix VT[1,3]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_m2")]
matrix VT[1,4]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p0")]
matrix VT[1,5]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p1")]
matrix VT[1,6]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p2")]
matrix VT[1,7]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p3")]
matrix VT[1,8]=e(V)[rownumb(e(V),"d_m4"),colnumb(e(V),"d_p4")]
matrix BT[1,2]=_b[d_m3]
matrix VT[2,1]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m4")]
matrix VT[2,2]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m3")]
matrix VT[2,3]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_m2")]
matrix VT[2,4]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p0")]
matrix VT[2,5]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p1")]
matrix VT[2,6]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p2")]
matrix VT[2,7]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p3")]
matrix VT[2,8]=e(V)[rownumb(e(V),"d_m3"),colnumb(e(V),"d_p4")]
matrix BT[1,3]=_b[d_m2]
matrix VT[3,1]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m4")]
matrix VT[3,2]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m3")]
matrix VT[3,3]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_m2")]
matrix VT[3,4]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p0")]
matrix VT[3,5]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p1")]
matrix VT[3,6]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p2")]
matrix VT[3,7]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p3")]
matrix VT[3,8]=e(V)[rownumb(e(V),"d_m2"),colnumb(e(V),"d_p4")]
matrix BT[1,4]=_b[d_p0]
matrix VT[4,1]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m4")]
matrix VT[4,2]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m3")]
matrix VT[4,3]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_m2")]
matrix VT[4,4]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p0")]
matrix VT[4,5]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p1")]
matrix VT[4,6]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p2")]
matrix VT[4,7]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p3")]
matrix VT[4,8]=e(V)[rownumb(e(V),"d_p0"),colnumb(e(V),"d_p4")]
matrix BT[1,5]=_b[d_p1]
matrix VT[5,1]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m4")]
matrix VT[5,2]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m3")]
matrix VT[5,3]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_m2")]
matrix VT[5,4]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p0")]
matrix VT[5,5]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p1")]
matrix VT[5,6]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p2")]
matrix VT[5,7]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p3")]
matrix VT[5,8]=e(V)[rownumb(e(V),"d_p1"),colnumb(e(V),"d_p4")]
matrix BT[1,6]=_b[d_p2]
matrix VT[6,1]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m4")]
matrix VT[6,2]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m3")]
matrix VT[6,3]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_m2")]
matrix VT[6,4]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p0")]
matrix VT[6,5]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p1")]
matrix VT[6,6]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p2")]
matrix VT[6,7]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p3")]
matrix VT[6,8]=e(V)[rownumb(e(V),"d_p2"),colnumb(e(V),"d_p4")]
matrix BT[1,7]=_b[d_p3]
matrix VT[7,1]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m4")]
matrix VT[7,2]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m3")]
matrix VT[7,3]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_m2")]
matrix VT[7,4]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p0")]
matrix VT[7,5]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p1")]
matrix VT[7,6]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p2")]
matrix VT[7,7]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p3")]
matrix VT[7,8]=e(V)[rownumb(e(V),"d_p3"),colnumb(e(V),"d_p4")]
matrix BT[1,8]=_b[d_p4]
matrix VT[8,1]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m4")]
matrix VT[8,2]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m3")]
matrix VT[8,3]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_m2")]
matrix VT[8,4]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p0")]
matrix VT[8,5]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p1")]
matrix VT[8,6]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p2")]
matrix VT[8,7]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p3")]
matrix VT[8,8]=e(V)[rownumb(e(V),"d_p4"),colnumb(e(V),"d_p4")]
matrix colnames BT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
matrix colnames VT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
matrix rownames VT=d_m4 d_m3 d_m2 d_p0 d_p1 d_p2 d_p3 d_p4
ereturn post BT VT, obs(`NN') dof(`DD')
post `mm' (2) ("TWFE_fixed") (`NN') (`GG') (`DD')
quietly lincom d_m4, level(95)
post `res' (2) ("TWFE_fixed") ("d_m4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m3, level(95)
post `res' (2) ("TWFE_fixed") ("d_m3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_m2, level(95)
post `res' (2) ("TWFE_fixed") ("d_m2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p0, level(95)
post `res' (2) ("TWFE_fixed") ("d_p0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p1, level(95)
post `res' (2) ("TWFE_fixed") ("d_p1") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p2, level(95)
post `res' (2) ("TWFE_fixed") ("d_p2") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p3, level(95)
post `res' (2) ("TWFE_fixed") ("d_p3") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom d_p4, level(95)
post `res' (2) ("TWFE_fixed") ("d_p4") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)
post `res' (2) ("TWFE_fixed") ("post_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly lincom (d_p2+d_p3+d_p4)/3, level(95)
post `res' (2) ("TWFE_fixed") ("late_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))
quietly test d_m4 d_m3 d_m2
post `jj' (2) ("TWFE_fixed") ("pretrend") (r(F)) (r(df)) (r(p))
quietly test d_p1 d_p2 d_p3 d_p4
post `jj' (2) ("TWFE_fixed") ("post_joint") (r(F)) (r(df)) (r(p))
matrix VV=e(V)
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_m4") (VV[1,1])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_m3") (VV[1,2])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_m2") (VV[1,3])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_p0") (VV[1,4])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_p1") (VV[1,5])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_p2") (VV[1,6])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_p3") (VV[1,7])
post `vv' (2) ("TWFE_fixed") ("d_m4") ("d_p4") (VV[1,8])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_m4") (VV[2,1])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_m3") (VV[2,2])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_m2") (VV[2,3])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_p0") (VV[2,4])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_p1") (VV[2,5])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_p2") (VV[2,6])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_p3") (VV[2,7])
post `vv' (2) ("TWFE_fixed") ("d_m3") ("d_p4") (VV[2,8])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_m4") (VV[3,1])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_m3") (VV[3,2])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_m2") (VV[3,3])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_p0") (VV[3,4])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_p1") (VV[3,5])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_p2") (VV[3,6])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_p3") (VV[3,7])
post `vv' (2) ("TWFE_fixed") ("d_m2") ("d_p4") (VV[3,8])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_m4") (VV[4,1])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_m3") (VV[4,2])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_m2") (VV[4,3])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_p0") (VV[4,4])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_p1") (VV[4,5])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_p2") (VV[4,6])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_p3") (VV[4,7])
post `vv' (2) ("TWFE_fixed") ("d_p0") ("d_p4") (VV[4,8])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_m4") (VV[5,1])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_m3") (VV[5,2])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_m2") (VV[5,3])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_p0") (VV[5,4])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_p1") (VV[5,5])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_p2") (VV[5,6])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_p3") (VV[5,7])
post `vv' (2) ("TWFE_fixed") ("d_p1") ("d_p4") (VV[5,8])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_m4") (VV[6,1])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_m3") (VV[6,2])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_m2") (VV[6,3])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_p0") (VV[6,4])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_p1") (VV[6,5])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_p2") (VV[6,6])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_p3") (VV[6,7])
post `vv' (2) ("TWFE_fixed") ("d_p2") ("d_p4") (VV[6,8])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_m4") (VV[7,1])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_m3") (VV[7,2])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_m2") (VV[7,3])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_p0") (VV[7,4])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_p1") (VV[7,5])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_p2") (VV[7,6])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_p3") (VV[7,7])
post `vv' (2) ("TWFE_fixed") ("d_p3") ("d_p4") (VV[7,8])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_m4") (VV[8,1])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_m3") (VV[8,2])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_m2") (VV[8,3])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_p0") (VV[8,4])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_p1") (VV[8,5])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_p2") (VV[8,6])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_p3") (VV[8,7])
post `vv' (2) ("TWFE_fixed") ("d_p4") ("d_p4") (VV[8,8])
postclose `res'
postclose `vv'
postclose `ww'
postclose `cc'
postclose `mm'
postclose `jj'
log close
exit, clear
