from pathlib import Path
import sys,json,shutil,hashlib,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.stats import t,f
from scipy.linalg import lstsq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from PIL import Image
O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\control_FE_sensitivity_post4')
for fn in ['level_models.log','LPDID_models.log','candidate_audit.log']:assert 'log close' in (O/fn).read_text(encoding='utf8',errors='replace')[-400:]
MD=pd.read_csv(O/'prespecified_models.csv');ML=pd.read_csv(O/'prespecified_LPDID_models.csv');FES=pd.read_csv(O/'prespecified_FE.csv');CFG=pd.read_csv(O/'prespecified_controls.csv')
R=pd.read_stata(O/'level_results.dta').merge(MD,on='model_id',validate='m:1');J=pd.read_stata(O/'level_joint.dta').merge(MD,on='model_id',validate='m:1');MS=pd.read_stata(O/'model_stats.dta').merge(MD,on='model_id',validate='m:1');V=pd.read_stata(O/'level_covariances.dta');W=pd.read_stata(O/'SA_weights.dta');C=pd.read_stata(O/'SA_cohort_points.dta')
L=pd.read_stata(O/'LPDID_results.dta').merge(ML,on='model_id',validate='m:1');L['h']=L.term.map(lambda s:-int(s[3:]) if s.startswith('pre') else int(s[3:]));P=pd.read_csv(O/'LPDID_independent_points_SE.csv');Q=pd.read_csv(O/'horizon_pairs.csv.gz');B=pd.read_stata(O/'candidate_wild.dta');LOO=pd.read_stata(O/'candidate_leave_one_province.dta')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
ck('108 complete level regressions',len(MS)==108 and R.groupby(['model_id','estimator']).size().eq(10).all())
ck('All level specifications estimated without failure',len(pd.read_stata(O/'level_failures.dta'))==0)
ck('All 18 LP-DiD specifications estimated without failure',len(pd.read_stata(O/'LPDID_failures.dta'))==0 and L.model_id.nunique()==18)
ck('Level FE and control comparisons use identical source samples',MS.groupby('sample').N.nunique().eq(1).all())
ck('All level estimates and CIs finite',np.isfinite(R[['b','se','p','lo','hi']]).all().all())
agg=C.merge(W,on=['model_id','cohort','term'],validate='1:1');agg['wb']=agg.b*agg.weight;agg=agg.groupby(['model_id','term']).wb.sum().reset_index().merge(R[R.estimator.eq('Sun_Abraham')],on=['model_id','term'],validate='1:1')
ck('All 288 SA event coefficients equal official cohort aggregation',len(agg)==288 and np.allclose(agg.wb,agg.b,atol=1e-8))
ck('All SA shares sum to one',np.allclose(W.groupby(['model_id','term']).weight.sum(),1,atol=1e-10))
for (mid,est),g in V.groupby(['model_id','estimator']):
 a=g.pivot(index='term1',columns='term2',values='value');q=R[R.model_id.eq(mid)&R.estimator.eq(est)].set_index('term');ns=['d_p1','d_p2','d_p3','d_p4']
 ck('Full-covariance average '+str(mid)+est,np.isclose(q.loc['post_average','se']**2,a.loc[ns,ns].to_numpy().sum()/16,atol=1e-8))
ck('Ten candidate wild-bootstrap tests completed',len(B)==10 and B.rc.eq(0).all() and B.p_wild.notna().all())
ck('Two candidate leave-one-province audits complete',len(LOO)==104 and LOO.rc.eq(0).all())

lp=L[L.h.ne(-1)].merge(P,on=['model_id','h'],suffixes=('','_py'),validate='1:1')
for col in ['b','se','N']:ck('144 independent LP-DiD '+col,len(lp)==144 and np.allclose(lp[col],lp[col+'_py'],atol=3e-6,rtol=3e-6))
L=L.merge(P[['model_id','h','G','treated']],on=['model_id','h'],how='left',validate='1:1');L['p_normal']=L.p;L['lo_normal']=L.lo;L['hi_normal']=L.hi
for i,r in L[L.h.ne(-1)].iterrows():
 crit=t.ppf(.975,r.G-1);L.loc[i,['p','lo','hi']]=[2*t.sf(abs(r.b/r.se),r.G-1),r.b-crit*r.se,r.b+crit*r.se]
