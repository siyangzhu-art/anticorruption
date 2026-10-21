from pathlib import Path
import sys,json,shutil,hashlib,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.stats import t
from scipy.linalg import lstsq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'with_officer_city_economics';SA=O/'SA_TWFE_common_sample';DY=O/'dynamic_TWFE_common_sample';LP=O/'LPDID_DoubleML_common_sample'
for p in [SA/'sun_abraham.log',DY/'validation.log',LP/'lpdid.log']:assert 'log close' in p.read_text(encoding='utf8',errors='replace')[-400:],p
R=pd.read_stata(SA/'coefficients.dta');W=pd.read_stata(SA/'weights.dta');C=pd.read_stata(SA/'cohort_coefficients.dta');M=pd.read_stata(SA/'models.dta');J=pd.read_stata(SA/'joint_tests.dta')
P=pd.read_csv(SA/'python_cohort_point_estimates.csv');D=pd.read_csv(SA/'analysis_panel.csv.gz')
EC=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
def kterm(term):return -int(term[3:]) if term.startswith('d_m') else (int(term[3:]) if term.startswith('d_p') else np.nan)
for q in [R,W,C]:q['k']=q.term.map(kterm)
R['econ']=R.model_id.ge(3);R['fe']=R.model_id.map({1:'I_YEAR',2:'I_PXY',3:'I_YEAR',4:'I_PXY'})
checks=pd.read_csv(O/'economic_matching_checks.csv').to_dict('records')
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
qc=C.merge(P,on=['model_id','cohort','k'],suffixes=('_st','_py'),validate='1:1');ck('All 60 supported SA cohort points independently reproduced',len(qc)==60 and np.allclose(qc.b_st,qc.b_py,atol=2e-6,rtol=2e-6))
qw=C.merge(W,on=['model_id','cohort','term','k'],validate='1:1');qw['wb']=qw.b*qw.weight
qq=qw.groupby(['model_id','term']).wb.sum().reset_index().merge(R[R.method.eq('Sun_Abraham')],on=['model_id','term'],validate='1:1');ck('Official IW equals manual aggregation',np.allclose(qq.wb,qq.b,atol=1e-8));ck('IW weights sum to one',np.allclose(W.groupby(['model_id','term']).weight.sum(),1,atol=1e-10))
ck('All SA and fixed TWFE use same sample',M.N.nunique()==1 and M.N.iloc[0]==len(D))
ck('Annual economic controls complete in SA common sample',D[EC].notna().all().all())
ck('Economic year follows each officer current city-year',D.economic_year.eq(D.year-1).all())
R.to_csv(SA/'results_with_economic_comparison.csv',index=False,encoding='utf-8-sig')

DR=pd.read_csv(DY/'coefficients.csv');DS=pd.read_stata(DY/'stata_validation.dta');DJ=pd.read_csv(DY/'joint_tests.csv');DJS=pd.read_stata(DY/'stata_joint.dta');DM=pd.read_csv(DY/'models.csv')
v=DR[~DR.reference].merge(DS,on=['model_id','contrast'],suffixes=('_py','_st'),validate='1:1')
for col in ['b','se','p','lo','hi','N','K','G','df']:ck('Dynamic TWFE Stata '+col,np.allclose(v[col+'_py'],v[col+'_st'],atol=3e-6,rtol=3e-6))
jq=DJ.merge(DJS,on=['model_id','test'],suffixes=('_py','_st'),validate='1:1');ck('All dynamic TWFE joint tests reproduced',np.allclose(jq.p_py,jq.p_st,atol=3e-6,rtol=3e-6))
ck('All four dynamic specifications share sample',DM.N.nunique()==1)

