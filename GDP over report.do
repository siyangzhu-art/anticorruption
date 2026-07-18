
use "inspection_Pyear.dta", clear
//GDP,night light,replicate GDP data preparation//
local directory_path `"C:\Users\siyang zhu\Desktop\Anti_corruption\proposition1"'
import excel "C:\Users\siyang zhu\Downloads\工作簿1.xlsx", firstrow clear
rename (省份 区县 城市 年份 区县代码) (province county city year area_code)
drop if missing(county) | missing(year)
duplicates drop province county year, force
tempfile gdp_data
save "`gdp_data'", replace
use "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\data\night_light.dta", clear
duplicates drop adm_code year, force
rename adm_code area_code
merge 1:1 area_code year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\data\replicate_GDP.dta", keep(match) nogenerate
merge 1:1 area_code year using "`gdp_data'", keep(match) nogenerate
merge m:1 province year using "inspection_Pyear.dta", keep(master match) nogenerate
replace anti_shock = 0 if anti_shock == .
tab year anti_shock, m
gen county_id = area_code
xtset county_id year

drop if year >= 2020
drop if year <= 2007
//Figure 1//
egen prov_year = group(province year)
egen city_year = group(city year)
sort county_id year
by county_id: gen growth_gdp = ln(GDP / GDP[_n-1])
by county_id: gen growth_sum = ln(sum / sum[_n-1])
by county_id: gen growth_realgdp = ln(realgdp / realgdp[_n-1])

