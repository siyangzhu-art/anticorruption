"""Union of pre-inspection hometown or school ties; same model specification."""
from pathlib import Path
import sys, importlib.util, json, shutil, hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd, numpy as np
from scipy.stats import t

engine_path=Path(__file__).with_name('hometown_classmate_event_study.py')
spec=importlib.util.spec_from_file_location('ties_engine',engine_path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
B=engine.B; O=B/'union_hometown_school_event_study_2026_10_21';REL='hometown_or_classmate'
engine.O=O;engine.REL={REL:'Hometown OR overlapping school ties'}

def csv(d,name):d.to_csv(O/name,index=False,encoding='utf-8-sig')
def report():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 m=pd.read_csv(O/'model_design.csv');design=pd.read_csv(O/'independent_design_and_points.csv');sup=pd.read_csv(O/'event_support.csv');summary=pd.read_csv(O/'sample_summary.csv');base=pd.read_csv(O/'baseline_classification.csv')
 r=pd.read_stata(O/'coefficients.dta');stats=pd.read_stata(O/'models.dta');j=pd.read_stata(O/'joint_tests.dta');fail=pd.read_stata(O/'failures.dta')
 assert fail.empty and len(stats)==4
 r['k']=r.term.map({engine.nm(k):k for k in engine.KS});r=r.merge(m,on='model_id',validate='m:1').merge(stats,on=['model_id','method'],suffixes=('','_stata'),validate='m:1')
 validation=r.merge(design[['model_id','method','k','python_b']],on=['model_id','method','k'],validate='1:1');validation['error_b']=(validation.b-validation.python_b).abs()
 assert validation.error_b.max()<2e-5
 sechecks=[]
 for mm in m.itertuples():
  d=pd.read_csv(O/f'data/{REL}_analysis_panel.csv.gz');kmodel=stats[stats.model_id.eq(mm.model_id)&stats.method.eq('TWFE_fixed')].iloc[0].K
  z=pd.DataFrame(engine.design(d,mm.fe,'TWFE_fixed',kmodel));z['model_id']=mm.model_id;sechecks.append(z)
 secheck=pd.concat(sechecks).merge(r[['model_id','method','k','se']],on=['model_id','method','k'],validate='1:1');secheck['error_se']=(secheck.se-secheck.python_se).abs();assert secheck.error_se.max()<2e-5
 rows=[]
 for x in design.to_dict('records'):
  q=r[r.model_id.eq(x['model_id'])&r.method.eq(x['method'])&r.k.eq(x['k'])]
  x.update(q.iloc[0].to_dict() if len(q) else dict(b=np.nan,se=np.nan,p=np.nan,lo=np.nan,hi=np.nan));x['reference']=False;rows.append(x)
 for mm in m.itertuples():
  for method in ['TWFE_fixed','Sun_Abraham']:rows.append(dict(model_id=mm.model_id,relation=REL,fe=mm.fe,method=method,k=-1,b=0.,lo=np.nan,hi=np.nan,p=np.nan,se=np.nan,estimable=True,reference=True,reason='Normalized reference; no estimated CI'))
 allr=pd.DataFrame(rows).sort_values(['fe','method','k']);j=j.merge(m,on='model_id',validate='m:1')
 csv(allr,'all_event_results.csv');csv(r,'estimated_coefficients.csv');csv(j,'joint_tests.csv');csv(stats,'model_stats.csv');csv(fail,'failed_models.csv');csv(validation,'independent_point_validation.csv');csv(secheck,'independent_TWFE_SE_validation.csv')
 # Show how the union changes the relationship group and the known-zero pool.
 source=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz');anchor=source[source.k.eq(-1)].copy()
 for rel,col in [('hometown_prefecture','H0'),('classmate_6m','S0')]:
  v=anchor[['legacy_'+rel+'_S','legacy_'+rel+'_G']];anchor[col]=np.where(v.eq(1).any(axis=1),1.,np.where(v.eq(0).all(axis=1),0.,np.nan))
 v=anchor[['H0','S0']];anchor['Union0']=np.where(v.eq(1).any(axis=1),1.,np.where(v.eq(0).all(axis=1),0.,np.nan))
 overlap=anchor[['person_id','name','H0','S0','Union0']].copy();overlap=overlap.merge(base[['person_id','C0']],on='person_id',validate='1:1');assert np.allclose(overlap.Union0,overlap.C0,equal_nan=True)
 csv(overlap,'baseline_overlap_audit.csv')
 s=summary.iloc[0]
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
 fig,axes=plt.subplots(1,2,figsize=(16,7.5),sharey=True);fig.subplots_adjust(left=.075,right=.98,top=.76,bottom=.29,wspace=.1)
 lo=min(-60,np.floor(r.lo.min()/20)*20);hi=max(60,np.ceil(r.hi.max()/20)*20)
 fm=lambda p:'<0.001' if p<.001 else f'{p:.3f}'
 for ax,fe in zip(axes,['I_YEAR','I_PXY']):
  for method,c,marker,off in [('TWFE_fixed','#c98432','s',-.085),('Sun_Abraham','#247f9f','o',.085)]:
   q=allr[allr.fe.eq(fe)&allr.method.eq(method)&allr.estimable&~allr.reference]
   ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=marker,ls='none',color=c,capsize=4,ms=6,label='TWFE' if method=='TWFE_fixed' else 'Sun-Abraham')
   ax.scatter([-1+off],[0],facecolors='white',edgecolors=c,marker=marker,s=40,zorder=5)
  ax.axhline(0,color='#999',ls='--',lw=1);ax.axvline(0,color='#c09546',ls=':',lw=1.2)
  for k in sup[sup.connected.eq(0)].k:ax.axvspan(k-.38,k+.38,color='#eeeeee',zorder=0);ax.text(k,hi-4,'No tied\nobservations',ha='center',va='top',fontsize=9,color='#666')
  jj=j[j.fe.eq(fe)].set_index('method').p
  ax.text(.02,.97,'Joint pretrend p: TWFE '+fm(jj['TWFE_fixed'])+'; SA '+fm(jj['Sun_Abraham']),transform=ax.transAxes,fontsize=10,va='top')
  ax.set_title('Individual + year FE' if fe=='I_YEAR' else 'Individual + province-by-year FE',fontsize=16,pad=12)
  ax.set_xlim(-4.5,4.5);ax.set_xticks(range(-4,5));ax.set_ylim(lo,hi);ax.grid(axis='y',alpha=.15);ax.set_xlabel('Years relative to first inspection (reference k = -1)')
 axes[0].set_ylabel('Change in the connection-related promotion gap (pp)');axes[0].legend(loc='lower right',frameon=False)
 fig.suptitle('Hometown OR overlapping school ties | Fixed pre-inspection group\nPromotion event study | Full C08 controls | 95% province-clustered t CIs',fontsize=21,y=.97)
 counts=', '.join(map(str,sup.sort_values('k').connected.astype(int)))
 fig.text(.075,.08,f'Identical N = {int(s.N):,} officer-years; {int(s.people)} officials; {int(s.provinces)} province clusters.\n{int(s.connected_people)} connected officials in {int(s.connected_provinces)} provinces. Connected observations at k=-4,...,+4: {counts}.\nUnion = hometown OR school tie to either provincial secretary or governor. All four component ties must be known zero to code unconnected.\nUnknown ties are excluded. Economics follow the official\'s appointment city (lagged one year).\nGray periods have no tied observations, not a zero effect. Reference has no estimated CI; points are not connected.',fontsize=10.5)
 for suffix in ['png','svg']:fig.savefig(O/'figures'/('01_union_ties_two_FE.'+suffix),dpi=180)
 plt.close(fig)
 checks={'four_models_estimated':len(stats)==4,'no_failures':fail.empty,'independent_points_match':validation.error_b.max()<2e-5,'independent_TWFE_SE_match':secheck.error_se.max()<2e-5,'positive_estimated_SE':r.se.gt(0).all(),'province_t_CI':np.allclose(r.lo,r.b-t.ppf(.975,r.df)*r.se),'baseline_union_matches':np.allclose(overlap.Union0,overlap.C0,equal_nan=True),'no_CI_clipping':lo<=r.lo.min() and hi>=r.hi.max(),'unsupported_not_zero':allr.loc[~allr.estimable,'b'].isna().all(),'reference_no_CI':allr.loc[allr.reference,'lo'].isna().all()}
 for rr in pd.read_csv(O/'input_manifest.csv').itertuples():checks['input_unchanged_'+Path(rr.path).name]=hashlib.sha256(Path(rr.path).read_bytes()).hexdigest()==rr.sha256
 assert all(checks.values()),checks
 (O/'validation_checks.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},ensure_ascii=False,indent=2),encoding='utf-8')
 with pd.ExcelWriter(O/'同乡或校友_合并关系_全部结果.xlsx') as w:
  for name,df in [('样本',summary),('各期支持',sup),('全部系数',allr),('事前联合检验',j),('关系重叠核验',overlap),('点估计核验',validation),('TWFE标准误核验',secheck),('模型统计',stats),('失败记录',fail)]:df.to_excel(w,sheet_name=name,index=False)
 reject=j.p.lt(.05).all()
 intro=('四个模型的事前联合检验均p&lt;0.05；不满足常规的事前平行差异趋势检验，不能将事后负系数解释成已识别的巡视因果效应。' if reject else '事前联合检验及全部逐点区间如下；不按显著性选择规格。')
 text=f'''<h1>同乡或同期校友：合并关系的晋升事件研究</h1><p>2026-10-21｜固定巡视前分组；TWFE与Sun–Abraham；个人＋年份、个人＋省份×年份两组FE；95%省聚类t区间。</p>
<h2>合并口径</h2><div class="equation">C0<sub>i</sub> = 1{{与基期省委书记或省长至少一人同乡，或者是同期校友}}</div>
<p>这是OR合并，不是同时满足两类关系，不加共事关系。四项分量（同乡×书记／省长、校友×书记／省长）任一已知为1即可归为关系组；只有四项都核实为0才归为无关系组；其余未知排除。</p>
<p>同乡＝CPED籍贯省＋地级市相同；同期校友＝合格普通学习经历中同校重叠至少6个月，形成于2012年前且早于双方当前共同任职。沿用k=-1年度行的上年末关系快照，2013批次为2011年末，2014批次为2012年末；固定后不随领导更替更新。</p>
<p>基期655人：合并关系21人，已知无关系238人，未知396人。严格保留未知会缩小对照组，所以结果不是前两张单独回归的加权平均。</p>
<h2>回归方程</h2><div class="equation">100 Promotion<sub>it</sub> = α<sub>i</sub> + λ<sub>t</sub> + Σ<sub>k≠−1</sub> β<sub>k</sub> C0<sub>i</sub>D<sub>pt</sub><sup>k</sup> + Σ<sub>k≠−1</sub>ρ<sub>k</sub>D<sub>pt</sub><sup>k</sup> + X′γ + ε<sub>it</sub></div>
<div class="equation">100 Promotion<sub>it</sub> = α<sub>i</sub> + λ<sub>pt</sub> + Σ<sub>k≠−1</sub> β<sub>k</sub> C0<sub>i</sub>D<sub>pt</sub><sup>k</sup> + X′γ + ε<sub>it</sub></div>
<p>Sun–Abraham进一步将关系交互项与巡视批次交互后聚合。β为关系组晋升差距相对k=-1的变化，不是当期绝对优势；无关系组也接受巡视。C0本身被个人FE吸收，省份×年份FE吸收事件时间主效应。</p>
<p>控制沿用完整C08：年龄平方、任期及平方、行政级别、书记／市长身份，以及跟随官员当年任职城市的上年GDP增长、log人均GDP、log人口。晋升定义、首次巡视对齐及主观察期2006—2017不变，展示k=-4至+4。</p>
<p class="note">{intro} 关系组所在省很少，常规省聚类推断也需谨慎。+4期没有关系组观测，留空，不能计算四期完整事后平均。</p>
<img src="figures/01_union_ties_two_FE.png" alt="同乡或校友合并关系：两种FE事件研究"><h2>样本与各期支持</h2>'''+summary.to_html(index=False)+sup.to_html(index=False)+'<h2>事前联合检验</h2>'+j.to_html(index=False)+'<details><summary>全部逐期结果</summary>'+allr[['fe','method','k','b','lo','hi','p','estimable','reason']].to_html(index=False)+'</details><p>固定基期队列仍有回溯选择、官员离任风险集变化和关系形成时间等限制；不以不显著判定关系作用消失。</p><p><a href="同乡或校友_合并关系_全部结果.xlsx">Excel全部结果</a> · <a href="all_event_results.csv">CSV系数</a> · <a href="code/union_hometown_school_event_study.py">可重跑代码</a></p>'
 html='<!doctype html><html lang="zh"><meta charset="utf-8"><title>同乡或校友合并关系事件研究</title><style>body{max-width:1300px;margin:30px auto;padding:0 24px;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif;color:#263744}img{width:100%;height:auto}h2{margin-top:40px;border-bottom:2px solid #247f9f}.equation,.note{padding:18px;background:#edf5f8;margin:20px 0}.note{background:#fff5df}table{border-collapse:collapse;display:block;overflow:auto;font-size:13px}th,td{padding:7px;border-bottom:1px solid #ddd}a{color:#247f9f}</style>'+text+'</html>'
 (O/'index.html').write_text(html,encoding='utf-8')
 main=B/'organized_main_results_corruption_checks_2026_10_21/index.html';h=main.read_text(encoding='utf-8');backup=main.parent/'code/index_before_union_ties.html'
 if not backup.exists():shutil.copy2(main,backup)
 marker='<!-- UNION_HOMETOWN_SCHOOL -->';block=marker+'<h2>补充：同乡或同期校友，合并关系</h2><p>任一关系成立即记1，未知不补0。<a href="../'+O.name+'/index.html">查看模型、样本支持与全部结果</a>。</p><p>'+intro+'</p><figure><img src="../'+O.name+'/figures/01_union_ties_two_FE.png" alt="同乡或校友合并关系事件研究"></figure>'
 if marker in h:h=h[:h.index(marker)]+block+h[h.index('<h2>文件与核验</h2>',h.index(marker)):]
 else:h=h.replace('<h2>文件与核验</h2>',block+'<h2>文件与核验</h2>')
 main.write_text(h,encoding='utf-8')
 for pp in [Path(__file__),engine_path,engine.helper]:shutil.copy2(pp,O/'code'/pp.name)
 print(summary.to_string(index=False));print(sup.to_string(index=False));print(r[['fe','method','k','b','lo','hi','p']].to_string(index=False));print(j[['fe','method','p']].to_string(index=False));print('VALIDATION',checks)

if __name__=='__main__':
 if sys.argv[1]=='prepare':
  engine.prepare()
  shutil.copy2(__file__,O/'code'/Path(__file__).name)
 elif sys.argv[1]=='report':report()
 else:raise ValueError('prepare or report')