L=pd.read_stata(LP/'lpdid_results.dta')
for col in ['b','se','p','lo','hi','N']:L[col]=L[col].astype('float64')
L['h']=L.term.map(lambda s:-int(s[3:]) if s.startswith('pre') else int(s[3:]));L['reference']=L.h.eq(-1);L['econ']=L.spec.str.endswith('_econ');L['fe']=L.spec.map(lambda x:'province' if x.startswith('province') else 'cohort')
MP=pd.read_csv(LP/'python_LPDID_RA_points.csv');Q=pd.read_csv(LP/'horizon_pairs.csv.gz')
L=L.merge(MP,on=['spec','h'],how='left',suffixes=('','_py'),validate='1:1')
ck('All 32 LP-DiD points independently reproduced',len(L[~L.reference])==32 and np.allclose(L.loc[~L.reference,'b'],L.loc[~L.reference,'b_py'],atol=3e-6,rtol=3e-6))
ck('LP-DiD all four variants identical pair counts',np.allclose(L.loc[~L.reference,'N'],L.loc[~L.reference,'N_py']) and L[~L.reference].groupby('h').N.nunique().eq(1).all())
L['p_normal']=L.p;L['lo_normal']=L.lo;L['hi_normal']=L.hi
for idx,r in L[~L.reference].iterrows():
 df=r.provinces-1;crit=t.ppf(.975,df);L.loc[idx,['p','lo','hi','df']]=[2*t.sf(abs(r.b/r.se),df),r.b-crit*r.se,r.b+crit*r.se,df]
for r in L[~L.reference].itertuples():
 q=Q[Q.h.eq(r.h)].copy();ctl=q.C0.eq(0).to_numpy();cols=['base_age','base_age2','base_tenure','base_tenure2','base_role']+(['base_growth','base_lngdppc','base_lnpop'] if r.econ else []);cat='anchor_province' if r.fe=='province' else 'G0'
 z=np.column_stack([np.ones(len(q)),q[cols].to_numpy(),pd.get_dummies(q.base_rank0,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q[cat],drop_first=True,dtype=float).to_numpy()]);norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0];bb=lstsq(z[ctl],q.deltaY.to_numpy()[ctl],cond=1e-10)[0];u=q.deltaY.to_numpy()-z@bb;val=u[~ctl].mean();sc=np.zeros(len(q));sc[~ctl]=(u[~ctl]-val)/(~ctl).sum();sc[ctl]=-u[ctl]*(z[ctl]@np.linalg.pinv(z[ctl].T@z[ctl],rcond=1e-10)@z[~ctl].mean(axis=0));sums=pd.Series(sc).groupby(q.anchor_province.to_numpy()).sum()
 ck('LP-DiD cluster IF SE '+r.spec+str(r.h),np.isclose(np.sqrt((sums**2).sum()),r.se,atol=5e-6,rtol=5e-6))
L.to_csv(LP/'LPDID_economic_comparison.csv',index=False,encoding='utf-8-sig')
F=pd.read_csv(LP/'doubleml_results.csv');REPS=pd.read_csv(LP/'doubleml_repetitions.csv');FOLD=pd.read_csv(LP/'province_fold_assignments.csv');PR=pd.read_csv(LP/'doubleml_predictions_scores.csv.gz')
ck('All 32 DML models completed',len(F)==32 and len(pd.read_csv(LP/'doubleml_failures.csv'))==0)
ck('DML same sample across four economic/learner variants',F.groupby('h').N.nunique().eq(1).all())
ck('No province leakage across cross-fit folds',FOLD.groupby(['h','rep','province']).fold.nunique().eq(1).all())
ck('Five repetitions for every DML model',REPS.groupby(['h','learner']).rep.nunique().eq(5).all())
ck('No imputed ML predictions',np.isfinite(PR[['m_hat','g0_hat']]).all().all())
ck('Preset propensity bounds respected',PR.m_hat.between(.01-1e-8,.99+1e-8).all())
for h,g in Q.groupby('h'):
 ck('Clean comparison exists in every province at h='+str(h),g.groupby('anchor_province').C0.min().eq(0).all())
 ck('DML and LPDID same horizon data '+str(h),F[F.h.eq(h)].N.eq(len(g)).all() and F[F.h.eq(h)].treated.eq(g.C0.sum()).all())