ck('LP-DiD common horizon samples',L[L.h.ne(-1)].groupby('h').N.nunique().eq(1).all())
lav=[];lj=[];lscores=[]
for m in ML.itertuples():
 scorecols={}
 for h,g in Q.groupby('h'):
  cols=(['base_age','base_age2','base_tenure','base_tenure2','base_role'] if m.personal else [])+([] if pd.isna(m.economic_controls) else m.economic_controls.split())
  z=np.column_stack([np.ones(len(g)),g[cols].to_numpy(),pd.get_dummies(g.base_rank0,drop_first=True,dtype=float).to_numpy() if m.personal else np.empty((len(g),0)),pd.get_dummies(g['anchor_province' if m.fe=='province' else 'G0'],drop_first=True,dtype=float).to_numpy()]);norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0];ctl=g.C0.eq(0).to_numpy();bb=lstsq(z[ctl],g.deltaY.to_numpy()[ctl],cond=1e-10)[0];u=g.deltaY.to_numpy()-z@bb;val=u[~ctl].mean();sc=np.zeros(len(g));sc[~ctl]=(u[~ctl]-val)/(~ctl).sum();sc[ctl]=-u[ctl]*(z[ctl]@np.linalg.pinv(z[ctl].T@z[ctl],rcond=1e-10)@z[~ctl].mean(axis=0));cs=pd.Series(sc).groupby(g.anchor_province.to_numpy()).sum();scorecols[h]=cs
  for p,s in cs.items():lscores.append(dict(model_id=m.model_id,h=h,province=p,score=s))
 sv=pd.DataFrame(scorecols).fillna(0);vv=sv.T@sv;q=L[L.model_id.eq(m.model_id)].set_index('h');hs=[1,2,3,4];b=q.loc[hs,'b'].mean();se=np.sqrt(vv.loc[hs,hs].to_numpy().sum()/16);df=q.loc[hs,'G'].min()-1;crit=t.ppf(.975,df)
 lav.append(dict(model_id=m.model_id,fe=m.fe,control_id=m.control_id,control_label=m.control_label,estimator='LPDID',term='post_average',b=b,se=se,p=2*t.sf(abs(b/se),df),lo=b-crit*se,hi=b+crit*se,df=df))
 for name,hs in [('pretrend',[-4,-3,-2]),('post_joint',[1,2,3,4])]:
  aa=q.loc[hs,'b'].to_numpy();va=vv.loc[hs,hs].to_numpy();rr=np.linalg.matrix_rank(va);ff=float(aa@np.linalg.pinv(va)@aa/rr);df=q.loc[hs,'G'].min()-1;lj.append(dict(model_id=m.model_id,test=name,F=ff,df_num=rr,df_den=df,p=f.sf(ff,rr,df)))
LA=pd.DataFrame(lav);LJ=pd.DataFrame(lj);pd.DataFrame(lscores).to_csv(O/'LPDID_cluster_scores.csv',index=False)

def holm(x):
 a=np.asarray(x);o=np.argsort(a);v=np.empty(len(a));v[o]=np.minimum(1,np.maximum.accumulate(a[o]*np.arange(len(a),0,-1)));return v
R['p_holm_spec']=np.nan;R['p_holm_all_post']=np.nan
for est in R.estimator.unique():
 for term in ['d_p1','d_p2','d_p3','d_p4','post_average']:
  ix=R.estimator.eq(est)&R.term.eq(term);R.loc[ix,'p_holm_spec']=holm(R.loc[ix,'p'])
 ix=R.estimator.eq(est)&R.term.isin(['d_p1','d_p2','d_p3','d_p4']);R.loc[ix,'p_holm_all_post']=holm(R.loc[ix,'p'])
L['p_holm_spec']=np.nan;L['p_holm_all_post']=np.nan
for h in [1,2,3,4]:
 ix=L.h.eq(h);L.loc[ix,'p_holm_spec']=holm(L.loc[ix,'p'])
