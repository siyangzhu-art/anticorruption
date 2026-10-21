from pathlib import Path
import sys,shutil,json,hashlib,zipfile
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'sun_abraham_fixed_connection_post4'
assert 'log close' in (O/'sun_abraham.log').read_text(encoding='utf8',errors='replace')[-400:]
R=pd.read_stata(O/'coefficients.dta');V=pd.read_stata(O/'covariances.dta');W=pd.read_stata(O/'weights.dta');C=pd.read_stata(O/'cohort_coefficients.dta');M=pd.read_stata(O/'models.dta');J=pd.read_stata(O/'joint_tests.dta');D=pd.read_csv(O/'analysis_panel.csv.gz');S=pd.read_csv(O/'event_support.csv');P=pd.read_csv(O/'python_cohort_point_estimates.csv')
def kt(term):return -int(term[3:]) if term.startswith('d_m') else (int(term[3:]) if term.startswith('d_p') else np.nan)
for q in [R,W,C]:q['k']=q.term.map(kt)
labels={1:'Individual + year FE',2:'Individual + province-by-year FE'}
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
ck('Analysis person-year unique',not D.duplicated(['person_id','year']).any())
ck('Fixed C0 and province and G0 per person',all(D.groupby('person_id')[x].nunique().eq(1).all() for x in ['C0','anchor_province','G0']))
ck('All four fits use identical N',M.N.eq(len(D)).all())
ck('All estimates and intervals finite',np.isfinite(R[['b','se','p','lo','hi']]).all().all())
ck('26 province clusters',M.G.eq(26).all())
ck('Cohort weights sum to one',np.allclose(W.groupby(['model_id','term']).weight.sum(),1,atol=1e-10))
ck('Cohort weights nonnegative',W.weight.ge(-1e-10).all())
Q=C.merge(W,on=['model_id','cohort','term','k'],validate='1:1');Q['wb']=Q.b*Q.weight
agg=Q.groupby(['model_id','term']).wb.sum().reset_index().merge(R[R.method.eq('Sun_Abraham')],on=['model_id','term'],validate='1:1')
ck('IW point estimates equal cohort weighted averages',np.allclose(agg.wb,agg.b,atol=1e-8))
QC=C.merge(P,on=['model_id','cohort','k'],suffixes=('_stata','_python'),validate='1:1')
ck('All 30 supported cohort coefficients independently reproduced',len(QC)==30 and np.allclose(QC.b_stata,QC.b_python,atol=2e-6,rtol=2e-6),abs(QC.b_stata-QC.b_python).max())
expected=S[S.C0.eq(1)].copy();expected['expected_weight']=expected.N/expected.groupby('k').N.transform('sum')
QW=W.merge(expected[['G0','k','expected_weight']],left_on=['cohort','k'],right_on=['G0','k'],how='left')
ck('Weights equal observed treated-cohort shares',np.allclose(QW.weight,QW.expected_weight.fillna(0),atol=1e-10))
ck('Fourth post year supported by 2013 only',W[W.k.eq(4)&W.cohort.eq(2013)].weight.eq(1).all() and W[W.k.eq(4)&W.cohort.eq(2014)].weight.abs().lt(1e-10).all())
ck('Only 4 connected officer-years at +4',S[S.C0.eq(1)&S.k.eq(4)].N.sum()==4)
for (mid,method),vv in V.groupby(['model_id','method']):
 A=vv.pivot(index='term1',columns='term2',values='value');ck('VCV symmetric PSD '+str(mid)+method,np.allclose(A,A.T,atol=1e-10) and np.linalg.eigvalsh(A).min()>-1e-8)
 a=R[R.model_id.eq(mid)&R.method.eq(method)&R.term.eq('post_average')].iloc[0];ns=['d_p1','d_p2','d_p3','d_p4'];ck('Average uses full VCV '+str(mid)+method,np.isclose(a.se,np.sqrt(A.loc[ns,ns].to_numpy().sum()/16),atol=1e-8))
