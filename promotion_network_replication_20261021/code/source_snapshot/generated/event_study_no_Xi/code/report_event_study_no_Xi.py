from pathlib import Path
import sys,json,shutil,hashlib,zipfile,html,re
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'event_study_no_Xi'
R=pd.read_csv(OUT/'event_study_coefficients.csv');JT=pd.read_csv(OUT/'joint_tests.csv');MM=pd.read_csv(OUT/'model_summary.csv')
S=pd.read_stata(OUT/'stata_event_validation.dta',convert_categoricals=False)
SJ=pd.read_stata(OUT/'stata_joint_validation.dta',convert_categoricals=False)
Q=R[~R.reference].merge(S,on=['model_id','contrast'],suffixes=('_python','_stata'),validate='1:1')
checks=pd.read_csv(OUT/'pre_stata_validation.csv').to_dict('records')
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
for c in ['b','se','p','lo','hi','N','K','G','df']:
 ck('Independent Stata '+c,np.allclose(Q[c+'_python'],Q[c+'_stata'],atol=2e-6,rtol=2e-6),float(abs(Q[c+'_python']-Q[c+'_stata']).max()))
JQ=JT.merge(SJ,on=['model_id','test'],suffixes=('_python','_stata'),validate='1:1')
for c in ['F','p','df_num']:ck('Independent Stata joint-test '+c,np.allclose(JQ[c+'_python'],JQ[c+'_stata'],atol=2e-6,rtol=2e-6))
ck('Five planned wild bootstraps completed',len(S[S.boot_rc.eq(0)])==3 and len(SJ[SJ.boot_rc.eq(0)])==2)
ck('Every nonreference contrast validated',len(Q)==len(R[~R.reference]))
assert all(x['passed'] for x in checks),checks
R=R.merge(S[['model_id','contrast','p_wild','boot_rc']],on=['model_id','contrast'],how='left',validate='1:1')
JT=JT.merge(SJ[['model_id','test','p_wild','boot_rc']],on=['model_id','test'],how='left',validate='1:1')
R.to_csv(OUT/'event_study_coefficients_validated.csv',index=False,encoding='utf-8-sig');JT.to_csv(OUT/'joint_tests_validated.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')

