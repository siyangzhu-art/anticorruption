from pathlib import Path
import sys,json,hashlib,shutil,zipfile,html,re
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'event_study_individual_FE'
R=pd.read_csv(OUT/'event_coefficients.csv');JT=pd.read_csv(OUT/'joint_tests.csv');MM=pd.read_csv(OUT/'model_summary.csv')
S=pd.read_stata(OUT/'stata_validation.dta',convert_categoricals=False);SJ=pd.read_stata(OUT/'stata_joint_validation.dta',convert_categoricals=False)
Q=R[~R.reference].merge(S,on=['model_id','contrast'],suffixes=('_python','_stata'),validate='1:1');checks=pd.read_csv(OUT/'pre_stata_validation.csv').to_dict('records')
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
for c in ['b','se','p','lo','hi','N','K','G','df']:ck('Independent Stata '+c,np.allclose(Q[c+'_python'],Q[c+'_stata'],atol=2e-6,rtol=2e-6),float(abs(Q[c+'_python']-Q[c+'_stata']).max()))
JQ=JT.merge(SJ,on=['model_id','test'],suffixes=('_python','_stata'),validate='1:1')
for c in ['F','p','df_num']:ck('Independent Stata joint '+c,np.allclose(JQ[c+'_python'],JQ[c+'_stata'],atol=2e-6,rtol=2e-6))
ck('All 198 nonreference contrasts independently validated',len(Q)==198)
ck('Eight wild bootstraps completed',S.boot_rc.eq(0).sum()==6 and SJ.boot_rc.eq(0).sum()==2)
assert all(c['passed'] for c in checks)
R=R.merge(S[['model_id','contrast','p_wild','boot_rc']],on=['model_id','contrast'],how='left',validate='1:1');JT=JT.merge(SJ[['model_id','test','p_wild','boot_rc']],on=['model_id','test'],how='left',validate='1:1')
R.to_csv(OUT/'event_coefficients_validated.csv',index=False,encoding='utf-8-sig');JT.to_csv(OUT/'joint_tests_validated.csv',index=False,encoding='utf-8-sig');pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
LABEL={'I_YEAR':'Individual + year FE','I_PXY':'Individual + province-by-year FE','PXY':'Province-by-year FE'}
COL={'I_YEAR':'#287c9e','I_PXY':'#cf8735','PXY':'#888888'}
gallery=[]
def pv(x):return 'NA' if pd.isna(x) else ('<0.001' if x<.001 else f'{x:.3f}')
def export(fig,name,title):fig.savefig(OUT/'figures'/name,dpi=180);plt.close(fig);gallery.append((name,title))
def curve(ax,mid,estimand='change',offset=0,label=None):
 q=R[R.model_id.eq(mid)&R.estimand.eq(estimand)].sort_values('relative_year');fe=q.fe.iloc[0];z=q[~q.reference]
 ax.errorbar(z.relative_year+offset,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ls='none',ms=5,capsize=4,color=COL[fe],label=label)
 ref=q[q.reference]
 if len(ref):ax.plot(ref.relative_year+offset,ref.b,marker='o',ls='none',mfc='white',mec=COL[fe],ms=6)
 return q
