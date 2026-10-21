from pathlib import Path
import sys,shutil,hashlib,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'cumulative_promotion_TWFE_12_24_36m'
for fn in ['TWFE.log','FD_validation.log']:assert 'closed on:' in (O/fn).read_text(errors='replace')[-900:]
M=pd.read_csv(O/'model_design.csv');R=pd.read_stata(O/'TWFE_results.dta').merge(M,on='model_id',suffixes=('','_design'),validate='1:1');FD=pd.read_stata(O/'FD_validation.dta');W=pd.read_stata(O/'wild_cluster_tests.dta');P=pd.read_csv(O/'all_estimation_panels.csv.gz');AUD=pd.read_csv(O/'cumulative_outcome_audit.csv.gz');EV=pd.read_csv(O/'promotion_event_evidence_all_careers.csv');EV.event_date=pd.to_datetime(EV.event_date);A=pd.read_csv(O/'cohort_anchor_all.csv.gz');F=pd.read_csv(O/'sample_flow.csv');checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
def save(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')
def holm(x):
 a=np.asarray(x);idx=np.argsort(a);z=np.empty(len(a));z[idx]=np.minimum(1,np.maximum.accumulate(a[idx]*np.arange(len(a),0,-1)));return z
ck('54 models completed',len(R)==54);ck('No model failures',len(pd.read_stata(O/'TWFE_failures.dta'))==0);ck('All expected observations retained',R.N.eq(R.N_design).all());ck('All models finite',np.isfinite(R[['b','se','p','lo','hi']]).all().all());ck('Every estimate has positive SE',R.se.gt(0).all())
v=R.merge(FD,on='model_id',suffixes=('_twfe','_fd'),validate='1:1');ck('All 54 TWFE points equal first-difference Stata OLS',len(v)==54 and np.allclose(v.b_twfe,v.b_fd,atol=1e-7),abs(v.b_twfe-v.b_fd).max())
independent=[]
for r in R.itertuples():
 d=P[P['sample'].eq(r.sample)&P.H.eq(r.H)];a=d[d.post.eq(0)].set_index('person_id').sort_index();z=d[d.post.eq(1)].set_index('person_id').reindex(a.index);dy=(z.Y-a.Y).to_numpy();c=a.C0.to_numpy();pieces=[np.ones((len(a),1))]
 if r.control!='none':
  cs=['age0','age20','tenure0','tenure20','role0']+(['growth0','lngdppc0','lnpop0'] if r.control=='full' else []);pieces+=[a[cs].to_numpy(),pd.get_dummies(a.rank0,drop_first=True,dtype=float).to_numpy()]
 if r.fe=='I_CALENDAR':pieces.append(pd.get_dummies(a.end_year,drop_first=True,dtype=float).to_numpy())
 if r.fe=='I_PXY':pieces.append(pd.get_dummies(a.anchor_province,drop_first=True,dtype=float).to_numpy())
 # reghdfe.mata: nested_adj=(df_a_nested>0), an extra one in the
 # cluster finite-sample denominator when person FE nest in province.
 Z=np.column_stack(pieces);norm=np.linalg.norm(Z,axis=0);Z=Z[:,norm>1e-10]/norm[norm>1e-10];yx=np.column_stack([dy,c]);res=yx-Z@lstsq(Z,yx,cond=1e-10)[0];yr=res[:,0];cr=res[:,1];bb=float(cr@yr/(cr@cr));err=yr-cr*bb;score=pd.Series(cr*err).groupby(a.anchor_province.to_numpy()).sum();se=np.sqrt((score**2).sum()/(cr@cr)**2*r.G/(r.G-1)*(r.N-1)/(r.N-r.K-1));independent.append(dict(model_id=r.model_id,b_python=bb,se_python=se,target_residual_norm=float(np.linalg.norm(cr))))
 ck(f'Python FWL point {r.model_id}',np.isclose(bb,r.b,atol=1e-7));ck(f'Python cluster covariance {r.model_id}',np.isclose(se,r.se,atol=1e-7),se-r.se)
ck('Three province wild tests complete',len(W)==3 and W.rc.eq(0).all() and W.p_wild.notna().all());W['p_wild_holm_three_H']=holm(W.p_wild)
R=R.merge(W,on='model_id',how='left',validate='1:1');R['p_holm_three_main_H']=np.nan;main=R['sample'].eq('common_all_H')&R.fe.eq('I_PXY')&R.control.eq('full');R.loc[main,'p_holm_three_main_H']=holm(R.loc[main,'p'])
R['p_holm_nine_specs_at_H']=np.nan
for key,d in R.groupby(['sample','H']):R.loc[d.index,'p_holm_nine_specs_at_H']=holm(d.p)
ck('One window record per person-H-phase',not AUD.duplicated(['person_id','H','post']).any());ck('Known zero requires full observation and no unresolved appointment',AUD.loc[AUD.Y.eq(0),'covered'].all() and AUD.loc[AUD.Y.eq(0),'uncertain_appointments'].eq(0).all())
for post,g in AUD.groupby('post'):
 a=g.pivot(index='person_id',columns='H',values='Y');ck(f'Cumulative successes monotone across nested windows, phase={post}',not ((a[12].eq(100)&a[24].eq(0))|(a[24].eq(100)&a[36].eq(0))).any())
for H,d in P[P['sample'].eq('common_all_H')].groupby('H'):
 ck(f'Common cohort exactly 422 officials H={H}',d.person_id.nunique()==422);ck(f'Paired two observations H={H}',d.groupby('person_id').size().eq(2).all());ck(f'Fixed personal connection H={H}',d.groupby('person_id').C0.nunique().eq(1).all())
for c in ['inspection_date','start','end_exclusive','event_date']:AUD[c]=pd.to_datetime(AUD[c])
positive=AUD[AUD.Y.eq(100)];match=positive.merge(EV[['person_id','event_row','event_date']].drop_duplicates(),on=['person_id','event_row'],suffixes=('','_e'),validate='m:1');ck('All positive windows have source-backed events',len(match)==len(positive) and match.event_date.eq(match.event_date_e).all());ck('Positive event is inside the exact window',positive.event_date.ge(positive.start).all() and positive.event_date.lt(positive.end_exclusive).all());ck('All windows within complete observation calendar',AUD.end_exclusive.le('2018-01-01').all())
old=pd.read_csv(B/'annual_official_panel.csv.gz');old=old[old.person_id.isin(A[A.eligible_controls&A.eligible_relation].person_id)&old.promotion.eq(1)].copy();old.event_date=pd.to_datetime(old.event_date);old=old.merge(EV[['person_id','event_date']].drop_duplicates().assign(found=True),on=['person_id','event_date'],how='left');ck('All prior audited positive annual events preserved',old.found.fillna(False).all());save(old[old.found.isna()],'annual_positive_event_disagreements.csv')
retention=AUD.groupby(['H','post','C0']).Y.agg(['count','size']).reset_index();retention['known_share']=retention['count']/retention['size'];save(retention,'outcome_observation_by_connection.csv')
rates=P[P['sample'].eq('common_all_H')].groupby(['H','post','C0']).Y.agg(['count','mean','sum']).reset_index().rename(columns={'mean':'promotion_rate_pct'});rates['promotion_events']=rates['sum']/100;save(rates,'raw_group_promotion_rates.csv')
save(R,'all_TWFE_results.csv');save(FD,'first_difference_validation.csv');save(W,'main_wild_cluster_tests.csv');save(pd.DataFrame(independent),'independent_Python_verification.csv');save(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False});gallery=[]
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=180,facecolor='white');plt.close(fig);gallery.append((name,title))
def draw(ax,d,color,marker,off,label):
 d=d.sort_values('H');x=d.H/12+off;ax.errorbar(x,d.b,yerr=[d.b-d.lo,d.hi-d.b],fmt=marker,ls='none',ms=6,capsize=4,color=color,label=label)