A=pd.read_csv(OUT/'analysis_panel_2006_2017.csv.gz',low_memory=False)
support=A.groupby('k').agg(N=('person_id','size'),connected=('C_any','sum'),promotions=('promotion','sum'),G=('province_code','nunique'),cohorts=('cohort','nunique')).reset_index();support['unconnected']=support.N-support.connected
support.to_csv(OUT/'support_by_relative_year.csv',index=False,encoding='utf-8-sig')
weights=pd.read_csv(OUT/'cohort_weights.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
gallery=[]
def pv(x):return 'NA' if pd.isna(x) else ('<0.001' if x<.001 else f'{x:.3f}')
def export(fig,name,title):
 fig.savefig(OUT/'figures'/name,dpi=180);plt.close(fig);gallery.append((name,title))
def plot_curve(ax,mid,estimand='change',color='#287c9e',offset=0,label=None):
 q=R[R.model_id.eq(mid)&R.estimand.eq(estimand)].sort_values('relative_year')
 est=q[~q.reference];ax.errorbar(est.relative_year+offset,est.b,yerr=[est.b-est.lo,est.hi-est.b],fmt='o',ls='none',ms=5,color=color,capsize=4,label=label)
 ref=q[q.reference]
 if len(ref):ax.plot(ref.relative_year+offset,ref.b,marker='o',mfc='white',mec=color,ls='none',ms=6)
 edge=q[q.single_cohort_endpoint&~q.reference]
 if len(edge):ax.plot(edge.relative_year+offset,edge.b,marker='s',mfc='white',mec=color,ls='none',ms=5)
 return q
def eventplot(mid,estimand,name,compare=False):
 fig,ax=plt.subplots(figsize=(12,7.4));ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1)
 q=plot_curve(ax,mid,estimand,label='Cohort-interacted, fixed-weight average' if compare else None)
 if compare:plot_curve(ax,2,estimand,color='#cf8735',offset=.10,label='Pooled event-time slopes');ax.legend(fontsize=9)
 ks=sorted(q.relative_year.astype(int));ax.set_xticks(ks);ax.set_xlim(min(ks)-.4,max(ks)+.4);ax.set_xlabel('Years relative to first provincial inspection')
 ax.set_ylabel('Change in connection-related promotion gap (pp)' if estimand=='change' else 'Connection-related promotion probability gap (pp)');ax.grid(axis='y',alpha=.15)
 title=('Event study: change in the promotion return to provincial ties' if estimand=='change' else 'Promotion return to provincial ties: conditional gap levels')
 title+='\nFirst inspection | '+('Reference: k = -1 | ' if estimand=='change' else '')+'95% province-clustered CIs'
 fig.suptitle(title,fontsize=15,y=.98)
 m=MM[MM.model_id.eq(mid)].iloc[0];jp=JT[JT.model_id.eq(mid)&JT.test.eq('pretrend')].iloc[0]
 annotation='Joint pretrend p: '+pv(jp.p)+(' | Wild-bootstrap p: '+pv(jp.p_wild) if pd.notna(jp.p_wild) else '')
 if estimand=='change':ax.text(.02,.97,annotation,transform=ax.transAxes,va='top',fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
 ns='; '.join(f'{k:+d}: {int(support.set_index("k").loc[k,"N"])} / {int(support.set_index("k").loc[k,"G"])}' for k in ks)
 ax.text(.5,-.21,'Relative year: N / provinces\n'+ns,ha='center',transform=ax.transAxes,fontsize=7.7)
 fig.subplots_adjust(top=.81,bottom=.34,left=.12,right=.97)
 txt='One connection indicator: a pre-existing tie to EITHER governor or provincial party secretary; no Xi conditioning.\nPooled mayors / city party secretaries; age, tenure, rank and role controls; '+('city + province-by-year FE.' if m.fe=='CITY_PXY' else 'province-by-year FE.')+'\n'+('2013/2014 inspection cohorts estimated separately, averaged using fixed k=-1 officer-count weights.' if m.kind=='cohort' else 'Comparison specification: common event-time slopes across inspection cohorts.')+'\n'+('Hollow circle at k=-1 is zero by normalization and has no estimated CI.' if estimand=='change' else 'Every point is a conditional gap estimate; k=-1 retains an estimated CI.')+' No rolling windows or connecting lines.\n'+('Hollow squares: only one inspection cohort contributes at that endpoint. ' if mid==4 else '')+'Dynamic leader ties and changing risk sets: conditional associations, not an identified causal ATT.'
 fig.text(.065,.025,txt,fontsize=8)
 export(fig,name,title)

eventplot(1,'change','01_event_study_change_short.png')
eventplot(1,'level','02_connection_gap_levels_short.png')
eventplot(3,'change','03_event_study_change_long.png')
eventplot(3,'level','04_connection_gap_levels_long.png')
eventplot(4,'change','05_event_study_full_2006_2017.png')
eventplot(1,'change','06_cohort_vs_pooled.png',compare=True)
eventplot(5,'change','07_city_FE_sensitivity.png')

main=R[R.model_id.eq(1)&R.estimand.isin(['pre_mean','post_mean','post_minus_pre'])].copy()
fig,ax=plt.subplots(figsize=(10,7))
for j,(est,label,color,mark) in enumerate([('pre_mean','Before: k=-3,-2,-1','#287c9e','o'),('post_mean','After: k=0,+1,+2','#cf8735','s'),('post_minus_pre','After - Before','#a9537e','D')]):
 r=main[main.estimand.eq(est)].iloc[0];ax.errorbar(j,r.b,yerr=[[r.b-r.lo],[r.hi-r.b]],fmt=mark,color=color,capsize=5,ms=7);ax.annotate(f'{r.b:+.2f}',(j,r.b),xytext=(9,5),textcoords='offset points')
ax.axhline(0,color='gray',ls='--',lw=1);ax.set_xticks([0,1,2],['Before\nk=-3,-2,-1','After\nk=0,+1,+2','After - Before']);ax.set_ylabel('Connection-related promotion gap (pp)');ax.set_xlim(-.4,2.5);ax.grid(axis='y',alpha=.15)
fig.suptitle('Average connection advantages before and after first inspection\nCohort-interacted model | 95% province-clustered CIs',fontsize=14)
ax.text(.5,-.23,'Raw p: '+' / '.join(pv(main[main.estimand.eq(e)].p.iloc[0]) for e in ['pre_mean','post_mean','post_minus_pre'])+'\nWild-bootstrap p: '+' / '.join(pv(main[main.estimand.eq(e)].p_wild.iloc[0]) for e in ['pre_mean','post_mean','post_minus_pre']),ha='center',transform=ax.transAxes,fontsize=9)
fig.subplots_adjust(top=.80,bottom=.36,left=.13,right=.96)
fig.text(.065,.035,'Averages give equal weight to each relative year, using fixed baseline weights across inspection cohorts.\nSame short-window model and all controls as the main event study; no Xi sample restriction.\nWebb wild bootstrap: 9,999 repetitions, seed 20261015. No connecting lines.\nA post CI crossing zero does not show that the relation advantage disappeared.',fontsize=8)
export(fig,'08_pre_post_average_gap.png','Average pre / post connection gaps and their difference')

# Cohort-specific curves reveal heterogeneity that an average could conceal.
BC=pd.read_csv(OUT/'underlying_slope_coefficients.csv');BC=BC[BC.model_id.eq(1)]
CV=pd.read_csv(OUT/'covariance_model_1.csv',index_col=0)
fig,axes=plt.subplots(1,2,figsize=(13,7))
for ax,g in zip(axes,[2013,2014]):
 q=BC[BC.term_cohort.eq(g)].sort_values('term_relative_year');base=q[q.term_relative_year.eq(-1)].iloc[0]
 ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1)
 for r in q.itertuples():
  if r.term_relative_year==-1:ax.plot(-1,0,'o',mfc='white',mec='#287c9e');continue
  bb=r.b-base.b;se=float(np.sqrt(max(0,CV.loc[r.term,r.term]+CV.loc[base.term,base.term]-2*CV.loc[r.term,base.term])));crit=2.055529438642871
  ax.errorbar(r.term_relative_year,bb,yerr=crit*se,fmt='o',ls='none',color='#287c9e',capsize=4)
 ax.set_title(f'First inspection in {g}');ax.set_xticks(range(-3,3));ax.set_xlabel('Years relative to first inspection');ax.set_ylabel('Change in connection-related promotion gap (pp)');ax.grid(axis='y',alpha=.15)
