from pathlib import Path
import sys,shutil,hashlib,json,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'event_study_window_sensitivity_post4'
assert 'log close' in (O/'validation.log').read_text(encoding='utf8',errors='replace')[-400:]
R=pd.read_csv(O/'coefficients.csv');J=pd.read_csv(O/'joint_tests.csv');M=pd.read_csv(O/'models.csv');S=pd.read_stata(O/'stata_validation.dta');SJ=pd.read_stata(O/'stata_joint.dta');support=pd.read_csv(O/'support.csv')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
Q=R[~R.reference].merge(S,on=['model_id','contrast'],suffixes=('_py','_st'),validate='1:1')
ck('All contrasts matched',len(Q)==len(R[~R.reference]))
for c in ['b','se','p','lo','hi','N','K','G','df']:ck('Stata comparison '+c,np.allclose(Q[c+'_py'],Q[c+'_st'],atol=2e-6,rtol=2e-6),abs(Q[c+'_py']-Q[c+'_st']).max())
QJ=J.merge(SJ,on=['model_id','test'],suffixes=('_py','_st'),validate='1:1')
for c in ['F','df_num','p']:ck('Stata joint comparison '+c,np.allclose(QJ[c+'_py'],QJ[c+'_st'],atol=2e-6,rtol=2e-6))
ck('All 24 bootstrap jobs completed',S.boot_rc.eq(0).sum()==12 and SJ.boot_rc.eq(0).sum()==12)
ck('Twelve models',len(M)==12)
ck('Identical FE comparison samples per window',M.groupby('L').N.nunique().eq(1).all())
ck('All four complete post years retained in every model',R[R.estimand.eq('change')&R.k.gt(0)].groupby('model_id').k.nunique().eq(4).all())
old=pd.read_csv(B/'event_study_individual_FE/event_coefficients_validated.csv')
for new,oldid in [(11,7),(12,8)]:
 q=R[R.model_id.eq(new)&R.estimand.eq('change')&~R.reference].merge(old[old.model_id.eq(oldid)&old.estimand.eq('change')],left_on='k',right_on='relative_year',suffixes=('_new','_old'))
 ck('Original full-sample coefficients reproduced '+str(new),np.allclose(q.b_new,q.b_old,atol=1e-7))
assert all(x['passed'] for x in checks),checks
R=R.merge(S[['model_id','contrast','p_wild','boot_rc']],on=['model_id','contrast'],how='left',validate='1:1');J=J.merge(SJ[['model_id','test','p_wild','boot_rc']],on=['model_id','test'],how='left',validate='1:1')
def holm(x):
 a=np.asarray(x);order=np.argsort(a);n=len(a);out=np.empty(n);out[order]=np.minimum(1,np.maximum.accumulate(a[order]*np.arange(n,0,-1)));return out
R['p_holm_family']=np.nan;R['p_wild_holm_family']=np.nan
for mask in [(R.estimand.eq('change')&R.k.between(1,4)),R.estimand.eq('post_change_1_4')]:
 R.loc[mask,'p_holm_family']=holm(R.loc[mask,'p'])
 if R.loc[mask,'p_wild'].notna().all():R.loc[mask,'p_wild_holm_family']=holm(R.loc[mask,'p_wild'])
mask=J.test.eq('post_joint_1_4');J.loc[mask,'p_holm_family']=holm(J.loc[mask,'p']);J.loc[mask,'p_wild_holm_family']=holm(J.loc[mask,'p_wild'])
R.to_csv(O/'coefficients_validated.csv',index=False,encoding='utf-8-sig');J.to_csv(O/'joint_tests_validated.csv',index=False,encoding='utf-8-sig')
criteria=[]
for m in M.itertuples():
 q=R[R.model_id.eq(m.model_id)&R.estimand.eq('change')&R.k.between(1,4)]
 avg=R[R.model_id.eq(m.model_id)&R.estimand.eq('post_change_1_4')].iloc[0];jj=J[J.model_id.eq(m.model_id)&J.test.eq('post_joint_1_4')].iloc[0]
 criteria.append(dict(model_id=m.model_id,window=m.window,fe=m.fe,N=m.N,negative_periods=int(q.b.lt(0).sum()),negative_sig5_periods=int((q.b.lt(0)&q.p.lt(.05)).sum()),negative_sig10_periods=int((q.b.lt(0)&q.p.lt(.1)).sum()),all4_negative=bool(q.b.lt(0).all()),all4_negative_sig5=bool((q.b.lt(0)&q.p.lt(.05)).all()),all4_negative_sig10=bool((q.b.lt(0)&q.p.lt(.1)).all()),average_change=avg.b,average_lo=avg.lo,average_hi=avg.hi,average_p=avg.p,average_wild_p=avg.p_wild,average_holm_p=avg.p_holm_family,joint_p=jj.p,joint_wild_p=jj.p_wild,joint_holm_p=jj.p_holm_family))