def event(mid,name,compare=False):
 m=MM[MM.model_id.eq(mid)].iloc[0];fig,ax=plt.subplots(figsize=(12.5,7.5));ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1)
 if compare:
  for i,tid in enumerate([1,2,3]):q=curve(ax,tid,offset=(i-1)*.11,label=LABEL[MM[MM.model_id.eq(tid)].fe.iloc[0]])
  ax.legend(fontsize=9,loc='best')
 else:q=curve(ax,mid)
 ks=sorted(q.relative_year.astype(int));ax.set_xticks(ks);ax.set_xlim(min(ks)-.4,max(ks)+.4);ax.set_xlabel('Years relative to first provincial inspection');ax.set_ylabel('Change in connection-related promotion gap (pp)');ax.grid(axis='y',alpha=.15)
 title='Event study: promotion return to either provincial-leader tie\n'+('Fixed-effect comparison on identical observations' if compare else LABEL[m.fe])+' | Reference k=-1 | 95% CIs'
 fig.suptitle(title,fontsize=15,y=.98)
 if not compare:
  j=JT[JT.model_id.eq(mid)&JT.test.eq('pretrend')].iloc[0]
  ax.text(.02,.97,'Joint pretrend p: '+pv(j.p)+(' | Wild p: '+pv(j.p_wild) if pd.notna(j.p_wild) else ''),transform=ax.transAxes,va='top',fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
 fig.subplots_adjust(top=.81,bottom=.27,left=.12,right=.97)
 note=f'N={int(m.N):,}; {int(m.people):,} officials; {int(m.G)} province clusters. Same complete-case observations across FE variants in each range.'
 fig.text(.065,.025,note+'\nUnified event-time slopes; no inspection-cohort interactions or Xi conditioning. Controls: age profile, tenure, rank and current role.\nEvent-time main effects included when not absorbed by FE. Linear age is absorbed by individual + time FE.\nProvince-clustered CR1 t CIs; pointwise, no connecting lines. Reference has no estimated CI. Dynamic ties: conditional associations.',fontsize=8.1)
 export(fig,name,title)

event(1,'01_individual_year_FE_event_study.png');event(2,'02_individual_province_year_FE_event_study.png');event(1,'03_fixed_effect_comparison_same_sample.png',True)
for mid,fn in [(4,'06_long_individual_year_FE.png'),(5,'07_long_individual_province_year_FE.png'),(7,'08_full_individual_year_FE.png'),(8,'09_full_individual_province_year_FE.png')]:event(mid,fn)

fig,axes=plt.subplots(1,2,figsize=(13,7))
for ax,mid in zip(axes,[1,2]):
 curve(ax,mid,'level');ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1);ax.set_xticks(range(-3,3));ax.set_xlabel('Years relative to first inspection');ax.set_ylabel('Conditional connection-related promotion gap (pp)');ax.grid(axis='y',alpha=.15);ax.set_title(LABEL[MM[MM.model_id.eq(mid)].fe.iloc[0]],fontsize=11)
fig.suptitle('Conditional relationship-gap levels with individual fixed effects\n95% province-clustered CIs; k=-1 is estimated here',fontsize=14)
fig.subplots_adjust(top=.79,bottom=.23,wspace=.27)
fig.text(.065,.035,'Same 3,420 officer-years and controls. C_any changes within 69 of 928 officials in this window.\nThe C_any main coefficient relies on within-person connection changes; interactions also use time-varying event indicators.\nThese levels are conditional within-person model parameters, not the previous cross-sectional gaps. No connecting lines.',fontsize=8.2)
export(fig,'04_conditional_gap_levels_individual_FE.png','Conditional gap levels under individual fixed effects')

fig,axes=plt.subplots(1,2,figsize=(13,7))
for ax,mid in zip(axes,[1,2]):
 q=R[R.model_id.eq(mid)&R.estimand.isin(['pre_mean','post_mean','post_minus_pre'])].set_index('estimand');ax.axhline(0,color='gray',ls='--',lw=1)
 for j,est in enumerate(['pre_mean','post_mean','post_minus_pre']):
  z=q.loc[est];ax.errorbar(j,z.b,yerr=[[z.b-z.lo],[z.hi-z.b]],fmt=['o','s','D'][j],capsize=4,color=['#287c9e','#cf8735','#a9537e'][j]);ax.annotate(f'{z.b:+.2f}',(j,z.b),xytext=(8,5),textcoords='offset points')
 ax.set_xticks([0,1,2],['Before\nk=-3,-2,-1','After\nk=0,+1,+2','After - Before']);ax.set_ylabel('Conditional promotion gap (pp)');ax.set_title(LABEL[MM[MM.model_id.eq(mid)].fe.iloc[0]],fontsize=11);ax.grid(axis='y',alpha=.15);ax.set_xlim(-.4,2.5)
 ax.text(.5,-.24,'Raw p: '+' / '.join(pv(q.loc[e,'p']) for e in ['pre_mean','post_mean','post_minus_pre'])+'\nWild p: '+' / '.join(pv(q.loc[e,'p_wild']) for e in ['pre_mean','post_mean','post_minus_pre']),transform=ax.transAxes,ha='center',fontsize=8.5)