fig.suptitle('Cohort-specific event-study changes\nSame interacted model | Reference k=-1 | 95% province-clustered CIs',fontsize=14)
fig.subplots_adjust(top=.80,bottom=.23,wspace=.28)
jp=JT[JT.model_id.eq(1)&JT.test.eq('pretrend_all_cohorts')].iloc[0]
fig.text(.065,.035,'Shared controls and province-by-year FE; each cohort normalized to its own k=-1 gap.\nAll-cohort pretrend joint p: '+pv(jp.p)+'; wild-bootstrap p: '+pv(jp.p_wild)+'.\nCIs use the joint model province-clustered covariance, df=26. Dynamic ties: conditional associations.',fontsize=8.5)
export(fig,'09_cohort_specific_changes.png','Cohort-specific event-study changes')

method=f'''# 与任一省级主官的关系与晋升：首次巡视事件研究（暂不处理Xi）

## 本轮定义和样本
不读取、也不筛选Xi关系。原始来源是上轮修订后的annual_official_panel.csv.gz：2006—2017，7749个人年。C=1当与当时省委书记或省长任一人的legacy_cowork_6m关系为1；仅两者已知均为0时记0；无正证据且有未知则保留未知。关系须有至少六个月共事证据，形成于2012前且早于双方当前共同任职开始。晋升沿用行政级别上升/市长转书记/同级副部市级主官新任副省长规则。未另剔除Xi相关省份或官员。
个人控制完整且Y、C可判断的年度主样本7249个人年。主事件窗实际限制k∈[-3,+2]，共3668个人年、1176人、337市、27省、557次晋升。此前滚动图不同：每个k代表单一相对年份，不是三年窗口。2006—2017全期图也一并保留。

## 回归和参照期
k=当年实际年份−基期任职省份首次中央巡视进驻年份。两批为2013、2014。年度观察仍用上一年12月31日在任官员及领导关系预测当年晋升。
基础表达：100 Promotion_it=省×年FE + beta C_it + sum_(k≠-1) delta_k C_it 1[event_time=k] + X gamma + error。
主规格允许2013/2014批次的每个event_time关系系数都不同：直接估计b_gk C_it×1[cohort=g,event_time=k]全部cell。主水平曲线beta_k=sum_g w_g b_gk；主变化曲线delta_k=sum_g w_g(b_gk−b_g,-1)。权重固定为k=-1样本人数：2013批次251/611，2014批次360/611；不按事后样本或显著性调整权重。每个cell比较同省同年有关系/无关系者，省×年FE吸收整体巡视及日历冲击。
变化图k=-1固定为0，空心参照点，无估计CI；水平图k=-1仍有估计值及CI。负的delta只表示关系差异比-1期小，不表示绝对晋升概率下降。水平图用来判断事前是否有关系优势。
控制：年龄及平方、任期及平方、基期行政级别、市长/市委书记职务；市长书记合并，每人每年只保留一条。主FE为省×年；补充城市+省×年。另保留不允许批次差异的pooled回归，作同一数据同控制的对照。

## 窗口和支持
主窗[-3,2]；长共同支持窗[-7,3]；全期[-8,4]。前两者每个event time均有2013及2014两批，实际每期省数、关系人数、晋升事件全部记录。
全期端点-8只有2014批，+4只有2013批，图中空心方点标记；该端点变化与同一批次自己的-1比较，不能当成固定两批权重的同组成点。没有把端点合并或拿不存在的另一批补齐。
不因系数符号、显著性或事前趋势检验结果选择模型。主窗是在估计前按上一轮显示范围确定，长窗与全期全部报告。

## 推断和正式检验
省聚类CR1标准误，95%逐点t(G-1)区间，G=27，df=26。主规格事前趋势联合检验delta_-3=delta_-2=0；事后变化联合检验delta_0=delta_1=delta_2=0。
另在同一模型计算三期事前平均水平、三期事后平均水平、两者之差，用完整协方差矩阵作线性组合，不能用两个独立SE相加替代。主规格事前/后均值、差异及事前趋势联合检验补充Webb wild bootstrap，9999次，固定种子20261015。均为探索性未调整p值；没有挑选检验结果。
主结果：前均值+5.4829pp（常规p=0.0196，wild p=0.0239）；后均值+6.9247pp（p=0.0919，wild p=0.1304）；变化+1.4419pp（p=0.7685，wild p=0.7849）。事前变化联合p=0.7455（wild=0.7585）。未拒绝事前系数为0不证明平行趋势，事后水平不显著不证明关系优势为0。

## 解释边界
主解释变量C_it随在任省级领导和市级官员更替变化，且年度风险集随晋升/离任变化；这里没有把connection永久冻结为某个事前处理组。因此该图是“关系晋升差异”的条件事件研究，尚不是固定处理组的因果DID/ATT。后期已无未巡视省份，2014批次只在其尚未巡视时能充当额外对照；本轮不冒称Sun–Abraham或Callaway–Sant'Anna估计。
允许批次不同并固定加权有助于避免强加两批相同关系差异，但不能解决巡视选择、关系暴露或人员更替的内生性。这个版本能检验当前条件关系模式有没有下降；如需因果结论，下一步需另定义事前固定关系暴露/冻结配对、核验风险集和明确可用未巡视对照。

## 核验与重跑
全部非参照系数、SE、p、CI、N、K、聚类数、自由度及{len(JT)}个联合检验均由Stata18 areg独立复算。另对所有批次全部事前变化共同为0作联合检验，主规格p=0.8362；其wild p值见联合检验表。5项主wild检验均完成。code/event_study_no_Xi.py→Stata code/validate_event_study.do→code/report_event_study_no_Xi.py。保留本机路径，迁移需调整BASE；无PDF、不覆盖旧图或网络。
'''
(OUT/'methods_中文.md').write_text(method,encoding='utf8')
with pd.ExcelWriter(OUT/'关系与晋升_首次巡视_event_study.xlsx',engine='openpyxl') as w:
 for name,d in [('Main_short',R[R.model_id.eq(1)]),('All_event_coefficients',R),('Pretrend_joint_tests',JT),('Model_summary',MM),('Support_by_year',support),('Support_cohort_year',pd.read_csv(OUT/'support_by_cohort_relative_year.csv')),('Cohort_weights',weights),('Analysis_panel',A),('Validation',pd.DataFrame(checks)),('Stata_contrasts',S),('Stata_joint',SJ),('Contrast_design',pd.read_csv(OUT/'contrast_design.csv'))]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>关系与晋升：巡视event study</title><style>body{max-width:1400px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}h2{font-size:20px}section{margin:32px 0}</style><h1>首次巡视事件研究：暂不处理Xi</h1><p>主图逐年估计，-1为参照；不是滚动图。关系为与省长或书记任一人有事前共事关系。省×年FE、省聚类95%CI，2013/2014批次固定权重合并。</p><p>事前平均优势+5.48pp；事后+6.92pp；变化+1.44pp（p=0.768）。未显示关系优势下降。事前联合检验不拒绝，也不证明平行趋势。</p><p><a href="关系与晋升_首次巡视_event_study.xlsx">Excel全部结果</a> · <a href="methods_中文.md">定义及方法</a></p>'
for name,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+name+'" alt="'+html.escape(title)+'"></section>'
page+='</html>';(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
ck('All HTML references resolve',all((OUT/x).is_file() for x in re.findall(r'(?:src|href)="([^"]+)"',page)))
for p in (OUT/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Nine PNG figures',len(list((OUT/'figures').glob('*.png')))==9)
ck('No PDF generated',not list(OUT.rglob('*.pdf')))
assert all(x['passed'] for x in checks)
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')
summary=dict(models=len(MM),contrasts=len(R),stata_validated_contrasts=len(Q),joint_tests=len(JT),checks=len(checks),all_checks_passed=True,figures=len(gallery),main=main.to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding='utf8')
pd.DataFrame([dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='file_manifest.csv']).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=BASE/'关系与晋升_首次巡视_event_study_数据图表代码.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps({k:v for k,v in summary.items() if k!='main'},ensure_ascii=False),flush=True)
