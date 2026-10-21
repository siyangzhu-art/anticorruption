from pathlib import Path
import sys,shutil,zipfile,html
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import t
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'province_year_vs_city_year_audit'
assert 'closed on:' in (O/'estimation.log').read_text(errors='replace')[-900:]
M=pd.read_csv(O/'model_design.csv');R=pd.read_stata(O/'results.dta').merge(M,on='model_id',validate='m:1');S=pd.read_stata(O/'model_stats.dta').merge(M,on='model_id',validate='m:1');J=pd.read_stata(O/'joint_tests.dta').merge(M,on='model_id',validate='m:1');F=pd.read_stata(O/'failures.dta');A=pd.read_stata(O/'all_parameters.dta').merge(M,on='model_id',validate='m:1');C=pd.read_csv(O/'sample_comparison.csv');I=pd.read_csv(O/'identification_rank.csv');U=pd.read_csv(O/'event_time_support.csv');Checks=[]
def ck(n,v,detail=''):Checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
def save(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')
ck('24 estimations completed',len(S)==24,len(S));ck('No estimation failures',len(F)==0);ck('216 contrasts saved',len(R)==216,len(R));ck('Expected sample retained by every fit',S.N.eq(S.N_expected).all());ck('All target design matrices full rank',I.targets.eq(I.target_rank).all());ck('Every event coefficient has positive standard error',R.se.gt(1e-8).all());ck('All finite estimates',np.isfinite(R[['b','se','p','lo','hi']]).all().all())
errors=[]
for mid,m in M.iterrows():
 a=pd.read_csv(O/f'data/independent_points_{m.model_id}.csv');b=R[(R.model_id==m.model_id)&R.estimator.str.startswith('TWFE')].merge(a,on='term',suffixes=('_stata','_python'))
 err=float(np.abs(b.b_stata-b.b_python).max());errors.append(dict(model_id=m.model_id,max_point_difference=err));ck(f'Independent FWL coefficients model {m.model_id}',err<1e-6,err)
for sample in ['fixed','dynamic']:
 for est in (['TWFE_fixed','Sun_Abraham'] if sample=='fixed' else ['TWFE_dynamic']):
  for fe,comp in [('I_CXY','common'),('I_PXY','common')]:
   d=R[(R['sample']==sample)&(R.estimator==est)&(R.fe==fe)&(R.comparison==comp)]
   if fe=='I_CXY':
    z=d.pivot(index='term',columns='control',values='b');delta=float(abs(z.personal-z.full).max());ck(f'GDP controls absorbed {sample} {est}',delta<1e-6,delta)
 for control in ['personal','full']:
  d=R[(R['sample']==sample)&(R.fe=='I_CXY')&(R.control==control)]
  z=d.pivot(index=['estimator','term'],columns='comparison',values='b');ck(f'CXY own maximum equals common {sample} {control}',np.allclose(z.CXY_max,z.common,atol=1e-8))
econ=A[A.fe.eq('I_CXY')&A.control.eq('full')&A.term.isin(['gdp_growth_lag','lngdppc_lag','lnpop_lag','o.gdp_growth_lag','o.lngdppc_lag','o.lnpop_lag'])]
ck('City-year absorbs all reported GDP control coefficients',len(econ)==12 and econ.se.eq(0).all(),len(econ))
for sample in ['fixed','dynamic']:
 a=pd.read_stata(O/f'data/{sample}_common.dta');g=a.groupby('cy')
 ck(f'Common sample exactly two officials in every city-year {sample}',g.size().eq(2).all());ck(f'No duplicate person-year {sample}',not a.duplicated(['person_id','year']).any());ck(f'Both FE common regressions have same N {sample}',S[(S['sample']==sample)&S.comparison.eq('common')].N.eq(len(a)).all())
 ck(f'All three economics constant within city-year {sample}',all(g[e].agg(lambda x:x.max()-x.min()).max()<1e-10 for e in ['gdp_growth_lag','lngdppc_lag','lnpop_lag']))
save(R,'all_coefficients.csv');save(S,'all_model_stats.csv');save(J,'all_joint_tests.csv');save(A,'all_parameters.csv');save(F,'estimation_failures.csv');save(pd.DataFrame(errors),'independent_point_checks.csv');save(pd.DataFrame(Checks),'validation_checks.csv');assert all(x['passed'] for x in Checks)

avg=R[R.control.eq('full')&R.term.eq('post_average')].copy();save(avg,'four_post_year_average.csv')
print('ALL-CONTROL AVERAGES:');print(avg[['sample','comparison','fe','estimator','b','se','p','lo','hi']].to_string(index=False));print('SUPPORT:');print(U[U.stage.eq('CXY_max_common')].to_string(index=False));print('All checks passed:',len(Checks))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
types=[('TWFE_dynamic','Dynamic annual connection'),('TWFE_fixed','Fixed pre-inspection connection'),('Sun_Abraham','Sun-Abraham | Fixed pre-inspection connection')]
versions=[('PXY_max','I_PXY','#909090','s',-.16,'Individual + province-year | maximum sample'),('common','I_PXY','#247da3','o',0,'Individual + province-year | common sample'),('common','I_CXY','#d0872c','^',.16,'Individual + city-year | common sample')]
fig,axs=plt.subplots(1,3,figsize=(18,6.5))
for ax,(est,title) in zip(axs,types):
 for comp,fe,color,marker,off,label in versions:
  d=R[R.estimator.eq(est)&R.control.eq('full')&R.comparison.eq(comp)&R.fe.eq(fe)&R.term.str.startswith('d_')].copy();d['k']=d.term.map(lambda n:-int(n[3:]) if n.startswith('d_m') else int(n[3:]));d=d.sort_values('k')
  ax.errorbar(d.k+off,d.b,yerr=np.vstack([d.b-d.lo,d.hi-d.b]),fmt=marker,linestyle='none',color=color,capsize=3,markersize=4,label=label)
  ax.scatter([-1+off],[0],facecolors='white',edgecolors=color,marker=marker,s=25,zorder=4)
 ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b39250',ls=':',lw=1);ax.set_xticks(range(-4,5));ax.set_xlabel('Years relative to first inspection');ax.set_title(title,fontsize=11);ax.grid(axis='y',alpha=.15)
axs[0].set_ylabel('Change in connection-related promotion gap (pp)');hh,ll=axs[0].get_legend_handles_labels();fig.legend(hh,ll,loc='lower center',bbox_to_anchor=(.5,.105),ncol=1,frameon=False,fontsize=9)
fig.suptitle('Province-year versus city-year fixed effects\nIndividual FE; personal controls; 95% province-clustered t intervals',fontsize=16)
fig.subplots_adjust(left=.055,right=.985,bottom=.32,top=.81,wspace=.25)
fig.text(.055,.035,'Full-control specifications shown. City-year FE absorb GDP growth, log GDP per capita and log population.\nReference k=-1 has no estimated CI. Points are not connected. Fixed group: N=2,808 to 1,802; dynamic group: N=4,113 to 3,532.\nThese are conditional differential associations. Risk-set composition and thin support at k=+4 remain limitations.',fontsize=9)
fig.savefig(O/'figures/01_FE_comparison_same_and_maximum_samples.png',dpi=190);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,4.8))
for ax,sample,title in zip(axs,['dynamic','fixed'],['Dynamic annual connection','Fixed pre-inspection connection']):
 d=C[C['sample'].eq(sample)&C.stage.isin(['PXY_max','CXY_max_common'])];ax.bar(['Province-year','City-year'],d.N,color=['#247da3','#d0872c'],width=.5)
 for i,(_,r) in enumerate(d.iterrows()):ax.text(i,r.N+45,f'N={int(r.N):,}\n{int(r.people):,} officials',ha='center')
 ax.set_ylim(0,d.N.max()*1.22);ax.set_title(title);ax.set_ylabel('Officer-year observations');ax.grid(axis='y',alpha=.15)
