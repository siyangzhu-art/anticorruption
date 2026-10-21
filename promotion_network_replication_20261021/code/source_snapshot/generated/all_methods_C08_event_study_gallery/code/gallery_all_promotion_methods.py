"""Replot every existing full-control promotion estimator; no new model selection."""
from pathlib import Path
import sys,shutil,hashlib,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'all_methods_C08_event_study_gallery'
for p in [O,O/'figures',O/'code']:p.mkdir(exist_ok=True)
G=B/'control_FE_sensitivity_post4';E=B/'with_officer_city_economics/LPDID_DoubleML_common_sample';CY=B/'province_year_vs_city_year_audit'
R=pd.read_csv(G/'all_level_results.csv');R=R[R.control_id.eq('C08')].copy()
MS=pd.read_stata(G/'model_stats.dta')
L=pd.read_csv(G/'all_LPDID_results.csv');L=L[L.control_id.eq('C08')].copy()
D=pd.read_csv(E/'doubleml_results.csv');D=D[D.economic_controls.eq(True)].copy()
Q=pd.read_csv(G/'horizon_pairs.csv.gz')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
def save(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')
flabel={'I_YEAR':'Individual + year','I_PXY':'Individual + province x year','I_CITY_YEAR':'Individual + city + year','I_CITY_PXY':'Individual + city + province x year'}
cols=['series','method','connection','fe','control_timing','k','b','se','p','lo','hi','N_model','G_model','N_period','G_period','connected_period','reference','source_file','source_model_id','p_holm_spec','p_holm_all_post']
unified=[]
for sample in ['fixed','dynamic']:
 a=pd.read_csv(G/f'{sample}_panel.csv.gz');c='C0' if sample=='fixed' else 'C_any'
 support=a.groupby('k').agg(N_period=('person_id','size'),G_period=('anchor_province','nunique'),connected_period=(c,'sum'))
 for (mid,method),z in R[R['sample'].eq(sample)&R.term.str.startswith('d_')].groupby(['model_id','estimator']):
  m=MS[MS.model_id.eq(mid)&MS.estimator.eq(method)].iloc[0];fe=z.fe.iloc[0];series=f'{method} | {fe}'
  for r in z.itertuples():
   k=-int(r.term[3:]) if r.term.startswith('d_m') else int(r.term[3:]);s=support.loc[k]
   unified.append(dict(series=series,method=method,connection='Fixed pre-inspection C0' if sample=='fixed' else 'Annual dynamic C_it',fe=fe,control_timing='Annual lagged officer-city economics',k=k,b=r.b,se=r.se,p=r.p,lo=r.lo,hi=r.hi,N_model=m.N,G_model=m.G,**s.to_dict(),reference=False,source_file=str(G/'all_level_results.csv'),source_model_id=mid,p_holm_spec=r.p_holm_spec,p_holm_all_post=r.p_holm_all_post))
  s=support.loc[-1]
  unified.append(dict(series=series,method=method,connection='Fixed pre-inspection C0' if sample=='fixed' else 'Annual dynamic C_it',fe=fe,control_timing='Annual lagged officer-city economics',k=-1,b=0,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan,N_model=m.N,G_model=m.G,**s.to_dict(),reference=True,source_file=str(G/'all_level_results.csv'),source_model_id=mid))
for r in L.itertuples():
 ref=r.h==-1
 unified.append(dict(series=f'LPDID | {r.fe}',method='LPDID',connection='Fixed pre-inspection C0',fe=r.fe,control_timing='Pre-inspection baseline officer-city economics',k=r.h,b=0 if ref else r.b,se=np.nan if ref else r.se,p=np.nan if ref else r.p,lo=np.nan if ref else r.lo,hi=np.nan if ref else r.hi,N_model=np.nan,G_model=np.nan,N_period=r.N if not ref else np.nan,G_period=r.G if not ref else np.nan,connected_period=r.treated if not ref else np.nan,reference=ref,source_file=str(G/'all_LPDID_results.csv'),source_model_id=r.model_id,p_holm_spec=r.p_holm_spec,p_holm_all_post=r.p_holm_all_post))
for learner,z in D.groupby('learner'):
 for r in z.itertuples():
  unified.append(dict(series=f'DoubleML | {learner}',method='DoubleML',connection='Fixed pre-inspection C0',fe='Inspection cohort covariate; no province or individual FE',control_timing='Pre-inspection baseline officer-city economics',k=r.h,b=r.b,se=r.se,p=r.p,lo=r.lo,hi=r.hi,N_model=np.nan,G_model=np.nan,N_period=r.N,G_period=r.G,connected_period=r.treated,reference=False,source_file=str(E/'doubleml_results.csv'),source_model_id=learner))
 unified.append(dict(series=f'DoubleML | {learner}',method='DoubleML',connection='Fixed pre-inspection C0',fe='Inspection cohort covariate; no province or individual FE',control_timing='Pre-inspection baseline officer-city economics',k=-1,b=0,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan,N_model=np.nan,G_model=np.nan,N_period=np.nan,G_period=np.nan,connected_period=np.nan,reference=True,source_file=str(E/'doubleml_results.csv'),source_model_id=learner))
U=pd.DataFrame(unified).reindex(columns=cols).sort_values(['series','k']).reset_index(drop=True)
ck('16 full-control series, 9 relative periods each',U.series.nunique()==16 and U.groupby('series').size().eq(9).all(),len(U))
ck('No duplicate method-period',not U.duplicated(['series','k']).any())
ck('Four complete post periods plotted for every series',U[U.k.gt(0)].groupby('series').k.nunique().eq(4).all())
ck('References have no estimated CI',U[U.reference][['se','p','lo','hi']].isna().all().all())
for r in U[~U.reference].itertuples():
 df=r.G_model-1 if np.isfinite(r.G_model) else r.G_period-1
 crit=t.ppf(.975,df)
 ck(f'CI equals stored province-clustered t interval: {r.series}, k={r.k}',np.isclose(r.lo,r.b-crit*r.se,atol=2e-6) and np.isclose(r.hi,r.b+crit*r.se,atol=2e-6))
ck('Fixed annual sample identical across four FE',U[U.method.isin(['Sun_Abraham','TWFE_fixed'])].N_model.eq(2807).all())
ck('Dynamic annual sample identical across four FE',U[U.method.eq('TWFE_dynamic')].N_model.eq(4111).all())
for h in [-4,-3,-2,0,1,2,3,4]:
 z=U[U.k.eq(h)&U.method.isin(['LPDID','DoubleML'])]
 ck(f'LP and DML same horizon pairs at k={h}',z.N_period.eq(len(Q[Q.h.eq(h)])).all() and z.connected_period.eq(Q[Q.h.eq(h)].C0.sum()).all())
save(U,'all_methods_full_controls_event_coefficients.csv');save(U[U.k.gt(0)],'all_methods_four_post_periods.csv')
save(R,'annual_C08_all_contrasts.csv');save(L,'LPDID_C08_results.csv');save(D,'DoubleML_economic_results.csv')
save(pd.read_csv(G/'all_level_joint_tests.csv').query("control_id == 'C08'"),'annual_C08_joint_tests.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
gallery=[]
def style(ax):
 ax.axhline(0,color='gray',ls='--',lw=.85);ax.axvline(0,color='#b18b36',ls=':',lw=.9);ax.set_xticks(range(-4,5));ax.set_xlim(-4.45,4.45);ax.set_xlabel('Years relative to first inspection');ax.grid(axis='y',alpha=.15)
def points(ax,series,label,color,marker='o',off=0):
 z=U[U.series.eq(series)].sort_values('k');assert len(z)==9
 d=z[~z.reference];ax.errorbar(d.k+off,d.b,yerr=np.vstack([d.b-d.lo,d.hi-d.b]),fmt=marker,ls='none',color=color,capsize=3,ms=4,label=label)
 ax.scatter([-1+off],[0],marker=marker,s=27,facecolors='white',edgecolors=color,zorder=4)
def export(fig,name,title):
 fig.savefig(O/'figures'/name,dpi=180,facecolor='white');plt.close(fig);gallery.append((name,title))

fig,axs=plt.subplots(2,2,figsize=(15,11),sharey=True)
for ax,fe in zip(axs.flat,flabel):
 points(ax,f'Sun_Abraham | {fe}','Sun-Abraham','#287c9e','o',-.07);points(ax,f'TWFE_fixed | {fe}','TWFE: fixed C0','#cf8735','s',.07);style(ax);ax.set_title(flabel[fe])
for ax in axs[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('Full personal and economic controls (C08): four FE structures\nFixed pre-inspection relationship group | 95% province-clustered CIs',fontsize=16,y=.98)
fig.legend(*axs[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=2,frameon=False)
fig.subplots_adjust(top=.83,bottom=.16,left=.08,right=.98,hspace=.3,wspace=.15)
fig.text(.06,.035,'Identical N=2,807 officer-years; 26 province clusters. Economics follow the official annual appointment city (lagged one year).\nCity FE here are additive, not city-by-year FE. Reference has no estimated CI; no connecting lines.\nAt k=+4 only 4 baseline-connected officials remain. Pointwise CIs do not account for specification search; adjusted p-values are exported.',fontsize=9)
export(fig,'01_Sun_Abraham_TWFE_fixed_four_FE.png','Sun-Abraham and fixed-C0 TWFE: four FE structures')

fig,axs=plt.subplots(2,2,figsize=(15,11),sharey=True)
for ax,fe in zip(axs.flat,flabel):
 points(ax,f'TWFE_dynamic | {fe}','TWFE: annual dynamic C_it','#287c9e');style(ax);ax.set_title(flabel[fe])
for ax in axs[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('Full personal and economic controls (C08): four FE structures\nAnnual dynamic connection | TWFE | 95% province-clustered CIs',fontsize=16,y=.98)
fig.subplots_adjust(top=.83,bottom=.16,left=.08,right=.98,hspace=.3,wspace=.15)
fig.text(.06,.035,'Identical N=4,111 officer-years; 27 province clusters. Includes the annual C_it main effect and event-time interactions.\nPersonal controls and lagged officer-city GDP growth, log GDP per capita and log population.\nChanging provincial leaders can change C_it exposure; this differs from fixed-C0 analysis. Additive city FE are not city-by-year FE.',fontsize=9)
export(fig,'02_TWFE_dynamic_four_FE.png','Annual dynamic-connection TWFE: four FE structures')

fig,axs=plt.subplots(2,2,figsize=(15,11),sharey=True)
for ax,fe in zip(axs[0],['cohort','province']):
 points(ax,f'LPDID | {fe}','LP-DiD RA','#287c9e');style(ax);ax.set_title('LP-DiD | '+('Inspection cohort FE' if fe=='cohort' else 'Province FE'))
for ax,learner,title in zip(axs[1],['Ridge_Logit_econ','RandomForest_econ'],['Ridge / Logit','Random forests']):
 points(ax,f'DoubleML | {learner}','DoubleML-DiD','#cf8735','s');style(ax);ax.set_title('DoubleML-DiD | '+title)
for ax in axs[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('LP-DiD and DoubleML-DiD: full baseline personal and economic controls\nFixed pre-inspection C0 | Same horizon pairs | 95% province-clustered CIs',fontsize=16,y=.98)
fig.subplots_adjust(top=.83,bottom=.18,left=.08,right=.98,hspace=.3,wspace=.15)
fig.text(.06,.035,'Controls fixed at each official k=-1 city: personal features, GDP growth, log GDP per capita and log population.\nPost +1/+2/+3/+4 pairs: N=340/274/168/43; connected=38/32/17/4; province clusters=24/23/22/8.\nLP: long differences remove individual fixed levels; no extra individual FE. DML: cohort covariate, no province FE; 3 province folds x 5 repetitions.\nSoftware cluster SEs with t(G-1) intervals; no connecting lines. Neither model is labeled as having the four annual FE structures.',fontsize=9)
export(fig,'03_LPDID_DoubleML_full_baseline_controls.png','LP-DiD and DoubleML-DiD: full baseline controls')

fig,axs=plt.subplots(2,3,figsize=(19,11),sharey=True)
selected=[('TWFE_fixed | I_PXY','TWFE: fixed C0 | Individual + province-year'),('Sun_Abraham | I_PXY','Sun-Abraham | Individual + province-year'),('TWFE_dynamic | I_PXY','TWFE: dynamic C_it | Individual + province-year'),('LPDID | province','LP-DiD RA | Province FE'),('DoubleML | Ridge_Logit_econ','DoubleML-DiD | Ridge / Logit'),('DoubleML | RandomForest_econ','DoubleML-DiD | Random forests')]
for ax,(series,title) in zip(axs.flat,selected):
 points(ax,series,title,'#287c9e');style(ax);ax.set_title(title,fontsize=11)
for ax in axs[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('All promotion estimation methods | Full personal and economic controls\n95% province-clustered pointwise CIs | Reference k=-1',fontsize=17,y=.98)
fig.subplots_adjust(top=.84,bottom=.17,left=.065,right=.985,hspace=.3,wspace=.12)
fig.text(.055,.035,'Methods have different comparison samples and control timing: annual TWFE/SA use lagged annual economics; LP/DML use fixed baseline economics.\nAnnual sample: fixed C0 N=2,807; dynamic C_it N=4,111. LP/DML post pairs N=340/274/168/43, connected=38/32/17/4.\nDML has no province FE. LP uses long differences. These are conditional differential associations; no four-period stable significant decline is established.',fontsize=10)
export(fig,'04_all_methods_overview.png','All methods: overview under the main available FE choices')

src=CY/'figures/01_FE_comparison_same_and_maximum_samples.png'
shutil.copy2(src,O/'figures/05_city_year_sample_comparison.png');gallery.append(('05_city_year_sample_comparison.png','Separate city-year FE audit: same sample and maximum sample'))
save(pd.read_csv(CY/'all_coefficients.csv'),'city_year_audit_all_coefficients.csv')
save(pd.read_csv(CY/'sample_comparison.csv'),'city_year_sample_comparison.csv')

method_notes='''# 全部晋升估计方法：完整控制图册

本轮只整理、重画此前已估计并核验的结果，不改变数据、晋升定义、关系定义、随机种子或模型，不根据显著性挑选规格。

1. Sun–Abraham与固定C0 TWFE：完整C08控制，四种年度FE：个人+年份；个人+省份×年份；个人+城市+年份；个人+城市+省份×年份。同一2807个人年。Sun–Abraham为官方eventstudyinteract批次交互加权，不是普通TWFE。
2. 动态C_it TWFE：相同四种年度FE，完整C08控制，同一4111个人年。关系含单独主项；与固定C0的估计对象不同，不能当作完全相同处理定义的重复验证。
3. LP-DiD：完整基期控制，批次FE和省FE各一版。采用长差分回归调整ATT；个人不变水平被差分，不重复加入个人FE。本轮没有新做城市FE或城市×年份FE的LP估计，不能把它们标成已完成。
4. DoubleML-DiD：完整基期控制，Ridge/Logit与随机森林两个既定learner。使用observational DiD ATT、3省折×5重复、省聚类。含巡视批次协变量，无个人/省份固定效应；不能把机器学习当作加入了四种年度FE。本轮不新增调参或重选分折。
5. 另附近期city×year核验图；这是与原图中的加法city FE不同的规格。其最大和共同样本分别列出，不强行与2807/4111的旧四FE图混作同一样本。

年度经济控制按官员结果t行的t-1年末任职城市匹配t-1日历年经济数据；LP/DML固定在k=-1的官员基期城市。所有主图展示-4至+4，-1为归零参照且无估计CI；不连线；95%省聚类区间。LP/DML的区间用软件聚类SE配t(G-1)，正态软件p仍在原始CSV。

LP/DML各h对同一人基期与目标期配对。事后N=340/274/168/43，有关系组38/32/17/4；缺失晋升不补0。年度固定C0的+4也仅4名关系官员，且2014巡视批次未观察到完整+4。风险集变化、少处理组和重叠不足仍存在。单期显著不等于四期稳定，非显著不证明效果为零。

图中的95%CI为逐点区间，不校正此前规格搜索；此前年度/LP Holm校正p保留于统一结果表。DoubleML本轮没有相同网格的Holm校正，不凭空填入。不同方法样本、控制时点和FE不同，主总览是并列展示，不表示严格相同估计对象。

所有输入哈希、统一144行逐期结果、64行事后结果、原方法全控制结果、样本支持、Excel和可重画代码都交付。可重画入口code/gallery_all_promotion_methods.py；使用既有项目绝对路径CSV，不会重估模型。无PDF。
'''
(O/'methods_中文.md').write_text(method_notes,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Five figures delivered',len(gallery)==5);ck('No PDFs created',not list(O.rglob('*.pdf')))
ck('128 nonreference estimates delivered',len(U[~U.reference])==128)
save(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
with pd.ExcelWriter(O/'全部方法_C08_逐期结果与固定效应对照.xlsx',engine='openpyxl') as w:
 for name,d in [('All_144_event_points',U),('All_64_post_points',U[U.k.gt(0)]),('Annual_C08_all_contrasts',R),('LPDID_C08',L),('DoubleML_econ',D),('Annual_C08_joint_tests',pd.read_csv(O/'annual_C08_joint_tests.csv')),('City_year_audit',pd.read_csv(CY/'all_coefficients.csv')),('City_year_samples',pd.read_csv(CY/'sample_comparison.csv')),('Validation',pd.DataFrame(checks))]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>All promotion methods</title><style>body{max-width:1700px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}section{margin:40px 0}</style><h1>全部晋升估计方法：完整控制与95%CI</h1><p>Sun–Abraham、固定C0 TWFE、动态C_it TWFE、LP-DiD及DoubleML。年度模型保留四种FE；LP和DML按其实际实现注明FE及控制时点。所有既有规格保留。</p><a href="全部方法_C08_逐期结果与固定效应对照.xlsx">Excel全部结果</a> · <a href="methods_中文.md">方法与比较范围</a>'
for name,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+name+'"></section>'
page+='<pre style="white-space:pre-wrap">'+html.escape(method_notes)+'</pre>'
(O/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
sourcepaths=[G/'all_level_results.csv',G/'model_stats.dta',G/'all_LPDID_results.csv',G/'fixed_panel.csv.gz',G/'dynamic_panel.csv.gz',G/'horizon_pairs.csv.gz',E/'doubleml_results.csv',CY/'all_coefficients.csv',src]
save(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sourcepaths]),'input_manifest.csv')
z=B/'全部晋升方法_C08_图册逐期结果代码.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in O.rglob('*'):
  if p.is_file():f.write(p,p.relative_to(O))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
print('Completed:',len(U),'event points;',len(checks),'checks passed; 5 figures')
print(U[U.k.gt(0)][['series','k','b','p']].to_string(index=False))
print('Gallery:',O/'index.html')