preserve
    collapse (mean) avg_realgdp = growth_realgdp (semean) se_realgdp = growth_realgdp, by(year)
    gen ci_lower_realgdp = avg_realgdp - 1.96 * se_realgdp
    gen ci_upper_realgdp = avg_realgdp + 1.96 * se_realgdp
    tempfile realgdp_natl
    save `realgdp_natl'
restore


preserve

bysort prov_year: egen rank_gdp = rank(growth_gdp)
bysort prov_year: egen count_gdp = count(growth_gdp)
gen pctile_gdp = (rank_gdp / count_gdp) * 100

bysort prov_year: egen rank_ntl = rank(growth_sum)
bysort prov_year: egen count_ntl = count(growth_sum)
gen pctile_ntl = (rank_ntl / count_ntl) * 100

gen gap_rank = pctile_gdp - pctile_ntl
bysort county_id: egen mean_pre_gap = mean(cond(year <= 2012, gap_rank, .))
gen over_reporter = (mean_pre_gap > 0) & !missing(mean_pre_gap)

collapse (mean) avg_gap = growth_gdp (semean) se_gap = growth_gdp [aweight=GDP], by(year over_reporter)

gen reporter_type = "Under-Reporter" if over_reporter == 0
replace reporter_type = "Over-Reporter" if over_reporter == 1


gen ci_lower = avg_gap - 1.96 * se_gap
gen ci_upper = avg_gap + 1.96 * se_gap


twoway (rarea ci_lower ci_upper year if over_reporter == 1, color(red%20) lwidth(none)) ///
       (rarea ci_lower ci_upper year if over_reporter == 0, color(ebblue%20) lwidth(none)) ///
       (line avg_gap year if over_reporter == 1, lcolor(red) lwidth(medium) lpattern(solid)) ///
       (line avg_gap year if over_reporter == 0, lcolor(ebblue) lwidth(medium) lpattern(solid)) ///
       , xline(2012, lpattern(dash) lcolor(gs8) lwidth(medium)) ///
         xlabel(2009(2)2020, labsize(medium)) ///
        xtitle("Year", size(medium)) ///
         ytitle("Log Difference Growth Rate", size(medium)) ///
         title("Evolution of GDP Over Time", size(medium)) ///
         subtitle("Anti corruption (2012)", size(small)) ///
         legend(order(3 "Over-Reporters" 4 "Under-Reporters") position(6) rows(1)) ///
         note("Shaded areas show 95% confidence intervals", size(vsmall)) ///
         graphregion(color(white)) ///
         name(fig3_trend, replace)

graph export "figure3_trend.png", width(2000) height(1500) replace
restore

* Core variables
gen ln_gdp      = ln(GDP)
gen ln_ntl      = ln(nightlight)
gen ln_real_gdp=ln(realgdp)

capture drop growth_gdp growth_realgdp
sort county_id year
by county_id: gen growth_gdp = (GDP - GDP[_n-1]) / GDP[_n-1]
sort county_id year
by county_id: gen growth_realgdp = (realgdp - realgdp[_n-1]) / realgdp[_n-1]
sort county_id year
by county_id: gen growth_night = (nightlight - nightlight[_n-1]) / nightlight[_n-1]

* Rename Original Variables to English
capture rename 行政区域土地面积_平方公里 area
capture rename 户籍人口数_万人 pop
capture rename 固定电话用户_户 phone
capture rename 年末总户数_户 Hu
capture rename 村民委员会个数_个 num_v
capture rename 年末单位从业人员_人 emp_n
capture rename 城镇单位在岗职工人数_人 emp_nc
capture rename 乡村从业人员数_人 emp_nv
capture rename 公共图书馆总藏量_千册 num_b
capture rename 普通中学专任教师数_人 num_mt
capture rename 普通小学专任教师数_人 num_pt
capture rename 医院和卫生院卫生人员数_卫生技术人员_人 num_th
capture rename 医院和卫生院卫生人员数_执业医师_人 num_td

capture rename 第一产业增加值_万元 ind1
capture rename 第二产业增加值_万元 ind2
capture rename 第三产业增加值_万元 ind3

capture rename 各项税收_万元 tax
capture rename 年末金融机构各项贷款余额_万元 loan
capture rename 城乡居民储蓄存款余额_万元 save
capture rename 地方财政一般预算支出_万元 fisc_exp
capture rename 地方财政一般预算收入_万元 fisc_rev
capture rename 各种社会福利收养性单位数_个 P
capture rename 普通小学在校生数_人 p
capture rename 普通中学在校学生数_人 m

gen ln_area   = ln(area)
gen ln_pop    = ln(pop)
gen ln_phone  = ln(phone)
gen ln_Hu     = ln(Hu)
gen ln_num_v  = ln(num_v)
gen ln_emp_n  = ln(emp_n + 1)
gen ln_emp_nc = ln(emp_nc + 1)
gen ln_num_b  = ln(num_b)
gen ln_num_mt = ln(num_mt)
gen ln_num_pt = ln(num_pt)
gen ln_num_th = ln(num_th)
gen ln_num_td = ln(num_td)

cap gen ln_P     = ln(各种社会福利收养性单位数_个)
cap gen ln_num_p = ln(普通小学在校生数_人)
cap gen ln_num_m = ln(普通中学在校学生数_人)



bysort county_id (year): egen c=sum(anti_shock)
capture drop prov_id
encode province, gen(prov_id)
capture drop city_id
encode city, gen(city_id)
xtset county_id year
capture drop d
gen d=0
replace d=1 if year>=2013

reghdfe ln_gdp  c.d##c.ln_ntl2, absorb(county_id) cluster(prov_id)
reghdfe ln_gdp  c.d##c.ln_ntl2 ln_area ln_pop,absorb(county_id) cluster(prov_id)
reghdfe ln_gdp  ln_ntl2 c.d#c.ln_ntl2, absorb(county_id year) cluster(prov_id)
reghdfe ln_gdp  ln_ntl2 c.d#c.ln_ntl2 ln_area ln_pop,absorb(county_id year) cluster(prov_id)
reghdfe ln_gdp ln_ntl2 c.d#c.ln_ntl2, absorb(county_id prov_year) cluster(prov_id)
reghdfe ln_gdp ln_ntl2 c.d#c.ln_ntl2 ln_area ln_pop , absorb(county_id prov_year) cluster(prov_id)
reghdfe ln_gdp ln_ntl2 c.d#c.ln_ntl2 ln_area ln_pop , absorb(county_id city_year) cluster(prov_id)
reghdfe ln_gdp ln_ntl2 c.d#c.ln_ntl2 ln_area ln_pop, absorb(county_id prov_year city_year) cluster(prov_id)

reghdfe ln_gdp  c.d##c.ln_real_gdp, absorb(county_id) cluster(prov_id)
reghdfe ln_gdp  c.d##c.ln_real_gdp ln_area ln_pop,absorb(county_id) cluster(prov_id)
reghdfe ln_gdp  ln_real_gdp c.d#c.ln_real_gdp, absorb(county_id year) cluster(prov_id)
reghdfe ln_gdp  ln_real_gdp c.d#c.ln_real_gdp ln_area ln_pop,absorb(county_id year) cluster(prov_id)
reghdfe ln_gdp ln_real_gdp c.d#c.ln_real_gdp, absorb(county_id prov_year) cluster(prov_id)
reghdfe ln_gdp ln_real_gdp c.d#c.ln_real_gdp ln_area ln_pop , absorb(county_id prov_year) cluster(prov_id)
reghdfe ln_gdp ln_real_gdp c.d#c.ln_real_gdp ln_area ln_pop , absorb(county_id city_year) cluster(prov_id)
reghdfe ln_gdp ln_real_gdp c.d#c.ln_real_gdp ln_area ln_pop, absorb(county_id prov_year city_year) cluster(prov_id)

capture gen total_ind = ind1 + ind2 + ind3
capture gen ind2_share = ind2 / total_ind
capture gen ind3_share=ind3/total_ind

local snap_vars "save loan tax pop ind2 area fisc_rev fisc_exp"
foreach v of local snap_vars {
    capture drop snap_`v' ln_snap_`v'
    bysort county_id: egen snap_`v' = max(cond(year == 2012, `v', .))
    gen ln_snap_`v' = ln(snap_`v' + 1)
}
gen ind2_2012_trend = ln_snap_ind2 * year
gen fisc_rev_2012_trend = ln_snap_fisc_rev * year
gen fisc_exp_2012_trend = ln_snap_fisc_exp * year
gen save_2012_trend = ln_snap_save * year
gen area_trend = ln_area * year

