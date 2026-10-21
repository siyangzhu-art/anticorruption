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
OUT=BASE/'Xi_province_union_rolling'
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
A['Xi_province']=np.where(A.Xi_G.eq(1)|A.Xi_S.eq(1),1.,np.where(A.Xi_G.eq(0)&A.Xi_S.eq(0),0.,np.nan))
province_roster=A[['year','baseline_date','province_code','province','S_person_id','S_name','G_person_id','G_name','Xi_S','Xi_G','Xi_S_status','Xi_G_status','Xi_province']].drop_duplicates()
save(province_roster,'province_Xi_group_by_year.csv')
ck('Province connected iff at least one leader has a documented Xi tie',A.Xi_province.eq(1).equals(A.Xi_G.eq(1)|A.Xi_S.eq(1)))
ck('Province group zero requires both leader statuses known zero',A.loc[A.Xi_province.eq(0),['Xi_G','Xi_S']].eq(0).all().all())
ck('Unique classification within province-year',A.groupby(['province_code','year']).Xi_province.nunique(dropna=False).le(1).all())
save(E,'Xi_all_cowork_evidence_including_excluded_central.csv')
save(local,'Xi_local_cowork_evidence.csv')
save(A.drop(columns='baseline_dt'),'annual_panel_with_Xi_status.csv.gz')

D=eng.sample(A,'promotion','cowork_6m','legacy','C1','maximal')
rows=[];status=[];dense=[];mid=0
for lead in ['G','S']:
 for xi in [0,1]:
  for center in range(-3,3):
   mid+=1;q=D[D.k.between(center-1,center+1)&D.Xi_province.eq(xi)].copy()
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
 ax.set_title(LEAD[lead]+' | Province: '+('Xi-connected' if xi else 'No observed Xi connection'),fontsize=11)
 ax.grid(axis='y',alpha=.15)
 ns='; '.join(f'{int(r.center):+d}: {int(r.N)} / {int(r.G)}' for r in st.itertuples())
 ax.text(.5,-.33,'Center: N / provinces\n'+ns,transform=ax.transAxes,ha='center',fontsize=7.7)

fig,axes=plt.subplots(2,2,figsize=(15,11))
for i,l in enumerate(['G','S']):
 for j,xi in enumerate([0,1]):panel(axes[i,j],l,xi)
fig.suptitle('City-principal promotion returns to provincial-leader ties\nProvince-year groups: governor OR secretary has a pre-2012 local coworking tie to Xi',fontsize=16,y=.98)
fig.subplots_adjust(top=.86,bottom=.22,hspace=.88,wspace=.23)
foot='Three-year windows; displayed centers -3 to +2 (edge windows use k=-4 and +3). Revised promotion; pooled mayors and secretaries.\nBoth city-to-provincial-leader ties jointly; personal and role controls; province-by-year FE; 95% province-clustered t CIs.\nProvince connected = either leader has a pre-2012 local tie to Xi; group 0 requires both leader statuses known zero.\nGray: window contains inspection year. Unsupported cells are blank; no relaxation of the original minimum-10-province rule.\nProvince groups can change with leadership turnover. Central co-membership and school work excluded; private ties are not observed.'
fig.text(.065,.035,foot,fontsize=8.5)
fig.savefig(OUT/'figures/01_four_panels_Xi_province.png',dpi=170);plt.close(fig)
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