def styling(ax):
 ax.axhline(0,color='gray',ls='--',lw=1);ax.set_xticks([1,2,3],['12 months','24 months','36 months']);ax.set_xlim(.65,3.35);ax.grid(axis='y',alpha=.15)
fig,ax=plt.subplots(figsize=(12,7.5))
for fe,col,mk,off,label in [('I_PERIOD','#909090','s',-.13,'Individual + pre/post period FE'),('I_CALENDAR','#287c9e','o',0,'Individual + window-end calendar year FE'),('I_PXY','#c77e27','^',.13,'Individual + province x pre/post period FE')]:draw(ax,R[R['sample'].eq('common_all_H')&R.control.eq('full')&R.fe.eq(fe)],col,mk,off,label)
styling(ax);ax.set_ylabel('Post-minus-pre change in connection-related gap (pp)');ax.legend(frameon=False,fontsize=10);fig.suptitle('Cumulative promotion within equal-length pre/post windows | TWFE\nFixed officials and pre-inspection ties | Full baseline controls | 95% CIs',fontsize=15)
fig.subplots_adjust(top=.82,bottom=.25,left=.1,right=.97);fig.text(.08,.04,'Same 422 officials at every horizon (45 connected), 24 province clusters; two records per official per horizon.\nOutcome: at least one documented promotion within each H-month window. Missing follow-up is not coded as zero.\nControls enter as baseline characteristics x Post; fixed levels are absorbed by individual FE. Points are not connected.\nCohort selection predates inspection but falls inside the 24/36-month pre-window: these are conditional associations.',fontsize=10)
export(fig,'01_cumulative_TWFE_three_horizons.png','Main cumulative TWFE: three horizons, three FE structures')

