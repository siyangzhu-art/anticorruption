"""Repeat existing main models after evidence-based whole-province exclusions."""
from pathlib import Path
import pandas as pd,numpy as np,shutil,json,hashlib
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'exclude_corruption_leader_provinces_2026_10_21'
for d in [O,O/'data',O/'code',O/'figures']:d.mkdir(exist_ok=True)
cases=[
 (310000,'上海','陈良宇','S','2006-09-24','strict','https://newyork.china-consulate.gov.cn/xw/200609/t20060927_4230881.htm','Removed as Shanghai secretary with investigation; pre-2012 case'),
 (500000,'重庆','薄熙来','S','2012-04-10','strict','https://www.ccdi.gov.cn/yaowen/201308/t20130827_129029.html','March 2012 departure followed by April case; same removal episode'),
 (500000,'重庆','孙政才','S','2017-07-24','strict','https://www.ccdi.gov.cn/scdcn/zggb/djcf/201709/t20170929_40177_m.html','Official decision states July 14 removal for discipline examination; formal case July24'),
 (130000,'河北','周本顺','S','2015-07-24','strict','https://m.ccdi.gov.cn/content/a5/a9/4712.html','Serving provincial secretary when investigation announced'),
 (350000,'福建','苏树林','G','2015-10-07','strict','https://m.ccdi.gov.cn/content/3b/67/6115.html','Serving governor when investigation announced'),
 (120000,'天津','黄兴国','G/S','2016-09-10','strict','https://m.ccdi.gov.cn/content/81/43/12051.html','Serving mayor and acting party secretary'),
 (510000,'四川','魏宏','G','2016-02-04','disciplinary','https://www.xinhuanet.com/politics/2016-02/04/c_128703422.htm','Disciplinary removal/demotion; not coded as a bribery conviction'),
 (210000,'辽宁','王珉','S','2016-03-04','recent_former','https://politics.people.com.cn/n1/2016/0304/c1001-28171756.html','Left Liaoning May2015; investigated March2016 in NPC office; not proven causal departure'),
 (620000,'甘肃','王三运','S','2017-07-11','recent_former','https://m.ccdi.gov.cn/content/6e/ee/19768.html?from=singlemessage&isappinstalled=0','Left Gansu March2017; investigated July2017; not asserted contemporaneous removal')]
C=pd.DataFrame(cases,columns=['province_code','province','leader','office','case_or_discipline_date','category','source_url','classification_note'])
C['verified_on']='2026-10-21';C.to_csv(O/'province_exclusion_evidence.csv',index=False,encoding='utf-8-sig')
masks={'Original':set(),'Strict':set(C.loc[C.category.eq('strict'),'province_code']),
       'Plus_discipline':set(C.loc[C.category.isin(['strict','disciplinary']),'province_code']),
       'Plus_recent':set(C.province_code)}
(O/'exclusion_rules.json').write_text(json.dumps({k:sorted(v) for k,v in masks.items()},indent=2),encoding='utf-8')
fes={'I_YEAR':'person_id year','I_PXY':'person_id py','I_CITY_YEAR':'person_id city_code year','I_CITY_PXY':'person_id city_code py'}
ks=[-4,-3,-2,0,1,2,3,4];terms=[f'd_m{-k}' if k<0 else f'd_p{k}' for k in ks]
A=pd.read_stata(B/'control_FE_sensitivity_post4/fixed_panel.dta')
assert (A.anchor_province==A.city_code//10000*10000).all()
def core(a):
    a=a.copy()
    for _ in range(100):
        keep=pd.Series(True,index=a.index)
        for key in ['person_id','city_code','provyear']:keep&=a.groupby(key)[key].transform('size').gt(1)
        if keep.all():return a
        a=a[keep].copy()
    raise ValueError('Singleton core failed')
sample=[];support=[];models=[];mid=0
L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/annual.log", text replace','tempname rr mm jj ff ww cc',
 'postfile `rr\' long model_id str16 estimator str20 term double(b se p lo hi) using "`out\'/annual_results.dta", replace',
 'postfile `mm\' long model_id str16 estimator double(N G df) using "`out\'/annual_stats.dta", replace',
 'postfile `jj\' long model_id str16 estimator str16 test double(p) using "`out\'/annual_joint.dta", replace',
 'postfile `ff\' long model_id str16 estimator long rc using "`out\'/annual_failures.dta", replace',
 'postfile `ww\' long model_id long cohort str16 term double weight using "`out\'/annual_SA_weights.dta", replace',
 'postfile `cc\' long model_id long cohort str16 term double b using "`out\'/annual_SA_cohort.dta", replace']
