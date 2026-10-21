"""Fixed-baseline hometown/classmate promotion event studies; no invented zeros."""
from pathlib import Path
import sys, json, hashlib, shutil, ast
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np, pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu

B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'hometown_classmate_fixed_event_study_2026_10_21'
KS=[-4,-3,-2,0,1,2,3,4]
EC=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
CTRL=['age2','tenure','tenure2','base_rank','role_secretary']+EC
REL={'hometown_prefecture':'Hometown ties','classmate_6m':'Overlapping school ties'}
FE={'I_YEAR':'person_id year','I_PXY':'person_id py'}
def nm(k):return f'd_m{-k}' if k<0 else f'd_p{k}'
def csv(d,name):d.to_csv(O/name,index=False,encoding='utf-8-sig')

# Import only the independently verified sparse FE projection helper, without
# executing the source file's data-loading or estimation commands.
helper=Path(__file__).with_name('event_study_individual_FE.py')
tree=ast.parse(helper.read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fe_project'],type_ignores=[]),str(helper),'exec'))

def design(d,fe,method,stata_K=None):
 groups=[pd.factorize(d.person_id)[0],pd.factorize(d.year if fe=='I_YEAR' else d.provyear)[0]]
 active=[k for k in KS if (d.k.eq(k)&d.C0.eq(1)).any()]
 cohorts=sorted(d.loc[d.C0.eq(1),'G0'].unique())
 keys=[(g,k) for k in active for g in cohorts] if method=='Sun_Abraham' else [(0,k) for k in active]
 targets=np.column_stack([(d.C0.eq(1)&d.k.eq(k)&(d.G0.eq(g) if g else True)).to_numpy(float) for g,k in keys])
 events=np.column_stack([d.k.eq(k).to_numpy(float) for k in KS]) if fe=='I_YEAR' else np.empty((len(d),0))
 controls=np.column_stack([d[['age2','tenure','tenure2','role_secretary']+EC].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),events])
 dm,_,_=fe_project(np.column_stack([d.Y,targets,controls]),groups)
 m=targets.shape[1];z=dm[:,m+1:];scale=np.linalg.norm(z,axis=0);z=z[:,scale>1e-8]/scale[scale>1e-8]
 yx=dm[:,:m+1];rr=yx-z@lstsq(z,yx,cond=1e-10)[0];x=rr[:,1:];y=rr[:,0]
 bb=lstsq(x,y,cond=1e-10)[0]
 proj=np.linalg.pinv(x,rcond=1e-10)@x
 V=None
 if method=='TWFE_fixed' and stata_K is not None:
  err=y-x@bb;bread=np.linalg.pinv(x.T@x,rcond=1e-10)
  gc=pd.factorize(d.anchor_province)[0];G=gc.max()+1
  sc=np.zeros((G,m));np.add.at(sc,gc,x*err[:,None])
  V=bread@sc.T@sc@bread*G/(G-1)*(len(d)-1)/(len(d)-stata_K-1)
 out=[]
 for k in KS:
  L=np.zeros(m)
  for j,(g,kk) in enumerate(keys):
   if kk==k:
    L[j]=(d.C0.eq(1)&d.k.eq(k)&d.G0.eq(g)).sum()/(d.C0.eq(1)&d.k.eq(k)).sum() if g else 1.
  known=k in active and np.linalg.norm(L-L@proj)<1e-7
  out.append(dict(method=method,fe=fe,k=k,estimable=known,python_b=float(L@bb) if known else np.nan,python_se=float(np.sqrt(L@V@L)) if known and V is not None else np.nan,estimability_error=float(np.linalg.norm(L-L@proj)),reason='' if known else ('No baseline-connected observations at this event time' if k not in active else 'Target not identified conditional on controls and FE')))
 return out