ix=L.h.isin([1,2,3,4]);L.loc[ix,'p_holm_all_post']=holm(L.loc[ix,'p']);LA['p_holm_spec']=holm(LA.p)
SUMMARY=[]
for (mid,est),g in R.groupby(['model_id','estimator']):
 q=g[g.term.isin(['d_p1','d_p2','d_p3','d_p4'])];a=g[g.term.eq('post_average')].iloc[0];p1=g[g.term.eq('d_p1')].iloc[0]
 SUMMARY.append(dict(model_id=mid,estimator=est,fe=a.fe,control_id=a.control_id,control_label=a.control_label,negative_periods=int(q.b.lt(0).sum()),negative_sig5=int((q.b.lt(0)&q.p.lt(.05)).sum()),negative_sig10=int((q.b.lt(0)&q.p.lt(.1)).sum()),four_negative_sig5=bool((q.b.lt(0)&q.p.lt(.05)).all()),four_negative_sig10=bool((q.b.lt(0)&q.p.lt(.1)).all()),average_b=a.b,average_p=a.p,average_holm=a.p_holm_spec,post1_b=p1.b,post1_p=p1.p,post1_holm=p1.p_holm_spec))
for mid,g in L.groupby('model_id'):
 q=g[g.h.isin([1,2,3,4])];a=LA[LA.model_id.eq(mid)].iloc[0];p1=g[g.h.eq(1)].iloc[0]
 SUMMARY.append(dict(model_id=mid,estimator='LPDID',fe=a.fe,control_id=a.control_id,control_label=a.control_label,negative_periods=int(q.b.lt(0).sum()),negative_sig5=int((q.b.lt(0)&q.p.lt(.05)).sum()),negative_sig10=int((q.b.lt(0)&q.p.lt(.1)).sum()),four_negative_sig5=bool((q.b.lt(0)&q.p.lt(.05)).all()),four_negative_sig10=bool((q.b.lt(0)&q.p.lt(.1)).all()),average_b=a.b,average_p=a.p,average_holm=a.p_holm_spec,post1_b=p1.b,post1_p=p1.p,post1_holm=p1.p_holm_spec))
SU=pd.DataFrame(SUMMARY)
for fn,q in [('all_level_results.csv',R),('all_level_joint_tests.csv',J),('all_LPDID_results.csv',L),('LPDID_average_results.csv',LA),('LPDID_joint_tests.csv',LJ),('all_specification_stability.csv',SU),('candidate_wild.csv',B),('candidate_leave_one_province.csv',LOO)]:q.to_csv(O/fn,index=False,encoding='utf-8-sig')
R[R.term.eq('post_average')].sort_values(['estimator','p']).to_csv(O/'all_average_rankings_exploratory.csv',index=False,encoding='utf-8-sig')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
gallery=[]
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=170,facecolor='white');plt.close(fig);gallery.append((name,title))
flabel={'I_YEAR':'Individual + year','I_PXY':'Individual + prov x year','I_CITY_YEAR':'Individual + city + year','I_CITY_PXY':'Individual + city + prov x year','cohort':'Cohort','province':'Province'}
def heatmap(avg=False):
 fig,axes=plt.subplots(4,1,figsize=(16,14),gridspec_kw={'height_ratios':[4,4,4,2]});cids=CFG.control_id.tolist()
 for ax,est in zip(axes,['Sun_Abraham','TWFE_fixed','TWFE_dynamic','LPDID']):
  if est=='LPDID':q=LA if avg else L[L.h.eq(1)];fs=['cohort','province']
  else:q=R[R.estimator.eq(est)&R.term.eq('post_average' if avg else 'd_p1')];fs=FES.fe.tolist()
  vals=q.pivot(index='fe',columns='control_id',values='b').reindex(index=fs,columns=cids);pp=q.pivot(index='fe',columns='control_id',values='p').reindex(index=fs,columns=cids)
  ax.imshow(vals,cmap='RdBu_r',norm=TwoSlopeNorm(vmin=-30,vcenter=0,vmax=30),aspect='auto')
  for i,fe in enumerate(fs):
   for j,c in enumerate(cids):
    p=pp.loc[fe,c];txt=f'{vals.loc[fe,c]:+.1f}\np='+('<.001' if p<.001 else f'{p:.3f}')
    ax.text(j,i,txt,ha='center',va='center',fontsize=8,color='white' if abs(vals.loc[fe,c])>20 else '#111111')
  ax.set_xticks(range(9),cids);ax.set_yticks(range(len(fs)),[flabel[x] for x in fs]);ax.set_title(est.replace('_',' '),loc='left',fontsize=12)
 fig.suptitle(('Four-year average change (+1 to +4)' if avg else 'First complete post year (+1)')+' across all control / FE specifications\nCell: coefficient in pp and raw p-value | All specifications retained',fontsize=17,y=.99)
 fig.subplots_adjust(top=.91,bottom=.17,left=.23,right=.98,hspace=.46)
 fig.text(.04,.035,'C00: FE only; C01: personal controls; C02: +GDP growth; C03: +log GDP per capita; C04: +log population.\nC05: personal + growth + GDPpc; C06: personal + growth + population; C07: personal + GDPpc + population; C08: all.\nLevel-model samples fixed across controls and FEs within network definition; LP-DiD uses common horizon pairs.\nRaw p-values are exploratory. Holm-adjusted p-values and all 95% CIs are in Excel / CSV. No four-period significant run.',fontsize=10)
 export(fig,'02_all_specs_average_heatmap.png' if avg else '01_all_specs_post1_heatmap.png','All specifications: average change' if avg else 'All specifications: first post year')