fig,axs=plt.subplots(1,2,figsize=(15,7.5),sharey=True)
for ax,fe,title in zip(axs,['I_CALENDAR','I_PXY'],['Individual + calendar year FE','Individual + province x pre/post FE']):
 for control,col,mk,off,label in [('none','#909090','s',-.13,'FE only'),('personal','#287c9e','o',0,'Baseline personal x Post'),('full','#c77e27','^',.13,'Personal and economic x Post')]:draw(ax,R[R['sample'].eq('common_all_H')&R.control.eq(control)&R.fe.eq(fe)],col,mk,off,label)
 styling(ax);ax.set_title(title)
axs[0].set_ylabel('Post-minus-pre change in connection-related gap (pp)');fig.suptitle('Control sensitivity on identical officials | Cumulative promotion TWFE\n95% province-clustered t confidence intervals',fontsize=16);fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=3,frameon=False,fontsize=10);fig.subplots_adjust(top=.76,bottom=.23,left=.08,right=.98,wspace=.12)
fig.text(.06,.04,'N=844 observations / 422 officials in every fit. FE-only benchmarks and both control sets are retained.\nBaseline personal: age, age squared, tenure, tenure squared, rank and city-secretary indicator.\nEconomics: pre-inspection officer-city GDP growth, log GDP per capita and log population. No post-inspection economics.',fontsize=10)
export(fig,'02_control_sensitivity_same_sample.png','Control sensitivity: all retained specifications')

fig,axs=plt.subplots(1,3,figsize=(16,6.5),sharey=True)
for ax,H in zip(axs,[12,24,36]):
 for j,c in enumerate([0,1]):
  q=rates[rates.H.eq(H)&rates.C0.eq(c)].sort_values('post');x=np.array([0,1])+(j-.5)*.32;ax.bar(x,q.promotion_rate_pct,width=.29,color=['#8c969c','#287c9e'][j],label='No baseline tie' if c==0 else 'Baseline tie')
  for xx,rr in zip(x,q.itertuples()):ax.text(xx,rr.promotion_rate_pct+1,f'{rr.promotion_rate_pct:.1f}%',ha='center',fontsize=10)
 ax.set_xticks([0,1],['Pre-inspection','Post-inspection']);ax.set_title(f'{H}-month windows');ax.set_ylim(0,72);ax.grid(axis='y',alpha=.15)
axs[0].set_ylabel('At least one promotion (%)');fig.suptitle('Raw cumulative promotion rates | Same 422 officials\nDescriptive group means, without covariate or FE adjustment',fontsize=16);fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.84),ncol=2,frameon=False);fig.subplots_adjust(top=.73,bottom=.23,left=.06,right=.98,wspace=.1)
fig.text(.055,.04,'377 officials without a baseline tie; 45 with a tie. These bars show raw rates, not estimated causal effects.\nThe pre-period raw promotion rate is not higher for the connected group in this fixed cohort. A negative TWFE change does not establish disappearance of a positive pre-advantage.',fontsize=10)
export(fig,'03_raw_cumulative_promotion_rates.png','Raw pre/post group promotion rates')

fig,axs=plt.subplots(1,2,figsize=(15,7),sharey=True)
for ax,fe,title in zip(axs,['I_CALENDAR','I_PXY'],['Individual + calendar year FE','Individual + province x pre/post FE']):
 for sample,col,mk,off,label in [('common_all_H','#287c9e','o',-.07,'Same cohort across all H'),('maximum_each_H','#c77e27','s',.07,'Maximum complete cohort for each H')]:draw(ax,R[R['sample'].eq(sample)&R.control.eq('full')&R.fe.eq(fe)],col,mk,off,label)
 styling(ax);ax.set_title(title)
