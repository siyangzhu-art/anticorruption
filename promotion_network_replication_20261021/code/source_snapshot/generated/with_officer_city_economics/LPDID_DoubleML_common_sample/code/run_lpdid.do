version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/with_officer_city_economics/LPDID_DoubleML_common_sample"
capture log close
log using "`out'/lpdid.log", text replace
which lpdid
tempname res
postfile `res' str16 spec str16 term double b se stat p lo hi N using "`out'/lpdid_results.dta", replace
use "`out'/lpdid_panel.dta", clear
isid person_id year
lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role) cluster(anchor_province) level(95) nograph
matrix RR=e(results)
local rn: rownames RR
local nr=rowsof(RR)
forvalues i=1/`nr' {
local nm: word `i' of `rn'
post `res' ("cohort") ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',3]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
use "`out'/lpdid_panel.dta", clear
isid person_id year
lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role) cluster(anchor_province) absorb(anchor_province) level(95) nograph
matrix RR=e(results)
local rn: rownames RR
local nr=rowsof(RR)
forvalues i=1/`nr' {
local nm: word `i' of `rn'
post `res' ("province") ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',3]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
use "`out'/lpdid_panel.dta", clear
isid person_id year
lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc base_lnpop) cluster(anchor_province) level(95) nograph
matrix RR=e(results)
local rn: rownames RR
local nr=rowsof(RR)
forvalues i=1/`nr' {
local nm: word `i' of `rn'
post `res' ("cohort_econ") ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',3]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
use "`out'/lpdid_panel.dta", clear
isid person_id year
lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc base_lnpop) cluster(anchor_province) absorb(anchor_province) level(95) nograph
matrix RR=e(results)
local rn: rownames RR
local nr=rowsof(RR)
forvalues i=1/`nr' {
local nm: word `i' of `rn'
post `res' ("province_econ") ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',3]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
postclose `res'
log close
exit, clear