//Nonparametric method for GDP over report measure//
lpoly growth_gdp growth_realgdp if !missing(growth_gdp, growth_realgdp), ///
        degree(1) at(growth_realgdp) generate(m_hat_growth_realgdp)
		
gen f_hat_growth_realgdp = growth_gdp - m_hat_growth_realgdp
gen gap=growth_gdp-growth_realgdp

reghdfe f_hat_growth_realgdp GDP realgdp ln_pop save loan tax ind2 area fisc_rev fisc_exp ind1 ,absorb(county_id city_year) cluster(prov_id)

lpoly  growth_gdp growth_night if !missing(growth_gdp, growth_realgdp), ///
        degree(1) at(growth_night) generate(m_hat_growth_night)
    gen f_hat_growth_night = growth_gdp - m_hat_growth_night
gen gap_night=growth_gdp-growth_night 

capture drop m_hat_struct2 f_hat_struct2
npregress kernel growth_gdp growth_realgdp ind2_share ind3_share 
predict m_hat_struct2, mean
gen f_hat_struct2 = growth_gdp - m_hat_struct2
save forcontdid,replace //For R ML method construct GDP over report//

use in 1/31836 using "C:\Users\siyang zhu\Desktop\Anti-corruption\anti_corruption_with_ml.dta", clear
merge 1:1 area_code year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\ins13.dta" //province inspection information//
drop if _merge==2
replace inspection=0 if inspection==.  
* ==============================================================================
* 1. Basline estimation
* ==============================================================================

local my_covs_v2 "area_trend ln_pop ind2_2012_trend fisc_rev_2012_trend fisc_exp_2012_trend inspection"
local proxies    "growth_realgdp"
local all_deps   "gap f_hat_growth_realgdp gap_night f_hat_growth_night"

