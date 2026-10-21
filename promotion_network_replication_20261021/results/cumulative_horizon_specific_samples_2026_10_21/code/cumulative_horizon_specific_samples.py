"""Each horizon uses only its own paired pre/post information. Old results stay intact."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.stats import t
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OLD=B/'cumulative_promotion_TWFE_12_24_36m';O=B/'cumulative_horizon_specific_samples_2026_10_21'
CTRL=['age0','age20','tenure0','tenure20','rank0','role0','growth0','lngdppc0','lnpop0']
MASKS={'Original':[],'Strict':[130000,350000,310000,120000,500000],'Plus_discipline':[130000,350000,310000,120000,500000,510000],'Plus_recent':[130000,350000,310000,120000,500000,510000,210000,620000]}
def save(d,name):d.to_csv(O/name,index=False,encoding='utf-8-sig')
def holm(p):
 p=np.asarray(p);ix=np.argsort(p);out=np.empty(len(p));out[ix]=np.minimum(1,np.maximum.accumulate(p[ix]*np.arange(len(p),0,-1)));return out

def prepare():
 for p in [O,O/'data',O/'code',O/'figures']:p.mkdir(parents=True,exist_ok=True)
 if (O/'coefficients.dta').exists():raise RuntimeError('Completed estimates exist. Use report, or a new output directory.')
 source=OLD/'cumulative_outcome_audit.csv.gz';a=pd.read_csv(source)
 assert not a.duplicated(['person_id','H','post']).any()
 flow=[];design=[];panels=[];drop=[];mid=0
 L=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/estimation.log", text replace','tempname rr ww ff','postfile `rr\' long model_id double(b se p lo hi N G df) using "`out\'/coefficients.dta", replace','postfile `ww\' long model_id double(p_wild) long rc using "`out\'/wild_tests.dta", replace','postfile `ff\' long model_id long rc using "`out\'/failures.dta", replace']
 for H in [12,24,36]:
  z=a[a.H.eq(H)].copy();npeople=z.person_id.nunique();pairs=z.groupby('person_id').Y.count().eq(2);ids=set(pairs.index[pairs]);paired=z[z.person_id.isin(ids)].copy()
  n=paired[paired.post.eq(0)].groupby('anchor_province').person_id.nunique();single=n[n.eq(1)].index
  dd=paired[paired.anchor_province.isin(single)].assign(exclusion='Singleton province within this horizon');drop.append(dd)
  d=paired[~paired.anchor_province.isin(single)].copy()
  # Independent ID/value match with the previous maximum-each-H sensitivity.
  previous=pd.read_stata(OLD/f'data/panel_maximum_each_H_{H}m.dta');assert set(d.person_id)==set(previous.person_id)
  q=d[['person_id','post','Y','C0']].merge(previous[['person_id','post','Y','C0']],on=['person_id','post'],suffixes=('_new','_old'),validate='1:1');assert np.allclose(q.Y_new,q.Y_old) and np.allclose(q.C0_new,q.C0_old)
  for variant,excluded in MASKS.items():
   p=d[~d.anchor_province.isin(excluded)].copy();p['CP']=p.C0*p.post;p['pid']=pd.factorize(p.person_id)[0]+1;p['pp']=pd.factorize(pd.MultiIndex.from_frame(p[['anchor_province','post']]))[0]+1
   assert p.groupby('person_id').size().eq(2).all() and p.groupby('person_id').C0.nunique().eq(1).all()
   assert p[['Y','C0']+CTRL].notna().all().all()
   csvname=f'data/panel_{variant}_{H}m.csv.gz';save(p,csvname);panels.append(p.assign(variant=variant))
   filename=f'data/panel_{variant}_{H}m.dta';cols=['person_id','pid','pp','post','anchor_province','H','C0','CP','Y']+CTRL;p[cols].to_stata(O/filename,write_index=False,version=118)
   n=p[p.post.eq(0)]
   flow.append(dict(variant=variant,H=H,eligible_people=npeople,paired_known_people=len(ids),horizon_unknown_people=npeople-len(ids),singleton_people=len(dd)//2,people=n.person_id.nunique(),rows=len(p),connected_people=int(n.C0.sum()),provinces=n.anchor_province.nunique(),connected_provinces=n[n.C0.eq(1)].anchor_province.nunique(),excluded_province_people=d.person_id.nunique()-n.person_id.nunique(),removed_connected_people=int(d[d.post.eq(0)].C0.sum()-n.C0.sum())))
   controls=['none','personal','full'] if variant=='Original' else ['full']
   for control in controls:
    mid+=1;design.append(dict(model_id=mid,variant=variant,H=H,control=control,fe='Individual + province-by-pre/post FE',N=len(p),G=p.anchor_province.nunique(),filename=filename))
    cov='' if control=='none' else 'c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0'
    fd='' if control=='none' else 'age0 age20 tenure0 tenure20 i.rank0 role0'
    if control=='full':cov+=' c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0';fd+=' growth0 lngdppc0 lnpop0'
    L += [f'use "`out\'/{filename}", clear','isid person_id post',f'capture noisily reghdfe Y CP {cov}, absorb(pid pp) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({mid}) (`rc\')','if `rc\'==0 {',f'assert e(N)=={len(p)}','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','quietly lincom CP, level(95)',f'post `rr\' ({mid}) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\') (`DD\')','}']
    if control=='full':
     L += [f'use "`out\'/{filename}", clear','keep person_id anchor_province post Y C0 '+ ' '.join(CTRL),'reshape wide Y, i(person_id) j(post)','gen double deltaY=Y1-Y0','egen prov=group(anchor_province)',f'regress deltaY C0 {fd} i.prov, vce(cluster anchor_province)','capture noisily boottest C0, cluster(anchor_province) reps(9999) seed(20261015) weight(webb) nograph','local rc=_rc',f'if `rc\'==0 post `ww\' ({mid}) (r(p)) (`rc\')',f'if `rc\'!=0 post `ww\' ({mid}) (.) (`rc\')']
 L += ['postclose `rr\'','postclose `ww\'','postclose `ff\'','log close','exit, clear']
 (O/'code/run_models.do').write_text('\n'.join(L)+'\n',encoding='utf-8');save(pd.DataFrame(flow),'sample_flow.csv');save(pd.DataFrame(design),'model_design.csv');save(pd.concat(drop),'horizon_specific_singleton_exclusions.csv');save(pd.concat(panels),'all_panels.csv.gz')
 inputs=[source,OLD/'all_TWFE_results.csv',B/'exclude_corruption_leader_provinces_2026_10_21/province_exclusion_evidence.csv'];save(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]),'input_manifest.csv')
 shutil.copy2(__file__,O/'code'/Path(__file__).name);print(pd.DataFrame(flow).to_string(index=False))

def report():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 m=pd.read_csv(O/'model_design.csv');flow=pd.read_csv(O/'sample_flow.csv');panels=pd.read_csv(O/'all_panels.csv.gz')
 r=pd.read_stata(O/'coefficients.dta').merge(m,on='model_id',suffixes=('','_design'),validate='1:1');w=pd.read_stata(O/'wild_tests.dta');fail=pd.read_stata(O/'failures.dta');assert len(r)==18 and fail.empty and len(w)==12 and w.rc.eq(0).all()
 r=r.merge(w[['model_id','p_wild']],on='model_id',how='left',validate='1:1');r['p_holm_3H']=np.nan;r['p_wild_holm_3H']=np.nan
 for variant in MASKS:
  ix=r.variant.eq(variant)&r.control.eq('full');r.loc[ix,'p_holm_3H']=holm(r.loc[ix,'p']);r.loc[ix,'p_wild_holm_3H']=holm(r.loc[ix,'p_wild'])
 original=r[r.variant.eq('Original')];main=original[original.control.eq('full')].sort_values('H')
 old=pd.read_csv(OLD/'all_TWFE_results.csv');oldmax=old[old['sample'].eq('maximum_each_H')&old.fe.eq('I_PXY')]
 verify=original.merge(oldmax[['H','control','b','se']],on=['H','control'],suffixes=('_new','_old'),validate='1:1');assert len(verify)==9 and np.allclose(verify.b_new,verify.b_old,atol=1e-8) and np.allclose(verify.se_new,verify.se_old,atol=1e-8)
 # Independently fit each first-difference equation; validate the point estimates.
 independent=[]
 for mm in m.itertuples():
  q=panels[panels.variant.eq(mm.variant)&panels.H.eq(mm.H)].copy();z=q.pivot(index='person_id',columns='post',values='Y');a=q[q.post.eq(0)].set_index('person_id').loc[z.index]
  X=[np.ones(len(a)),a.C0.to_numpy()]
  if mm.control!='none':X += [a[['age0','age20','tenure0','tenure20','role0']].to_numpy(),pd.get_dummies(a.rank0,drop_first=True,dtype=float).to_numpy()]
  if mm.control=='full':X += [a[['growth0','lngdppc0','lnpop0']].to_numpy()]
  X += [pd.get_dummies(a.anchor_province,drop_first=True,dtype=float).to_numpy()];X=np.column_stack(X);scale=np.linalg.norm(X,axis=0);X=X[:,scale>1e-10]/scale[scale>1e-10];bb=np.linalg.lstsq(X,(z[1]-z[0]).to_numpy(),rcond=1e-10)[0][1]/scale[1]
  target=r[r.model_id.eq(mm.model_id)].iloc[0].b;independent.append(dict(model_id=mm.model_id,b_python=bb,b_stata=target,error=bb-target))
 assert max(abs(x['error']) for x in independent)<1e-7
 save(r,'all_results.csv');save(main,'main_horizon_specific.csv');save(pd.DataFrame(independent),'independent_FD_point_checks.csv');save(verify,'comparison_to_preexisting_maximum_sample.csv')
 rates=panels[panels.variant.eq('Original')].groupby(['H','post','C0']).Y.agg(['size','mean','sum']).reset_index().rename(columns={'mean':'promotion_rate_pct','size':'officials'});save(rates,'raw_group_rates.csv')
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
 oldcommon=old[old['sample'].eq('common_all_H')&old.fe.eq('I_PXY')&old.control.eq('full')].sort_values('H')
 fig,ax=plt.subplots(figsize=(11,6.5));fig.subplots_adjust(left=.12,right=.98,bottom=.3,top=.8)
 for q,off,col,mk,label in [(main,-.09,'#247f9f','o','Each horizon: its own paired sample'),(oldcommon,.09,'#929ca4','s','Previous common cohort (422 officials)')]:
  xx=np.arange(3)+off;ax.errorbar(xx,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=mk,ls='none',capsize=5,color=col,ms=7,label=label)
 ax.axhline(0,color='#999',ls='--');ax.set_xticks(range(3),['12 months','24 months','36 months']);ax.set_ylabel('Change in the cumulative promotion gap (pp)');ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,loc='lower left');fig.suptitle('Cumulative promotion | Horizon-specific samples\nIndividual + province-by-pre/post FE | 95% province-clustered t CIs',fontsize=17,y=.98)
 txt=[]
 for rr in main.itertuples():
  s=flow[flow.variant.eq('Original')&flow.H.eq(rr.H)].iloc[0];txt.append(f'{int(rr.H)}m: {int(s.people)} officials ({int(s.connected_people)} tied); wild p={rr.p_wild:.3f}; Holm(3H)={rr.p_wild_holm_3H:.3f}')
 fig.text(.09,.055,'\n'.join(txt)+'\nOutcome: at least one promotion within each equal-length pre/post window, not employment at the endpoint.\nEach horizon requires only its own two known outcomes; samples differ across horizons. Points are not connected.',fontsize=10)
 for ext in ['png','svg']:fig.savefig(O/'figures'/f'01_horizon_specific_vs_previous.{ext}',dpi=180)
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(11,6));fig.subplots_adjust(left=.12,right=.98,bottom=.25,top=.8)
 for control,off,c,mk,label in [('none',-.18,'#929ca4','s','FE only'),('personal',0,'#c68436','^','Personal controls'),('full',.18,'#247f9f','o','Full baseline controls')]:
  q=original[original.control.eq(control)].sort_values('H');ax.errorbar(np.arange(3)+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=mk,ls='none',capsize=4,color=c,ms=6,label=label)
 ax.axhline(0,color='#999',ls='--');ax.set_xticks(range(3),['12 months','24 months','36 months']);ax.set_ylabel('Change in the cumulative promotion gap (pp)');ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,loc='lower left');fig.suptitle('Horizon-specific paired samples | Control sensitivity\nIndividual + province-by-pre/post FE | 95% province-clustered t CIs',fontsize=17,y=.98);fig.text(.09,.06,'12m: 497 officials; 24m: 466; 36m: 425. Identical observations across controls within each horizon.\nBaseline controls are interacted with Post; fixed C0 is absorbed by individual FE. Points are not connected.\nThis sample revision does not resolve retrospective cohort selection or informative outcome censoring.',fontsize=10)
 fig.savefig(O/'figures/02_control_sensitivity.png',dpi=180);plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(15,6.5),sharey=True);fig.subplots_adjust(left=.075,right=.98,bottom=.28,top=.79,wspace=.12)
 labels={'Original':'Original','Strict':'Strict exclusion','Plus_discipline':'+ Discipline','Plus_recent':'+ Recent cases'}
 for ax,H in zip(axes,[12,24,36]):
  q=r[r.H.eq(H)&r.control.eq('full')].set_index('variant').loc[list(MASKS)]
  for j,(variant,rr) in enumerate(q.iterrows()):ax.errorbar(j,rr.b,yerr=[[rr.b-rr.lo],[rr.hi-rr.b]],fmt='o',ls='none',capsize=4,color=['#247f9f','#c68436','#885889','#8b989d'][j]);ax.text(j,rr.hi+2,f'pW={rr.p_wild:.3f}',ha='center',fontsize=8)
  ax.axhline(0,color='#999',ls='--');ax.set_xticks(range(4),[labels[v] for v in MASKS],rotation=25,ha='right',fontsize=10);ax.set_title(f'{H} months');ax.grid(axis='y',alpha=.15)
 axes[0].set_ylabel('Change in the cumulative promotion gap (pp)');fig.suptitle('Corruption-related provincial-leader exclusion checks\nHorizon-specific samples | Full controls | 95% province-clustered t CIs',fontsize=17,y=.98);fig.text(.075,.055,'Same within-horizon sample rule, outcomes, baseline connections, controls and dates in every variant.\npW: province wild-cluster bootstrap p-value (Webb, 9,999 replications; seed 20261015).\nExcluding provinces does not remove all patron turnover and may change the comparison population.',fontsize=10);fig.savefig(O/'figures/03_corruption_exclusion_horizon_specific.png',dpi=180);plt.close(fig)
 merged=main.merge(flow[flow.variant.eq('Original')][['H','people','connected_people','provinces']],on='H',validate='1:1')
 table=merged[['H','people','connected_people','b','lo','hi','p','p_wild','p_wild_holm_3H']].copy()
 def main_table():
  z=table.copy();z.columns=['期限（月）','人数','关系组人数','θ（百分点）','95%下限','95%上限','常规p','wild p','wild Holm(3H)'];return z.to_html(index=False,float_format=lambda x:f'{x:.4f}')
 equation='<div class="equation">100 Y<sub>is</sub>(H) = α<sub>i</sub> + λ<sub>p,s</sub> + θ<sub>H</sub>C0<sub>i</sub>Post<sub>s</sub> + (X<sub>i0</sub>×Post<sub>s</sub>)′γ<sub>H</sub> + ε<sub>is</sub></div>'
 body='''<h1>累计晋升：每个期限使用自己的前后完整样本</h1><p>2026-10-21｜本次修改入样规则；保持晋升事件、关系基期、巡视日期、控制与主FE不变。原共同422人结果保留作对照。</p><h2>什么叫“12个月有信息”</h2><p>Y(H)是窗内是否至少晋升一次，不是第H个月末是否仍任职。记录到窗内晋升即可确认1；没有记录到晋升时，要有足够完整的履历才能确认0，否则未知。等长前后窗口TWFE需要该H的前期和后期两条结果，但不再要求其他H也完整。只看巡视后一次结果不能估计这里的个人FE前后差分。</p>'''+equation+'<h2>样本与主结果</h2>'+flow[flow.variant.eq('Original')].to_html(index=False)+main_table()+'<img src="figures/01_horizon_specific_vs_previous.png" alt="新版与旧共同样本对照"><h2>控制敏感性</h2><img src="figures/02_control_sensitivity.png" alt="同一期限内控制敏感性"><h2>同步更新的腐败排除检查</h2><img src="figures/03_corruption_exclusion_horizon_specific.png" alt="新版样本腐败排除检查">'+r[r.control.eq('full')][['variant','H','b','lo','hi','p','p_wild','p_wild_holm_3H']].to_html(index=False,float_format=lambda x:f'{x:.4f}')+'<p class="note">本次减少了为了跨期限统一名单而额外删人，但仍没有消除每个期限内的信息性删失。24／36个月前窗仍早于选人快照；原广义晋升仍含人大政协职级上升，事件标签待核验问题也未在本轮悄悄修改。各H样本不同，不能把系数跨H变化全解释为同一批人效应持续性。</p><p><a href="每期限独立样本_全部结果.xlsx">全部Excel</a> · <a href="all_results.csv">所有系数CSV</a> · <a href="sample_flow.csv">样本流程</a> · <a href="code/cumulative_horizon_specific_samples.py">可重跑代码</a></p>'
 (O/'index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>累计晋升每期限独立样本</title><style>body{max-width:1250px;margin:30px auto;padding:0 24px;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif;color:#263745}h2{margin-top:40px;border-bottom:2px solid #247f9f}img{width:100%;height:auto}table{border-collapse:collapse;display:block;overflow:auto;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ddd}.note,.equation{padding:18px;background:#fff5df;margin:20px 0}a{color:#247f9f}</style>'+body+'</html>',encoding='utf-8')
 with pd.ExcelWriter(O/'每期限独立样本_全部结果.xlsx') as w:
  for name,df in [('主结果',merged),('全部18规格',r),('样本流程',flow),('原始分组率',rates),('独立差分核验',pd.DataFrame(independent)),('旧最大样本复核',verify),('单例排除',pd.read_csv(O/'horizon_specific_singleton_exclusions.csv'))]:df.to_excel(w,sheet_name=name,index=False)
 checks={'18_models_complete':len(r)==18,'12_wild_tests_complete':len(wild:=pd.read_stata(O/'wild_tests.dta'))==12 and wild.rc.eq(0).all(),'original_counts_497_466_425':flow[flow.variant.eq('Original')].people.tolist()==[497,466,425],'independent_points_match':max(abs(x['error']) for x in independent)<1e-7,'nine_preexisting_maximum_models_match':np.allclose(verify.b_new,verify.b_old,atol=1e-8),'CI_uses_province_t':np.allclose(r.lo,r.b-t.ppf(.975,r.df)*r.se)}
 for x in pd.read_csv(O/'input_manifest.csv').itertuples():checks['unchanged_'+Path(x.path).name]=hashlib.sha256(Path(x.path).read_bytes()).hexdigest()==x.sha256
 assert all(checks.values()),checks;(O/'validation_checks.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},ensure_ascii=False,indent=2),encoding='utf-8');shutil.copy2(__file__,O/'code'/Path(__file__).name)
 # Update only the curated page, retaining a full backup and all old estimates.
 target=B/'organized_main_results_corruption_checks_2026_10_21/index.html';backup=O/'index_before_horizon_specific.html'
 if not backup.exists():shutil.copy2(target,backup)
 h=backup.read_text(encoding='utf-8')
 start=h.index('<h3>1.4 固定同一批官员');end=h.index('<h2 id="corruption">',start)
 img=lambda f,alt:'<figure><img src="../'+O.name+'/figures/'+f+'" alt="'+alt+'"></figure>'
 new='<section id="cumulative-horizon-specific"><h3>1.4 累计晋升：12／24／36个月各用自己的前后完整样本</h3><p><strong>新版：</strong>每个H只要求该H前后结果均可确定，不再要求六个窗口全部完整。12个月497人（57有关系）、24个月466人（52有关系）、36个月425人（46有关系），均25省；每H每人两行。<a href="../'+O.name+'/index.html">完整模型、样本流程与同步排省结果</a>。</p>'+equation+'<p>Y表示窗口内至少晋升一次，不是第H个月末是否有任职记录。正向事件可确认1；无正向事件须有充分履历覆盖才能确认0；其他记未知。个人FE吸收固定C0，省份×前后期FE吸收Post；这不是逐年省份×年份FE。</p>'+main_table()+img('01_horizon_specific_vs_previous.png','每期限独立样本与旧共同422人对照')+img('02_control_sensitivity.png','新版控制敏感性')+'<p>灰色旧共同422人结果仅作对照；新版各期限样本不同，不将系数跨H变化全部解释为同一批人的动态效应。24／36个月事前窗仍涉及较晚选人的回溯选择，晋升定义与信息性删失问题仍保留。原始p值与三期限Holm校正都报告，不判定“关系优势消失”。</p></section>'
 h=h[:start]+new+h[end:]
 h=h.replace('<h3>2.2 原联系对象是否仍在：提示性核查</h3>','<h3>2.2 原联系对象是否仍在：旧共同样本的描述性核查</h3><p><strong>口径说明：</strong>本小节45名关系官员及下一小节的描述统计保留自旧共同422人版本，不是新版每个期限各自的关系组人数。用于解释退出机制的局限，不能直接当作新版样本的比例。</p>')
 a0=h.index('<h3>2.4 整省排除后重跑主回归</h3>');a1=h.index('<h3>2.5 建议用于汇报的表述</h3>',a0)
 annual_table=pd.read_csv(target.parent/'data/corruption_checks_annual.csv');annual_table=annual_table[annual_table.fe.eq('I_CITY_YEAR')].pivot(index='variant',columns='estimator',values='b').reindex(list(MASKS))
 checktable=r[r.H.eq(24)&r.control.eq('full')][['variant','b','lo','hi','p_wild','p_wild_holm_3H']].copy()
 newcheck='<h3>2.4 整省排除后重跑：累计部分已同步使用各期限独立样本</h3><p>Strict排除河北、福建及原本不在主样本中的沪津渝；Plus_discipline再排四川；Plus_recent再排辽宁、甘肃。保留原关系、结果、日期、控制和FE。年度event study没有改样本，本次只将累计排省检查同步至新版每期限面板。</p>'+img('03_corruption_exclusion_horizon_specific.png','每期限独立样本的腐败排除检查')+'<p>新版24个月主规格：</p>'+checktable.to_html(index=False,float_format=lambda x:f'{x:.4f}')+'<p>各期限删样人数和有关系者人数见完整样本流程。整省排除仍不能替代逐一核验原支持者退出；按事后查处选省也改变比较总体。</p><details><summary>未改动的年度城市＋年份FE结果</summary>'+annual_table.to_html(float_format=lambda x:f'{x:.3f}')+'<figure><img src="figures/04_corruption_exclusion_annual.png" alt="未改动的年度排省检查"></figure></details>'
 h=h[:a0]+newcheck+h[a1:]
 a0=h.index('<h3>2.5 建议用于汇报的表述</h3>');a1=h.index('<!-- HOMETOWN_SCHOOL_EXTENSION -->',a0) if '<!-- HOMETOWN_SCHOOL_EXTENSION -->' in h[a0:] else h.index('<h2>文件与核验</h2>',a0)
 h=h[:a0]+'<h3>2.5 当前可用表述</h3><p>“累计晋升分析对每个期限分别使用其前后结果完整的官员样本，并将旧共同样本作为对照；条件关联、各期限样本构成与腐败相关排省结果分别报告。年度event study仍对FE敏感，较晚选人、信息性删失和晋升类型混合尚未解决，因此不能宣布巡视已因果性地消除关系作用。”</p>'+h[a1:]
 # Version the earlier audit so its 422-person diagnostics are not mistaken for the new samples.
 marker='<!-- METHODS_AUDIT_20261021 -->'
 if marker in h:
  p0=h.index(marker);p1=h.index('</div>',p0)+len('</div>');h=h[:p0]+marker+'<div style="padding:18px;background:#fff2d9;border-left:5px solid #bf8032;margin:24px 0"><strong>版本说明：</strong><a href="../audit_main_page_methods_2026_10_21/index.html">方法审查报告</a>核验的是旧共同422人版本；本页1.4及2.4已按用户要求改为每期限独立样本。旧报告中的样本数字属于历史版本；队列选择、删失与晋升分类的提醒仍适用。</div>'+h[p1:]
 h=h.replace('<a href="主结果与腐败官员检查_汇总.xlsx">下载汇总Excel</a>','<a href="../'+O.name+'/每期限独立样本_全部结果.xlsx">下载新版累计结果Excel</a>；<a href="主结果与腐败官员检查_汇总.xlsx">旧共同样本汇总Excel（历史版本）</a>')
 target.write_text(h,encoding='utf-8');save(main,'main_results_for_page.csv')
 print(main[['H','b','lo','hi','p','p_wild','p_wild_holm_3H']].to_string(index=False));print(flow[flow.variant.eq('Original')].to_string(index=False));print('VALIDATION',checks)

if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='report':report()
 else:raise ValueError('prepare or report')