def prepare():
 if (O/'coefficients.dta').exists():raise RuntimeError('Completed outputs already exist; refusing to overwrite estimates.')
 for q in [O,O/'code',O/'data',O/'figures']:q.mkdir(parents=True,exist_ok=True)
 source=B/'with_officer_city_economics/annual_economics_rematched.csv.gz'
 a=pd.read_csv(source,low_memory=False);assert not a.duplicated(['person_id','year']).any()
 assert a.year.between(2006,2017).all()
 summary=[];models=[];validation=[];support=[];anchors=[]
 lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/estimation.log", text replace','which reghdfe','which eventstudyinteract','tempname rr mm jj vv ff ww',
 'postfile `rr\' long model_id str18 method str24 term double b se p lo hi using "`out\'/coefficients.dta", replace',
 'postfile `mm\' long model_id str18 method double N G df K using "`out\'/models.dta", replace',
 'postfile `jj\' long model_id str18 method str24 test double F df_num p using "`out\'/joint_tests.dta", replace',
 'postfile `vv\' long model_id str18 method str16 term1 str16 term2 double value using "`out\'/covariances.dta", replace',
 'postfile `ff\' long model_id str18 method long rc using "`out\'/failures.dta", replace',
 'postfile `ww\' long model_id long cohort str16 term double weight using "`out\'/SA_weights.dta", replace']
 mid=0
 for rel in REL:
  z=a[a.k.eq(-1)].copy();r=z[['legacy_'+rel+'_S','legacy_'+rel+'_G']]
  z['C0']=np.where(r.eq(1).any(axis=1),1.,np.where(r.eq(0).all(axis=1),0.,np.nan));z['relation']=rel
  anchors.append(z[['person_id','name','year','baseline_date','province_code','S_person_id','G_person_id','C0','relation']])
  anchor=z[['person_id','province_code','first_inspection_year','C0','baseline_date','S_person_id','G_person_id']].rename(columns={'province_code':'anchor_province','first_inspection_year':'G0','baseline_date':'anchor_snapshot','S_person_id':'anchor_S','G_person_id':'anchor_G'})
  d=a.merge(anchor,on='person_id',validate='m:1');d=d[d.C0.notna()&d.province_code.eq(d.anchor_province)].copy();d['k']=d.year-d.G0
  d=d[d.k.between(-4,4)].dropna(subset=['promotion']+CTRL).copy();d['Y']=100*d.promotion;d['provyear']=d.anchor_province*10000+d.year
  before=len(d);drops=[]
  for step in range(100):
   keep=d.groupby('person_id').person_id.transform('size').gt(1)&d.groupby('provyear').provyear.transform('size').gt(1)
   if keep.all():break
   drops.append(d[~keep].assign(step=step));d=d[keep].copy()
  else:raise RuntimeError('Singleton pruning failed')
  csv(pd.concat(drops) if drops else d.iloc[:0],f'data/{rel}_singleton_exclusions.csv')
  assert d.groupby('person_id').C0.nunique().eq(1).all()
  d['never']=d.C0.eq(0).astype(int);d['treated_cohort']=d.G0.where(d.C0.eq(1))
  csv(d,f'data/{rel}_analysis_panel.csv.gz')
  columns=['person_id','year','anchor_province','city_code','G0','k','Y','C0','never','treated_cohort']+CTRL
  d[columns].to_stata(O/f'data/{rel}_panel.dta',write_index=False,version=118)
  for k,q in d.groupby('k'):
   tied=q[q.C0.eq(1)];support.append(dict(relation=rel,k=int(k),N=len(q),people=q.person_id.nunique(),provinces=q.anchor_province.nunique(),connected=len(tied),connected_provinces=tied.anchor_province.nunique(),connected_promotions=tied.promotion.sum(),unconnected_promotions=q[q.C0.eq(0)].promotion.sum()))
  summary.append(dict(relation=rel,anchor_total=len(z),anchor_connected=int(z.C0.eq(1).sum()),anchor_unconnected=int(z.C0.eq(0).sum()),anchor_unknown=int(z.C0.isna().sum()),N=len(d),people=d.person_id.nunique(),connected_people=d[d.C0.eq(1)].person_id.nunique(),provinces=d.anchor_province.nunique(),connected_provinces=d[d.C0.eq(1)].anchor_province.nunique(),singletons_removed=before-len(d)))
  for fe,absorb in FE.items():
   mid+=1;models.append(dict(model_id=mid,relation=rel,fe=fe,absorb=absorb,N=len(d)))
   active=[k for k in KS if (d.C0.eq(1)&d.k.eq(k)).any()];names=[nm(k) for k in active]
   for method in ['TWFE_fixed','Sun_Abraham']:
    check=design(d,fe,method)
    for r in check:r.update(model_id=mid,relation=rel)
    validation.extend(check)
   lines+=['use "`out\'/data/'+rel+'_panel.dta", clear','isid person_id year','egen py=group(anchor_province year)']
   for k in KS:
    lines += [f'gen double all_{nm(k)}=(k=={k})']
    if k in active:lines += [f'gen double {nm(k)}=(k=={k})*C0']
   cov='age2 tenure tenure2 i.base_rank i.role_secretary '+' '.join(EC)+(' '+' '.join('all_'+nm(k) for k in KS) if fe=='I_YEAR' else '')
   for method in ['TWFE_fixed','Sun_Abraham']:
    cmd=('reghdfe Y '+' '.join(names)+' '+cov+f', absorb({absorb}) vce(cluster anchor_province)') if method=='TWFE_fixed' else ('eventstudyinteract Y '+' '.join(names)+f', cohort(treated_cohort) control_cohort(never) absorb({absorb}) covariates({cov}) vce(cluster anchor_province)')
    lines += ['capture noisily '+cmd,'local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) ("{method}") (`rc\')','if `rc\'==0 {','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','local KK=e(df_m)+e(df_a)',f'assert `NN\'=={len(d)}',f'post `mm\' ({mid}) ("{method}") (`NN\') (`GG\') (`DD\') (`KK\')']
    if method=='Sun_Abraham':
     cohorts=sorted(d.loc[d.C0.eq(1),'G0'].unique())
     lines+=['matrix BI=e(b_iw)','matrix VI=e(V_iw)','matrix WI=e(ff_w)']
     for i,k in enumerate(active,1):
      for j,g in enumerate(cohorts,1):lines += [f'post `ww\' ({mid}) ({int(g)}) ("{nm(k)}") (WI[{j},{i}])']
     lines+=['ereturn post BI VI, obs(`NN\') dof(`DD\')']
    for k in active:
     if next(x for x in validation if x['model_id']==mid and x['method']==method and x['k']==k)['estimable']:
      lines += [f'quietly lincom {nm(k)}, level(95)',f'post `rr\' ({mid}) ("{method}") ("{nm(k)}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
    # A four-post-year mean cannot be reported if any component lacks support.
    if all(k in active and next(x for x in validation if x['model_id']==mid and x['method']==method and x['k']==k)['estimable'] for k in [1,2,3,4]):
     lines += ['quietly lincom (d_p1+d_p2+d_p3+d_p4)/4, level(95)',f'post `rr\' ({mid}) ("{method}") ("post_average") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub))']
    pre=[nm(k) for k in [-4,-3,-2] if next(x for x in validation if x['model_id']==mid and x['method']==method and x['k']==k)['estimable']]
    if pre:
     lines+=['capture quietly test '+' '.join(pre),'if _rc==0 {',f'post `jj\' ({mid}) ("{method}") ("pretrend") (r(F)) (r(df)) (r(p))','}']
    lines+=['matrix VV=e(V)']
    for n1 in names:
     for n2 in names:lines += [f'post `vv\' ({mid}) ("{method}") ("{n1}") ("{n2}") (VV[rownumb(VV,"{n1}"),colnumb(VV,"{n2}")])']
    lines+=['}']
 lines+=['postclose `rr\'','postclose `mm\'','postclose `jj\'','postclose `vv\'','postclose `ff\'','postclose `ww\'','log close','exit, clear']
 (O/'code/run_models.do').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 csv(pd.DataFrame(summary),'sample_summary.csv');csv(pd.DataFrame(support),'event_support.csv');csv(pd.DataFrame(models),'model_design.csv');csv(pd.DataFrame(validation),'independent_design_and_points.csv');csv(pd.concat(anchors),'baseline_classification.csv')
 inputs=[source,helper,Path(r'C:\Users\siyang zhu\ado\plus\e\eventstudyinteract.ado'),Path(r'C:\Users\siyang zhu\ado\plus\r\reghdfe.ado')]
 csv(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]),'input_manifest.csv')
 shutil.copy2(__file__,O/'code'/Path(__file__).name)
 print(pd.DataFrame(summary).to_string(index=False));print(pd.DataFrame(validation).groupby(['relation','method','fe']).estimable.sum().to_string())