preserve
foreach proxy in `proxies' {
    di _n(2) "=================================================="
    di ">>> Current Proxy: `proxy'"
    di "=================================================="
    
    foreach y in `all_deps' {
        di _n "--------------------------------------------------"
        di ">>> Outcome Variable: `y'"
        di "--------------------------------------------------"
        
        * ----------------------------------------
        * A: lpdid 
        * ----------------------------------------
        di "--> [lpdid] Running WITHOUT controls..."
        lpdid `y', unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp rw

            
        di "--> [lpdid] Running WITH controls..."
        lpdid `y', unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp controls(`my_covs_v2') 


        * ----------------------------------------
        * B: did_multiplegt_dyn 
        * ----------------------------------------
        di "--> [did_multiplegt_dyn] Running WITHOUT controls..."
        cap noisily did_multiplegt_dyn `y' county_id year anti_shock, ///
            same_switchers effects(1) placebo(1) cluster(prov_id)
        if _rc == 0 graph export "DID_`y'_nocov.png", replace
        
  
        di "--> [did_multiplegt_dyn] Running WITH controls..."
        cap noisily did_multiplegt_dyn `y' county_id year anti_shock, ///
            controls(`my_covs_v2') same_switchers effects(1) placebo(1) ///
            cluster(prov_id)
        if _rc == 0 graph export "DID_`y'_cov.png", replace
		
		
    }
    
    cap drop gap f_hat_`proxy' m_hat_`proxy' 
}
restore


//Robustness check ML method and consider industral share//
local my_covs_v2 "area_trend ln_pop ind2_2012_trend fisc_rev_2012_trend fisc_exp_2012_trend inspection"
local proxies    "growth_realgdp"
local all_deps   "f_hat_stack f_hat_gam f_hat_mars f_hat_svm f_hat_xgb f_hat_rf f_hat_struct2"

preserve
foreach proxy in `proxies' {
    di _n(2) "=================================================="
    di ">>> Current Proxy: `proxy'"
    di "=================================================="
    
    foreach y in `all_deps' {
        di _n "--------------------------------------------------"
        di ">>> Outcome Variable: `y'"
        di "--------------------------------------------------"
        
        * ----------------------------------------
        * A: lpdid 
        * ----------------------------------------
        di "--> [lpdid] Running WITHOUT controls..."
        lpdid `y', unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp 

            
        di "--> [lpdid] Running WITH controls..."
        lpdid `y', unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp controls(`my_covs_v2') 


        * ----------------------------------------
        * B: did_multiplegt_dyn 
        * ----------------------------------------
        di "--> [did_multiplegt_dyn] Running WITHOUT controls..."
        cap noisily did_multiplegt_dyn `y' county_id year anti_shock, ///
            same_switchers effects(1) placebo(1) cluster(prov_id) controls(inspection)
        if _rc == 0 graph export "DID_`y'_nocov.png", replace
        
  
        di "--> [did_multiplegt_dyn] Running WITH controls..."
        cap noisily did_multiplegt_dyn `y' county_id year anti_shock, ///
            controls(`my_covs_v2') same_switchers effects(1) placebo(1) ///
            cluster(prov_id)
        if _rc == 0 graph export "DID_`y'_cov.png", replace
		
		
    }
    
    cap drop gap f_hat_`proxy' m_hat_`proxy' 
}
restore


lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(1, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(3, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(4, oneoff) nocomp rw




* ==============================================================================
* PART B: CSDID (Staggered DiD) - Keep only 2014 and earlier
* ==============================================================================

preserve

keep if year <= 2014
bysort province (year): gen temp_year = year if anti_shock == 1
bysort province: egen first_treat_year = min(temp_year)
gen gvar_csdid = first_treat_year
replace gvar_csdid = 0 if missing(gvar_csdid)
local my_covs_v2 "area_trend ln_pop ind2_2012_trend fisc_rev_2012_trend fisc_exp_2012_trend save_2012_trend inspection"
local proxies    "growth_realgdp"
local all_deps   "f_hat_growth_realgdp"

foreach proxy in `proxies' {
    di ">>> Using proxy: `proxy'"
    
    foreach y in `all_deps' {
        di ">>> Outcome: `y'"
         
      
        csdid `y', ivar(county_id) time(year) gvar(gvar_csdid) ///
            drimp cluster(prov_id) agg(event) baseperiod(-1)
        estat event, window(-4 1)
        csdid_plot, title("No Covs: `y'") name(g1, replace)
        graph export "CSDID_`y'_nocov.png", replace
        
        csdid `y' `my_covs_v2', ivar(county_id) time(year) gvar(gvar_csdid) ///
            drimp cluster(prov_id) agg(event) baseperiod(-1)
        estat event, window(-4 1)
        csdid_plot, title("With Covs: `y'") name(g2, replace)
        graph export "CSDID_`y'_cov.png", replace
    }
     
    cap drop m_hat_`proxy' f_hat_`proxy'
}

restore


	

* ==============================================================================
* PART C: In-Space Placebo Test (Split-sample by over-reporting status)
* ==============================================================================

local proxies "growth_realgdp"
local target_vars "m P mt pt p"
local my_covs_v2 "ln_area ln_pop"

preserve
sort county_id year

* Calculate growth rates for algorithm variables
by county_id: gen growth_m = (m - m[_n-1]) / m[_n-1]
by county_id: gen growth_P = (P - P[_n-1]) / P[_n-1]
by county_id: gen growth_mt = (num_mt - num_mt[_n-1]) / num_mt[_n-1]
by county_id: gen growth_pt = (num_pt - num_pt[_n-1]) / num_pt[_n-1]
by county_id: gen growth_p = (p - p[_n-1]) / p[_n-1]

foreach proxy in `proxies' {
    di ">>> Using proxy: `proxy'"
    
    foreach var in `target_vars' {
        di "    >>> Processing variable: `var'"
        
        cap confirm variable growth_`var'
        if _rc continue
        
        * Nonparametric residual via Lowess
        cap drop f_hat_`var'
        qui lowess growth_`var' `proxy', bwidth(0.3) generate(m_hat_`var')
        gen f_hat_`var' = growth_`var' - m_hat_`var'
        
 
        did_multiplegt_dyn f_hat_`var' county_id year anti_shock, ///
            controls(`my_covs_v2') same_switchers effects(1) placebo(1) cluster(prov_id)
        graph rename fig_placO_`var'_`proxy', replace

    }
}

restore



local snap_vars "f_hat_growth_realgdp "

foreach v in `snap_vars' {
    capture drop snap_`v' ln_snap_`v' mean_pre_`v'
}

tempname memhold
tempfile results
postfile `memhold' str32 var_name str32 method group period beta se lower upper using `results'

preserve

