"""Four requested governor/secretary by Xi-tie panels, with original support rules.
No external data and no relaxation of minimum-cluster rules to populate panels.
"""
from pathlib import Path
import sys,json,shutil,importlib.util,html,hashlib,zipfile
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
BASE=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'
NET=ROOT/'result/cped_pre_anticorruption_person_network_20261019'
CLASS=ROOT/'result/cped_city_province_connections_20261019'
OUT=BASE/'Xi_stratified_rolling'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True);(OUT/'figures').mkdir(exist_ok=True)
shutil.copy2(BASE/'code/estimate_revised.py',OUT/'code/regression_engine.py')
spec=importlib.util.spec_from_file_location('regression_engine',OUT/'code/regression_engine.py');eng=importlib.util.module_from_spec(spec);spec.loader.exec_module(eng)
def save(d,name):d.to_csv(OUT/name,index=False,encoding='utf-8-sig')
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))

A=pd.read_csv(BASE/'annual_official_panel.csv.gz',low_memory=False)
A['baseline_dt']=pd.to_datetime(A.baseline_date)
E=pd.read_csv(NET/'relationship_evidence_pre2012.csv.gz',low_memory=False)
E=E[(E.person_a.eq(406)|E.person_b.eq(406))&E.relation.eq('cowork_6m')].copy()
E['leader_id']=E.person_b.where(E.person_a.eq(406),E.person_a).astype(int)
E['leader_name']=E.name_b.where(E.person_a.eq(406),E.name_a)
E['formation_dt']=pd.to_datetime(E.formation_date)
E['local_cowork']=~E.match_key.str.contains(r'\|840000\||^学校\|',na=False)
local=E[E.local_cowork].copy()
first=local.groupby('leader_id').formation_dt.min().to_dict()
J=pd.read_csv(CLASS/'workplace_classification.csv.gz',low_memory=False)
for c in ['start','end']:J[c]=pd.to_datetime(J[c],errors='coerce')
J['is_local']=~J.workplace_key.str.contains(r'\|840000\||^学校\|',na=False)
J['threshold']=J.start+pd.DateOffset(months=6)
eligible=J[J.work_eligible&J.is_local&J.dates_valid&J.threshold.le(J.end)]
basis=eligible.groupby('person_id').threshold.min().to_dict()
xi_keys=set(J.loc[J.person_id.eq(406)&J.is_local&J.work_eligible,'workplace_key'])
ambiguous=J[J.work_eligible&J.is_local&~J.dates_valid&J.workplace_key.isin(xi_keys)]
amb_ids=set(ambiguous.person_id)

cache={};roster=[]
def xi_status(pid,dt):
 if pd.isna(pid):return np.nan,'provincial_leader_missing',pd.NaT
 pid=int(pid);cut=min(dt,pd.Timestamp('2011-12-31'))
 key=(pid,cut)
 if key in cache:return cache[key]
 form=first.get(pid,pd.NaT)
 if pid==406:ans=(np.nan,'Xi_himself_excluded',pd.NaT)
 elif pd.notna(form) and form<=cut:ans=(1.,'documented_pre2012_local_cowork',form)
 elif basis.get(pid,pd.Timestamp.max)<=cut and basis.get(406,pd.Timestamp.max)<=cut and pid not in amb_ids:
  ans=(0.,'no_documented_local_cowork_with_comparison_basis',form)
 else:ans=(np.nan,'insufficient_or_ambiguous_career_coverage',form)
 cache[key]=ans;return ans
for lead in ['G','S']:
 vals=[xi_status(pid,dt) for pid,dt in zip(A[lead+'_person_id'],A.baseline_dt)]
 A['Xi_'+lead]=[v[0] for v in vals]
 A['Xi_'+lead+'_status']=[v[1] for v in vals]
 A['Xi_'+lead+'_formation']=[v[2] for v in vals]
 for _,r in A[['year','baseline_date','province_code','province',lead+'_person_id',lead+'_name','Xi_'+lead,'Xi_'+lead+'_status','Xi_'+lead+'_formation']].drop_duplicates().iterrows():
  roster.append(dict(year=r.year,baseline_date=r.baseline_date,province_code=r.province_code,province=r.province,leader_role=lead,leader_id=r[lead+'_person_id'],leader_name=r[lead+'_name'],xi_tie=r['Xi_'+lead],xi_status=r['Xi_'+lead+'_status'],formation_date=r['Xi_'+lead+'_formation']))