method='''# 按省份当年与Xi的关系分组：四格滚动回归

本轮依用户明确选择定义省份分组：该省当年（基期上一年12月31日）省委书记或省长至少一人与习近平有已形成的、2012年前地方共事关系，则XiProvince=1。只有两人的关系状态都可判断且均为0，才令XiProvince=0。一人未知且另一人为0，省份状态未知，不补0；一人有明确正关系即归1，不受另一人未知影响。
分组单位为省×年；同一省同一年所有市级官员采用完全相同分组。它不是把某省永久标为connected，也不是分别按书记自身/省长自身分组；人员更替可改变省份分组。province_Xi_group_by_year.csv逐年列出两位领导及其状态。

四格：两行分别估计市级官员与省长、省委书记关系的晋升系数；两列分别是XiProvince=0、=1。每一省份分组/窗口内，CS和CG同时进入同一回归，四格图只展示对应系数。XiProvince分组在两行完全相同。
因变量沿用修订后的年度实际晋升：行政级别提升/市长升市委书记/副部级市级主官新任副省长亦计晋升。市长和书记合并，控制当前职务、年龄及平方、任期及平方、基期行政级别，省×年FE。两类关系均为至少六个月、2012前且共同任职前形成的共事关系。
习近平关系仍严格依据CPED习近平person_id=406的全部同单位至少六个月地方共事证据；排除中央机构共同任职、学校工作单位。证据必须不晚于基期且早于2012。无正证据只有在具备可比地方履历且不存在同单位日期歧义时才记0；否则未知。它衡量履历关系，不声称观察私人关系或忠诚。

三年居中窗显示中心-3至+2；各点使用[s-1,s+1]，边缘实际包含k=-4和+3。省聚类95%t区间，不连线，灰色表示窗口含巡视年。主样本仍从2006—2017年度面板取符合窗口的观测。
沿用原至少10省、10晋升事件、CS/CG各10个有/无关系观测和系数可识别要求。XiProvince=1各窗只有2—4省，12个对应面板点不满足省数要求，因此不输出其系数或CI；这不是零效应或不显著，也不是两组没有差别。每格列出N/省数，全部失败记录保存。不能通过把省份内许多城市当成独立省级关系案例扩大有效样本。
两个行的同一分组/窗口使用同一回归设计，24个目标面板窗口实质对应12个分组窗口回归；其中XiProvince=0的6个回归可报告两项系数。脚本为核验每项面板分别复算，因此保留24条目标支持记录。
全部成功拟合由独立完整FE虚拟变量回归核验系数与SE。没有按显著性筛选、没有放宽阈值、没有重做wild bootstrap。不能凭当前图判断两类省份关系晋升回报是否不同，更不识别巡视的因果作用。
'''
(OUT/'methods_中文.md').write_text(method,encoding='utf8')
with pd.ExcelWriter(OUT/'按省级Xi关系分组_四格回归.xlsx',engine='openpyxl') as w:
 for name,d in [('Panel_estimates',P),('Window_support',ST),('All_coefficients',R),('Xi_leader_year',ROSTER),('Province_group_year',province_roster),('Xi_local_evidence',local),('Xi_all_evidence',E),('Validation',pd.DataFrame(checks)),('Independent_check',V)]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2'
page='<!doctype html><meta charset="utf-8"><title>按省级Xi关系分组四格图</title><style>body{max-width:1500px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}</style><h1>按省份与习近平关系分组：四组滚动回归</h1><p>右侧Xi-connected省份组每窗仅2—4省，未满足原至少10省规则，故不报告系数/CI。空白不代表零效应。</p><p><a href="按省级Xi关系分组_四格回归.xlsx">Excel结果及支持表</a> · <a href="methods_中文.md">方法说明</a></p><img src="figures/01_four_panels_Xi_province.png">'
for fn in gallery:page+='<h2>'+html.escape(fn)+'</h2><img src="figures/'+fn+'">'
(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
summary=dict(models_requested=len(ST),models_supported=int(ST.status.eq('OK').sum()),displayed_points=len(P),checks_passed=all(c['passed'] for c in checks),unsupported_status_counts=ST.loc[ST.status.ne('OK'),'status'].value_counts().to_dict(),status_by_panel=ST.groupby(['leader','Xi_group']).agg(min_provinces=('G','min'),max_provinces=('G','max'),min_N=('N','min'),max_N=('N','max')).reset_index().to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
save(pd.DataFrame([dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [BASE/'annual_official_panel.csv.gz',NET/'relationship_evidence_pre2012.csv.gz',CLASS/'workplace_classification.csv.gz']]),'input_manifest.csv')
archive=BASE/'按省级Xi关系分组_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
