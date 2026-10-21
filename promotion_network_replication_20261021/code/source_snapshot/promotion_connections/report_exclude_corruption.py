from pathlib import Path
import sys,shutil,hashlib,json,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'exclude_corruption_leader_provinces_2026_10_21'
for f in ['annual.log','cumulative.log']:
    assert 'closed on:' in (O/f).read_text(encoding='utf-8',errors='replace')[-1000:],f+' unfinished'
checks=[]
def ck(name,ok):
    checks.append(dict(check=name,passed=bool(ok)))
    assert ok,name
def save(d,name):d.to_csv(O/name,index=False,encoding='utf-8-sig')
def holm(values):
    p=np.array(values,float);order=np.argsort(p);ans=np.empty(len(p));ans[order]=np.minimum(1,np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p)))));return ans
AM=pd.read_csv(O/'annual_models.csv');CM=pd.read_csv(O/'cumulative_models.csv')
A=pd.read_stata(O/'annual_results.dta').merge(AM,on='model_id',validate='m:1')
AS=pd.read_stata(O/'annual_stats.dta').merge(AM,on='model_id',validate='m:1')
AJ=pd.read_stata(O/'annual_joint.dta').merge(AM,on='model_id',validate='m:1')
A=A.merge(AS[['model_id','estimator','N','G','df']],on=['model_id','estimator'],validate='m:1')
C=pd.read_stata(O/'cumulative_results.dta').merge(CM,on='model_id',validate='1:1')
CW=pd.read_stata(O/'cumulative_wild.dta');C=C.merge(CW,on='model_id',how='left',validate='1:1')
FD=pd.read_stata(O/'cumulative_FD_points.dta').rename(columns={'b':'b_FD'})
V=C.merge(FD,on='model_id',validate='1:1');V['abs_diff']=abs(V.b-V.b_FD)
ck('32 annual models completed',len(AS)==32)
ck('108 cumulative models completed',len(C)==108)
ck('No annual estimation failures',pd.read_stata(O/'annual_failures.dta').empty)
ck('No cumulative estimation failures',pd.read_stata(O/'cumulative_failures.dta').empty)
ck('All cumulative point estimates independently reproduced in first differences',V.abs_diff.max()<1e-6)
ck('12 wild tests succeeded',len(CW)==12 and CW.rc.eq(0).all() and CW.p_wild.notna().all())
ck('Annual same sample across four FEs per exclusion rule',AS.N.eq(AS.expected_N).all())
ck('Cumulative same original outcome-complete common cohort after province exclusions',C.N.eq(C.expected_N).all())
oldA=pd.read_csv(B/'control_FE_sensitivity_post4/all_level_results.csv').query("control_id=='C08' and sample=='fixed'")
z=A[A.variant.eq('Original')].merge(oldA,on=['estimator','fe','term'],suffixes=('','_old'),validate='1:1')
for col in ['b','se','p','lo','hi']:ck('Original annual '+col+' reproduced',len(z)==80 and np.allclose(z[col],z[col+'_old'],atol=1e-6,equal_nan=True))
oldC=pd.read_csv(B/'cumulative_promotion_TWFE_12_24_36m/all_TWFE_results.csv').query("sample=='common_all_H'")
z=C[C.variant.eq('Original')].merge(oldC,on=['H','fe','control'],suffixes=('','_old'),validate='1:1')
for col in ['b','se','p','lo','hi']:ck('Original cumulative '+col+' reproduced',len(z)==27 and np.allclose(z[col],z[col+'_old'],atol=1e-6,equal_nan=True))
W=pd.read_stata(O/'annual_SA_weights.dta');P=pd.read_stata(O/'annual_SA_cohort.dta')
z=W.merge(P,on=['model_id','cohort','term']);z['component']=z.weight*z.b
ag=z.groupby(['model_id','term']).component.sum().reset_index()
sa=A[A.estimator.eq('Sun_Abraham')&A.term.str.startswith('d_')].merge(ag,on=['model_id','term'],validate='1:1')
ck('All 128 Sun-Abraham cohort-weighted points verified',len(sa)==128 and np.allclose(sa.b,sa.component,atol=1e-6))
for label,d in [('Annual',A),('Cumulative',C)]:
    ck(label+' all coefficients identified',d.se.gt(0).all() and d.b.notna().all())
    crit=t.ppf(.975,d.df)
    ck(label+' 95 percent province-clustered t intervals verified',np.allclose(d.lo,d.b-crit*d.se,atol=1e-6) and np.allclose(d.hi,d.b+crit*d.se,atol=1e-6))