ROSTER=pd.DataFrame(roster);save(ROSTER,'province_leader_Xi_status_by_year.csv')
save(E,'Xi_all_cowork_evidence_including_excluded_central.csv')
save(local,'Xi_local_cowork_evidence.csv')
save(A.drop(columns='baseline_dt'),'annual_panel_with_Xi_status.csv.gz')

D=eng.sample(A,'promotion','cowork_6m','legacy','C1','maximal')
rows=[];status=[];dense=[];mid=0
for lead in ['G','S']:
 for xi in [0,1]:
  for center in range(-3,3):
   mid+=1;q=D[D.k.between(center-1,center+1)&D['Xi_'+lead].eq(xi)].copy()
   sup=eng.support(q);why=eng.reason(sup)
   target='C'+lead
   nprovvariation=int(q.groupby('province_code')[target].nunique().gt(1).sum()) if len(q) else 0
   meta=dict(model_id=mid,leader=lead,Xi_group=xi,center=center,width=3,requested_k_lo=center-1,requested_k_hi=center+1,distinct_provincial_leaders=q[lead+'_person_id'].nunique(),provinces_with_target_tie_variation=nprovvariation,**sup)
   if why:status.append({**meta,'status':why});continue
   try:
    fit=eng.fit(q,'C1','PXY',False)
    for r in fit:rows.append({**meta,**r,'requested_leader':lead,'estimated_leader':r['leader']})
    status.append({**meta,'status':'OK'})
    # Independent full FE-dummy regression validates both coefficients in all
    # supported models, not only a preferred sign/window.
    chunks=[np.ones((len(q),1)),q[['CS','CG','age','age2','tenure','tenure2','role_secretary']].to_numpy(float),pd.get_dummies(q.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q.provyear,drop_first=True,dtype=float).to_numpy()]
    X=np.column_stack(chunks);norm=np.linalg.norm(X,axis=0);Xn=X/norm
    b,_,rank,_=lstsq(Xn,q.Y.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');b=b/norm
    u=q.Y.to_numpy()*100-X@b;bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10)
    gc=pd.factorize(q.province_code)[0];G=int(gc.max()+1);score=np.zeros((G,X.shape[1]));np.add.at(score,gc,Xn*u[:,None]);V=bread@score.T@score@bread*G/(G-1)*(len(q)-1)/(len(q)-rank);V=V/norm[:,None]/norm[None,:]
    for rr,col in zip(fit,[1,2]):
     se=float(np.sqrt(V[col,col]));dense.append(dict(model_id=mid,estimated_leader=rr['leader'],b=rr['b'],b_independent=b[col],se=rr['se'],se_independent=se,passed=abs(rr['b']-b[col])<1e-6 and abs(rr['se']-se)<1e-6))
   except Exception as ex:status.append({**meta,'status':str(ex)});raise