foreach v in `snap_vars' {
    

    bysort county_id: egen mean_pre_`v' = mean(cond(year <= 2012, `v', .))
    
    * Rolling windows (14 groups) - 使用均值
    forval i = 1/14 {
        local lp = (`i'-1)*5
        local up = `lp' + 35
        if `lp' == 0 local lp = 0
        if `up' > 100 local up = 100
        
        local cut_low = 100 - `lp'
        local cut_high = 100 - `up'
        
        qui centile mean_pre_`v' if !missing(mean_pre_`v'), centile(`cut_low' `cut_high')
        local val_low  = r(c_1)  
        local val_high = r(c_2)  
        
        cap drop over_`v'
        if `i' == 1 {
            gen over_`v' = (mean_pre_`v' >= `val_high') & !missing(mean_pre_`v')
        }
        else {
            gen over_`v' = (mean_pre_`v' >= `val_high' & mean_pre_`v' < `val_low') & !missing(mean_pre_`v')
        }
        
        * Two methods: gap and f_hat
        foreach y in f_hat_growth_realgdp {
            
            local mname = cond("`y'"=="gap", "Simple Difference", "Nonparametric Residual")
            
            qui count if over_`v' == 1 & !missing(`y') & !missing(anti_shock)
            if r(N) >= 30 {
                cap noisily did_multiplegt_dyn `y' county_id year anti_shock if over_`v' == 1, ///
                    same_switchers effects(1) placebo(1) cluster(prov_id)
                
                if _rc == 0 {
                    matrix b = e(b)
                    matrix V = e(V)
                    local coefnames : colnames b
                    
                    foreach name in `coefnames' {
                        if strpos("`name'", "Effect_") == 1 {
                            local period = subinstr("`name'", "Effect_", "", .)
                            local beta = b[1, colnumb(b, "`name'")]
                            local se   = sqrt(V[colnumb(V, "`name'") , colnumb(V, "`name'")])
                            
                            if !missing(`beta') & !missing(`se') {
                                post `memhold' ("ln_snap_`v'") ("`mname'") (`i') (`period') ///
                                    (`beta') (`se') (`beta'-1.96*`se') (`beta'+1.96*`se')
                            }
                        }
                        else if strpos("`name'", "Placebo_") == 1 {
                            local period_num = subinstr("`name'", "Placebo_", "", .)
                            local period = "-`period_num'"
                            local beta = b[1, colnumb(b, "`name'")]
                            local se   = sqrt(V[colnumb(V, "`name'") , colnumb(V, "`name'")])
                            
                            if !missing(`beta') & !missing(`se') {
                                post `memhold' ("ln_snap_`v'") ("`mname'") (`i') (`period') ///
                                    (`beta') (`se') (`beta'-1.96*`se') (`beta'+1.96*`se')
                            }
                        }
                    }
                }
                else {
                    di as error ">>> DID failed for `y' with over_`v' (group `i')"
                }
            }
            else {
                di ">>> Insufficient observations for `y' with over_`v' (group `i'): N = r(N)"
            }
        }
        
        cap drop over_`v'
    }
}

postclose `memhold'
restore

use `results', clear

keep if period == 1

qui count
if r(N) == 0 {
    di as error ">>> No results found! Please check estimation."
    exit
}


gen threshold = 35 + (group-1)*5
replace threshold = 100 if threshold > 100

local xlabel 40 "Top 35" 40 "5-40" 45 "10-45" 50 "15-50" 55 "20-55" 60 "25-60" 65 "30-65" 70 "35-70" 75 "40-75" 80 "45-80" 85 "50-85" 90 "55-90" 95 "60-95" 100 "65-100"

* ==============================================================================
* Plot all variables (both methods in one graph)
* ==============================================================================

foreach v in `snap_vars' {
    preserve
        keep if var_name == "ln_snap_`v'"
        
        * Check if both methods exist
        qui count if method == "Simple Difference"
        local has_gap = r(N) > 0
        qui count if method == "Nonparametric Residual"
        local has_fhat = r(N) > 0
        
        if `has_gap' == 0 & `has_fhat' == 0 {
            di as error ">>> No data for ln_snap_`v' - skipping"
            restore
            continue
        }
        
        twoway ///
            (rcap lower upper threshold if method == "Simple Difference", lcolor(cranberry%40)) ///
            (connected beta threshold if method == "Simple Difference", lcolor(cranberry) mcolor(cranberry) msymbol(O) lp(solid)) ///
            (rcap lower upper threshold if method == "Nonparametric Residual", lcolor(navy%40)) ///
            (connected beta threshold if method == "Nonparametric Residual", lcolor(navy) mcolor(navy) msymbol(D) lp(dash)), ///
            yline(0, lcolor(gs12) lp(dash)) ///
            xlabel(`xlabel', angle(45) labsize(small)) ///
            xtitle("Group") ytitle("Estimated Effect") ///
            legend(order(2 "Simple Difference" 4 "Nonparametric Residual") rows(2)) ///
            graphregion(color(white)) ///
            title("Sensitivity Analysis: ln_snap_`v' (Pre-2012 Mean)", size(medium))
        
        graph export "Sensitivity_ln_snap_`v'.png", replace
    restore
}