assert all(c['passed'] for c in checks),checks
for name,q in [('coefficients',R),('covariances',V),('weights',W),('cohort_coefficients',C),('models',M),('joint_tests',J),('cohort_validation',QC)]:q.to_csv(O/(name+'.csv'),index=False,encoding='utf-8-sig')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
def plot(compare=False):
 fig,axes=plt.subplots(1,2,figsize=(15,8),sharey=True)
 for ax,mid in zip(axes,[1,2]):
  methods=['Sun_Abraham','TWFE_fixed'] if compare else ['Sun_Abraham']
  for i,method in enumerate(methods):
   q=R[R.model_id.eq(mid)&R.method.eq(method)&R.k.notna()].sort_values('k');off=(i-.5)*.13 if compare else 0
   ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s'][i],ls='none',capsize=4,ms=5,color=['#287c9e','#ce8735'][i],label=['Sun-Abraham IW','TWFE: same fixed group and sample'][i])
   ax.plot(-1+off,0,marker=['o','s'][i],ls='none',mfc='white',mec=['#287c9e','#ce8735'][i],ms=6)
  ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b28b39',ls=':',lw=1);ax.set_xticks(range(-4,5));ax.set_xlim(-4.4,4.4);ax.set_xlabel('Years relative to first inspection');ax.set_title(labels[mid],fontsize=12);ax.grid(axis='y',alpha=.15)
  jj=J[J.model_id.eq(mid)&J.method.eq('Sun_Abraham')&J.test.eq('pretrend')].iloc[0];aa=R[R.model_id.eq(mid)&R.method.eq('Sun_Abraham')&R.term.eq('post_average')].iloc[0]
  ax.text(.02,.97,f'Pretrend p={jj.p:.3f}\nAverage +1 to +4: {aa.b:+.2f} pp (p={aa.p:.3f})',va='top',transform=ax.transAxes,fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
 axes[0].set_ylabel('Change in promotion gap relative to k=-1 (pp)')
 title='Sun-Abraham: fixed pre-inspection connections' if not compare else 'Sun-Abraham versus TWFE on the same fixed-group sample'
 fig.suptitle(title+'\nFour complete post years | 95% province-clustered CIs',fontsize=17,y=.97)
 if compare:fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False,fontsize=10)
 fig.subplots_adjust(left=.075,right=.98,top=.77 if compare else .80,bottom=.26,wspace=.12)
 fig.text(.06,.045,'C0 fixed from the k=-1 record; 68 connected and 556 comparison officials. N=3,260 officer-years; 26 province clusters.\nBaseline-unconnected officials are the comparison group for differential network exposure; they also experienced inspection.\nCohort-specific effects aggregated with observed cohort shares. k=+4: 2013 cohort only, 4 connected observations.\nUnbalanced promotion risk set; t(25) pointwise CIs; no connecting lines. Reference has no estimated CI.',fontsize=9)
 fn='02_SA_TWFE_same_sample.png' if compare else '01_Sun_Abraham_four_post_years.png';fig.savefig(O/'figures'/fn,dpi=180,facecolor='white');plt.close(fig)
