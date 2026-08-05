//--------------------------//
* ==============================================================================
* 1. GDP over report
* ==============================================================================
//--------------------------//
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
capture drop prov_id
encode province, gen(prov_id)
capture drop city_id
encode city, gen(city_id)
xtset county_id year
reghdfe f_hat_growth_realgdp GDP realgdp ln_pop save loan tax ind2 area fisc_rev fisc_exp ind1 ,absorb(county_id city_year) cluster(prov_id)

lpoly  growth_gdp growth_night if !missing(growth_gdp, growth_realgdp), ///
        degree(1) at(growth_night) generate(m_hat_growth_night)
    gen f_hat_growth_night = growth_gdp - m_hat_growth_night
gen gap_night=growth_gdp-growth_night 

capture drop m_hat_struct2 f_hat_struct2
npregress kernel growth_gdp growth_realgdp ind2_share ind3_share 
predict m_hat_struct2, mean
gen f_hat_struct2 = growth_gdp - m_hat_struct2
save forcontdid,replace //For save it for R using ML method construct GDP over report//
//-------------------------//
/*Running robustness ML for GDP over report.R on your R get result(anti_corruption_with_ml.dta)*/

use in 1/31836 using "C:\Users\siyang zhu\Desktop\Anti-corruption\anti_corruption_with_ml.dta", clear //
merge 1:1 area_code year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\ins13.dta" //province inspection information//
drop if _merge==2
replace inspection=0 if inspection==.  
* ==============================================================================
* 1.1. Basline estimation
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
    
}
restore
* ==============================================================================
* 1.2.Robustness check
* ==============================================================================
//1.2.1 Robustness check ML method and consider industral share//
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
    
}
restore

//1.2.2 Robustness check for LP did//

lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(1, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(2, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(3, oneoff) nocomp rw
lpdid f_hat_growth_realgdp, unit(county_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(prov_id) nonabsorbing(4, oneoff) nocomp rw

//1.2.3 CSDID (Staggered DiD) - Keep only 2014 and earlier //
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

//1.2.4 In-Space Placebo Test//
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


bysort prov_year: egen rank_gdp = rank(growth_gdp)
bysort prov_year: egen count_gdp = count(growth_gdp)
gen pctile_gdp = (rank_gdp / count_gdp) * 100

bysort prov_year: egen rank_realgdp = rank(growth_realgdp)
bysort prov_year: egen count_realgdp = count(growth_realgdp)
gen pctile_realgdp = (rank_realgdp / count_realgdp) * 100
gen gap_rank = pctile_gdp - pctile_realgdp

//1.2.4 Rule out measurement error issue//
local snap_vars "gap_rank"

tempname memhold
tempfile results
postfile `memhold' str32 var_name str32 method group period beta se lower upper using `results'

preserve

foreach v in `snap_vars' {
    

    bysort county_id: egen mean_pre_`v' = mean(cond(year <= 2012, `v', .))
    
    * Rolling windows (14 groups)
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
        foreach y in f_hat_growth_realgdp gap{
            
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
//--------------------------//
* ==============================================================================
* 2. Provinical fiscal 
* ==============================================================================
//--------------------------//
import excel "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\data\2008年各省财政指标汇总表.xlsx", sheet("Sheet1") firstrow clear
capture rename 省份 province
capture rename 年份 year
gen anti_shock = 0
label var anti_shock "中央巡视冲击(年度频，当年受巡即为1)"

local treat_2013 "内蒙古 江西 湖北 重庆 贵州 山西 吉林 安徽 湖南 广东 云南"

local treat_2014 "北京 天津 辽宁 福建 山东 河南 海南 甘肃 宁夏 新疆 河北 黑龙江 上海 江苏 浙江 广西 四川 西藏 陕西 青海"

local treat_2015 ""
local treat_2016 "辽宁 安徽 山东 湖南 天津 江西 河南 湖北 北京 广西 重庆 甘肃"
local treat_2017 "内蒙古 吉林 云南 陕西"

local treat_2018 "河北 山西 辽宁 黑龙江 江苏 福建 山东 河南 湖南 广东 海南 四川 贵州 宁夏  湖北 甘肃 青海 新疆"

local treat_2019 ""

local treat_2020 "北京 天津 内蒙古 吉林 上海 浙江 安徽 江西 湖北 广西 重庆 云南 西藏 陕西 甘肃 青海 新疆"

forvalues y = 2013/2020 {
    if "`treat_`y''" != "" {
        foreach p in `treat_`y'' {
            replace anti_shock = 1 if strmatch(province, "*`p'*") & year == `y'
        }
    }
}

gen Tr=0
replace Tr=1 if year >= 2016
gen D = Tr * anti_shock

bysort 省份代码 (year): gen inspection_round = sum(anti_shock)
gen C= Tr*inspection_round
local outcome "财政收入稳健指数 债务可持续指数 财政支出结构指数 社保基金可持续指数 预算管理指数 c透明度指数 b审计违规金额占比"
foreach y of local outcome {
	 reghdfe `y' Tr, absorb(省份代码) 
        
        reghdfe `y' inspection_round, absorb(省份代码 year) 
      
       reghdfe `y'  C, absorb(省份代码 year) 

}
	
gen ratio= 地方城投公司的有息债务余额/ GDP


did_multiplegt_dyn 债务可持续指数 省份代码 year D,  effects(2) placebo(2) trends_lin  same_switchers
did_multiplegt_dyn 社保基金可持续指数 省份代码 year D,  effects(2) placebo(2)   same_switchers 
did_multiplegt_dyn  地方城投公司的有息债务余额 省份代码 year D,  effects(2) placebo(2)   same_switchers trends_lin
did_multiplegt_dyn  ratio 省份代码 year D,  effects(2) placebo(2)   same_switchers trends_lin


//--------------------------//
* ==============================================================================
* 3. Enviornmental policy
* ==============================================================================
//--------------------------//
import delimited "C:\Users\siyang zhu\Desktop\Anti-corruption\data\city_co.csv", clear encoding(UTF-8)
duplicates drop adm_code year month, force
tempfile co
save `co'

import delimited "C:\Users\siyang zhu\Desktop\Anti-corruption\data\city_no2.csv", clear encoding(UTF-8)
duplicates drop adm_code year month, force
tempfile no2
save `no2'

import delimited "C:\Users\siyang zhu\Desktop\Anti-corruption\data\city_pm10.csv", clear encoding(UTF-8)
duplicates drop adm_code year month, force
tempfile pm10
save `pm10'

import delimited "C:\Users\siyang zhu\Desktop\Anti-corruption\data\city_so2.csv", clear encoding(UTF-8)
duplicates drop adm_code year month, force
tempfile so2
save `so2'

import delimited "C:\Users\siyang zhu\Desktop\Anti-corruption\data\city_pm25.csv", clear encoding(UTF-8)
duplicates drop adm_code year month, force
tempfile pm25
save `pm25'

import excel "C:\Users\siyang zhu\Desktop\Anti-corruption\data\大气重点控制区DID（2010-2024）\中国各省市是否属于大气重点控制区匹配数据（2010-2024）.xlsx", sheet("Sheet1") firstrow clear
duplicates drop 行政区划代码 年份, force
xtset 行政区划代码 年份


capture rename 行政区划代码 adm_code
capture rename 城市 地区
capture rename 年份 year
drop if year >= 2021
destring year, replace force
duplicates drop adm_code year, force
tempfile match_air
save `match_air'

use `co', clear
merge 1:1 adm_code year month using `no2', nogenerate
merge 1:1 adm_code year month using `so2', nogenerate
merge 1:1 adm_code year month using `pm25', nogenerate
merge 1:1 adm_code year month using `pm10', nogenerate
merge m:1 adm_code year using `match_air', nogenerate

save "C:\Users\siyang zhu\Desktop\Anti-corruption\final_panel_data.dta", replace

use "C:\Users\siyang zhu\Desktop\Anti-corruption\final_panel_data.dta", clear
capture rename 所属省份 province
capture rename 地区 city
tostring province city, replace
capture rename 大气重点控制区 大气重点控制
collapse (mean) Co = co ///
         (mean) Pm25 = pm25 ///
         (mean) So2 = so2 ///
         (mean) No2 = no2 ///
		 (mean) Pm10 = pm10 ///
         (max) 大气重点控制 = 大气重点控制 , by(province city adm_code year)
drop if 大气重点控制==.
merge 1:1 city year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\ins12.dta"
drop if _merge==2

replace inspection=0 if inspection==.
gen anti_shock = 0
label var anti_shock "中央巡视冲击(年度，当年有巡视入驻为1)"
local treat_2013 "内蒙古 江西 湖北 重庆 贵州 山西 吉林 安徽 湖南 广东 云南"
local treat_2014 "北京 天津 辽宁 福建 山东 河南 海南 甘肃 宁夏 新疆 河北 黑龙江 上海 江苏 浙江 广西 四川 西藏 陕西 青海"
local treat_2015 ""
local treat_2016 "辽宁 安徽 山东 湖南 天津 江西 河南 湖北 北京 广西 重庆 甘肃"
local treat_2017 "内蒙古 吉林 云南 陕西"
local treat_2018 "河北 山西 辽宁 黑龙江 江苏 福建 山东 河南 湖南 广东 海南 四川 贵州 宁夏  湖北 甘肃 青海 新疆"
local treat_2019 ""
local treat_2020 "北京 天津 内蒙古 吉林 上海 浙江 安徽 江西 湖北 广西 重庆 云南 西藏 陕西 甘肃 青海 新疆"


forvalues y = 2013/2020 {
    if "`treat_`y''" != "" {
        foreach p in `treat_`y'' {
            replace anti_shock = 1 if strmatch(province, "*`p'*") & year == `y'
        }
    }
}
encode province,gen(prov_id)
encode city,gen(city_id)
bysort adm_code: egen suspect = max(city_id == . & year == 2010)
drop if suspect == 1
egen prov_year = group(province year)
egen city_year = group(city year)
bysort adm_code (year): gen cum_anti_shock = sum(anti_shock)
drop if year<2009
xtset adm_code year
describe
summarize

gen d=cum_anti_shock*大气重点控制

replace d=0 if d==.
local outcomes "Co No2 So2 Pm25 Pm10"
foreach y of local outcomes {
   reghdfe `y' cum_anti_shock, absorb(adm_code year) vce(cluster prov_id)
      reghdfe `y' cum_anti_shock 大气重点控制, absorb(adm_code year) vce(cluster prov_id)
	     reghdfe `y' cum_anti_shock 大气重点控制 d, absorb(adm_code year) vce(cluster prov_id)
		     reghdfe `y' cum_anti_shock 大气重点控制, absorb(adm_code prov_year) vce(cluster prov_id)
	     reghdfe `y' cum_anti_shock 大气重点控制 d, absorb(adm_code prov_year) vce(cluster prov_id)
}
gen d2=anti_shock*大气重点控制
replace d2=0 if d2==.
gen C=大气重点控制*inspection
replace C=0 if C==.
bysort adm_code (year): gen cum_inspection = sum(inspection)
gen prov_id_trend=prov_id
local outcomes "Co No2 So2 Pm25 Pm10"

foreach y of local outcomes {
    
    
    di as text "Processing: `y'"
    
    * ---------- (1) 运行 DCDH  ----------
    did_multiplegt_dyn `y' adm_code year d2, ///
        same_switchers effects(2) placebo(2) ///
      cluster(prov_id)  controls(大气重点控制 anti_shock inspection C) trends_nonparam(prov_id)
   
    
   
}

//--------------------------//
* ==============================================================================
* 4.Compliance 
* ==============================================================================
//--------------------------//
import excel "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\results\city_panel_full.xlsx", sheet("Sheet1") firstrow clear

capture rename City city
capture rename Year year
duplicates drop city year , force
 
capture rename city 地区
capture rename year 年份
merge 1:1 地区 年份 using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\data\city_string.dta", keep(match) nogenerate
capture rename 年份 year
capture rename 地区 city
merge 1:1 city year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\For.dta",keep(match) nogenerate
capture rename 市代码 adm_code
merge 1:1 adm_code year using "C:\Users\siyang zhu\Desktop\Anti-corruption\proposition1\D.dta",keep(match) nogenerate

encode province,gen(prov_id)
encode city,gen(city_id)
egen prov_year = group(province year)
reghdfe realgdp JS_Plan ,absorb(year city)
reghdfe realgdp JS_Plan ,absorb(year city) cluster(prov_id)
reghdfe realgdp JS_Plan  全市第二产业增加值占GDP比重 全市自然增长率  全市地区生产总值增长率 全市农林牧渔业从业人员数万人 全市制造业从业人员数万人 全市建筑业从业人员数万人 全市金融业从业人员数万人 ,absorb(year city) cluster(prov_id)



reghdfe realgdp Cosine_Plan ,absorb(year city)
reghdfe realgdp Cosine_Plan,absorb(year city) cluster(prov_id)
reghdfe realgdp Cosine_Plan  全市第二产业增加值占GDP比重 全市自然增长率  全市地区生产总值增长率 全市农林牧渔业从业人员数万人 全市制造业从业人员数万人 全市建筑业从业人员数万人 全市金融业从业人员数万人 ,absorb(year city) cluster(prov_id)

reghdfe realgdp JS_Plan if year>=2013 ,absorb(year city) cluster(prov_id)
reghdfe realgdp JS_Plan if year<2013 ,absorb(year city) cluster(prov_id)


local outcomes "JS_Plan Cosine_Plan"
xtset city_id year
foreach y of local outcomes {
        di _n "--------------------------------------------------"
        di ">>> Outcome Variable: `y'"
        di "--------------------------------------------------"
       
        * ----------------------------------------
        * A: lpdid 
        * ----------------------------------------
        di "--> [lpdid] Running WITHOUT controls..."
        lpdid `y', unit(city_id) time(year) treat(anti_shock) ///
            pre_window(2) post_window(0) cluster(city_id) nonabsorbing(2, oneoff) nocomp rw 
			  cap noisily did_multiplegt_dyn `y' city_id year anti_shock, ///
            same_switchers effects(1) placebo(1) cluster(city_id) 

 
}