R=pd.DataFrame(rows);ST=pd.DataFrame(status);V=pd.DataFrame(dense)
save(R,'all_supported_coefficients.csv');save(ST,'all_window_support_and_failures.csv');save(V,'independent_dense_validation.csv')
# A model estimates both CS and CG; each requested panel shows only its
# corresponding leader coefficient.
P=R[R.requested_leader.eq(R.estimated_leader)].copy();save(P,'four_panel_estimates.csv')
ck('Unique annual person years',not A.duplicated(['person_id','year']).any())
ck('Xi statuses binary or missing',all(A['Xi_'+l].dropna().isin([0,1]).all() for l in ['G','S']))
ck('Xi himself not assigned zero',all(A.loc[A[l+'_person_id'].eq(406),'Xi_'+l].isna().all() for l in ['G','S']))
ck('No future Xi ties',all(A.loc[A['Xi_'+l].eq(1),'Xi_'+l+'_formation'].le(A.loc[A['Xi_'+l].eq(1),'baseline_dt']).all() for l in ['G','S']))
ck('All positive Xi ties pre2012',all(A.loc[A['Xi_'+l].eq(1),'Xi_'+l+'_formation'].lt(pd.Timestamp('2012-01-01')).all() for l in ['G','S']))
ck('Xi local evidence excludes central committee and school workplace keys',not local.match_key.str.contains(r'\|840000\||^学校\|',na=False).any())
ck('Exactly 24 requested leader/group/window models',len(ST)==24 and not ST.duplicated(['leader','Xi_group','center']).any())
ck('Every supported model meets original support rules',all(eng.reason(r._asdict())=='' for r in ST[ST.status.eq('OK')].itertuples()))
ck('No unsupported estimates plotted',set(P.model_id)<=set(ST.loc[ST.status.eq('OK'),'model_id']))
ck('Every supported model independently checked',len(V)==2*ST.status.eq('OK').sum() and V.passed.all(),len(V))
ck('No original relation or outcome altered',all(A[c].equals(pd.read_csv(BASE/'annual_official_panel.csv.gz',usecols=[c])[c]) for c in ['promotion','legacy_cowork_6m_G','legacy_cowork_6m_S']))
save(pd.DataFrame(checks),'validation_checks.csv');assert all(c['passed'] for c in checks)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
LEAD={'G':'Governor','S':'Provincial party secretary'}
def panel(ax,lead,xi):
 q=P[P.requested_leader.eq(lead)&P.Xi_group.eq(xi)].sort_values('center')
 st=ST[ST.leader.eq(lead)&ST.Xi_group.eq(xi)].sort_values('center')
 ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1);ax.axvspan(-1.3,1.3,color='#eeeeee',zorder=0)
 if len(q):
  ax.errorbar(q.center,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt='o',ls='none',color='#287c9e',capsize=4,ms=4.5)
  ax.set_ylabel('Promotion probability difference (pp)')
 else:
  ax.set_ylim(-1,1);ax.set_yticks([])
  ax.text(.5,.68,'Insufficient cluster support\nNo coefficient or CI reported',ha='center',va='center',transform=ax.transAxes,fontsize=11,color='#8c3c30',bbox=dict(facecolor='white',edgecolor='#d5b7b0',alpha=.95))
  ax.text(.5,.26,'Original rule: at least 10 provinces per window',ha='center',transform=ax.transAxes,fontsize=9)
  ax.set_ylabel('Not estimable under support rules')
 ax.set_xlim(-3.4,2.4);ax.set_xticks(range(-3,3));ax.set_xlabel('Window center relative to first inspection')
 ax.set_title(LEAD[lead]+' | '+('Pre-2012 local coworking tie to Xi' if xi else 'No observed pre-2012 local coworking tie to Xi'),fontsize=11)
 ax.grid(axis='y',alpha=.15)
 ns='; '.join(f'{int(r.center):+d}: {int(r.N)} / {int(r.G)}' for r in st.itertuples())
 ax.text(.5,-.33,'Center: N / provinces\n'+ns,transform=ax.transAxes,ha='center',fontsize=7.7)

fig,axes=plt.subplots(2,2,figsize=(15,11))
for i,l in enumerate(['G','S']):
 for j,xi in enumerate([0,1]):panel(axes[i,j],l,xi)
fig.suptitle('City-principal promotion returns to provincial-leader ties\nStratified by the corresponding leader\'s pre-2012 local coworking tie to Xi',fontsize=16,y=.98)
fig.subplots_adjust(top=.86,bottom=.22,hspace=.88,wspace=.23)
foot='Three-year windows; displayed centers -3 to +2 (edge windows use k=-4 and +3). Revised promotion; pooled mayors and secretaries.\nBoth city-to-provincial-leader ties jointly; personal and role controls; province-by-year FE; 95% province-clustered t CIs.\nXi ties must predate the observation and 2012. Central co-membership and school workplaces excluded; unknown status excluded.\nGray: window contains inspection year. Unsupported cells are blank; no relaxation of the original minimum-10-province rule.\nGroup 0 means no documented qualifying tie with usable career coverage; it does not establish the absence of a private connection.'
fig.text(.065,.035,foot,fontsize=8.5)
fig.savefig(OUT/'figures/01_four_panels_Xi_stratified.png',dpi=170);plt.close(fig)
gallery=[]
for lead in ['G','S']:
 for xi in [0,1]:
  fig,ax=plt.subplots(figsize=(10,7.5));panel(ax,lead,xi)
  fig.suptitle('Three-year rolling regressions | Centers -3 to +2\n95% CIs where original support rules are met',fontsize=14)
  fig.subplots_adjust(top=.79,bottom=.41,left=.13,right=.97)
  fig.text(.065,.025,foot,fontsize=7.5)
  fn=f'{lead}_Xi{xi}.png';fig.savefig(OUT/'figures'/fn,dpi=170);plt.close(fig);gallery.append(fn)
