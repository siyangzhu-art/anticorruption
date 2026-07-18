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




/*
bysort prov_year:egen mean_realgdp=mean(realgdp)
bysort prov_year:egen mean_JSPlan=mean(JS_Plan)
bysort prov_year:egen sd_realgdp=sd(realgdp)
bysort prov_year:egen sd_JSPlan=sd(JS_Plan)

gen st_realgdp=(realgdp-mean_realgdp)/sd_realgdp
gen st_JSPlan=(JS_Plan-mean_JSPlan)/sd_JSPlan
twoway scatter st_JSPlan st_realgdp if year<2013 || lfit st_JSPlan st_realgdp

twoway scatter st_JSPlan st_realgdp if year>=2013 || lfit st_JSPlan st_realgdp

* ==========================================
* 正确步骤 1：全样本统一控制固定效应（基准一致）
* ==========================================
reghdfe realgdp,   absorb(city_id prov_year) residuals(res_y_gdp)
reghdfe JS_Plan,   absorb(city_id prov_year) residuals(res_x_js)


* ==========================================
* 正确步骤 2：处理残差中的异常值（Outliers）
* ==========================================

* --- 方案 A：双侧 1% 缩尾处理（将超出 1% 和 99% 分位数的异常值拉回边界，最常用） ---
/*winsor2 res_y_gdp, cuts(1 99)
winsor2 res_x_js,  cuts(1 99)*/

* --- 方案 B（备选）：直接将极端异常值设为缺失（根据你原图的右侧长尾，剔除x残差 > 0.3 的点） ---
* gen w_res_y = res_y_gdp if res_x_js <= 0.3 & res_x_js >= -0.15
* gen w_res_x = res_x_js  if res_x_js <= 0.3 & res_x_js >= -0.15


* ==========================================
* 正确步骤 3：在处理完异常值的【干净残差】上进行时间分段
* ==========================================
gen w_res_x_before = res_x_js if year < 2013
gen w_res_x_after  = res_x_js if year >= 2013


* ==========================================
* 正确步骤 4：一键绘制无异常值干扰的学术图表
* ==========================================
twoway ///
    || scatter  res_y_gdp w_res_x_before, mcolor(gs12%20) msize(small) yaxis(1) /// 1. 缩尾后的整体散点
	 || scatter  res_y_gdp w_res_x_after, mcolor(gs12%60) msize(small) yaxis(1) /// 1. 缩尾后的整体散点
    || lfit res_y_gdp w_res_x_before, lcolor(blue) lwidth(medthick) yaxis(2)  /// 2. 2013前拟合线
    || lfit res_y_gdp w_res_x_after,  lcolor(red) lwidth(medthick) yaxis(2)   /// 3. 2013后拟合线
    ||, /// 图表美化
    title("Piecewise Linear Fit: JS_Plan & RealGDP (Outliers Removed)", size(medium)) ///
    xtitle("JS_Plan (Winsorized Residual)") ///
    ytitle("RealGDP Residual (Scatter)", axis(1)) ///
    ytitle("RealGDP Residual (Fitted Slope Trend)", axis(2)) ///
    legend(order(1 "Residual Scatter" 2 "Pre-2013 Fit" 3 "Post-2013 Fit") rows(4))

* 清理临时变量
drop res_y_gdp res_x_js res_y w_res_x w_res_x_before w_res_x_after


* ==========================================
* 同理应用到方案二：Cosine_Plan 与 RealGDP
* ==========================================
reghdfe realgdp,     absorb(city_id year prov_year) residuals(res_y_cos)
reghdfe Cosine_Plan, absorb(city_id year prov_year) residuals(res_cx_all)

* 双侧 1% 缩尾
winsor2 res_y_cos,  cuts(1 99)
winsor2 res_cx_all, cuts(1 99)

gen w_res_cx_before = res_cx_all_w if year <= 2013
gen w_res_cx_after  = res_cx_all_w  if year >= 2013

twoway ///
    || scatter res_y_cos_w res_cx_all_w, mcolor(gs12%40) msize(small) yaxis(1) ///
    || lfit res_y_cos_w w_res_cx_before, lcolor(midblue) lwidth(medthick) yaxis(2)  ///
    || lfit res_y_cos_w w_res_cx_after,  lcolor(orange) lwidth(medthick) yaxis(2)   ///
    ||, ///
    title("Piecewise Linear Fit: Cosine_Plan & RealGDP (Outliers Removed)", size(medium)) ///
    xtitle("Cosine_Plan (Winsorized Residual)") ///
    ytitle("RealGDP Residual (Scatter)", axis(1)) ///
    ytitle("RealGDP Residual (Fitted Slope Trend)", axis(2)) ///
    legend(order(1 "Residual Scatter" 2 "Pre-2013 Fit" 3 "Post-2013 Fit") rows(3))

drop res_y_cos res_cx_all w_res_y_cos w_res_cx w_res_cx_before w_res_cx_after