for variant in C.variant.unique():
    ix=C.index[C.variant.eq(variant)&C.fe.eq('I_PXY')&C.control.eq('full')]
    C.loc[ix,'p_holm_three_H']=holm(C.loc[ix,'p']);C.loc[ix,'p_wild_holm_three_H']=holm(C.loc[ix,'p_wild'])
for (v,e),g in A[A.term.eq('post_average')].groupby(['variant','estimator']):A.loc[g.index,'p_holm_four_FE']=holm(g.p)
save(A,'annual_all_results.csv');save(AS,'annual_model_samples.csv');save(AJ,'annual_joint_tests.csv')
save(C,'cumulative_all_results.csv');save(V[['model_id','b','b_FD','abs_diff']],'FD_validation.csv')
SF=pd.read_csv(O/'sample_flow.csv');SP=pd.read_csv(O/'annual_support.csv');CA=pd.read_csv(O/'province_exclusion_evidence.csv')
lab={'Original':'Original sample','Strict':'Exclude corruption removals','Plus_discipline':'+ exclude Sichuan','Plus_recent':'+ exclude Liaoning and Gansu'}
colors={'Original':'#888888','Strict':'#247e9e','Plus_discipline':'#d08a31','Plus_recent':'#9b4f81'}
markers={'Original':'o','Strict':'s','Plus_discipline':'D','Plus_recent':'^'}
flab={'I_YEAR':'Individual + year','I_PXY':'Individual + province x year','I_CITY_YEAR':'Individual + city + year','I_CITY_PXY':'Individual + city + province x year'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
gallery=[]
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=170,facecolor='white');plt.close(fig);gallery.append((name,title))
def draw(ax,q,label,color,marker,offset):
    q=q[q.term.str.startswith('d_')].copy();q['k']=q.term.map(lambda x:-int(x[3:]) if x.startswith('d_m') else int(x[3:]));q=q.sort_values('k')
    ax.errorbar(q.k+offset,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=marker,linestyle='none',capsize=3,markersize=4,color=color,label=label)
    ax.scatter([-1+offset],[0],s=24,marker=marker,facecolors='white',edgecolors=color,zorder=4)
def style(ax):
    ax.axhline(0,color='gray',ls='--',lw=.8);ax.axvline(0,color='#b38c39',ls=':',lw=.9)
    ax.set_xticks(range(-4,5));ax.set_xlabel('Years relative to first inspection');ax.grid(axis='y',alpha=.15)
fig,axs=plt.subplots(1,2,figsize=(15,6.8),sharey=True)
for ax,est in zip(axs,['Sun_Abraham','TWFE_fixed']):
    for j,v in enumerate(lab):draw(ax,A[A.variant.eq(v)&A.fe.eq('I_PXY')&A.estimator.eq(est)],lab[v],colors[v],markers[v],(j-1.5)*.10)
    style(ax);ax.set_title('Sun-Abraham' if est=='Sun_Abraham' else 'TWFE: fixed baseline connection')