axs[0].set_ylabel('Post-minus-pre change in connection-related gap (pp)');fig.suptitle('Sample sensitivity | Full baseline controls | 95% province-clustered CIs',fontsize=16);fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.89),ncol=2,frameon=False);fig.subplots_adjust(top=.76,bottom=.21,left=.08,right=.98,wspace=.12)
fig.text(.06,.04,'Common sample: 422 officials / 24 provinces. Horizon-specific maximum: 497 / 466 / 425 officials at 12 / 24 / 36 months.\nOnly mathematical singleton province-period cells are removed for FE comparison; no minimum-10-province rule is imposed.',fontsize=10)
export(fig,'04_common_vs_horizon_maximum_samples.png','Common cohort and horizon-specific maximum cohorts')

mainR=R[R['sample'].eq('common_all_H')&R.fe.eq('I_PXY')&R.control.eq('full')].sort_values('H')
notes='''# 同一官员、固定事前关系：12/24/36个月等长前后窗口TWFE

用户选择了等长前后窗口TWFE。每个H分别估计，而不是把三个事后累计指标直接当作个人+年份面板。Y_pre=1{在[G-H,G)至少一次晋升}；Y_post=1{在[G,G+H)至少一次晋升}；乘100。G是该省首次中央巡视官方报告的开始/进驻日期。不得将动员会日期、新闻发布时间、反馈时间或1月1日统一当作G。31省日期另存逐省官方来源，未覆盖旧年份/季度表。

## 名单与关系
延续旧固定C0口径：取年度k=-1记录，该行按上一年末快照。因此2013巡视省使用2011-12-31官员和关系，2014巡视省使用2012-12-31。关系为与当时省委书记或省长任一人的2012年前至少六个月事前共事关系；未知不补0；不混入同乡或校友。655个候选锚点，629个关系已知；基期个人和三项经济控制完整后545人。本轮不要求基期年度晋升结果已知。
三种H的主比较使用所有六个窗口都能判定的同一名单，另统一剔除只有一名官员的省份（这是省×前后FE的数学singleton，不是人为最小省数门槛）。最终422人、其中45有关系，24省，各H844条。每个H最大完整样本另报497/466/425人。不能把跨H换人造成的变化解释为期限效应。

## 完整履历与晋升
只读用户CPED原zip，哈希固定。跟踪全部后续实质职位，离开市级岗位不会自动从结果中删除。保留已核验的原年度正向晋升事件，并补充完整职业履历中有先前职级/职务证据的新任职事件。晋升定义沿用职级上升、市长升市委书记、首次新任副省长（包括同为副部级）。普通委员/代表身份、同级平调、同职续任不自动算晋升；原广义口径包含职级上升的人大/政协领导岗位。
每窗至少一个有原始履历支持的正向事件则记1，即使随后离开市级岗位。零要求整个窗口有连续、职级可判断的实质履历覆盖，且没有未能判断职级的新任职；间隙/右删失/不明去向保持缺失。免职退休等竞争退出单列，不凭一次退出断定随后整个H都不会晋升。CPED部分结束月与下一任开始月有间隙：原先已审计的正向事件仍保留，但这些间隙不用于填补负向观察。所有正向事件有event_row和日期，旧已审计正向日期全部保留。
至少一次不等于首次观测事件肯定是生涯第一次晋升；有履历间隙时只称窗口内首个已观察到的晋升。日期按CPED原记录使用，部分记录集中在月初，日级真实性未另行独立核实。所有窗口截至2017年内，不使用不完整2018年作为完整随访。

## 回归及控制
100Y_i,s(H)=个人FE+时间FE+theta_H C0_i×Post_s+gamma_H X0_i×Post_s+误差。
三个时间FE版本：共同前后期；窗口结束日对应的实际日历年份；基期省×前后期。后者在该两期数据中等价于基期省×窗口结束年，不能冒称逐年追踪每一年内的结果。每个H只有一次前后差，不能做事前平行趋势联合检验，也不估计全省共同的巡视平均效应。
固定C0和固定基期X的单独项被个人FE吸收。个人/完整控制版本加入X0×Post，允许初始特征预测结果变化；这是额外条件趋势假设，不是声称不变X水平在个人FE中仍有系数。个人X含年龄及平方、当前职务任期及平方、职级、书记身份，不使用任期阶段×职务，不使用未来离任日期。完整版加基期官员任职城市上年GDP增长、对数人均GDP、对数人口并与Post交互；不使用晋升后的目的地经济数据。全部控制组合使用同一完整经济样本；FE-only基准也保留。

## 推断、核验与解释限制
省级聚类、95% t(G-1)逐点CI，不连线。36个控制模型和18个FE-only基准共54规格全部保留。独立Stata一阶差分OLS复核54个点估计；Python FWL与省级聚类协方差复核每个系数和标准误。面板SE使用reghdfe的实际有限样本校正，FD命令自己的有限样本校正不同，其SE不强行要求相等。主规格为共同名单、完整控制、省×前后FE，另用等价FD方程做省级Webb wild bootstrap，9999次，种子20261015。常规与wild原始p、三个H的Holm校正p并列。补充样本、FE和控制比较属于探索，不消除更早轮次规格搜索的不确定性。
负theta表示关系组的累计晋升差异在巡视后相对巡视前下降，不等于巡视后绝对关系差异为负，也不证明关系作用消失。原始分组均值也报告；不能忽略事前原始优势并非为正。
关键选择限制：锚点名单在12个月事前窗开始前形成，但处在24、36个月事前窗口内部。长窗前期部分晋升可能影响之后进入这个市级主官名单；个人FE和固定名单不能消除这种选择/均值回归。固定C0也可能因省委领导更替而失去实际政治支持。因此本轮只能作为该事前名单的条件前后关联，不能独立证明反腐或巡视因果削弱关系作用。

重跑：cumulative_twfe_prepare.py → cumulative_twfe_checks_prepare.py → cumulative_twfe_add_fe_only.py → cumulative_twfe_checks_prepare.py → Stata run_TWFE.do 和run_FD_validation.do → cumulative_twfe_report.py。本机绝对路径需保持/调整。原数据与网络未覆盖，无PDF。
'''
(O/'methods_中文.md').write_text(notes,encoding='utf8')
with pd.ExcelWriter(O/'累计晋升_12_24_36个月_TWFE全部结果.xlsx',engine='openpyxl') as w:
 for name,d in [('Main_full_PXY',mainR),('All_54_TWFE',R),('Main_wild',W),('Raw_group_rates',rates),('Sample_flow',F),('Observation_by_tie',retention),('Model_design',M),('First_difference',FD),('Python_validation',pd.DataFrame(independent)),('Inspection_dates',pd.read_csv(O/'inspection_dates_official_sources.csv')),('All_window_outcomes',AUD),('Positive_events',EV),('Validation',pd.DataFrame(checks))]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>Cumulative promotion TWFE</title><style>body{max-width:1600px;margin:auto;padding:25px;font:16px system-ui}img{width:100%}section{margin:40px 0}td,th{padding:6px;border-bottom:1px solid #ddd}</style><h1>累计晋升：12／24／36个月等长前后窗口TWFE</h1><p>同一422名官员、固定事前关系；24省聚类。报告全部54规格及原始组均值，不能将事后不显著视为等效。</p><p><a href="累计晋升_12_24_36个月_TWFE全部结果.xlsx">Excel</a> · <a href="methods_中文.md">方法与限制</a></p>'+mainR[['H','b','p','lo','hi','p_wild','p_holm_three_main_H','p_wild_holm_three_H']].to_html(index=False)
for name,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+name+'"></section>'
page+='<pre style="white-space:pre-wrap">'+html.escape(notes)+'</pre>'; (O/'index.html').write_text(page,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Four readable figures',len(gallery)==4);ck('No PDF generated',not list(O.rglob('*.pdf')));save(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks)
for name in ['cumulative_twfe_prepare.py','cumulative_twfe_checks_prepare.py','cumulative_twfe_add_fe_only.py','cumulative_twfe_report.py']:shutil.copy2(Path(__file__).with_name(name),O/'code'/name)
save(pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']),'file_manifest.csv')
archive=B/'累计晋升_TWFE_12_24_36个月_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(O))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('ALL CHECKS PASSED:',len(checks));print('MAIN:');print(mainR[['H','b','se','p','lo','hi','p_wild','p_holm_three_main_H','p_wild_holm_three_H']].to_string(index=False));print('FE-ONLY:');print(R[R['sample'].eq('common_all_H')&R.control.eq('none')][['H','fe','b','p']].to_string(index=False));print('DELIVERED:',O)