def store(mid,est):
    ls=[f'post `mm\' ({mid}) ("{est}") (`NN\') (`GG\') (`DD\')']
    for label,expr in [(t,t) for t in terms]+[('post_average','(d_p1+d_p2+d_p3+d_p4)/4'),('late_average','(d_p2+d_p3+d_p4)/3')]:
        ls+=['quietly lincom '+expr+', level(95)',f'post `rr\' ({mid}) ("{est}") ("{label}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
    for label,expr in [('pretrend','d_m4 d_m3 d_m2'),('post_joint','d_p1 d_p2 d_p3 d_p4')]:
        ls+=['quietly test '+expr,f'post `jj\' ({mid}) ("{est}") ("{label}") (r(p))']
    return ls
for variant,drop in masks.items():
    q=A[~A.anchor_province.isin(drop)].copy();q['provyear']=q.anchor_province*10000+q.year
    n0=len(q);q=core(q)
    q.to_stata(O/f'data/annual_{variant}.dta',write_index=False,version=118)
    sample.append(dict(design='Annual',variant=variant,N=len(q),people=q.person_id.nunique(),G=q.anchor_province.nunique(),connected_people=q.loc[q.C0.eq(1),'person_id'].nunique(),excluded_rows=len(A)-n0,singleton_rows=n0-len(q)))
    s=q.groupby('k').agg(N=('person_id','size'),G=('anchor_province','nunique'),connected=('C0','sum')).reset_index();s['variant']=variant;support.append(s)
    for fe,absorb in fes.items():
        mid+=1;models.append(dict(model_id=mid,variant=variant,fe=fe,expected_N=len(q)))
        L += [f'use "`out\'/data/annual_{variant}.dta", clear','isid person_id year','egen py=group(anchor_province year)']
        for t,k in zip(terms,ks):L += [f'gen double {t}=(k=={k})*C0',f'gen double all_{t}=(k=={k})']
        cov='age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag'
        if fe in ['I_YEAR','I_CITY_YEAR']:cov+=' '+' '.join('all_'+t for t in terms)
        L += ['capture noisily eventstudyinteract Y '+' '.join(terms)+f', cohort(treated_cohort) control_cohort(never) absorb({absorb}) vce(cluster anchor_province) covariates({cov})','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) ("Sun_Abraham") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)',f'assert `NN\'=={len(q)}','matrix BI=e(b_iw)','matrix VI=e(V_iw)','matrix WI=e(ff_w)','matrix CI=e(b_interact)']
        for i,t in enumerate(terms,1):
            for j,cohort in enumerate([2013,2014],1):L += [f'post `ww\' ({mid}) ({cohort}) ("{t}") (WI[{j},{i}])',f'post `cc\' ({mid}) ({cohort}) ("{t}") (CI[{j},{i}])']
        L += ['ereturn post BI VI, obs(`NN\') dof(`DD\')']+store(mid,'Sun_Abraham')+['}']
        L += ['capture noisily reghdfe Y '+' '.join(terms)+' '+cov+f', absorb({absorb}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) ("TWFE_fixed") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)',f'assert `NN\'=={len(q)}']+store(mid,'TWFE_fixed')+['}']
L += ['postclose `rr\'','postclose `mm\'','postclose `jj\'','postclose `ff\'','postclose `ww\'','postclose `cc\'','log close','exit, clear']
(O/'code/run_annual.do').write_text('\n'.join(L)+'\n',encoding='utf-8')
pd.DataFrame(models).to_csv(O/'annual_models.csv',index=False)
pd.concat(support).to_csv(O/'annual_support.csv',index=False)
# Cumulative design: retain the SAME original common cohort, controls, dates and outcomes.
CM=[];mid=0
L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/cumulative.log", text replace','tempname rr ff ww vv',
 'postfile `rr\' long model_id double(b se p lo hi N G df K) using "`out\'/cumulative_results.dta", replace',
 'postfile `ff\' long model_id long rc using "`out\'/cumulative_failures.dta", replace',
 'postfile `ww\' long model_id double(p_wild) long rc using "`out\'/cumulative_wild.dta", replace',
 'postfile `vv\' long model_id double b using "`out\'/cumulative_FD_points.dta", replace']
