version 18
clear all
set more off
set processors 2
local out "C:/Users/siyang zhu/Desktop/hometown/project_organized/result/promotion_connections_revised_2006_2017_2026_10_20/control_FE_sensitivity_post4"
capture log close
log using "`out'/LPDID_models.log", text replace
tempname rr ff
postfile `rr' long model_id str16 term double(b se p lo hi N) using "`out'/LPDID_results.dta", replace
postfile `ff' long model_id long rc using "`out'/LPDID_failures.dta", replace
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 ) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (1) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (1) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role ) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (2) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (2) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (3) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (3) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lngdppc) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (4) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (4) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lnpop) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (5) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (5) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (6) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (6) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lnpop) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (7) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (7) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lngdppc base_lnpop) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (8) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (8) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc base_lnpop) cluster(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (9) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (9) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 ) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (10) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (10) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role ) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (11) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (11) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (12) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (12) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lngdppc) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (13) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (13) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lnpop) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (14) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (14) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (15) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (15) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lnpop) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (16) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (16) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_lngdppc base_lnpop) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (17) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (17) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
use "`out'/lpdid_panel.dta", clear
capture noisily lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls(i.G0 base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role base_growth base_lngdppc base_lnpop) cluster(anchor_province) absorb(anchor_province) level(95) nograph
local rc=_rc
if `rc'!=0 post `ff' (18) (`rc')
if `rc'==0 {
matrix RR=e(results)
local rn: rownames RR
forvalues i=1/9 {
local nm: word `i' of `rn'
post `rr' (18) ("`nm'") (RR[`i',1]) (RR[`i',2]) (RR[`i',4]) (RR[`i',5]) (RR[`i',6]) (RR[`i',7])
}
}
postclose `rr'
postclose `ff'
log close
exit, clear