ck('DML all coefficients finite',np.isfinite(F[['b','se','p','lo','hi']]).all().all())
assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
gallery=[];CO=['#929292','#287c9e'];MARK=['s','o']
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=180,facecolor='white');plt.close(fig);gallery.append((name,title))
def axes_style(ax):
 ax.axhline(0,color='gray',ls='--',lw=.9);ax.axvline(0,color='#b18b36',ls=':',lw=.9);ax.set_xticks(range(-4,5));ax.set_xlim(-4.4,4.4);ax.set_xlabel('Years relative to first provincial inspection');ax.grid(axis='y',alpha=.14)
def points(ax,q,x='k',off=0,color=CO[1],marker='o',label=None):ax.errorbar(q[x]+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=marker,ls='none',color=color,capsize=3,ms=4,label=label)
fig,axes=plt.subplots(2,2,figsize=(15,12),sharex=True,sharey=True)
for i,method in enumerate(['Sun_Abraham','TWFE_fixed']):
 for j,fe in enumerate(['I_YEAR','I_PXY']):
  ax=axes[i,j]
  for z,e in enumerate([False,True]):
   q=R[R.method.eq(method)&R.fe.eq(fe)&R.econ.eq(e)&R.k.notna()].sort_values('k');points(ax,q,off=(z-.5)*.13,color=CO[z],marker=MARK[z],label='Plus officer-city economic controls' if e else 'Without economics: same sample');ax.plot(-1+(z-.5)*.13,0,marker=MARK[z],ls='none',mfc='white',mec=CO[z],ms=5)
  axes_style(ax);ax.set_title(('Sun-Abraham IW' if i==0 else 'TWFE: fixed C0')+' | '+('Individual + year FE' if j==0 else 'Individual + province-by-year FE'),fontsize=11)
for ax in axes[:,0]:ax.set_ylabel('Change in promotion gap (pp), relative to k=-1')
fig.suptitle('Annual economic controls follow each official\nFixed pre-inspection ties | Common sample | 95% province-clustered CIs',fontsize=16,y=.98)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.92),ncol=2,frameon=False,fontsize=10)
fig.subplots_adjust(left=.08,right=.98,top=.85,bottom=.15,hspace=.25,wspace=.10)
fig.text(.06,.035,f'N={len(D):,} officer-years in all eight regressions. Annual controls: lag log GDP per capita, GDP growth and log population.\nEconomic data match the city held at the prior-year-end snapshot; destination-city economics after a move, not the previous city.\nC0 and inspection timing fixed as in the previous Sun-Abraham analysis. Post +4: 2013 inspection cohort only.\nGray is re-estimated on the economic-complete sample; differences from previous graphs can also reflect sample changes.',fontsize=9)
export(fig,'01_SA_TWFE_officer_city_GDP.png','Sun-Abraham and fixed-group TWFE: economic controls')

fig,axes=plt.subplots(1,2,figsize=(15,8),sharey=True)
for j,fe in enumerate(['I_YEAR','I_PXY']):
 ax=axes[j]
 for z,e in enumerate([False,True]):
  q=DR[DR.fe.eq(fe)&DR.economic_controls.eq(e)&DR.estimand.eq('change')&~DR.reference].sort_values('k');points(ax,q,off=(z-.5)*.13,color=CO[z],marker=MARK[z],label='Plus annual officer-city economics' if e else 'Without economics: same sample');ax.plot(-1+(z-.5)*.13,0,marker=MARK[z],ls='none',mfc='white',mec=CO[z],ms=5)
 axes_style(ax);ax.set_title('Individual + year FE' if j==0 else 'Individual + province-by-year FE')