axs[0].set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('Exclude provinces with corruption-related leadership removals\nFull C08 controls | Individual + province-by-year FE | 95% province-clustered CIs',fontsize=15)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.865),ncol=2,frameon=False)
fig.subplots_adjust(top=.70,bottom=.24,wspace=.10,left=.07,right=.98)
fig.text(.06,.03,'Strict exclusions remove Hebei/Fujian from the observed city-official sample; Shanghai/Tianjin/Chongqing were absent already.\nDisciplinary sensitivity additionally removes Sichuan; recent-former sensitivity also removes Liaoning/Gansu.\nOriginal baseline relationships, outcomes, dates and controls preserved. Whole provinces removed in all years.\nSelection based on observed subsequent removals is a sensitivity analysis; ordinary leader turnover is still possible.',fontsize=9)
export(fig,'01_main_event_study_province_year.png','Main event study: original and all exclusion definitions')
for v in ['Strict','Plus_discipline','Plus_recent']:
    fig,axs=plt.subplots(2,2,figsize=(14,10),sharey=True)
    for ax,fe in zip(axs.flat,flab):
        for est,marker in [('Sun_Abraham','o'),('TWFE_fixed','s')]:
            for j,variant in enumerate(['Original',v]):
                offset=({('Sun_Abraham','Original'):-.15,('TWFE_fixed','Original'):-.05,('Sun_Abraham',v):.05,('TWFE_fixed',v):.15})[(est,variant)]
                draw(ax,A[A.variant.eq(variant)&A.fe.eq(fe)&A.estimator.eq(est)],('Original' if variant=='Original' else 'Excluded')+' | '+('Sun-Abraham' if est=='Sun_Abraham' else 'TWFE'),colors[variant],marker,offset)
        style(ax);ax.set_title(flab[fe])
    for ax in axs[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
    fig.suptitle(lab[v]+' | Full C08 controls\nSun-Abraham and TWFE | Four FE structures | 95% province-clustered CIs',fontsize=15)
    fig.legend(*axs[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=2,frameon=False)
    fig.subplots_adjust(top=.79,bottom=.14,wspace=.10,hspace=.32,left=.07,right=.98)
    fig.text(.06,.035,'Same observations across FE variants within each province-exclusion sample. City FE are additive, not city-by-year.\nPoint estimates and CIs only; reference k=-1 has no estimated CI. Full annual personal and lagged officer-city economic controls.\nAt k=+4 only four baseline-connected officials remain; province exclusion does not cure this limited support.',fontsize=9)
    export(fig,f'02_four_FE_{v}.png','Four FE comparisons: '+lab[v])
fig,axs=plt.subplots(1,3,figsize=(15,6.8),sharey=True)
for ax,fe in zip(axs,['I_PERIOD','I_CALENDAR','I_PXY']):
    for j,v in enumerate(lab):
        q=C[C.variant.eq(v)&C.fe.eq(fe)&C.control.eq('full')].sort_values('H');x=np.arange(3)+(j-1.5)*.13
        ax.errorbar(x,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=markers[v],linestyle='none',color=colors[v],capsize=3,ms=4,label=lab[v])
    ax.axhline(0,color='gray',ls='--',lw=.8);ax.set_xticks(range(3),['12m','24m','36m']);ax.grid(axis='y',alpha=.15)
    ax.set_title({'I_PERIOD':'Individual + pre/post phase','I_CALENDAR':'Individual + endpoint year','I_PXY':'Individual + province x phase'}[fe])
axs[0].set_ylabel('Change in cumulative promotion gap (pp)')
fig.suptitle('Equal-length pre/post cumulative promotion TWFE\nOriginal and excluded-province samples | Full controls | 95% province-clustered CIs',fontsize=15)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.87),ncol=2,frameon=False)
fig.subplots_adjust(top=.71,bottom=.22,wspace=.08,left=.07,right=.98)
fig.text(.06,.035,'Same original cohort within all three horizons after whole-province exclusions; fixed C0 and baseline X x Post.\nPre/post periods have equal lengths. Province x phase FE here are not an annual province-year panel.\nOriginal / strict / +discipline / +recent: 422 / 393 / 367 / 324 officials; 45 / 45 / 44 / 33 connected.\nLong pre-window cohort selection and leader turnover remain limitations; wild-bootstrap and Holm results are exported.',fontsize=9)
export(fig,'03_cumulative_TWFE_full_controls.png','Cumulative TWFE: original versus exclusions')
fig,axs=plt.subplots(1,3,figsize=(15,6),sharey=True)
for ax,control in zip(axs,['none','personal','full']):
    for j,v in enumerate(lab):
        q=C[C.variant.eq(v)&C.fe.eq('I_PXY')&C.control.eq(control)].sort_values('H');x=np.arange(3)+(j-1.5)*.13
        ax.errorbar(x,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=markers[v],linestyle='none',color=colors[v],capsize=3,ms=4,label=lab[v])
    ax.axhline(0,color='gray',ls='--',lw=.8);ax.set_xticks(range(3),['12m','24m','36m']);ax.grid(axis='y',alpha=.15);ax.set_title({'none':'FE only','personal':'Baseline personal controls x Post','full':'Full baseline controls x Post'}[control])
axs[0].set_ylabel('Change in cumulative promotion gap (pp)')
fig.suptitle('Cumulative TWFE | Individual + province x pre/post phase\nControl sensitivity on identical observations | 95% province-clustered CIs',fontsize=15)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False)
fig.subplots_adjust(top=.69,bottom=.17,wspace=.08,left=.07,right=.98)
fig.text(.06,.035,'All control combinations shown; none selected by significance. Baseline sample, relationship flags and outcome coding preserved.\nProvince exclusions are based on subsequent leadership outcomes; these are conditional sensitivity estimates.',fontsize=9)
export(fig,'04_cumulative_control_sensitivity.png','Cumulative control sensitivity')
with pd.ExcelWriter(O/'剔除腐败更替省份_主回归全部结果.xlsx') as w:
    A.to_excel(w,sheet_name='Annual_SA_TWFE',index=False);AJ.to_excel(w,sheet_name='Annual_joint',index=False)
    C.to_excel(w,sheet_name='Cumulative_TWFE',index=False);SF.to_excel(w,sheet_name='Sample_flow',index=False)
    SP.to_excel(w,sheet_name='Event_support',index=False);CA.to_excel(w,sheet_name='Exclusion_evidence',index=False)
    pd.DataFrame(checks).to_excel(w,sheet_name='Validation',index=False)