def report():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from html import escape
 from scipy.stats import t
 design_df=pd.read_csv(O/'model_design.csv');checks_df=pd.read_csv(O/'independent_design_and_points.csv');support=pd.read_csv(O/'event_support.csv');summary=pd.read_csv(O/'sample_summary.csv')
 result=pd.read_stata(O/'coefficients.dta');stats=pd.read_stata(O/'models.dta');joint=pd.read_stata(O/'joint_tests.dta');fail=pd.read_stata(O/'failures.dta')
 assert fail.empty,fail
 assert len(stats)==8
 result['k']=result.term.map({nm(k):k for k in KS});result=result.merge(design_df,on='model_id',validate='m:1').merge(stats,on=['model_id','method'],validate='m:1',suffixes=('','_stata'))
 valid=result.merge(checks_df[['model_id','method','k','python_b','estimable']],on=['model_id','method','k'],validate='1:1')
 valid['point_error']=(valid.b-valid.python_b).abs();assert valid.point_error.max()<2e-5,valid[['method','point_error']]
 independent_se=[]
 for m in design_df.itertuples():
  d=pd.read_csv(O/f'data/{m.relation}_analysis_panel.csv.gz')
  kk=stats[stats.model_id.eq(m.model_id)&stats.method.eq('TWFE_fixed')].iloc[0].K
  zz=pd.DataFrame(design(d,m.fe,'TWFE_fixed',kk));zz['model_id']=m.model_id
  independent_se.append(zz)
 secheck=pd.concat(independent_se).merge(result[['model_id','method','k','se']],on=['model_id','method','k'],validate='1:1')
 secheck['se_error']=(secheck.se-secheck.python_se).abs();assert secheck.se_error.max()<2e-5,secheck
 csv(secheck,'independent_TWFE_SE_validation.csv')
 assert result.se.gt(0).all() and np.isfinite(result[['b','se','lo','hi']]).all().all()
 assert np.allclose(result.lo,result.b-t.ppf(.975,result.df)*result.se)
 rows=[]
 for r in checks_df.to_dict('records'):
  q=result[result.model_id.eq(r['model_id'])&result.method.eq(r['method'])&result.k.eq(r['k'])]
  r.update(q.iloc[0].to_dict() if len(q) else dict(b=np.nan,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan));r['reference']=False;rows.append(r)
 for m in design_df.itertuples():
  for method in ['TWFE_fixed','Sun_Abraham']:rows.append(dict(model_id=m.model_id,relation=m.relation,fe=m.fe,method=method,k=-1,b=0.,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan,reference=True,estimable=True,reason='Normalized reference; no estimated CI'))
 allr=pd.DataFrame(rows).sort_values(['relation','fe','method','k'])
 plot_lo=min(-60,np.floor(result.lo.min()/20)*20);plot_hi=max(60,np.ceil(result.hi.max()/20)*20)
 joint=joint.merge(design_df,on='model_id',validate='m:1')
 csv(allr,'all_event_results.csv');csv(result,'estimated_coefficients.csv');csv(joint,'joint_tests.csv');csv(stats,'model_stats.csv');csv(valid,'independent_point_validation.csv');csv(fail,'failed_models.csv')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
 colors={'TWFE_fixed':'#ca8433','Sun_Abraham':'#247f9f'};labels={'TWFE_fixed':'TWFE','Sun_Abraham':'Sun-Abraham'}
 fig,axes=plt.subplots(2,2,figsize=(16,11),sharex=True,sharey=True);fig.subplots_adjust(top=.88,bottom=.16,hspace=.4,wspace=.12,left=.08,right=.98)
 for i,rel in enumerate(REL):
  for j,fe in enumerate(FE):
   ax=axes[i,j];s=summary[summary.relation.eq(rel)].iloc[0]
   for method,off,mk in [('TWFE_fixed',-.08,'s'),('Sun_Abraham',.08,'o')]:
    q=allr[allr.relation.eq(rel)&allr.fe.eq(fe)&allr.method.eq(method)&~allr.reference&allr.estimable]
    ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=mk,ls='none',color=colors[method],capsize=3,ms=5,label=labels[method])
    ax.scatter([-1+off],[0],facecolors='white',edgecolors=colors[method],marker=mk,s=35,zorder=5)
   ax.axhline(0,color='#999',ls='--',lw=1);ax.axvline(0,color='#c19245',ls=':',lw=1)
   no=support[support.relation.eq(rel)&support.connected.eq(0)].k.tolist()
   for k in no:ax.axvspan(k-.38,k+.38,color='#eeeeee',zorder=0);ax.text(k,plot_hi-4,'No tied\nobservations',ha='center',va='top',fontsize=8,color='#666')
   ax.set_title(REL[rel]+'\n'+('Individual + year FE' if fe=='I_YEAR' else 'Individual + province-by-year FE'),fontsize=14)
   ax.set_xticks(range(-4,5));ax.set_xlim(-4.5,4.5);ax.set_ylim(plot_lo,plot_hi);ax.grid(axis='y',alpha=.15)
   pp=joint[joint.relation.eq(rel)&joint.fe.eq(fe)].set_index('method').p
   fmt=lambda p:'<0.001' if p<.001 else f'{p:.3f}'
   ax.text(.02,.97,'Joint pretrend p: TWFE '+fmt(pp['TWFE_fixed'])+'; SA '+fmt(pp['Sun_Abraham']),transform=ax.transAxes,va='top',fontsize=9)
   ax.text(.98,.03,f'N = {int(s.N):,}; {int(s.people)} officials; {int(s.provinces)} provinces\n{int(s.connected_people)} tied officials in {int(s.connected_provinces)} provinces',transform=ax.transAxes,fontsize=9,ha='right')
   if j==0:ax.set_ylabel('Change in the promotion gap (pp)')
   if i==1:ax.set_xlabel('Years relative to first inspection (reference k = -1)')
 axes[0,0].legend(loc='lower right',bbox_to_anchor=(1,.12),frameon=False)
 fig.suptitle('Fixed pre-inspection hometown and school ties\nPromotion event studies | Full C08 controls | 95% province-clustered t CIs',fontsize=20,y=.98)
 fig.text(.08,.045,'Ties to either the provincial secretary or governor, frozen at the pre-inspection baseline. Unknown ties are excluded, not coded zero.\nHometown: same recorded home prefecture. School: at least six months of overlapping ordinary study, formed before 2012 and before current joint tenure.\nIdentical observations across the two FE structures within each relationship type; relationship samples differ. Gray periods have no tied observations: no estimate.\nReference k = -1 has no estimated CI. Points are not connected. Sparse tied officials/provinces limit inference; no four-post-period mean is identified.',fontsize=10)
 for suffix in ['png','svg']:fig.savefig(O/'figures'/('01_hometown_classmate_two_FE.'+suffix),dpi=180)
 plt.close(fig)
 # Individual relation figures avoid overly small text in the HTML page.
 for rel in REL:
  sub=allr[allr.relation.eq(rel)]
  fig,axes=plt.subplots(1,2,figsize=(15,6.5),sharey=True);fig.subplots_adjust(top=.77,bottom=.27,left=.08,right=.98,wspace=.1)
  for ax,fe in zip(axes,FE):
   for method,off,mk in [('TWFE_fixed',-.08,'s'),('Sun_Abraham',.08,'o')]:
    q=sub[sub.fe.eq(fe)&sub.method.eq(method)&~sub.reference&sub.estimable]
    ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=mk,ls='none',color=colors[method],capsize=3,ms=5,label=labels[method]);ax.scatter([-1+off],[0],facecolors='white',edgecolors=colors[method],marker=mk,s=35)
   ax.axhline(0,color='#999',ls='--');ax.axvline(0,color='#c19245',ls=':');ax.set_xticks(range(-4,5));ax.set_xlim(-4.5,4.5);ax.set_ylim(plot_lo,plot_hi);ax.grid(axis='y',alpha=.15)
   for k in support[support.relation.eq(rel)&support.connected.eq(0)].k:ax.axvspan(k-.38,k+.38,color='#eeeeee',zorder=0);ax.text(k,plot_hi-8,'NA',ha='center',color='#666')
   pp=joint[joint.relation.eq(rel)&joint.fe.eq(fe)].set_index('method').p
   ax.text(.02,.97,'Joint pretrend p: TWFE '+fmt(pp['TWFE_fixed'])+'; SA '+fmt(pp['Sun_Abraham']),transform=ax.transAxes,va='top',fontsize=9)
   ax.set_title('Individual + year FE' if fe=='I_YEAR' else 'Individual + province-by-year FE',fontsize=14);ax.set_xlabel('Years relative to first inspection')
  axes[0].set_ylabel('Change in the promotion gap (pp)');axes[0].legend(loc='lower right',frameon=False)
  s=summary[summary.relation.eq(rel)].iloc[0]
  fig.suptitle(REL[rel]+' | Fixed baseline ties\nFull C08 controls | 95% province-clustered t CIs',fontsize=19,y=.98)
  counts=support[support.relation.eq(rel)].sort_values('k').connected.astype(int).tolist()
  fig.text(.08,.07,f'N = {int(s.N):,}; {int(s.people)} officials; {int(s.provinces)} provinces. Tied observations at k=-4,...,+4: '+', '.join(map(str,counts))+'.\nGray periods: no tied observations; no estimate. Unknown ties are excluded. The reference is normalized, without an estimated CI.\nEconomics follow the official\'s appointment city (lagged one year). Sparse connected groups limit province-clustered inference.',fontsize=10)
  fig.savefig(O/'figures'/f'{rel}_event_study.png',dpi=180);fig.savefig(O/'figures'/f'{rel}_event_study.svg');plt.close(fig)
 text='''<h1>同乡与同期校友：固定事前关系的晋升事件研究</h1>
<p>2026-10-21｜沿用首次巡视时间、k=-1参照、完整C08控制。每种关系分别估计个人＋年份FE、个人＋省份×年份FE；每组展示TWFE及Sun–Abraham。</p>
<p class="note"><strong>结果概况：</strong>同乡版巡视后+1、+2期相对-1期为负，但事前联合检验也显著；同期校友版事前差异明显，事后支持更少。八个模型的三项事前交互系数联合检验均p&lt;0.05，不能据此解释为已经通过平行趋势检验的巡视因果效应。同乡关系者12人、同期校友8人，各自仅分布于4个省。</p>
<h2>定义与模型</h2><p>C0在k=-1年度行固定：当时与书记或省长任一人有该类关系记1；两人均可核实无关系才记0；其余未知排除。沿用年度上年末快照：2013批次对应2011年末、2014批次对应2012年末。不是随领导更替更新分组。</p>
<p>同乡＝CPED籍贯省与地级市相同，不是出生地或现任地。同期校友＝既有普通在校学习口径下，同校时间重叠至少六个月，关系在2012年前且早于双方当前共同任职开始；不是仅凭同校毕业或最高学历标签。</p>
<div class="equation">100 Promotion<sub>it</sub> = α<sub>i</sub> + λ<sub>t</sub> + Σ<sub>k≠−1</sub> β<sub>k</sub> C0<sub>i</sub> D<sub>pt</sub><sup>k</sup> + Σ<sub>k≠−1</sub> ρ<sub>k</sub>D<sub>pt</sub><sup>k</sup> + X′γ + ε<sub>it</sub></div>
<div class="equation">100 Promotion<sub>it</sub> = α<sub>i</sub> + λ<sub>pt</sub> + Σ<sub>k≠−1</sub> β<sub>k</sub> C0<sub>i</sub> D<sub>pt</sub><sup>k</sup> + X′γ + ε<sub>it</sub></div>
<p>Sun–Abraham把交互项进一步与巡视批次交互再聚合。固定C0被个人FE吸收；省份×年份FE吸收事件时间主效应。β是关系组晋升差距相对-1期的变化，不是当期绝对关系优势。两组都接受巡视，不能把无该类关系者称作未巡视组。</p>
<p>X＝年龄平方、任期及平方、行政级别、书记/市长身份，以及跟随官员当年任职城市的上年GDP增长、log人均GDP、log人口。线性年龄被个人＋时间FE吸收。Y保留原晋升定义。每种关系内两种FE使用相同完整样本；两种关系之间的样本不同，不强制交集。</p>
<h2>样本与各期支持</h2>'''+summary.to_html(index=False)+support.to_html(index=False)+'''<p class="note">同期校友缺失较多，同乡关系也少。没有关系组观测的时期没有可识别的系数，图中留空；不将软件可能省略的交互项记作零效应，也不计算+1至+4平均。省聚类区间的有效信息主要来自少数有关系者所在省，常规p值须谨慎看待。</p>'''
 for rel in REL:
  text+='<h2>'+('同乡' if rel=='hometown_prefecture' else '同期校友')+'</h2><img src="figures/'+rel+'_event_study.png" alt="'+REL[rel]+' event study">'
 text+='<h2>事前联合检验与全部结果</h2><p>原始p值，不按显著性选择规格。没有纳入此前大量探索的调整；本轮重点是样本支持、系数和区间。</p>'+joint.to_html(index=False)+'<details><summary>全部系数及不可识别原因</summary>'+allr[['relation','fe','method','k','b','lo','hi','p','estimable','reason']].to_html(index=False)+'</details>'
 text+='<p>限制：固定基期队列的回溯选择、早期校友边是否已形成、官员离任后的风险集，以及巡视时点的潜在内生性均保留。不能由事后不显著认定关系优势消失。</p><p><a href="全部结果_同乡同期校友.xlsx">Excel全部结果</a> · <a href="all_event_results.csv">CSV系数</a> · <a href="event_support.csv">各期样本支持</a> · <a href="code/hometown_classmate_event_study.py">可重跑代码</a></p>'
 html='<!doctype html><html lang="zh"><meta charset="utf-8"><title>同乡与同期校友晋升事件研究</title><style>body{max-width:1300px;margin:30px auto;padding:0 22px;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif;color:#243542}h2{margin-top:45px;border-bottom:2px solid #247f9f}img{width:100%;height:auto}table{border-collapse:collapse;font-size:13px;display:block;overflow:auto}th,td{padding:7px;border-bottom:1px solid #ddd}.equation,.note{padding:18px;background:#eef5f8;margin:20px 0}.note{background:#fff5df}a{color:#247f9f}</style>'+text+'</html>'
 (O/'index.html').write_text(html,encoding='utf-8')
 with pd.ExcelWriter(O/'全部结果_同乡同期校友.xlsx') as w:
  for name,df in [('样本',summary),('各期支持',support),('全部系数',allr),('事前联合检验',joint),('模型统计',stats),('基期分类',pd.read_csv(O/'baseline_classification.csv')),('独立点估计核验',valid),('TWFE标准误核验',secheck),('失败记录',fail)]:df.to_excel(w,sheet_name=name,index=False)
 checks={'8_models_complete':len(stats)==8,'no_failed_models':fail.empty,'independent_points_match':valid.point_error.max()<2e-5,'independent_TWFE_SE_match':secheck.se_error.max()<2e-5,'all_actual_SE_positive':result.se.gt(0).all(),'CI_uses_province_t':np.allclose(result.lo,result.b-t.ppf(.975,result.df)*result.se),'plot_does_not_clip_CI':plot_lo<=result.lo.min() and plot_hi>=result.hi.max(),'no_false_post4_average':not result.term.eq('post_average').any(),'unsupported_rows_NA':allr.loc[~allr.estimable,'b'].isna().all(),'reference_no_CI':allr.loc[allr.reference,'lo'].isna().all()}
 for r in pd.read_csv(O/'input_manifest.csv').itertuples():checks['input_unchanged_'+Path(r.path).name]=hashlib.sha256(Path(r.path).read_bytes()).hexdigest()==r.sha256
 (O/'validation_checks.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},ensure_ascii=False,indent=2),encoding='utf-8');assert all(checks.values()),checks
 # Add this new, separate analysis to the user's existing results page.
 main=B/'organized_main_results_corruption_checks_2026_10_21/index.html';h=main.read_text(encoding='utf-8');backup=main.parent/'code/index_before_hometown_school_extension.html'
 if not backup.exists():shutil.copy2(main,backup)
 marker='<!-- HOMETOWN_SCHOOL_EXTENSION -->'
 block=marker+'<h2>补充：同乡与同期校友的事件研究</h2><p>沿用固定巡视前分组、C08控制及两组FE。关系组很小，缺乏支持的后期留空。<strong>两类关系在两组FE与两种方法下的事前联合检验均p&lt;0.05，不能把事后系数解读为通过平行趋势的因果效应。</strong><a href="../'+O.name+'/index.html">查看模型、各期样本支持及全部结果</a>。</p><figure><img src="../'+O.name+'/figures/01_hometown_classmate_two_FE.png" alt="同乡与校友两组FE事件研究"></figure>'
 if marker in h:
  h=h[:h.index(marker)]+block+h[h.index('<h2>文件与核验</h2>',h.index(marker)):]
 else:h=h.replace('<h2>文件与核验</h2>',block+'<h2>文件与核验</h2>')
 main.write_text(h,encoding='utf-8');shutil.copy2(__file__,O/'code'/Path(__file__).name)
 print(summary.to_string(index=False));print(result[['relation','fe','method','k','b','lo','hi','p']].to_string(index=False));print('VALIDATION',checks)

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='report':report()
 else:raise ValueError('prepare or report')
