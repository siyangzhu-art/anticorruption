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




