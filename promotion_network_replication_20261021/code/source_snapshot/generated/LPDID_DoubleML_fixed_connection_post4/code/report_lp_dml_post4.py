from pathlib import Path
import sys,json,shutil,hashlib,zipfile
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t,f
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'LPDID_DoubleML_fixed_connection_post4'
assert 'log close' in (O/'lpdid.log').read_text(encoding='utf8',errors='replace')[-400:]
LP=pd.read_stata(O/'lpdid_results.dta');DML=pd.read_csv(O/'doubleml_results.csv');Q=pd.read_csv(O/'horizon_pairs.csv.gz');MP=pd.read_csv(O/'python_LPDID_RA_points.csv');FOLD=pd.read_csv(O/'province_fold_assignments.csv');PR=pd.read_csv(O/'doubleml_predictions_scores.csv.gz');REPS=pd.read_csv(O/'doubleml_repetitions.csv')
for col in ['b','se','stat','p','lo','hi','N']:LP[col]=LP[col].astype('float64')
LP['h']=LP.term.map(lambda s:-int(s[3:]) if s.startswith('pre') else int(s[3:]));LP['reference']=LP.h.eq(-1)
LP=LP.merge(MP,on=['spec','h'],how='left',suffixes=('','_python'),validate='1:1')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
ck('Sixteen LP-DiD point estimates independently reproduced',np.allclose(LP.loc[~LP.reference,'b'],LP.loc[~LP.reference,'b_python'],atol=2e-6,rtol=2e-6))
ck('LP-DiD pair counts match manual construction',np.allclose(LP.loc[~LP.reference,'N'],LP.loc[~LP.reference,'N_python']))
LP['p_normal']=LP.p;LP['lo_normal']=LP.lo;LP['hi_normal']=LP.hi
for idx,r in LP[~LP.reference].iterrows():
 df=r.provinces-1;crit=t.ppf(.975,df)
 LP.loc[idx,['p','lo','hi','df']]=[2*t.sf(abs(r.b/r.se),df),r.b-crit*r.se,r.b+crit*r.se,df]
LP['method']='LPDID_RA';LP['variant']=LP.spec
DML['variant']=DML.learner
cscores=[]
for r in LP[~LP.reference].itertuples():
 q=Q[Q.h.eq(r.h)].copy();cat='anchor_province' if r.spec=='province' else 'G0'
 z=np.column_stack([np.ones(len(q)),q[['base_age','base_age2','base_tenure','base_tenure2','base_role']].to_numpy(),pd.get_dummies(q.base_rank0,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q[cat],drop_first=True,dtype=float).to_numpy()]);norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0]
 treated=q.C0.eq(1).to_numpy();bb=lstsq(z[~treated],q.deltaY.to_numpy()[~treated],cond=1e-10)[0];u=q.deltaY.to_numpy()-z@bb;theta=u[treated].mean();score=np.zeros(len(q));score[treated]=(u[treated]-theta)/treated.sum();score[~treated]=-u[~treated]*(z[~treated]@np.linalg.pinv(z[~treated].T@z[~treated],rcond=1e-10)@z[treated].mean(axis=0));cs=pd.Series(score).groupby(q.anchor_province.to_numpy()).sum()
 ck('LP-DiD influence SE '+r.spec+str(r.h),np.isclose(np.sqrt((cs**2).sum()),r.se,atol=3e-6,rtol=3e-6))
 for province,s in cs.items():cscores.append(dict(spec=r.spec,h=r.h,province=province,score=s))
CS=pd.DataFrame(cscores);avg=[];joint=[]
for spec in ['cohort','province']:
 c=CS[CS.spec.eq(spec)].pivot(index='province',columns='h',values='score').fillna(0);vv=c.T@c
 for name,hs in [('pretrend',[-4,-3,-2]),('post_joint',[1,2,3,4])]:
  b=LP[LP.spec.eq(spec)].set_index('h').loc[hs,'b'].to_numpy();V=vv.loc[hs,hs].to_numpy();rr=np.linalg.matrix_rank(V);ff=b@np.linalg.pinv(V)@b/rr;df=int(LP[LP.spec.eq(spec)&LP.h.isin(hs)].provinces.min()-1);joint.append(dict(spec=spec,test=name,F=ff,df_num=rr,df_den=df,p=f.sf(ff,rr,df)))
 hs=[1,2,3,4];b=float(LP[LP.spec.eq(spec)&LP.h.isin(hs)].b.mean());se=float(np.sqrt(vv.loc[hs,hs].to_numpy().sum()/16));df=int(LP[LP.spec.eq(spec)&LP.h.isin(hs)].provinces.min()-1);crit=t.ppf(.975,df);avg.append(dict(spec=spec,b=b,se=se,p=2*t.sf(abs(b/se),df),lo=b-crit*se,hi=b+crit*se,df=df,estimand='unweighted mean of horizon-specific ATT; changing risk sets'))