for f in (OUT/'figures').glob('*.png'):
 with Image.open(f) as im:im.verify()

method='''# 省级领导与习近平事前地方共事关系：四组滚动回归

四格：省长有/无Xi地方共事关系、省委书记有/无Xi地方共事关系。每格因变量是原修订版市级官员晋升，解释变量仍为市级官员与对应省级领导的事前共事关系，而不是XiTie本身。每个分组中CS、CG同时进入，图只取对应领导的系数。合并市长与市委书记，加当前职务指示。

Xi关系依据CPED习近平person_id=406的全部六个月共事证据，排除中央机构编码840000及学校工作单位，保留地方的确切同工作单位重叠。共事日期必须早于2012，且不晚于当期基期日（上一年12月31日）。有证据=1；无证据且双方有事前可比履历且没有同单位缺失日期歧义=0；其他为未知并排除。习近平本人不定义为与自己有/无关系。0表示未观察到这种履历关系，不表示没有私人关系或不忠诚。未纳入同乡/校友；中央同期任职单列保留，不能混入主组。

使用2006—2017年原面板；三年居中窗，显示中心-3,-2,-1,0,1,2。实际窗口分别[s-1,s+1]，所以不是严格样本k∈[-3,2]。个人控制C1最大样本：年龄和平方、任期和平方、基期行政级别；省×年FE；CS与CG同时进入；省聚类95%t(G-1)区间。不连线，灰窗含巡视年。Xi组按各年基期在任省级领导动态归属，个人既有关系不取消。

沿用原支持要求：至少10省、10个晋升事件、CS与CG各至少10个有关系和10个无关系观测，且两系数分别可识别。Xi有地方共事关系组每窗仅0—3省，因此不得报告其合格系数/CI。这是信息不足，不是零效应或不显著。图在相应格留空并列每窗N/省数；没有事后放宽阈值填图。

全部24个目标分组窗口的支持和失败原因保存，所有成功模型由独立全FE虚拟变量回归核验两项系数与SE。未对本轮重做wild bootstrap，也未进行有Xi/无Xi差异的正式交互检验；由于Xi组省数少，不从这张图推出中央网络与地方网络效果不同。
'''
(OUT/'methods_中文.md').write_text(method,encoding='utf8')
with pd.ExcelWriter(OUT/'Xi关系分组_四格滚动回归.xlsx',engine='openpyxl') as w:
 for name,d in [('Panel_estimates',P),('Window_support',ST),('All_coefficients',R),('Xi_leader_year',ROSTER),('Xi_local_evidence',local),('Xi_all_evidence',E),('Validation',pd.DataFrame(checks)),('Independent_check',V)]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2'
page='<!doctype html><meta charset="utf-8"><title>Xi关系分组四格图</title><style>body{max-width:1500px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}</style><h1>省级领导与习近平关系：四组滚动回归</h1><p>右侧有Xi关系两格的窗口仅0—3省，未满足原至少10省规则，故不报告系数/CI。空白不代表零效应。</p><p><a href="Xi关系分组_四格滚动回归.xlsx">Excel结果及支持表</a> · <a href="methods_中文.md">方法说明</a></p><img src="figures/01_four_panels_Xi_stratified.png">'
for fn in gallery:page+='<h2>'+html.escape(fn)+'</h2><img src="figures/'+fn+'">'
(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
summary=dict(models_requested=len(ST),models_supported=int(ST.status.eq('OK').sum()),displayed_points=len(P),checks_passed=all(c['passed'] for c in checks),unsupported_status_counts=ST.loc[ST.status.ne('OK'),'status'].value_counts().to_dict(),status_by_panel=ST.groupby(['leader','Xi_group']).agg(min_provinces=('G','min'),max_provinces=('G','max'),min_N=('N','min'),max_N=('N','max')).reset_index().to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
save(pd.DataFrame([dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [BASE/'annual_official_panel.csv.gz',NET/'relationship_evidence_pre2012.csv.gz',CLASS/'workplace_classification.csv.gz']]),'input_manifest.csv')
archive=BASE/'Xi关系分组_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