axes[0].set_ylabel('Change in connection-related promotion gap (pp)');fig.suptitle('Original dynamic-connection TWFE with officer-city economics\n95% province-clustered CIs | Same 4,113 officer-years',fontsize=16,y=.97);fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False,fontsize=10);fig.subplots_adjust(left=.08,right=.98,top=.77,bottom=.23,wspace=.10)
fig.text(.06,.04,'This preserves the original annual C_it, separate from the fixed-C0 Sun-Abraham comparison.\nEconomics follow each officer annual city_code, matched to exactly t-1. Controls do not come from the previous officer row.\nAll models are re-estimated on the same complete sample. Four complete post years +1 to +4; no connecting lines.',fontsize=9)
export(fig,'02_dynamic_TWFE_officer_city_GDP.png','Original dynamic-connection TWFE economic comparison')

fig,axes=plt.subplots(1,2,figsize=(15,8),sharey=True)
for ax,fe in zip(axes,['cohort','province']):
 for z,e in enumerate([False,True]):
  q=L[L.fe.eq(fe)&L.econ.eq(e)&~L.reference].sort_values('h');points(ax,q,x='h',off=(z-.5)*.13,color=CO[z],marker=MARK[z],label='Plus baseline officer-city economics' if e else 'Without economics: same pairs');ax.plot(-1+(z-.5)*.13,0,marker=MARK[z],ls='none',mfc='white',mec=CO[z],ms=5)
 axes_style(ax);ax.set_title('LP-DiD RA | '+('cohort FE' if fe=='cohort' else 'province FE'))
axes[0].set_ylabel('Change in promotion gap (pp), relative to k=-1');fig.suptitle('LP-DiD with pre-inspection officer-city economics\nSame baseline-to-horizon pairs | 95% province-clustered CIs',fontsize=16,y=.97);fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False);fig.subplots_adjust(left=.08,right=.98,top=.77,bottom=.25,wspace=.10)
fig.text(.06,.035,'Economics taken from each official city at the k=-1 baseline, then fixed; no post-inspection economic controls in this LP.\nPost +1/+2/+3/+4 pairs: N=340/274/168/43; baseline-connected=38/32/17/4.\nAll variants exclude province-horizon cells without a comparison official. Province-clustered SEs; t(G-1) intervals.\nMissing outcomes are not filled. Changing risk sets; k=+4 includes only 2013 inspection cohort, 8 provinces.',fontsize=9)
export(fig,'03_LPDID_baseline_city_GDP.png','LP-DiD baseline economic comparison')

fig,axes=plt.subplots(1,2,figsize=(15,8),sharey=True)
for ax,learner,title in zip(axes,['Ridge_Logit','RandomForest'],['Ridge / Logit','Random forests']):
 for z,e in enumerate([False,True]):
  q=F[F.learner.eq(learner+('_econ' if e else '_base'))].sort_values('h');points(ax,q,x='h',off=(z-.5)*.13,color=CO[z],marker=MARK[z],label='Plus baseline officer-city economics' if e else 'Without economics: same pairs');ax.plot(-1+(z-.5)*.13,0,marker=MARK[z],ls='none',mfc='white',mec=CO[z],ms=5)
 axes_style(ax);ax.set_title('DoubleML-DiD | '+title)
axes[0].set_ylabel('Change in promotion gap (pp), relative to k=-1');fig.suptitle('DoubleML-DiD with pre-inspection officer-city economics\n3 province folds x 5 repetitions | 95% province-clustered CIs',fontsize=16,y=.97);fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False);fig.subplots_adjust(left=.08,right=.98,top=.77,bottom=.25,wspace=.10)
fig.text(.06,.035,'Same baseline-to-horizon pairs as LP-DiD. Same folds and learner settings before/after adding economic covariates.\nEconomic controls are fixed at the officer pre-inspection city, avoiding post-treatment controls in the DiD score.\nBaseline personal features and inspection cohort included; no province FE in cluster-held-out machine learning.\nk=+4: 43 officials, 4 connected; t(7) intervals. Weak propensity overlap remains visible in the exported diagnostics.',fontsize=9)
export(fig,'04_DoubleML_baseline_city_GDP.png','DoubleML baseline economic comparison')