fig.suptitle('Sample retained after recursive singleton removal');fig.tight_layout();fig.savefig(O/'figures/02_sample_retention.png',dpi=170);plt.close(fig)

methods='''# 省份×年份与城市×年份固定效应核验

本轮不改变晋升、关系、巡视日期定义。年度观察期2006—2017；事件窗[-4,+4]，-1为参照。分别核验动态关系C_it及固定事前关系C0；固定关系另报Sun–Abraham。不是将city+year误写为city×year。

模型含个人FE和省份×年份FE，或个人FE和城市×年份FE；后者嵌套前者，无须重复加入省份×年份。均含年龄平方、职务任期及平方、基期职级、当期书记职务指示；full版另加按官员当期所在城市匹配的上年GDP增长、对数人均GDP、对数人口。城市×年份会完全吸收这三个经济控制。所有规格起点使用经济控制完整样本，personal/full比较不改变样本。

分别保存各FE的最大可用样本，以及二者共同样本。单例按个人和对应FE单元反复剔除到收敛。更严格的城市×年份样本是共同样本。不能将被剔除行的晋升补0。

个人+城市×年份比较同城同年市长与书记，并结合个人跨年变化；剩余样本每个城市年恰好两名主官。相同connection的城市年也可帮助估计控制、个人效应等；不能把“有关系差异的配对数量”说成全模型的唯一有效样本量。关系不同只是直接组内关系变化的一个可解释诊断；最终检查在吸收全部FE和控制后，目标设计矩阵是否满秩。满秩只证明可估计，不证明外生性或因果识别。

标准误沿用按省聚类，95% t(G-1)区间。保存全部24个模型，不依显著性取舍；本轮没有新做wild bootstrap或多重检验校正。Sun–Abraham仍以事前无关系组作为差异暴露比较组，不是从未巡视省份；动态风险集与事后薄样本问题仍在。

固定关系输入已沿用此前经济完整及个人/省年单例处理的2808条；动态输入4364条，省年单例后4113条。报告的是这一既有事件窗、既有定义和经济覆盖范围内的最大可用样本，并非CPED原始库所有记录。

重跑顺序：运行code/test_city_year_FE.py；Stata18执行code/run_audit.do；运行code/report_city_year_FE.py。Python脚本依赖此前保存的项目输入和已验证FE helper；后者随包保存在code。Stata需reghdfe与eventstudyinteract。全部结果仅为条件关联，不以事后不显著声称关系消失。
'''
(O/'methods_中文.md').write_text(methods,encoding='utf8')
with pd.ExcelWriter(O/'prov_year_city_year_核验与结果.xlsx',engine='openpyxl') as w:
 for name,d in [('sample_comparison',C),('model_design',M),('all_coefficients',R),('all_model_stats',S),('joint_tests',J),('four_post_average',avg),('event_support',U),('identification_rank',I),('parameters',A),('validation',pd.DataFrame(Checks))]:d.to_excel(w,sheet_name=name,index=False)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
shutil.copy2(Path(__file__).with_name('event_study_individual_FE.py'),O/'code/event_study_individual_FE.py')
doc='<meta charset="utf-8"><title>Province-year vs city-year audit</title><style>body{font:16px Arial;max-width:1500px;margin:30px auto}img{width:100%}td,th{padding:6px;border-bottom:1px solid #ddd}</style><h1>Province-year vs city-year FE</h1><p>All specifications retained; 95% province-clustered confidence intervals.</p>'+C.to_html(index=False)+'<img src="figures/01_FE_comparison_same_and_maximum_samples.png"><img src="figures/02_sample_retention.png">'+avg[['sample','comparison','fe','estimator','b','p','lo','hi']].to_html(index=False)+'<pre>'+html.escape(methods)+'</pre>'
(O/'index.html').write_text(doc,encoding='utf8')
z=B/'prov_year_city_year_样本识别核验_图表代码.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as f:
 for p in O.rglob('*'):
  if p.is_file():f.write(p,p.relative_to(O))
with zipfile.ZipFile(z) as f:assert f.testzip() is None
print('Deliverables ready:',O)