plot();plot(True)
methods='''# Sun–Abraham：事前固定关系与首次巡视后的晋升差距

## 实际软件
使用Liyang Sun官方eventstudyinteract（本机2022-01-24版），reghdfe 6.13.1。分别估计个人+年份FE、个人+省份×年份FE；省级聚类，95%区间采用t(25)。点估计和e(V_iw)由官方命令直接输出，e(V_iw)包含软件实现的cohort-share估计不确定性。没有把普通TWFE换个名称冒充Sun–Abraham。

## 固定分组与估计对象
当前年度C_it会因在任领导更替开关，不能直接充当Sun–Abraham的吸收型处理。构造C_i^0：巡视相对期k=-1那行的C_any，按省委书记/省长任一人事前至少六个月共事；未知不补0。注意年度行采用上年末快照：2013巡视批次取2012年行的2011-12-31关系，2014批次取2013年行的2012-12-31关系。并非直接取进驻日前一天的关系。
原k=-1名单655人：2013批次23有关系、232无关系、6未知；2014批次47有关系、327无关系、20未知。共26人关系未知不用于分组。其后回归完整性和singleton筛选留下624人，其中68名C0=1、556名C0=0，3260个人年、26省。
只保留这些事前名单官员的原籍任职省观测，固定G和省份；不补写离任后的晋升0，不将去向不明填0。巡视后新进入且事前名单没有的官员不纳入这个固定群体。年度结果仍是修订的总晋升口径，2006—2017可用来源，实际相对窗[-4,+4]。
赋值E_i=G_p给C0=1者，C0=0者在命令中作为control_cohort，即“事前无关系比较组”，不是从未受到巡视的官员。吸收型暴露为C0×1[t>=G_p]。估计的是巡视后事前有关系组相对事前无关系组的晋升变化；不是巡视对全部官员的总效应。

## 方程与聚合
Y_it=alpha_i+lambda_pt+sum_(g in {2013,2014}) sum_(k != -1) delta_gk C0_i 1[G_i=g]1[t-G_i=k]+X_it gamma+error。
个人+年份FE版改lambda_pt为lambda_t，并补入不与C0相乘的省巡视相对时间主项。控制同前：年龄平方、任期及平方、行政级别、当前主官角色。个人+时间FE吸收线性年龄和C0主项。
官方命令分别估计cohort×相对时间，再按该相对期实际有关系观测的批次占比聚合。不是把两批次系数直接简单平均；+4的2014权重为0，2013权重为1。其余权重和批次系数全部输出。-1归零且无估计CI。0保留，四个完整事后期指+1到+4。
个人FE模型与此前动态C回归的样本/处理定义不同，因此新增同C0同样本的普通TWFE作对照，用以区分分组变化和估计器变化。不得把新旧图差异全部归于Sun–Abraham。

## 复核和解释边界
30个有样本支持的批次×相对期点估计由Python独立稀疏FE回归复核；官方IW点估计与手工批次加权核对，检查权重/样本/协方差/平均线性组合。官员风险集非平衡，晋升退出/关系组的选择问题仍存在。官方帮助文件也明确原文理论首先针对平衡面板、无协变量情形，本软件允许非平衡/协变量不意味着所有额外识别假设已获验证。
两组都经历巡视；将C0=0作比较组，需要关于未受关系差异影响时两组差距走势的额外假设。不宣称C0=0真的从未受巡视，也不把相对差异变化叫做总巡视ATT。
本轮未做新的显著性窗口筛选，未追加wild bootstrap。+4只有4条有关系官员年，统计区间很宽，不据此宣称长期效应为零。

重跑：sun_abraham_post4.py → Stata code/run_sun_abraham.do → report_sun_abraham_post4.py。本机已装eventstudyinteract/reghdfe/ftools/avar；输入与包版本哈希列于input_manifest.csv。原网络和此前结果未覆盖。无PDF。

官方帮助：https://github.com/lsun20/EventStudyInteract/blob/main/eventstudyinteract.sthlp
原文：https://doi.org/10.1016/j.jeconom.2020.09.006
'''
(O/'methods_中文.md').write_text(methods,encoding='utf8')
with pd.ExcelWriter(O/'Sun_Abraham_事后四期_结果.xlsx',engine='openpyxl') as w:
 for name,q in [('Sun_Abraham',R[R.method.eq('Sun_Abraham')]),('All_coefficients',R),('Models',M),('Joint_tests',J),('Cohort_weights',W),('Cohort_coefficients',C),('Covariances',V),('Support',S),('Panel',D),('Validation',pd.DataFrame(checks))]:
  q.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Two readable figures',len(list((O/'figures').glob('*.png')))==2);ck('No PDF',not list(O.rglob('*.pdf')))
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig');assert all(x['passed'] for x in checks)
(O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Sun-Abraham四期</title><style>body{max-width:1500px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}</style><h1>Sun–Abraham：事前固定关系，事后四期</h1><p>官方eventstudyinteract，两种个人FE，同样本TWFE对照。两种FE的+1期显著负；四期平均变化不显著。+4仅4名有关系官员的观察。</p><p><a href="Sun_Abraham_事后四期_结果.xlsx">全部结果Excel</a> · <a href="methods_中文.md">方法与固定分组口径</a></p><img src="figures/01_Sun_Abraham_four_post_years.png"><img src="figures/02_SA_TWFE_same_sample.png">',encoding='utf8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']).to_csv(O/'file_manifest.csv',index=False)
archive=B/'Sun_Abraham_事后四期_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(R[R.method.eq('Sun_Abraham')][['model_id','term','b','p','lo','hi']].to_string(index=False));print('All checks pass',len(checks))