heatmap();heatmap(True)

fig,axes=plt.subplots(2,2,figsize=(15,11),sharey=True)
for ax,fe in zip(axes.flat,FES.fe):
 for j,est in enumerate(['Sun_Abraham','TWFE_fixed']):
  q=R[R.fe.eq(fe)&R.control_id.eq('C08')&R.estimator.eq(est)&R.term.str.startswith('d_')].copy();q['k']=q.term.map(lambda s:-int(s[3:]) if s.startswith('d_m') else int(s[3:]));q=q.sort_values('k');off=(j-.5)*.13
  ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s'][j],ls='none',color=['#287c9e','#cf8735'][j],capsize=3,ms=4,label=est.replace('_',' '));ax.plot(-1+off,0,marker=['o','s'][j],ls='none',mfc='white',mec=['#287c9e','#cf8735'][j])
 ax.axhline(0,color='gray',ls='--',lw=.8);ax.axvline(0,color='#b18b36',ls=':',lw=.8);ax.set_xticks(range(-4,5));ax.grid(axis='y',alpha=.15);ax.set_title(flabel[fe]);ax.set_xlabel('Years relative to first inspection')
for ax in axes[:,0]:ax.set_ylabel('Change in promotion gap (pp), reference k=-1')
fig.suptitle('All personal and economic controls (C08): compare four FE structures\nFixed pre-inspection relationship group | 95% province-clustered CIs',fontsize=16,y=.98);fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=2,frameon=False);fig.subplots_adjust(top=.83,bottom=.16,left=.08,right=.98,wspace=.14,hspace=.30)
fig.text(.06,.035,'Identical 2,807 officer-years and controls across FE comparisons. +4 has only 4 baseline-connected officials.\nThe strong city-FE four-year average is partly driven by +4; +1 to +3 are not a run of 5% significant negative effects.\nAdding province-by-year shocks weakens the pattern. Changing role / city and promotion risk sets remain potential selection channels.',fontsize=9)
export(fig,'03_all_controls_four_FE_event_studies.png','Full controls: event studies under four FE structures')