fig.suptitle('Average conditional connection gaps: before / after / change\nSame sample | Individual fixed effects | 95% CIs',fontsize=14)
fig.subplots_adjust(top=.80,bottom=.35,wspace=.28)
fig.text(.065,.025,'Unweighted averages across the three pre / three post relative years, using full covariance for contrasts.\nWebb wild bootstrap: 9,999 repetitions, seed 20261015. A nonsignificant post gap does not establish zero advantage.\nSingle-period changes and average before/after differences are separate tests.',fontsize=8.5)
export(fig,'05_pre_post_average_individual_FE.png','Average conditional relationship-gap levels before and after')

methods='''# 个人固定效应：统一事件研究重新估计

## 为什么重新考虑FE
此前省×年FE控制同一省同一年共同的政策、财政与晋升环境，但没有吸收官员不随时间变化的能力、背景等差异。个人+年份FE是控制这些个人异质性的自然基准；个人+省×年FE进一步控制省级当年共同冲击。两者解决不同混淆，省×年不能替代个人FE。

## 这次实际方程
主基准：100 Promotion_it=alpha_i+lambda_t+beta C_it+sum_(k≠-1)[eta_k Event_pt^k+theta_k C_it Event_pt^k]+X_it gamma+error。
更严格对照：alpha_i+lambda_pt，Event主项被lambda_pt吸收；另存没有alpha_i的lambda_pt规格作对照。全部使用统一event-time系数，不再分G_p=g，不按Xi分组。
Event_pt^k=1[t-G_p=k]，G_p为基期省份首次巡视年。C=1为与基期在任省长或省委书记至少一人有事前至少六个月共事关系；关系形成早于2012且早于双方当前共同任职开始。仅两者已知均为0才记0，未知不补0。Y是上一年末在任官员在当年的实际晋升，沿用修订主定义。
年份FE版必须补入Event主项，允许有/无关系者共同受到巡视影响。该主项在省×年FE下被吸收。所有Event主项作为控制空间，若与FE共线由秩分解/Stata自动处理；不将无法单独识别的Event共同效应冒充结果。
个人+时间FE精确吸收线性年龄，因此该项明确省略；年龄平方、任期及平方、行政级别和当前职务继续控制。无个人FE对照仍控制线性年龄。没有添加大区趋势或按显著性挑选控制。

## 样本及识别
原源面板2006—2017年，个人控制、C及Y可判断的7249个人年。主相对窗[-3,2]最初3668个人年、1176人。为公平比较，三种FE都用同一完整样本，递归剔除个人或省×年FE singleton，删除248条只有一年记录，留下3420个人年、928人、27省。删除列表另存，未覆盖原始数据。这些单年官员不能提供个人内变动。
该共同样本中69人的C状态在观察期内变化。C主项/基期关系水平的识别依赖这些人的关系变化；即使某人的C不变，C×Event也可能在其任内变化，仍可贡献动态交互项。个人FE的条件关系水平与原来的跨个人差异不是同一估计对象，不能把两版系数直接当作同一总体效应。
共同长窗[-7,3]及全期[-8,4]全部报告，9个规格均保留；各窗不同FE的样本一致。全期端点只有一个巡视批次支持，支持表及源面板可核查。
主窗有8人跨省调动，审计表记录；本轮标准误继续按基期任职省份聚类，与此前口径一致。个人FE不自动处理所有跨省流动、关系内生性或晋升后的风险集退出。

## 推断和检验
27省聚类CR1与t(26)的95%逐点CI，无连线。-1为归零参照，无估计CI。统一事件研究中的theta是相对-1关系差异的变化；beta+theta是个人FE条件下的当期关系水平。
主窗个人+年FE与个人+省×年FE，各自报告事前变化联合检验、事后变化联合检验、三期前/后三期平均水平及其差。前均值、后均值、两者之差及事前联合检验补充Webb wild bootstrap，9999次、固定种子20261015。未按显著性筛点，逐点区间不是同时置信带；单个时期显著不说明持续下降。
个人+年FE：前均值+3.519pp，后均值+0.146pp，差-3.373pp（p=.627，wild=.607）。+1期相对-1为-16.700pp（常规p=.0266），+2期为-2.862pp（p=.769）。个人+省×年FE：平均差-2.629pp（p=.701，wild=.655），+1期-14.552pp（p=.0696）。前期平均水平两种个人FE下均不显著。不能据此认定“反腐前关系有用、反腐后作用消失”。
不拒绝事前检验不是平行趋势证明。动态C随领导和官员更替改变；个人FE吸收不变个人特征，但不解决全部时间变化混淆或处理选择，因此结果仍解释为条件关系回报的事件变化。

## 实现及复核
Python使用稀疏全秩FE虚拟变量投影：二部图每个连通分量固定一个基准节点，精确计算FE秩和残差，而非依赖不收敛的交替去均值。线性年龄吸收明确处理。全部198个非参照线性组合及18个联合检验由Stata18 areg独立复算；8项wild检验完成。真实数据和关系图不改写。
重跑：code/event_study_individual_FE.py → Stata code/validate_individual_FE.do → code/report_individual_FE.py。本机路径保留，移动项目需调整BASE。无PDF。
'''
(OUT/'methods_中文.md').write_text(methods,encoding='utf8')
with pd.ExcelWriter(OUT/'个人固定效应_event_study_全部结果.xlsx',engine='openpyxl') as w:
 for n,d in [('Main_TWFE',R[R.model_id.eq(1)]),('Short_all_FE',R[R.range.eq('short')]),('All_event_coefficients',R),('Joint_tests',JT),('Models',MM),('Person_identification',pd.read_csv(OUT/'individual_identification_audit.csv')),('Singleton_exclusions',pd.read_csv(OUT/'singleton_exclusions.csv.gz')),('Validation',pd.DataFrame(checks)),('Stata_contrasts',S),('Stata_joint_tests',SJ)]:
  d.to_excel(w,sheet_name=n,index=False);w.sheets[n].freeze_panes='A2';w.sheets[n].auto_filter.ref=w.sheets[n].dimensions