C=pd.DataFrame(criteria);C.to_csv(O/'stability_diagnostics.csv',index=False,encoding='utf-8-sig')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
colors={'I_YEAR':'#287c9e','I_PXY':'#cc8737'};labels={'I_YEAR':'Individual + year FE','I_PXY':'Individual + province-by-year FE'}
gallery=[]
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=170,facecolor='white');plt.close(fig);gallery.append((name,title))
def pstr(p):return '<0.001' if p<.001 else f'{p:.3f}'
fig,axes=plt.subplots(3,2,figsize=(16,14),sharex=True,sharey=True)
for ax,L in zip(axes.flat,range(3,9)):
 for j,fe in enumerate(colors):
  q=R[R.L.eq(L)&R.fe.eq(fe)&R.estimand.eq('change')&R.k.ge(-4)&~R.reference]
  ax.errorbar(q.k+(j-.5)*.13,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s'][j],ls='none',ms=4,capsize=3,color=colors[fe],label=labels[fe])
  ax.plot(-1+(j-.5)*.13,0,marker=['o','s'][j],ls='none',mfc='white',mec=colors[fe],ms=5)
 ax.axhline(0,color='gray',ls='--',lw=.8);ax.axvline(0,color='#a98c4a',ls=':',lw=.8);ax.grid(axis='y',alpha=.14)
 ax.set_title(f'Estimation window: [-{L}, +4] | N={int(M[M.L.eq(L)].N.iloc[0]):,}')
 ax.set_xticks(range(-4,5));ax.set_xlim(-4.4,4.4)
for ax in axes[-1]:ax.set_xlabel('Years relative to first inspection')
for ax in axes[:,0]:ax.set_ylabel('Change in connection-related promotion gap (pp)')
axes[0,0].legend(fontsize=9,loc='lower left')
fig.suptitle('Window sensitivity: four complete post-inspection years\nPersonal controls fixed | Reference k=-1 | 95% province-clustered CIs',fontsize=17,y=.985)
fig.subplots_adjust(top=.91,bottom=.12,hspace=.25,wspace=.10)
fig.text(.07,.025,'All six estimation windows shown; pre-period display truncated at -4. Each window is re-estimated, not a display crop.\nSame observations across the two FE specifications within each window. Linear age absorbed by individual + time FE.\nk=+4 has only the 2013 inspection cohort (10 provinces); other post periods include both cohorts.\nPointwise CR1 t(26) CIs; no connecting lines. Dynamic connections: conditional associations, not causal inspection effects.',fontsize=9)
export(fig,'01_all_windows_event_studies.png','All six estimation windows, both FE specifications')

fig,axes=plt.subplots(2,2,figsize=(14,10),sharex=True,sharey=True)
for ax,k in zip(axes.flat,range(1,5)):
 for j,fe in enumerate(colors):
  q=R[R.fe.eq(fe)&R.estimand.eq('change')&R.k.eq(k)].sort_values('L')
  y=np.arange(6)+(j-.5)*.18
  ax.errorbar(q.b,y,xerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s'][j],ls='none',capsize=3,color=colors[fe],label=labels[fe])
 ax.axvline(0,color='gray',ls='--',lw=.8);ax.set_yticks(range(6),[f'[-{L}, +4]' for L in range(3,9)]);ax.set_ylim(5.5,-.5);ax.grid(axis='x',alpha=.15);ax.set_title(f'Post-inspection year k=+{k}')
fig.legend(*axes[0,0].get_legend_handles_labels(),fontsize=9,loc='upper center',bbox_to_anchor=(.5,.915),ncol=2,frameon=False)
for ax in axes[-1]:ax.set_xlabel('Change relative to k=-1 (pp)')
fig.suptitle('Post-period stability across all estimation windows\n95% province-clustered CIs',fontsize=16)
fig.subplots_adjust(top=.82,bottom=.14,hspace=.28,wspace=.10)
fig.text(.07,.025,'All windows and both FE specifications retained. No four-period run of significant negative estimates.\nk=+4: 2013 inspection cohort only. Pointwise intervals, unadjusted for window search; Holm p-values in workbook.',fontsize=9)
export(fig,'02_four_post_periods_window_stability.png','Each of four post periods across all windows')

fig,axes=plt.subplots(1,2,figsize=(14,7),sharey=True)
for ax,est,title in zip(axes,['post_change_1_4','late_change_2_4'],['Average change: k=+1 to +4','Later average: k=+2 to +4']):
 for j,fe in enumerate(colors):
  q=R[R.fe.eq(fe)&R.estimand.eq(est)].sort_values('L');yy=np.arange(6)+(j-.5)*.18
  ax.errorbar(q.b,yy,xerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s'][j],ls='none',capsize=4,color=colors[fe],label=labels[fe])
 ax.axvline(0,color='gray',ls='--',lw=.8);ax.set_yticks(range(6),[f'[-{L}, +4]' for L in range(3,9)]);ax.set_ylim(5.5,-.5);ax.set_title(title);ax.set_xlabel('Average change relative to k=-1 (pp)');ax.grid(axis='x',alpha=.15)
axes[0].legend(fontsize=8,loc='lower left');fig.suptitle('Average post-inspection changes across all windows\nContrasts use full coefficient covariance | 95% CIs',fontsize=16)
fig.subplots_adjust(top=.83,bottom=.21,wspace=.15)
fig.text(.07,.04,'All average-change intervals include zero. A significant joint test can reflect variation across periods, without a significant mean decline.\nFour-year averages exclude the partial inspection year k=0. Full tables include k=0 to +4 and pre/post level differences.\nWebb wild bootstrap: 9,999 repetitions; seed 20261015. Province clustering; no connecting lines.',fontsize=9)
export(fig,'03_average_post_changes_all_windows.png','Average post changes across all windows')

method='''# 事后至少四期的窗口敏感性分析

沿用修订年度晋升指标、2006—2017 CPED官员面板、年度动态C_any（与在任省委书记/省长至少一人有事前六个月共事关系），不分Xi。个人关系边不删除，年度在任领导变化可改变暴露。源文件未修改。

本轮六个实际回归窗口：[-3,+4]、[-4,+4]、[-5,+4]、[-6,+4]、[-7,+4]、[-8,+4]。每窗分别个人+年份FE及个人+省×年FE，共12个规格。每个窗口均实际重新估计，与此前裁图不同。控制保持年龄平方、任期及平方、行政级别、当前书记/市长身份，不按显著性改变控制。个人+时间FE吸收线性年龄。省×年FE吸收巡视事件主项；个人+年FE加入事件主项。

共同完整样本在每窗口递归删除个人和省×年singleton，并使两种FE使用相同观测。-1为参照，没有估计CI。全部事前期保留在回归中，主图只显示最近四期。因变量为100×当年晋升0/1，系数单位为百分点。

四个完整事后期指+1,+2,+3,+4，0为进驻年，另报0到+4的结果。首次巡视仅2013、2014批次：+4只有2013批次的10省，其他事后期两批次都有。无法从此数据识别两批次都覆盖的+4，也没有+5；不外推或补齐。各期风险集发生变化，不是固定官员全程平衡样本。

报告逐期系数、条件关系水平、平均变化(+1..+4)、晚期平均(+2..+4)、事后0..+4平均、事前/事后水平差。所有线性组合使用完整协方差。报告事前联合检验、事后0..4/1..4/2..4联合检验。联合拒绝所有系数为0，不等于每期负显著，也不等于平均负显著。

27省聚类CR1与t(26)逐点95%CI。全部12规格的+1..+4平均变化及联合检验做省级Webb wild bootstrap9999次，种子20261015。Holm校正分别覆盖48个事后逐期检验、12个平均变化检验、12个事后联合检验；后两者另报wild p的Holm校正。窗口高度重叠，不能将12个规格当作12次独立复现。

Python稀疏FE投影沿用上轮已验证函数，本轮全部非参照线性组合和联合检验再由Stata18 areg/lincom/test独立复核。完整[-8,+4]两规格与前轮原结果核对。boottest失败不会默认为成功。

结果：个人+年FE六窗口均为+1、+3负且原始p<.05；+2略正、+4接近0。个人+省×年FE的+1仅部分窗在10%显著，+3全部不显著，+2/+4不显著。没有窗口满足四期全部负显著，亦无+1..+4平均下降在常规5%水平显著。不能宣布连续四期稳定下降，更不能据此证明关系失效。窗口检索为探索性，原始p值不能视作预先指定检验的确认性证据。数据不支持目标形态时如实报告，不丢弃不符合的窗口。

重跑：window_post4.py → Stata validate.do → report_post4.py。当前脚本路径本机配置，移机调整BASE及依赖路径。代码与源文件SHA256随包交付，无PDF。
'''
(O/'methods_中文.md').write_text(method,encoding='utf8')
with pd.ExcelWriter(O/'事后四期_全部窗口结果.xlsx',engine='openpyxl') as w:
 for name,d in [('Stability',C),('All_coefficients',R),('Joint_tests',J),('Models',M),('Event_support',support),('Validation',pd.DataFrame(checks)),('Failed_models',pd.read_csv(O/'failures.csv'))]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>事后四期：窗口敏感性</title><style>body{max-width:1500px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}section{margin:35px 0}</style><h1>六个窗口 × 两种个人固定效应</h1><p>每个窗口重新估计并保留全部结果。未发现+1至+4四期持续负显著，也没有显著的四年平均下降。+4只有2013批次支持；联合显著不等于平均下降显著。</p><p><a href="事后四期_全部窗口结果.xlsx">全部结果Excel</a> · <a href="methods_中文.md">方法说明</a></p>'
for fn,title in gallery:page+='<section><h2>'+html.escape(title)+'</h2><img src="figures/'+fn+'"></section>'
(O/'index.html').write_text(page,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Three figures readable',len(gallery)==3);ck('No PDF',not list(O.rglob('*.pdf')))
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig');assert all(x['passed'] for x in checks)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']).to_csv(O/'file_manifest.csv',index=False)
with zipfile.ZipFile(B/'事后四期_全部窗口_数据图表代码.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,O.name+'/'+p.relative_to(O).as_posix())
print(C.to_string(index=False));print('validated contrasts',len(Q),'joint tests',len(QJ),'checks',len(checks),'all pass')
