"""Restricted inspection-relative promotion analysis and a separate display-only crop."""
from pathlib import Path
import sys,json,shutil,importlib.util,html,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'inspection_k_minus3_plus2'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
shutil.copy2(BASE/'code/estimate_revised.py',OUT/'code/regression_engine.py')
spec=importlib.util.spec_from_file_location('regression_engine',OUT/'code/regression_engine.py');eng=importlib.util.module_from_spec(spec);spec.loader.exec_module(eng)
A=pd.read_csv(BASE/'annual_official_panel.csv.gz',low_memory=False)
restricted=A[A.k.between(-3,2)].copy()
restricted.to_csv(OUT/'annual_panel_k_minus3_plus2.csv.gz',index=False,encoding='utf-8-sig')
rows=[];status=[];checks=[];validation=[];mid=0
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
def run(d,meta,pooled=False):
 global mid
 mid+=1;meta={**meta,'model_id':mid}
 sup=eng.support(d,pooled);why=eng.reason(sup)
 if why:status.append({**meta,**sup,'status':why});return
 try:
  rr=eng.fit(d,meta['controls'],meta['fe'],pooled)
  for r in rr:rows.append({**meta,**r,'k_min':int(d.k.min()),'k_max':int(d.k.max())})
  status.append({**meta,**sup,'status':'OK'})
  # Independent dense dummy regression validates every displayed main model.
  if meta['role']=='all' and meta['controls']=='C1' and meta['fe']=='PXY':
   target=np.column_stack([d.CS,d.CG,d.CS*d.post,d.CG*d.post]) if pooled else d[['CS','CG']].to_numpy(float)
   Z=[np.ones((len(d),1)),target,d[['age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(d.provyear,drop_first=True,dtype=float).to_numpy()]
   X=np.column_stack(Z);norm=np.linalg.norm(X,axis=0);Xn=X/norm
   beta,_,rank,_=lstsq(Xn,d.Y.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');b=beta/norm;res=d.Y.to_numpy()*100-X@b
   bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10);codes=pd.factorize(d.province_code)[0];G=int(codes.max()+1)
   score=np.zeros((G,X.shape[1]));np.add.at(score,codes,Xn*res[:,None]);V=bread@score.T@score@bread*G/(G-1)*(len(d)-1)/(len(d)-rank);V=V/norm[:,None]/norm[None,:]
   for r in rr:
    j=1 if r['leader']=='S' else 2;L=np.zeros(X.shape[1]);L[j]=int(not pooled or r['estimand'] in ['pre','post'])
    if pooled:L[j+2]=int(r['estimand'] in ['post','change'])
    bd=float(L@b);sd=float(np.sqrt(L@V@L));validation.append(dict(model_id=mid,leader=r['leader'],estimand=r['estimand'],b_saved=r['b'],b_independent=bd,se_saved=r['se'],se_independent=sd,passed=abs(bd-r['b'])<1e-6 and abs(sd-r['se'])<1e-6))
 except Exception as ex:status.append({**meta,**sup,'status':str(ex)});raise

for role in ['all','mayor','secretary']:
 b=A.copy() if role=='all' else A[A.role.eq(role)]
 d=eng.sample(b,'promotion','cowork_6m','legacy','C1','maximal')
 # Display-only crop: each center still uses a full three-year window,
 # so the two edge windows extend outside [-3,+2].
 for center in range(-3,3):
  q=d[d.k.between(center-1,center+1)].copy()
  run(q,dict(kind='rolling_display_crop',role=role,controls='C1',fe='PXY',sampling='maximal',center=center,width=3))
 # Actual restricted sample; only complete three-year windows are estimated.
 trim=d[d.k.between(-3,2)].copy()
 for center in range(-2,2):
  q=trim[trim.k.between(center-1,center+1)].copy()
  run(q,dict(kind='rolling_restricted_sample',role=role,controls='C1',fe='PXY',sampling='maximal',center=center,width=3))
 # Keep the two leader connections jointly. Before=[-3,-1], After=[0,+2].
 for controls in ['C0','C1','C2']:
  for fe in ['PXY','PY','CITY_PXY']:
   q=eng.sample(b,'promotion','cowork_6m','legacy',controls,'maximal')
   q=q[q.k.between(-3,2)].copy();q['post']=q.k.ge(0).astype(float)
   run(q,dict(kind='pre_post_restricted_sample',role=role,controls=controls,fe=fe,sampling='maximal',center=np.nan,width=6),True)

R=pd.DataFrame(rows);ST=pd.DataFrame(status);VV=pd.DataFrame(validation)
save(R,'all_estimates.csv');save(ST,'model_status.csv');save(VV,'independent_dense_validation.csv')
orig=pd.read_csv(BASE/'all_estimates_validated.csv',low_memory=False)
old=orig[orig.kind.eq('rolling')&orig.unit.eq('annual')&orig.outcome.eq('promotion')&orig.relation.eq('cowork_6m')&orig.timing.eq('legacy')&orig.controls.eq('C1')&orig.fe.eq('PXY')&orig.sampling.eq('maximal')&orig.axis.eq('inspection_relative')&orig.width.eq(3)&orig.center.between(-3,2)]
new=R[R.kind.eq('rolling_display_crop')].merge(old,on=['role','center','leader'],suffixes=('_new','_old'),validate='1:1')
ck('Display crop exactly reproduces previous coefficients and CIs',len(new)==36 and all(np.allclose(new[c+'_new'],new[c+'_old'],atol=1e-8) for c in ['b','se','lo','hi','p']))
ck('Independent full-dummy estimates and SEs',len(VV)==26 and VV.passed.all(),len(VV))
ck('Restricted panel only k=-3..+2',restricted.k.between(-3,2).all())
ck('Annual person-year unique',not restricted.duplicated(['person_id','year']).any())
q=R[R.kind.ne('rolling_display_crop')]
ck('Restricted regressions never use observations outside interval',q.k_min.ge(-3).all() and q.k_max.le(2).all())
ck('Complete rolling centers are -2,-1,0,+1',set(R[R.kind.eq('rolling_restricted_sample')].center)=={-2.,-1.,0.,1.})
ck('All output intervals finite',np.isfinite(R[['b','lo','hi','se']]).all().all())
save(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
names={'all':'All city principals','mayor':'Mayors','secretary':'City party secretaries'}
leaders={'S':'Provincial party secretary','G':'Governor'}
gallery=[]
def export(fig,name,title):
 fig.savefig(OUT/'figures'/name,dpi=180);plt.close(fig);gallery.append((name,title))
def roll(kind,filename,roles=['all'],only_governor=False):
 leads=['G'] if only_governor else ['S','G'];fig,axes=plt.subplots(len(roles),len(leads),figsize=(7*len(leads),4.8*len(roles)+1.5),squeeze=False)
 for i,role in enumerate(roles):
  for j,lead in enumerate(leads):
   ax=axes[i,j];q=R[R.kind.eq(kind)&R.role.eq(role)&R.leader.eq(lead)].sort_values('center')
   ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1);ax.axvspan(-1.3,1.3,color='#eeeeee',zorder=0)
   ax.errorbar(q.center,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt='o',ls='none',ms=5,capsize=4,color='#287c9e')
   ax.set_xticks(range(-3,3));ax.set_xlim(-3.4,2.4);ax.set_ylabel('Promotion probability difference (pp)');ax.set_xlabel('Window center relative to first inspection');ax.grid(axis='y',alpha=.15)
   ax.set_title(names[role]+' | Tie to '+leaders[lead],fontsize=12)
 title='Three-year rolling regressions | '+('Display centers: -3 to +2' if kind=='rolling_display_crop' else 'Actual sample restricted to k = -3 to +2')
 fig.suptitle(title+'\n95% province-clustered confidence intervals',fontsize=15,y=.98)
 fig.subplots_adjust(top=.80 if len(roles)==1 else .91,bottom=.23 if len(roles)==1 else .14,hspace=.5,wspace=.27)
 note='Display crop only: edge windows use k=[-4,-2] and [1,3]; coefficients unchanged.' if kind=='rolling_display_crop' else 'Only full three-year windows: centers -2,-1,0,+1. No endpoint extrapolation.'
 fig.text(.07,.025,note+'\nGray windows contain inspection year. Both leader ties jointly; personal controls; province-by-year FE.\nPooled roles include a secretary indicator. Revised promotion definition; no connecting lines.\nThese are rolling association levels, not event-study effects normalized to k=-1.',fontsize=8.5)
 export(fig,filename,title)
roll('rolling_display_crop','01_governor_display_minus3_plus2.png',only_governor=True)
roll('rolling_display_crop','02_both_leaders_display_minus3_plus2.png')
roll('rolling_restricted_sample','03_actual_restriction_rolling.png')
roll('rolling_restricted_sample','04_actual_restriction_split_roles.png',roles=['all','mayor','secretary'])

M=R[R.kind.eq('pre_post_restricted_sample')&R.role.eq('all')&R.controls.eq('C1')&R.fe.eq('PXY')]
fig,axes=plt.subplots(1,2,figsize=(13,7))
for ax,lead in zip(axes,['S','G']):
 q=M[M.leader.eq(lead)].set_index('estimand');ax.axhline(0,color='gray',ls='--',lw=1)
 for j,est in enumerate(['pre','post','change']):
  r=q.loc[est];ax.errorbar(j,r.b,yerr=[[r.b-r.lo],[r.hi-r.b]],fmt=['o','s','D'][j],color=['#287c9e','#cf8735','#a9537e'][j],capsize=4)
  ax.annotate(f'{r.b:+.2f}',(j,r.b),xytext=(8,5),textcoords='offset points')
 ax.set_xticks([0,1,2],['Before\nk=-3,-2,-1','After\nk=0,+1,+2','After - Before']);ax.set_xlim(-.45,2.55);ax.set_title('Tie to '+leaders[lead]);ax.set_ylabel('Promotion probability difference (pp)');ax.grid(axis='y',alpha=.15)
 ax.text(.5,-.22,'Raw p: '+' / '.join(f'{q.loc[e,"p"]:.3f}' for e in ['pre','post','change']),ha='center',transform=ax.transAxes,fontsize=9)
fig.suptitle('Actual sample restricted to k = -3 to +2\nAll city principals | Before / after / change | 95% CIs',fontsize=15)
fig.subplots_adjust(top=.82,bottom=.31,wspace=.3)
fig.text(.065,.045,'Both leader ties jointly; personal and current-role controls; province-by-year FE. Province-clustered t intervals.\nInspection entry year is included as Post. Conditional associations; post-hoc window choice; no causal claim.\nNo equality inference from a post coefficient crossing zero. Compare the change directly.',fontsize=8.5)
export(fig,'05_actual_restriction_pre_post.png','Restricted sample: before / after / change')

with pd.ExcelWriter(OUT/'巡视相对时间_minus3_plus2.xlsx',engine='openpyxl') as w:
 for n,d in [('All_results',R),('Main_pre_post',M),('Restricted_panel',restricted),('Model_status',ST),('Independent_checks',VV),('Validation',pd.DataFrame(checks))]:
  d.to_excel(w,sheet_name=n,index=False);w.sheets[n].freeze_panes='A2'
method='''# 巡视相对时间 -3 至 +2
两种版本明确分开：
1. 显示范围裁剪：保留三年滚动窗中心s=-3,-2,-1,0,1,2。每点仍取[s-1,s+1]，边缘窗口实际用到k=-4和k=+3；逐点重新估计并核对原结果，系数和CI不变。
2. 实际样本限制：先删去k<-3或k>2的观测，再估计。完整三年窗中心只能为-2,-1,0,+1；不把两年端点冒充三年窗。另估计[-3,-1]与[0,+2]的前后交互回归，保留进驻年为Post。
主指标、关系、控制和推断沿用2006—2017修订版：行政级别提高/市长转书记/同级副部市级主官新任省级副省长；前2012且共同任职前至少六个月共事；CS与CG同时进入；年龄、任期及平方、基期行政级别，合并样本加书记职务指示；省×年FE；省聚类95%t置信区间；个人控制最大可用样本。
原始2006—2017面板先限定，再按首次巡视年份计算k，因此本轮实际为2010—2016中符合各省k区间的观测。不是把所有省统一以2012为断点。
保留两类职务分组、C0/C1/C2与三种FE的限定样本前后结果。新一轮未重新做wild bootstrap，主p值为省聚类常规t检验。独立全固定效应虚拟变量回归核验全部合并主图的系数与SE。
这是一项看到前图之后提出的探索性时间窗敏感性分析，不能作为独立确认性检验。滚动窗水平不是归一化事件研究，不将-1置零。
'''
(OUT/'methods_中文.md').write_text(method,encoding='utf8')
cards=''.join(f'<section><h2>{html.escape(t)}</h2><img src="figures/{n}" alt="{html.escape(t)}"></section>' for n,t in gallery)
(OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>巡视相对时间 -3 至 +2</title><style>body{max-width:1400px;margin:auto;padding:24px;font:16px system-ui}img{width:100%}section{margin:35px 0}h2{font-size:20px}</style><h1>巡视相对时间 −3 至 +2</h1><p>前两图仅裁剪中心年份；后三图限制实际样本。两者不可混淆。</p><p><a href="巡视相对时间_minus3_plus2.xlsx">Excel结果</a> · <a href="methods_中文.md">定义和方法</a></p>'+cards,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
summary=dict(restricted_rows=len(restricted),restricted_people=int(restricted.person_id.nunique()),actual_calendar_years=sorted(map(int,restricted.year.unique())),models=len(ST),successful=int(ST.status.eq('OK').sum()),validation_checks=checks,main_pre_post=M.to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,default=str),flush=True)