for variant,drop in masks.items():
    for h in [12,24,36]:
        q=pd.read_stata(B/f'cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_{h}m.dta')
        q=q[~q.anchor_province.isin(drop)].copy();assert not q.duplicated(['person_id','post']).any()
        assert q.groupby('person_id').size().eq(2).all()
        filename=f'cumulative_{variant}_{h}.dta';q.to_stata(O/'data'/filename,write_index=False,version=118)
        if h==12:sample.append(dict(design='Cumulative',variant=variant,N=len(q),people=q.person_id.nunique(),G=q.anchor_province.nunique(),connected_people=q.loc[q.C0.eq(1),'person_id'].nunique(),excluded_rows=844-len(q),singleton_rows=0))
        for fe,absorb in [('I_PERIOD','pid post'),('I_CALENDAR','pid end_year'),('I_PXY','pid pp')]:
            for control in ['none','personal','full']:
                mid+=1;CM.append(dict(model_id=mid,variant=variant,H=h,fe=fe,control=control,filename=filename,expected_N=len(q)))
                cov='' if control=='none' else 'c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0'
                if control=='full':cov+=' c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0'
                L += [f'use "`out\'/data/{filename}", clear',f'capture noisily reghdfe Y CP {cov}, absorb({absorb}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) (`rc\')','if `rc\'==0 {',f'assert e(N)=={len(q)}','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','local KK=e(df_m)+e(df_a)','quietly lincom CP, level(95)',f'post `rr\' ({mid}) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\') (`DD\') (`KK\')','}']
                fd='' if control=='none' else 'age0 age20 tenure0 tenure20 i.rank0 role0'
                if control=='full':fd+=' growth0 lngdppc0 lnpop0'
                if fe=='I_CALENDAR':fd+=' i.end_year0'
                if fe=='I_PXY':fd+=' i.prov'
                L += [f'use "`out\'/data/{filename}", clear','keep person_id anchor_province C0 post Y end_year age0 age20 tenure0 tenure20 rank0 role0 growth0 lngdppc0 lnpop0','reshape wide Y end_year, i(person_id) j(post)','gen deltaY=Y1-Y0','egen prov=group(anchor_province)',f'quietly regress deltaY C0 {fd}, vce(cluster anchor_province)',f'post `vv\' ({mid}) (_b[C0])']
                if fe=='I_PXY' and control=='full':L += ['capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph','local rc=_rc',f'if `rc\'==0 post `ww\' ({mid}) (r(p)) (`rc\')',f'if `rc\'!=0 post `ww\' ({mid}) (.) (`rc\')']
L += ['postclose `rr\'','postclose `ff\'','postclose `ww\'','postclose `vv\'','log close','exit, clear']
(O/'code/run_cumulative.do').write_text('\n'.join(L)+'\n',encoding='utf-8')
pd.DataFrame(CM).to_csv(O/'cumulative_models.csv',index=False)
pd.DataFrame(sample).to_csv(O/'sample_flow.csv',index=False)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
print(pd.DataFrame(sample).to_string(index=False));print('Prepared 32 annual and 108 cumulative regressions; 12 cumulative wild tests.')
