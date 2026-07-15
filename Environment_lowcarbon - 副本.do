
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