pd.DataFrame(avg).to_csv(O/'LPDID_four_period_average.csv',index=False);pd.DataFrame(joint).to_csv(O/'LPDID_joint_tests.csv',index=False);CS.to_csv(O/'LPDID_cluster_influence.csv',index=False)
ck('All sixteen DoubleML fits completed',len(DML)==16 and len(pd.read_csv(O/'doubleml_failures.csv'))==0)
ck('All DML estimates finite',np.isfinite(DML[['b','se','lo','hi','p']]).all().all())
ck('Province held out as whole clusters',FOLD.groupby(['h','rep','province']).fold.nunique().eq(1).all())
ck('Each officer has exactly one validation fold per repetition',not FOLD.duplicated(['h','rep','person_id']).any())
ck('Five repetitions retained for every model',REPS.groupby(['h','learner']).rep.nunique().eq(5).all())
ck('All propensity scores clipped within preset bounds',PR.m_hat.between(.01-.0000001,.99+.0000001).all())
ck('All out-of-fold outcome predictions finite',np.isfinite(PR.g0_hat).all())
for h in [-4,-3,-2,0,1,2,3,4]:
 q=Q[Q.h.eq(h)];d=DML[DML.h.eq(h)];ck('Horizon sample '+str(h),d.N.eq(len(q)).all() and d.treated.eq(q.C0.sum()).all())
ck('Fourth horizon contains 4 connected and 44 comparison officials',DML[DML.h.eq(4)].treated.eq(4).all() and DML[DML.h.eq(4)].controls.eq(44).all())
ck('Outcome gaps not set to zero',pd.read_csv(O/'lpdid_panel.csv.gz').Y.isna().any())
assert all(c['passed'] for c in checks),checks
LP.to_csv(O/'LPDID_results_validated.csv',index=False,encoding='utf-8-sig');DML.to_csv(O/'DoubleML_results_validated.csv',index=False,encoding='utf-8-sig')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
COL=['#287c9e','#cf8735'];ms=['o','s'];gallery=[]
def export(fig,name,title):fig.savefig(O/'figures'/name,dpi=180,facecolor='white');plt.close(fig);gallery.append((name,title))
def draw(postonly=False):
 fig,axes=plt.subplots(1,2,figsize=(15.5,8),sharey=True)
 for j,(spec,label) in enumerate([('cohort','LP-DiD: cohort FE + baseline covariates'),('province','LP-DiD: province FE + baseline covariates')]):
  q=LP[LP.spec.eq(spec)&~LP.reference].sort_values('h');q=q[q.h.ge(1)] if postonly else q
  axes[0].errorbar(q.h+(j-.5)*.13,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=ms[j],ls='none',capsize=4,ms=5,color=COL[j],label=label)
 for j,(learner,label) in enumerate([('Ridge_Logit','DoubleML-DiD: Ridge / Logit'),('RandomForest','DoubleML-DiD: random forests')]):
  q=DML[DML.learner.eq(learner)].sort_values('h');q=q[q.h.ge(1)] if postonly else q
  axes[1].errorbar(q.h+(j-.5)*.13,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=ms[j],ls='none',capsize=4,ms=5,color=COL[j],label=label)
 for ax,title in zip(axes,['LP-DiD: reweighted / regression-adjusted ATT','DoubleML-DiD: cluster-disjoint cross-fitting']):
  ax.axhline(0,color='gray',ls='--',lw=1);ax.grid(axis='y',alpha=.15);ax.set_title(title,fontsize=12);ax.set_xlabel('Years relative to first provincial inspection');ax.legend(fontsize=8,loc='upper left')
  ax.set_xticks(range(1,5) if postonly else range(-4,5));ax.set_xlim(.5,4.5) if postonly else ax.set_xlim(-4.5,4.5)
  if not postonly:
   ax.axvline(0,color='#b18a34',ls=':',lw=1)
   for j in range(2):ax.plot(-1+(j-.5)*.13,0,marker=ms[j],ls='none',mfc='white',mec=COL[j],ms=6)
 axes[0].set_ylabel('Change in promotion gap relative to k=-1 (pp)')
 fig.suptitle('Fixed pre-inspection connections: LP-DiD and DoubleML-DiD\nFour complete post years | Point estimates and 95% CIs',fontsize=17,y=.97)
 fig.subplots_adjust(left=.07,right=.98,top=.82,bottom=.28,wspace=.12)
 fig.text(.06,.045,'Identical baseline-to-horizon pairs across methods. Post +1/+2/+3/+4: N=390/310/191/48; connected=42/35/19/4.\nLP-DiD: official lpdid, rw, never-exposed comparison; unit effects removed by long differences.\nDoubleML: observational DiD score; baseline covariates + cohort, no province FE; 3 province folds x 5 repetitions, seed 20261015.\nProvince-clustered SEs, displayed with t(G-1) critical values. k=+4: 2013 cohort only, 9 provinces.\nBoth groups experienced inspection. Changing promotion risk sets; no connecting lines; no zero-filling of missing outcomes.',fontsize=9)
 export(fig,'02_post_four_periods.png' if postonly else '01_LPDID_DoubleML_event_studies.png','Post four periods' if postonly else 'Full event study comparison')