fig,axes=plt.subplots(1,2,figsize=(14,10),sharey=True)
province_order=sorted(LOO.removed_province.unique())
for ax,contrast,title in zip(axes,['post_average','post4'],['Average change: +1 to +4','Change at +4']):
 for j,cid in enumerate(['C02','C08']):
  ids=MD[MD['sample'].eq('fixed')&MD.fe.eq('I_CITY_YEAR')&MD.control_id.eq(cid)].model_id
  q=LOO[LOO.model_id.isin(ids)&LOO.contrast.eq(contrast)].set_index('removed_province').reindex(province_order);crit=t.ppf(.975,24)
  ax.errorbar(q.b,np.arange(len(q))+(j-.5)*.16,xerr=crit*q.se,fmt=['o','s'][j],ls='none',ms=3,capsize=2,color=['#287c9e','#cf8735'][j],label=cid)
 ax.axvline(0,color='gray',ls='--',lw=.8);ax.set_yticks(range(len(province_order)),[str(int(x)) for x in province_order]);ax.set_ylim(len(province_order)-.5,-.5);ax.grid(axis='x',alpha=.15);ax.set_title(title);ax.set_xlabel('Coefficient (pp); each row drops one province')
axes[0].set_ylabel('Excluded province code');axes[0].legend();fig.suptitle('Post-search diagnostic: individual + city + year FE\nLeave-one-province-out point estimates and 95% CIs',fontsize=16);fig.subplots_adjust(top=.87,bottom=.13,wspace=.12)
fig.text(.06,.025,'C02: personal controls + GDP growth; C08: all personal/economic controls. Exploratory audit after observing the specification grid.\nIntervals use t(24); province clustering. This does not account for specification selection or establish causal identification.',fontsize=9)
export(fig,'04_leave_one_province_diagnostic.png','Exploratory leave-one-province diagnostic')