save(pd.DataFrame(checks),'validation_checks.csv')
page='<html><meta charset="utf-8"><title>Province exclusion sensitivity</title><style>body{max-width:1300px;margin:30px auto;font:17px sans-serif}img{width:100%}</style><h1>剔除腐败更替省份：主回归敏感性</h1><p>严格腐败离任、加四川违纪撤职、加辽宁甘肃离任后被查三种口径均保留。原样本并列。</p>'
for f,title in gallery:page+=f'<h2>{html.escape(title)}</h2><img src="figures/{f}">'
page+='</html>';(O/'index.html').write_text(page,encoding='utf-8')
methods='''# 排除腐败相关领导更替省份，重跑主回归

主版Strict：河北、福建、天津、上海、重庆，在2006—2017年发生任内腐败查处关联的书记/省长更替。直辖市本来不在主地级市样本，实际删除河北福建。
Plus_discipline：主版加四川魏宏严重违纪撤职。官方处分未在此被改写成受贿定罪。
Plus_recent：再加辽宁王珉、甘肃王三运，二人离任后12个月内被查。不能由该时间接近认定普通调职当时由案件引起。
所有省份整段删除；不是只删查处当年，不改变关系、晋升、经济控制或任期定义。没有要求删除省份仍需达到10省。
苏荣已离任江西书记一年多后被查；白恩培离任云南书记数年后被查，不属于这些腐败更替定义。孟学农为安全事故责任辞职，不作腐败离任。副省长、常委案件不自动认定省长或省委书记被更替。
省级任职表/CPED基本信息提供候选；官方纪检通报核实分类，所有证据链接在province_exclusion_evidence.csv。没有将后任普通调动都解释成反腐因果。

年度：复用2807条原固定C0共同样本，C08全部个人控制和跟随官员任职城市的滞后经济控制；Sun-Abraham及TWFE，各四类FE。k=-4至+4，k=-1参照；四个FE在每种排除规则内部用相同观测。递归检查单例，保存所有支持数量。
累计：复用422人原共同完整样本，只剔除基期所在省；每H两条等长前后窗。原C0和原较早的关系快照原封保留；本轮不声称将其改成巡视前一刻。三类FE、三组控制全保存。省份×phase不是年度省份×年份。十二个月/二十四个月/三十六个月均提供原省聚类t区间；主FE全部控制规格补充9999次Webb wild bootstrap，seed20261015，以及三期限Holm校正。
所有累计点估计另用一阶差分回归独立校验；原年度与累计的全部对应点、SE、p、区间精确复现，SA点按cohort权重另验。未生成PDF或覆盖原数据。

解释：这是剔除已观察领导查处事件的事后样本敏感性分析。查处可能是巡视机制之一，事后筛样会改变目标总体且可能引入选择，不能直接认定巡视的净因果效应。普通调任、退休、其他原支持者离任仍然存在。年度+4仅4名事前有关系者，省份排除不解决薄弱支持；累计长事前窗存在按后续在任状态选入基期队列的问题。
'''
(O/'口径与方法.md').write_text(methods,encoding='utf-8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
manifest=[]
for f in [B/'control_FE_sensitivity_post4/fixed_panel.dta']+[B/f'cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_{h}m.dta' for h in [12,24,36]]:
    manifest.append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
save(pd.DataFrame(manifest),'source_manifest.csv')
with zipfile.ZipFile(B/'剔除腐败更替省份_主回归图表数据代码.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in O.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(O))
with zipfile.ZipFile(B/'剔除腐败更替省份_主回归图表数据代码.zip') as z:assert z.testzip() is None
print('Validation checks:',len(checks),'all passed')
print('Annual PXY post average:');print(A[A.fe.eq('I_PXY')&A.term.eq('post_average')][['variant','estimator','b','lo','hi','p','N','G']].to_string(index=False))
print('Cumulative main:');print(C[C.fe.eq('I_PXY')&C.control.eq('full')][['variant','H','b','lo','hi','p','p_wild','p_holm_three_H','p_wild_holm_three_H','N','G']].to_string(index=False))