audit=pd.read_csv(O/'officer_city_change_audit.csv');ex=pd.read_csv(O/'moving_official_examples.csv');econA=pd.read_csv(O/'annual_economics_rematched.csv.gz')
dictionary=econA.drop_duplicates('city_code').set_index('city_code').city.to_dict();ex['previous_city_name']=ex.previous_city.map(dictionary);ex.to_csv(O/'moving_official_examples.csv',index=False,encoding='utf-8-sig')
notes='''# GDP跟随官员任职城市：经济控制重新估计

## 匹配规则与数据来源
原始经济系列来自既有市级年鉴整理面板 result/city_outcomes_province_Local_2026_10_19/analysis_panel.csv.gz 的old_gdp_growth_pct、old_gdp_per_capita_yuan、old_population_wan；本轮重新读取并以citycode×100与官员city_code匹配，未用省GDP替代。面板的上游原始来源仍沿用该年鉴项目既有口径，本轮不宣称新收集了独立年鉴原表。
新增三个变量：gdp_growth_lag（上年GDP增长率，原始百分数口径）；lngdppc_lag（上年人均GDP元的自然对数）；lnpop_lag（上年人口万人的自然对数）。这是人均GDP及人口，不是另加未经核实的总GDP列。人口对数以万人而非人计量只差常数，不改变控制的实质。
对结果年份t，先取官员t-1年末的实际任职城市，再匹配该城市t-1日历年的经济数据。不是先沿人员ID取上一行GDP，也不是固定在首次进入样本城市，更不是用t年末晋升后的目的地城市倒填本年GDP。453条城市变动记录单独审计；独立重匹配与旧列逐值一致。无插值、无最近年份替代、缺失不补0。所有来源哈希保留。

## 年度Sun-Abraham与TWFE
Sun-Abraham保持C0、基期省份、首次巡视批次不变；年度经济变量则随官员实际任职城市改变。在共同完整经济样本上，先重跑不加经济控制，再加入三项年度上年经济控制。个人+年份FE、个人+省×年FE均报告，SA与同样本固定C0 TWFE都做，共8个规格。共同样本2808个人年、547人，其中63名事前有关系。
另外重做原始动态C_it的TWFE，保留[-4,+4]窗口，两种FE×两种经济控制共4规格，共同样本4113个人年。与固定C0版分开交付，不把两种处理定义混合。
上年GDP在巡视后的某些年份可能已受先前巡视影响，因此年度经济控制版本是条件关联/敏感性规格，不自动代表巡视总效应。

## LP-DiD和DoubleML
采用官员k=-1记录的任职城市经济信息，然后固定为事前协变量。对于2013巡视批次，k=-1是2012结果行，其经济变量来自2011年该官员任职城市；2014批次相应为2012年经济信息。这个固定来自事前设计，不是错误地把全时期GDP锁在旧城市。
仅基期三项经济信息缺失者剔除，不要求每个事后年份GDP均完整，以免因事后协变量缺失额外选样。原624名固定名单中，最终有526人满足基期结果/个人控制/经济控制要求；各h仍需同一人结果可观察。为让省内回归调整有实际比较组，+1剔除海南/新疆各1名仅剩关系组的官员、+2剔除新疆1名；全部LP/DML无经济与有经济版本统一剔除这3个人年。不是为了p值挑样本。原始观测另列，没有覆盖原数据。
LP-DiD继续官方lpdid的rw回归调整ATT，分别批次FE及省FE，基期个人控制一致。DoubleML继续observational DiD ATT、Ridge/Logit及RF两套预定learner、3省折×5重复、种子20261015；经济前后使用完全相同样本、分折和参数。DoubleML没有省FE；不能声称等同省×年FE。四个事后期样本340/274/168/43，关系组38/32/17/4。
为验证比较组支持，网格中的已知处理和基期协变量可以填入，缺失结果不填0；仅将无比较组的目标期排除标记为缺失参与分析，Y_source保留原观察。LP官方和手工长差分回归调整逐点核对。

## 推断与交付
95%逐点CI、不连线。SA/TWFE保留Stata省聚类推断；LP-DiD和DoubleML以软件省聚类SE配t(G-1)临界值作展示，同时保留软件原始正态p/CI。少聚类尤其+4很弱，不能认为这种t近似已经解决少处理组或重叠问题。原动态TWFE均值附预定种子wild检验，但不将其与SA或DML的常规p混淆。
新旧系数比较分两部分：旧最大样本→新共同样本，反映样本变化；同一共同样本无经济→有经济，反映增加经济控制。所有版本都保留，不按显著性选择。
独立复核城市年匹配、60个SA批次点估计、全部动态TWFE的Stata对照、32个LP-DiD点估计及聚类SE、DML省级分折独立性和全部重复。代码/CSV/Excel/HTML/图册，无PDF，未覆盖原网络和既有结果。

重跑入口：add_city_economics.py → code/estimate_SA_TWFE_economic.py → 对应Stata do；build_economic_dynamic_twfe.py → code/estimate_economic_dynamic_TWFE.py → 对应Stata do；build_economic_lp_dml.py → code/prepare_economic_lp_dml.py → Stata run_lpdid.do，并运行code/fit_economic_doubleml.py；最后report_officer_city_economics.py。本机路径与依赖配置保留。
'''
(O/'methods_中文.md').write_text(notes,encoding='utf8')
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig')
with pd.ExcelWriter(O/'官员任职城市GDP_全部方法与同样本对照.xlsx',engine='openpyxl') as w:
 for name,q in [('SA_fixed_TWFE',R),('SA_models',M),('SA_joint_tests',J),('SA_weights',W),('Dynamic_TWFE',DR),('Dynamic_joint',DJ),('LPDID',L),('DoubleML',F),('LP_DML_support',MP),('Moving_examples',ex),('City_changes_audit',audit),('Match_checks',pd.read_csv(O/'economic_matching_checks.csv')),('Validation',pd.DataFrame(checks)),('DML_repetitions',REPS)]:
  q.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>GDP跟随官员任职城市</title><style>body{max-width:1500px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}section{margin:35px 0}</style><h1>加入官员任职城市的经济控制：全部方法</h1><p>年度GDP按官员每年任职城市匹配；LP-DiD/DoubleML用官员事前任职城市的经济特征。同一样本重新估计无经济/有经济两版，区别控制效应与样本变化。全部保留。</p><p><a href="官员任职城市GDP_全部方法与同样本对照.xlsx">Excel全部结果</a> · <a href="methods_中文.md">口径与匹配说明</a> · <a href="moving_official_examples.csv">调任官员实例</a></p>'
for fn,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+fn+'"></section>'
(O/'index.html').write_text(page,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Four readable figures',len(gallery)==4);ck('No PDF',not list(O.rglob('*.pdf')))
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig');assert all(c['passed'] for c in checks)
for name in ['add_city_economics.py','build_economic_lp_dml.py','build_economic_dynamic_twfe.py','report_officer_city_economics.py']:
 source=Path(__file__).with_name(name);target=O/'code'/name
 if source.resolve()!=target.resolve():shutil.copy2(source,target)
pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']).to_csv(O/'file_manifest.csv',index=False)
archive=B/'官员城市GDP_全部回归图表与代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('VALIDATED',len(checks),'checks')
print('SA/TWFE with economics',R[R.econ&R.term.isin(['d_p1','post_average'])][['fe','method','term','b','p']].to_string(index=False));print('LP with economics',L[L.econ&L.h.gt(0)][['fe','h','b','p','N']].to_string(index=False));print('DML with economics',F[F.economic_controls&F.h.gt(0)][['learner','h','b','p','N']].to_string(index=False))