page='<!doctype html><meta charset="utf-8"><title>个人固定效应：关系与晋升event study</title><style>body{max-width:1450px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}h2{font-size:20px}section{margin:30px 0}</style><h1>个人+年份FE基准；个人+省份×年份FE对照</h1><p>统一event dummy系数，无Xi分组。相同重复观察样本比较FE；年份FE版本补充巡视event主项。主窗3420个人年、928人，69人关系状态变化。</p><p>个人+年FE的+1期下降16.70pp（p=.027），但平均前后差-3.37pp（p=.627）；加入个人FE后前期平均优势也估得不精确。不能据此认定关系作用消失。</p><p><a href="个人固定效应_event_study_全部结果.xlsx">Excel全部结果</a> · <a href="methods_中文.md">模型及识别说明</a></p>'
for name,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+name+'" alt="'+html.escape(title)+'"></section>'
page+='</html>';(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
ck('All HTML references valid',all((OUT/p).is_file() for p in re.findall(r'(?:src|href)="([^"]+)"',page)))
for p in (OUT/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Nine readable PNG figures',len(list((OUT/'figures').glob('*.png')))==9)
ck('No PDF generated',not list(OUT.rglob('*.pdf')))
assert all(c['passed'] for c in checks)
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')
(OUT/'summary.json').write_text(json.dumps(dict(models=len(MM),contrasts=len(R),stata_validated=len(Q),joint_tests=len(JT),checks=len(checks),all_checks_passed=True,figures=len(gallery)),ensure_ascii=False,indent=2),encoding='utf8')
pd.DataFrame([dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='file_manifest.csv']).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
archive=BASE/'个人固定效应_event_study_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print((OUT/'summary.json').read_text(encoding='utf8'),flush=True)
