"""Pre-only fixed-C0 levels versus within-official changes; common FE support."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('MKL_NUM_THREADS','2')
import sys,json,hashlib,shutil,html,argparse
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t,f
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'preinspection_FE_combinations_2026_10_21'
SOURCE=B/'preinspection_fixed_C0_levels_2026_10_21/preinspection_panel.csv.gz'
CTRL='age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag'
SPECS=[
 dict(model_id=1,fe='PXY',absorb='py',label='Province x year',kind='level'),
 dict(model_id=2,fe='CITY_YEAR',absorb='city_code year',label='City + year',kind='level'),
 dict(model_id=3,fe='CITY_PXY',absorb='city_code py',label='City + province x year',kind='level'),
 dict(model_id=4,fe='I_YEAR',absorb='person_id year',label='Individual + year',kind='change'),
 dict(model_id=5,fe='I_PXY',absorb='person_id py',label='Individual + province x year',kind='change'),
 dict(model_id=6,fe='I_CITY_YEAR',absorb='person_id city_code year',label='Individual + city + year',kind='change'),
 dict(model_id=7,fe='I_CITY_PXY',absorb='person_id city_code py',label='Individual + city + province x year',kind='change'),
]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csv(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')

def prepare():
 for p in [O,O/'code',O/'figures']:p.mkdir(parents=True,exist_ok=True)
 if (O/'stata_results.dta').exists():raise RuntimeError('Completed estimates already exist; use a new folder.')
 a=pd.read_csv(SOURCE,low_memory=False);assert len(a)==1562
 d=a.copy();drops=[]
 for step in range(100):
  keep=pd.Series(True,index=d.index)
  for col in ['person_id','city_code','py']:keep &= d.groupby(col)[col].transform('size').gt(1)
  if keep.all():break
  drops.append(d[~keep].assign(singleton_step=step));d=d[keep].copy()
 else:raise RuntimeError('Common FE core did not converge')
 assert len(d)==1456 and d.person_id.nunique()==441
 assert not d.duplicated(['person_id','year']).any() and d.k.between(-4,-1).all()
 assert d.groupby('person_id').C0.nunique().eq(1).all()
 for k in [-4,-3,-2]:
  d[f'd_m{-k}']=d.k.eq(k).astype(float);d[f'c_m{-k}']=d.C0*d[f'd_m{-k}']
 d.to_csv(O/'common_preinspection_panel.csv.gz',index=False)
 csv(pd.concat(drops,ignore_index=True),'singleton_exclusions.csv')
 cols=['person_id','city_code','year','anchor_province','py','k','C0','Y','age','age2','tenure','tenure2','base_rank','role_secretary','gdp_growth_lag','lngdppc_lag','lnpop_lag']+[f'{p}_m{k}' for p in ['d','c'] for k in [4,3,2]]
 d[cols].to_stata(O/'common_preinspection_panel.dta',write_index=False,version=118)
 csv(pd.DataFrame(SPECS),'model_specifications.csv')
 csv(d.groupby(['k','C0']).agg(N=('Y','size'),people=('person_id','nunique'),promotions=('promotion','sum'),rate=('Y','mean')).reset_index(),'event_support.csv')
 csv(d.groupby('person_id').agg(C0=('C0','first'),observations=('Y','size'),cities=('city_code','nunique'),first_k=('k','min'),last_k=('k','max')).reset_index(),'person_city_support.csv')
 meta=dict(source_N=len(a),common_N=len(d),removed=len(a)-len(d),people=d.person_id.nunique(),tied_people=d[d.C0.eq(1)].person_id.nunique(),G=d.anchor_province.nunique(),cities=d.city_code.nunique(),city_movers=int(d.groupby('person_id').city_code.nunique().gt(1).sum()),promotions=int(d.promotion.sum()))
 (O/'sample_summary.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
 csv(pd.DataFrame([dict(path=str(SOURCE),sha256=sha(SOURCE))]),'input_manifest.csv')
 lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/estimation.log", text replace','tempname rr jj vv',
 'postfile `rr\' long model_id str20 term double(b se p lo hi N G df K df_a df_nested) using "`out\'/stata_results.dta", replace',
 'postfile `jj\' long model_id double(F df_num df_den p) using "`out\'/joint_tests.dta", replace',
 'postfile `vv\' long model_id str12 term1 str12 term2 double value using "`out\'/covariances.dta", replace']
 for m in SPECS:
  targets=['C0'] if m['kind']=='level' else ['c_m4','c_m3','c_m2']
  cov=CTRL+(' d_m4 d_m3 d_m2' if m['fe'] in ['I_YEAR','I_CITY_YEAR'] else '')
  lines += ['use "`out\'/common_preinspection_panel.dta", clear','isid person_id year','local initialN=_N',f'reghdfe Y {" ".join(targets)} {cov}, absorb({m["absorb"]}) vce(cluster anchor_province)',
  "assert e(N)==`initialN'",'local nn=e(N)','local gg=e(N_clust)','local dd=e(df_r)','local da=e(df_a)','local dn=e(df_a_nested)','quietly _ms_omit_info e(b)',"local kk=e(df_a)+colsof(e(b))-r(k_omit)"]
  for nm in targets+(['pre_average_change'] if m['kind']=='change' else []):
   expr=nm if nm!='pre_average_change' else '(c_m4+c_m3+c_m2)/3'
   lines += [f'quietly lincom {expr}, level(95)',f'post `rr\' ({m["model_id"]}) ("{nm}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`nn\') (`gg\') (`dd\') (`kk\') (`da\') (`dn\')']
  if m['kind']=='change':lines += ['quietly test c_m4 c_m3 c_m2',f'post `jj\' ({m["model_id"]}) (r(F)) (r(df)) (r(df_r)) (r(p))']
  for n1 in targets:
   for n2 in targets:lines += [f'post `vv\' ({m["model_id"]}) ("{n1}") ("{n2}") (e(V)[rownumb(e(V),"{n1}"),colnumb(e(V),"{n2}")])']
 lines += ['postclose `rr\'','postclose `jj\'','postclose `vv\'','log close','exit, clear']
 (O/'code/run_preinspection_FE.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
 shutil.copy2(__file__,O/'code'/Path(__file__).name)
 print(json.dumps(meta));print(d.groupby(['k','C0']).size().to_string())

def independent(d,m,K):
 names=['C0'] if m['kind']=='level' else ['c_m4','c_m3','c_m2']
 zparts=[d[['age','age2','tenure','tenure2','gdp_growth_lag','lngdppc_lag','lnpop_lag']].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(d.role_secretary,drop_first=True,dtype=float).to_numpy()]
 for group in m['absorb'].split():zparts.append(pd.get_dummies(d[group],drop_first=False,dtype=float).to_numpy())
 if m['fe'] in ['I_YEAR','I_CITY_YEAR']:zparts.append(d[['d_m4','d_m3','d_m2']].to_numpy(float))
 z=np.column_stack(zparts);zn=np.linalg.norm(z,axis=0);z=z[:,zn>1e-10]/zn[zn>1e-10]
 yx=np.column_stack([d.Y.to_numpy(float),d[names].to_numpy(float)])
 bb,_,zr,_=lstsq(z,yx,cond=1e-10,lapack_driver='gelsd');res=yx-z@bb;y=res[:,0];x=res[:,1:]
 b,_,rank,_=lstsq(x,y,cond=1e-10);assert rank==len(names)
 assert np.linalg.svd(x,compute_uv=False).min()>1e-7
 u=y-x@b;bread=np.linalg.inv(x.T@x);gc=pd.factorize(d.anchor_province)[0];G=gc.max()+1;N=len(d)
 scores=np.zeros((G,len(names)));np.add.at(scores,gc,x*u[:,None]);V=bread@scores.T@scores@bread*G/(G-1)*(N-1)/(N-K)
 return b,V,int(zr),float(np.linalg.svd(x,compute_uv=False).min())

def report():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 d=pd.read_csv(O/'common_preinspection_panel.csv.gz',low_memory=False)
 r=pd.read_stata(O/'stata_results.dta').merge(pd.DataFrame(SPECS),on='model_id',validate='m:1');j=pd.read_stata(O/'joint_tests.dta');vv=pd.read_stata(O/'covariances.dta')
 meta=json.loads((O/'sample_summary.json').read_text());checks=[];ver=[]
 def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
 ck('Source descriptive panel unchanged',sha(SOURCE)==pd.read_csv(O/'input_manifest.csv').sha256.iloc[0])
 ck('Seven FE models, nineteen estimated contrasts',r.model_id.nunique()==7 and len(r)==19)
 ck('All models use identical common sample',r.N.eq(len(d)).all())
 ck('All cluster counts and degrees of freedom agree',r.G.eq(meta['G']).all() and r.df.eq(meta['G']-1).all())
 ck('Only pre-inspection observations',d.k.between(-4,-1).all())
 ck('C0 constant within every official',d.groupby('person_id').C0.nunique().eq(1).all())
 ck('Person FE exactly absorb C0',np.max(np.abs(d.C0-d.groupby('person_id').C0.transform('mean')))==0)
 for m in SPECS:
  q=r[r.model_id.eq(m['model_id'])];targets=['C0'] if m['kind']=='level' else ['c_m4','c_m3','c_m2'];q0=q.set_index('term').loc[targets]
  bb,V,zr,sv=independent(d,m,int(q.K.iloc[0]));svv=vv[vv.model_id.eq(m['model_id'])].pivot(index='term1',columns='term2',values='value').loc[targets,targets].to_numpy()
  ck('Independent coefficients '+m['fe'],np.allclose(bb,q0.b,atol=2e-6))
  ck('Independent clustered covariance '+m['fe'],np.allclose(V,svv,atol=2e-6,rtol=1e-7))
  for n,b,s in zip(targets,bb,np.sqrt(np.diag(V))):ver.append(dict(model_id=m['model_id'],term=n,python_b=b,python_se=s,nuisance_rank=zr,min_singular=sv))
  if m['kind']=='change':
   row=q.set_index('term').loc['pre_average_change'];ck('Average includes full covariance '+m['fe'],np.isclose(row.b,bb.mean(),atol=1e-7) and np.isclose(row.se**2,V.sum()/9,atol=1e-6))
   rank=np.linalg.matrix_rank(V);F=bb@np.linalg.pinv(V)@bb/rank;rowj=j[j.model_id.eq(m['model_id'])].iloc[0];ck('Joint test '+m['fe'],np.isclose(rowj.F,F,rtol=1e-7) and np.isclose(rowj.p,f.sf(F,rank,meta['G']-1),atol=1e-8))
 ck('All estimated intervals finite',np.isfinite(r[['b','se','p','lo','hi']]).all().all())
 ck('CI and p values match clustered t inference',np.allclose(r.lo,r.b-t.ppf(.975,r.df)*r.se,atol=1e-8) and np.allclose(r.p,2*t.sf(np.abs(r.b/r.se),r.df),atol=1e-8))
 csv(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
 csv(r,'all_FE_results.csv');csv(j,'joint_preperiod_change_tests.csv');csv(vv,'clustered_covariances.csv');csv(pd.DataFrame(ver),'independent_verification.csv')
 levels=r[r.kind.eq('level')].copy();levels['identified']=True
 missing=pd.DataFrame([{**m,'term':'C0','b':np.nan,'se':np.nan,'p':np.nan,'lo':np.nan,'hi':np.nan,'N':len(d),'G':meta['G'],'identified':False,'reason':'Fixed C0 absorbed by individual FE'} for m in SPECS if m['kind']=='change'])
 levels=pd.concat([levels,missing],ignore_index=True);csv(levels,'absolute_level_identification.csv')
 er=r[r.kind.eq('change')&r.term.ne('pre_average_change')].copy();er['k']=-er.term.str[3:].astype(int)
 for m in [m for m in SPECS if m['kind']=='change']:
  er=pd.concat([er,pd.DataFrame([{**m,'term':'reference','k':-1,'b':0,'se':np.nan,'p':np.nan,'lo':np.nan,'hi':np.nan,'N':len(d),'G':meta['G']}])],ignore_index=True)
 csv(er,'preperiod_event_coefficients.csv')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(2,2,figsize=(14.8,10),sharex=True,sharey=True)
 for ax,m in zip(axes.flat,[m for m in SPECS if m['kind']=='change']):
  q=er[er.model_id.eq(m['model_id'])].sort_values('k');z=q[q.k.ne(-1)];ax.errorbar(z.k,z.b,yerr=[z.b-z.lo,z.hi-z.b],fmt='o',ls='none',capsize=5,color='#247e9d',ms=6)
  ax.scatter([-1],[0],facecolors='white',edgecolors='#247e9d',s=55,zorder=4)
  ax.axhline(0,color='#888',ls='--');ax.set_xticks([-4,-3,-2,-1]);ax.grid(axis='y',alpha=.15);rowj=j[j.model_id.eq(m['model_id'])].iloc[0]
  ax.set_title(m['label']+f'\nJoint pre-period change p = {rowj.p:.3f}')
  ax.set_xlabel('Years relative to first inspection');ax.set_ylabel('Change in tied-minus-untied gap (pp)')
 fig.suptitle('Pre-inspection FE comparison | Fixed baseline relationship group\nReference k = -1 | Full controls | 95% province-clustered CIs',fontsize=18,y=.98)
 fig.text(.06,.035,f'Identical N={len(d):,} officer-years; {meta["people"]} officials ({meta["tied_people"]} tied); {meta["G"]} provinces. Strictly pre-inspection k=-4,...,-1.\nAll panels include personal and lagged appointment-city economic controls; age linear term is absorbed by individual + time FE.\nThese are changes relative to -1, not absolute connection advantages. Reference is normalized to zero and has no estimated CI. No connecting lines.\nPre-period-only models differ from the full pre/post event study. Non-rejection does not establish parallel trends; retrospective cohort selection remains.',fontsize=10)
 fig.subplots_adjust(top=.80,bottom=.20,left=.08,right=.98,hspace=.45,wspace=.25);fig.savefig(O/'figures/01_preinspection_individual_city_FE_changes.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(13.8,7))
 labels=[m['label'] for m in SPECS]
 for i,m in enumerate(SPECS):
  y=6-i
  if m['kind']=='level':
   row=r[r.model_id.eq(m['model_id'])].iloc[0];ax.errorbar(row.b,y,xerr=[[row.b-row.lo],[row.hi-row.b]],fmt='o',ls='none',capsize=5,color='#247e9d');ax.annotate(f'{row.b:+.2f} pp; p={row.p:.3f}',(row.b,y),xytext=(0,12),textcoords='offset points',ha='center',fontsize=10)
  else:ax.text(.60,y,'Absorbed by individual FE; no coefficient or CI',transform=ax.get_yaxis_transform(),ha='center',va='center',color='#777',fontsize=10)
 ax.set_yticks(range(6,-1,-1),labels);ax.axvline(0,color='#888',ls='--');ax.grid(axis='x',alpha=.15);ax.set_ylim(-.6,6.7);ax.set_xlabel('Absolute pre-inspection conditional promotion gap (pp)')
 ax.set_title('Fixed-C0 levels across FE combinations\nFull controls; identical pre-period sample; 95% province-clustered CIs',fontsize=17)
 fig.text(.035,.035,'A time-invariant baseline relationship cannot be estimated with individual FE. Missing estimates are not zeros.\nNo-individual-FE coefficients are between-official conditional associations. See the separate four-panel chart for within-official changes.\nThe cohort was selected at a later pre-inspection snapshot, so earlier observations are retrospective. CIs are pointwise, exploratory.',fontsize=10)
 fig.subplots_adjust(left=.34,right=.98,top=.82,bottom=.22);fig.savefig(O/'figures/02_absolute_levels_and_absorption.png',dpi=180);plt.close(fig)
 note=f'''# 巡视前：个人、城市及时间固定效应组合

输入为上一轮严格事前面板1562个人年。为统一不同FE比较，反复剔除个人、城市和省年singleton，共删除{meta['removed']}行，得到所有模型共同的{meta['common_N']}个人年、{meta['people']}人，其中{meta['tied_people']}名有关系，{meta['G']}省、{meta['cities']}城市。{meta['city_movers']}人在事前观测中换过城市。每轮删除和逐期支持均交付。禁止把与上一轮图的差异全部解释为FE作用，因为此共同样本发生变化。

绝对水平三种FE：省×年；城市+年；城市+省×年。方程Y=delta C0+FE+X gamma+error。此处X包含年龄及平方、任期及平方、职级与市长/书记角色，以及跟随年度任职城市的上年GDP增长、对数人均GDP、对数人口。没有事后观测，Y乘100，系数为百分点。

含个人FE四种组合：个人+年；个人+省×年；个人+城市+年；个人+城市+省×年。固定C0被个人FE精确吸收，因此不报告伪造的0系数/0CI。改估计Y=个人FE+其他FE+sum_(k=-4,-3,-2) beta_k C0*1[event=k]+X gamma+error，参照k=-1。没有省年FE时补入相对时间主项；有省年FE时主项被吸收。全部组合包含相同控制变量，线性年龄在个人+时间FE下自动吸收。城市FE是加法FE，不是城市×年份。

四张主图画的是事前年份的关系差距相对-1的变化，不是事前绝对关系优势。-1为归零参照，没有估计CI。另报告(-4,-3,-2)系数等权平均及其完整协方差CI，以及三个系数同时为0的联合检验；不能把未拒绝当作组间等效或平行趋势成立。

本轮仅事前重新估计，系数可能不同于全事前/事后事件研究，因为FE和控制系数都由事前样本估计。原主DID不覆盖。全部模型同一样本；省聚类CR1、95%t(G-1)逐点CI，Stata18 reghdfe。显式FE虚拟变量矩阵投影、FWL和省级聚类sandwich独立核验点估计与协方差，有限样本K使用Stata实际元数据。没有新窗口搜索或择显著性报告，没有wild bootstrap。后验探索区间未覆盖此前所有规格搜索的不确定性。

名单、关系、晋升定义与前轮一致。固定事前关系对早期年份仍是回溯分类，关系可能尚未形成，晋升也可能影响后来进入名单；不能把控制/FE当成消除了所有选择。该结果既不是巡视总效应，也不证明关系因果作用。

可重跑：Python preinspection_FE_combinations.py prepare；Stata code/run_preinspection_FE.do；Python preinspection_FE_combinations.py report。prepare不覆盖已完成结果。图、表、数据与代码保存在本目录，不生成PDF。
'''
 (O/'方法与结果.md').write_text(note,encoding='utf8')
 with pd.ExcelWriter(O/'事前个人城市FE组合_全部结果.xlsx',engine='openpyxl') as x:
  for n,dd in [('全部估计',r),('逐期图数据',er),('绝对水平可识别性',levels),('联合检验',j),('逐期支持',pd.read_csv(O/'event_support.csv')),('核验',pd.DataFrame(checks))]:dd.to_excel(x,sheet_name=n,index=False)
 page='<html><meta charset="utf-8"><body style="max-width:1400px;margin:auto;font-family:Arial"><h1>Pre-inspection FE combinations</h1>'
 for nm in ['01_preinspection_individual_city_FE_changes.png','02_absolute_levels_and_absorption.png']:page+=f'<img style="width:100%" src="figures/{nm}">'
 page+='<pre style="white-space:pre-wrap">'+html.escape(note)+'</pre></body></html>';(O/'index.html').write_text(page,encoding='utf8')
 shutil.copy2(__file__,O/'code'/Path(__file__).name)
 print(r[['model_id','fe','term','b','lo','hi','p','N','G']].to_string(index=False));print(j.to_string(index=False));print('Checks',len(checks),'all passed')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','report']);args=ap.parse_args();prepare() if args.stage=='prepare' else report()