draw();draw(True)
fig,axes=plt.subplots(1,2,figsize=(13,6))
for j,(y,title) in enumerate([('N','Observed baseline-to-horizon pairs'),('treated','Baseline-connected officials')]):
 q=DML[DML.learner.eq('Ridge_Logit')].sort_values('h');axes[j].bar(q.h,q[y],color='#287c9e',width=.65);axes[j].set_xticks(range(-4,5));axes[j].set_xlabel('Inspection-relative year');axes[j].set_title(title)
 for r in q.itertuples():axes[j].text(r.h,getattr(r,y)+max(q[y])*.02,str(int(getattr(r,y))),ha='center',fontsize=9)
 axes[j].set_ylim(0,max(q[y])*1.2)
fig.suptitle('Sample support changes with the promotion-risk horizon',fontsize=15);fig.subplots_adjust(top=.82,bottom=.22,wspace=.2);fig.text(.07,.04,'A horizon requires the same official observed at k=-1 and k=h. No outcomes imputed after exit.\nAt k=+4: 48 officials, including 4 baseline-connected officials in 4 provinces; total 9 provinces.',fontsize=9)
export(fig,'03_sample_support.png','Sample support by relative year')
methods='''# LP-DiD与DoubleML-DiD：固定事前关系，事后四期

## 样本和结果含义
沿用Sun–Abraham版C0和事前名单，不重新筛关系或按显著性换窗口。C0取k=-1记录的事前至少六个月共事关系，与当时省委书记/省长任一人有关系为1，两者均已知无关系才为0。名单624人中16人缺少完整的-1期结果或控制，配对基线剩608人。只使用原任职省的记录。
每个h只保留同一人-1和h的晋升结果均可判断的观测，因变量deltaY=100*(Promotion_h-Promotion_-1)。四个完整事后期为+1,+2,+3,+4，0保留单列。晋升仍是原修订年度总晋升定义。事后样本390/310/191/48人，关系组42/35/19/4人；+4只来自2013批次，9省，关系组分布4省。离任/缺失不补0，不将风险集外官员硬补回。
两组都经历巡视；处理是事前关系暴露×首次巡视后的差异性暴露，不是把无关系组称作从未被巡视者。结果仍需差距走势假设，不能自动解释成巡视总ATT。

## LP-DiD实际实现
使用官方Stata lpdid 1.1.0，pre(4) post(4) nevertreated rw，限制冲击基期year==G0，控制为基期年龄及平方、任期及平方、行政级别、角色。rw+controls使用回归调整，目标是等权处理组ATT：先在比较组拟合基线到h的结果变化，再对关系组的预测残差取平均；不是原普通LPM的方差加权斜率。报告批次FE（自动包含冲击日历年）和省FE两版。每省只有一次冲击基期，所以这里的省FE在长差分中控制各省这段时期的共同变化；个人不变效应已由差分消除，不能再机械添加个人FE。
为让命令验证吸收型暴露，给固定名单建立日历网格，缺失Y保持缺失，仅按已知C0和G0填入处理状态及基期特征。不生成新的晋升结果。never-exposed仅指C0=0的比较组。命令的if限制在建立差分前不删除原始时间行，因此所有差分可追溯。
16个非参照点估计、样本数及16个聚类影响函数SE由Python手工回归调整独立复核。官方rw分支使用正态p/CI，另保留原始正态结果；展示统一改用原聚类SE配t(G-1)临界值。未把这个近似称为精确少聚类推断。LP平均和联合检验由跨期省级影响函数协方差计算，平均对象是各期不同风险集的平均，df取对应期最小省数-1。

## DoubleML实际实现
使用本机DoubleML 0.11.4的DoubleMLDID/DoubleMLDIDData支持接口（该接口已标弃用，但当前版本可运行；不虚构成更新API）。score=observational，对相同长差分结果估计关系组的双重稳健DiD ATT。
机器学习分别拟合比较组的条件结果变化g0(X)和关系概率m(X)，而不是直接用随机森林预测晋升再比较预测值。X仅用基期年龄及平方、任期及平方、职级虚拟变量、角色、巡视批次；没有用事后控制。
预先固定两套learner：StandardScaler+Ridge(alpha=10)，StandardScaler+Logit(C=.5)；或200棵、深度3、min_leaf5的随机森林。每期3折、5次重复，固定种子20261015。分折整省留出，并以关系组省份分散到多折保证训练可运行；只参考处理支持和省份，不参考Y或显著性。所有重复结果保留，不挑某个seed或某个分折。
DoubleML使用省级聚类交叉拟合及聚类SE；展示t(G-1)95%CI，同时保留软件原正态p值。propensity预先固定裁剪[.01,.99]，披露裁剪比例。整省留出无法学习留出省自己的虚拟变量截距，因此本版没有省FE；它与LP批次FE+事前特征版更接近，不冒充个人+省×年FE。个人不变水平通过长差分消除。
本轮不再调参/调窗口以找显著，全部16个DML模型和5次重复都交付。机器学习无法增加+4的4名关系官员，也不能解决晋升退出导致的样本选择。

## 结论读取
没有连续四期负显著。前期某些系数也负且显著：不能只报事后负值来宣称巡视造成差距下降。LP省FE的+4在官方正态p下接近10%，改用9省的t(8)后更弱；需要明确区分推断口径。DML RF的+1仅10%显著，其他事后期不显著。详细原值由Excel/CSV提供。

重跑：prepare_lp_dml_post4.py → Stata run_lpdid.do，另运行fit_doubleml_post4.py → report_lp_dml_post4.py。依赖与输入路径保留本机配置。无PDF；原网络和既有结果不覆盖。

LP-DiD原文：https://www.nber.org/papers/w31184
官方代码：https://github.com/danielegirardi/lpdid
DoubleML DiD：https://docs.doubleml.org/stable/api/generated/doubleml.did.DoubleMLDID.html
'''
(O/'methods_中文.md').write_text(methods,encoding='utf8')
config=json.loads((O/'doubleml_configuration.json').read_text(encoding='utf8'))
with pd.ExcelWriter(O/'LPDID_DoubleML_事后四期_全部结果.xlsx',engine='openpyxl') as w:
 for name,q in [('LPDID',LP),('DoubleML',DML),('LPDID_average',pd.DataFrame(avg)),('LPDID_joint',pd.DataFrame(joint)),('Horizon_support',MP),('DML_repetitions',REPS),('Province_folds',FOLD),('Validation',pd.DataFrame(checks)),('Paired_data',Q),('DML_config',pd.DataFrame([dict(key=k,value=json.dumps(v,ensure_ascii=False)) for k,v in config.items()]))]:
  q.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>LP-DiD与DoubleML</title><style>body{max-width:1500px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}</style><h1>LP-DiD与DoubleML-DiD：事后四期</h1><p>固定事前关系，同人配对，不填补退出后的结果。未出现连续四期显著下降，部分事前期也出现负差异。DoubleML仅调整事前特征与巡视批次，不包含省×年FE。</p><p><a href="LPDID_DoubleML_事后四期_全部结果.xlsx">全部结果Excel</a> · <a href="methods_中文.md">详细方法</a></p>'
for fn,title in gallery:page+='<h2>'+title+'</h2><img src="figures/'+fn+'">'
(O/'index.html').write_text(page,encoding='utf8')
for p in (O/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()
ck('Three readable PNG figures',len(gallery)==3);ck('No PDF',not list(O.rglob('*.pdf')))
pd.DataFrame(checks).to_csv(O/'validation_checks.csv',index=False,encoding='utf-8-sig');assert all(c['passed'] for c in checks)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file() and p.name!='file_manifest.csv']).to_csv(O/'file_manifest.csv',index=False)
archive=B/'LPDID_DoubleML_事后四期_数据代码图表.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('LPDID post:');print(LP[LP.h.gt(0)][['spec','h','b','se','p','lo','hi','N']].to_string(index=False));print('DML post:');print(DML[DML.h.gt(0)][['learner','h','b','p','lo','hi','N','clipped_fraction']].to_string(index=False));print('Checks pass:',len(checks));print('LPDID pre tests',joint)