methods='''# 控制组合与固定效应的完整敏感性分析

本轮研究窗口固定[-4,+4]，不再与控制组合同时选择时间范围。不按显著性删除规格。DoubleML本轮未新增调参或变量搜索；上一轮DoubleML结果仍单独保存，不将其冒称本轮新增规格。

## 预先列出的规格
控制C00仅FE；C01个人控制；C02个人+GDP增长；C03个人+对数人均GDP；C04个人+对数人口；C05个人+增长+人均GDP；C06个人+增长+人口；C07个人+人均GDP+人口；C08个人+全部经济控制。个人变量沿用年龄特征、任期及平方、职级、书记/市长身份；年度个人+时间FE吸收线性年龄，LP使用基期年龄及平方。
年度FE四种：个人+年；个人+省×年；个人+城市+年；个人+城市+省×年。所有年度模型都含个人FE。C00是描述性基准，不因p值较小就代替完整控制主规格。
Sun-Abraham固定事前C0，36个组合；固定C0 TWFE同36个；原动态C_it TWFE同36个；LP-DiD基期控制×批次/省FE共18个。合计126个规格。LP没有额外加个人FE，因为长差分已滤除个人不变水平。

## 共同样本与GDP随官员
沿用上一轮独立重匹配的城市经济列：年度t按官员t-1年末任职城市，匹配该市t-1日历年GDP增长、对数人均GDP、对数人口。调任者采用对应任职城市经济信息。LP取k=-1记录的任职城市事前经济特征并固定。原始数据及网络未覆盖。
固定C0样本递归剔除个人/城市/省×年singleton后2807个人年，四类FE使用相同样本；动态C_it共同样本4111个人年。新增城市FE比此前各另删除少量singleton，因此旧图与新图不能只按控制差异比较。所有控制版本，包括不含经济变量版本，都在相同完整经济样本上重跑。
LP使用此前基期经济完整、且同省存在比较组的配对样本；同一h的18规格样本一致，事后样本340/274/168/43，关系组38/32/17/4。+4仍只有2013巡视批次支持，不能外推2014批次。

## 方程和推断
Sun-Abraham继续官方eventstudyinteract的cohort×event交互加权，未将普通TWFE改名。固定C0 TWFE与动态C_it TWFE的估计对象分开报告。城市FE吸收任职城市不变特征，但在有个人FE时城市效应主要依赖跨城市流动识别；任职城市可能受巡视、调动和晋升影响，加入它不自动代表因果设计更好。
个人+年份FE和个人+城市+年份FE加入巡视event主项；省×年版本吸收主项。省级聚类，95%逐点CI，不连线。LP保留官方正态p/CI，同时主展示采用相同SE配t(G-1)，不将其当作精确少聚类推断。
各模型报告完整逐期系数、四期平均、晚期平均、事前/事后联合检验。平均使用完整跨期协方差；联合拒绝全零不等于每期负显著，也不等于平均负显著。LP的平均来自跨期省级影响函数协方差，风险集跨h变化。

## 多重检验与后续审计
每种年度估计器的+1、+2、+3、+4以及四期平均，分别对36个控制/FE规格做Holm校正；另对全部144个事后单期检验作校正。LP相应为18规格和72个单期检验。原始p值与校正p并列，排名仅作探索，不能将最低p视作预先指定的确认性结果。
查看完整网格后，对固定C0 TWFE的C08四类FE、以及原始平均p较小的城市FE C02，共5个规格做省级Webb wild bootstrap，9999次，种子20261015，检验平均及+4，共10项。boottest不支持多组吸收FE，因此bootstrap时仅吸收个人FE，其他相同FE改成显式虚拟变量，并逐项断言点估计与原多维吸收规格相同。原始常规p和SE仍来自原模型。城市FE的C02/C08另做26次逐省剔除，各存平均与+4。这是观察网格后追加的诊断，不是新的独立确认样本。
独立复核全部144个LP-DiD点估计、聚类SE和样本数；核对288个SA事件系数的批次加权、108个四期平均的完整协方差，以及全部FE/控制版本的共同样本。Stata日志、失败记录、预列模型清单和所有结果都交付。未为了显著性改网络、晋升标签、聚类或删去不符合预期的控制。

重跑：control_fe_multiverse.py → Stata run_level_models.do 与run_LPDID_models.do → audit_control_fe_candidates.py → Stata audit_candidates.do → report_control_fe_multiverse.py。绝对路径为本机配置，移机需调整。无PDF。
'''
(O/'methods_中文.md').write_text(methods,encoding='utf8')
with pd.ExcelWriter(O/'控制组合_FE_全部126规格.xlsx',engine='openpyxl') as w:
 for name,q in [('All_spec_stability',SU),('All_level_results',R),('Level_joint',J),('Level_models',MS),('LPDID_all_results',L),('LPDID_averages',LA),('LPDID_joint',LJ),('Candidate_wild',B),('Leave_one_province',LOO),('Controls',CFG),('FE',FES),('Prespecified_models',MD),('LP_models',ML),('Common_samples',pd.read_csv(O/'common_samples.csv')),('Validation',pd.DataFrame(checks))]:
  q.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>控制与FE完整敏感性</title><style>body{max-width:1600px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}section{margin:35px 0}</style><h1>9种控制 × 4种年度FE；126个规格全部保留</h1><p>固定[-4,+4]。报告原始及Holm校正p值；平均变化、逐期变化和联合检验分开。城市FE可能使固定事前关系模型的平均变化更显著，但+4仅4名关系官员，且加入省×年FE后证据减弱。图不是确认性因果证据。</p><p><a href="控制组合_FE_全部126规格.xlsx">Excel全部结果</a> · <a href="methods_中文.md">方法、校正与后续诊断</a></p>'
for fn,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+fn+'"></section>'
(O/'index.html').write_text(page,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Four readable figures',len(gallery)==4);ck('No PDF generated',not list(O.rglob('*.pdf')))
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig');assert all(x['passed'] for x in checks)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']).to_csv(O/'file_manifest.csv',index=False)
archive=O.parent/'控制组合_FE_126规格_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('Validation checks:',len(checks),'all pass')
print('Best raw average, per estimator:');print(SU.sort_values('average_p').groupby('estimator').head(1).to_string(index=False));print('Four consecutive significant negatives',SU.four_negative_sig5.sum(),SU.four_negative_sig10.sum())
print('Candidate wild:',B.merge(MD[['model_id','fe','control_id']],on='model_id').to_string(index=False))
print('LOO average ranges',LOO[LOO.contrast.eq('post_average')].groupby('model_id').agg(min_b=('b','min'),max_b=('b','max'),min_p=('p','min'),max_p=('p','max')).to_string())
