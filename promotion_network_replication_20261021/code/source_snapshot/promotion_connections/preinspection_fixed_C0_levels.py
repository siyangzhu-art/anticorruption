"""Pre-inspection association levels on the existing main DID sample; no refitting DID."""
from pathlib import Path
import sys, hashlib, json, shutil, html, argparse
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np
import pandas as pd
from scipy.linalg import lstsq
from scipy.stats import t

B = Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O = B / 'preinspection_fixed_C0_levels_2026_10_21'
SOURCE = B / 'control_FE_sensitivity_post4/fixed_panel.csv.gz'
EC = ['gdp_growth_lag', 'lngdppc_lag', 'lnpop_lag']
PERSONAL = ['age', 'age2', 'tenure', 'tenure2']
STATA_PERSONAL = 'age age2 tenure tenure2 i.base_rank i.role_secretary'
SPECS = [
    dict(model_id=1, label='Province x year FE only', controls='', kind='pooled'),
    dict(model_id=2, label='Personal controls', controls=STATA_PERSONAL, kind='pooled'),
    dict(model_id=3, label='Personal + city economics (main)', controls=STATA_PERSONAL+' '+' '.join(EC), kind='pooled'),
    dict(model_id=4, label='Exact C08 columns (age squared only)', controls=STATA_PERSONAL.replace('age ', '', 1)+' '+' '.join(EC), kind='pooled'),
    dict(model_id=5, label='Annual levels: full controls', controls=STATA_PERSONAL+' '+' '.join(EC), kind='annual'),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def csv(d, name):
    d.to_csv(O / name, index=False, encoding='utf-8-sig')

def prepare():
    for p in [O, O/'code', O/'figures']:
        p.mkdir(parents=True, exist_ok=True)
    if (O/'stata_results.dta').exists():
        raise RuntimeError('Existing estimates found; do not overwrite a completed run.')
    a = pd.read_csv(SOURCE, low_memory=False)
    assert len(a) == 2807 and a.person_id.nunique() == 547
    assert not a.duplicated(['person_id','year']).any()
    assert a.groupby('person_id').C0.nunique().eq(1).all()
    d = a[a.k.between(-4,-1)].copy()
    assert len(d) == 1562
    d['py'] = pd.factorize(pd.MultiIndex.from_arrays([d.anchor_province, d.year]))[0]+1
    singleton = d.groupby('py').py.transform('size').eq(1)
    csv(d[singleton], 'pre_only_singletons.csv')
    d = d[~singleton].copy()
    assert not d[['Y','C0','age','age2','tenure','tenure2','base_rank','role_secretary']+EC].isna().any().any()
    assert d.Y.isin([0,100]).all() and d.C0.isin([0,1]).all()
    assert d.province_code.eq(d.anchor_province).all()
    assert d.economic_year.eq(d.year-1).all()
    for k in range(-4,0):
        d['c_m'+str(-k)] = d.C0*d.k.eq(k)
    d.to_csv(O/'preinspection_panel.csv.gz', index=False)
    cols = ['person_id','year','anchor_province','py','k','Y','C0','age','age2','tenure','tenure2','base_rank','role_secretary']+EC+['c_m4','c_m3','c_m2','c_m1']
    d[cols].to_stata(O/'preinspection_panel.dta', write_index=False, version=118)
    csv(pd.DataFrame(SPECS), 'model_specifications.csv')
    rates = d.groupby('C0').agg(officer_years=('Y','size'),people=('person_id','nunique'),provinces=('anchor_province','nunique'),promotion_events=('promotion','sum'),promotion_rate_pct=('Y','mean')).reset_index()
    annual = d.groupby(['k','C0']).agg(officer_years=('Y','size'),people=('person_id','nunique'),provinces=('anchor_province','nunique'),promotion_events=('promotion','sum'),promotion_rate_pct=('Y','mean')).reset_index()
    csv(rates, 'raw_pooled_rates.csv'); csv(annual, 'raw_annual_rates.csv')
    cell = d.groupby(['anchor_province','year','k']).agg(N=('Y','size'),connected=('C0','sum'),groups=('C0','nunique'),promotions=('promotion','sum')).reset_index()
    cell['both_groups'] = cell.groups.eq(2)
    csv(cell, 'province_year_identification_support.csv')
    people = d.groupby('person_id').agg(C0=('C0','first'),rows=('Y','size'),first_k=('k','min'),last_k=('k','max'),anchor_snapshot=('anchor_snapshot','first'),province=('anchor_province','first'),promotions=('promotion','sum')).reset_index()
    csv(people, 'preinspection_person_support.csv')
    d['row_precedes_anchor'] = pd.to_datetime(d.baseline_date).lt(pd.to_datetime(d.anchor_snapshot))
    audit = d.groupby(['k','C0']).agg(rows=('Y','size'),rows_before_snapshot=('row_precedes_anchor','sum')).reset_index()
    csv(audit, 'retrospective_anchor_audit.csv')
    flow = dict(source_rows=len(a), source_people=a.person_id.nunique(), pre_rows_before_singletons=int(a.k.between(-4,-1).sum()), pre_singletons=int(singleton.sum()), pre_rows=len(d), pre_people=d.person_id.nunique(), connected_people=d[d.C0.eq(1)].person_id.nunique(), provinces=d.anchor_province.nunique(), start=int(d.year.min()), end=int(d.year.max()), pre_promotion_events=int(d.promotion.sum()))
    (O/'sample_summary.json').write_text(json.dumps(flow,ensure_ascii=False,indent=2),encoding='utf8')
    manifest = pd.DataFrame([dict(path=str(SOURCE),sha256=sha(SOURCE)),dict(path=str(B/'all_methods_C08_event_study_gallery/methods_中文.md'),sha256=sha(B/'all_methods_C08_event_study_gallery/methods_中文.md'))])
    csv(manifest,'input_manifest.csv')
    lines = ['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/estimation.log", text replace','tempname rr',
             'postfile `rr\' long model_id str12 term double(b se p lo hi N G df K df_a df_nested residual_sd dense_b dense_se) using "`out\'/stata_results.dta", replace']
    for m in SPECS:
        terms = 'C0' if m['kind']=='pooled' else 'c_m4 c_m3 c_m2 c_m1'
        targets = terms.split()
        lines += ['use "`out\'/preinspection_panel.dta", clear','isid person_id year','local initialN=_N',
                  f'reghdfe Y {terms} {m["controls"]}, absorb(py) vce(cluster anchor_province)',
                  "assert e(N)==`initialN'",'local nn=e(N)','local gg=e(N_clust)','local dd=e(df_r)','local da=e(df_a)','local dn=e(df_a_nested)',
                  'quietly _ms_omit_info e(b)',"local kk=e(df_a)+colsof(e(b))-r(k_omit)"]
        for nm in targets:
            lines += [f'quietly lincom {nm}, level(95)',f'local b_{nm}=r(estimate)',f'local s_{nm}=r(se)',f'local p_{nm}=r(p)',f'local l_{nm}=r(lb)',f'local h_{nm}=r(ub)']
        # Audit residualized relation support against all nuisance covariates.
        for nm in targets:
            other = ' '.join(n for n in targets if n!=nm)
            lines += [f'quietly regress {nm} {other} {m["controls"]} i.py','predict double rr_'+nm+', residuals',f'quietly summarize rr_{nm}',f'local rs_{nm}=r(sd)']
        # Independent full dummy OLS; its CR1 small-sample correction counts all FE.
        lines += [f'quietly regress Y {terms} {m["controls"]} i.py, vce(cluster anchor_province)']
        for nm in targets:
            lines += [f'post `rr\' ({m["model_id"]}) ("{nm}") (`b_{nm}\') (`s_{nm}\') (`p_{nm}\') (`l_{nm}\') (`h_{nm}\') (`nn\') (`gg\') (`dd\') (`kk\') (`da\') (`dn\') (`rs_{nm}\') (_b[{nm}]) (_se[{nm}])']
    lines += ['postclose `rr\'','log close','exit, clear']
    (O/'code/run_preinspection.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
    shutil.copy2(__file__,O/'code'/Path(__file__).name)
    print(json.dumps(flow,ensure_ascii=False)); print(rates.to_string(index=False))

def independent_fit(d, m, K):
    names = ['C0'] if m['kind']=='pooled' else ['c_m4','c_m3','c_m2','c_m1']
    zcols = []
    if m['model_id']!=1:
        zcols = ['age2','tenure','tenure2'] if m['model_id']==4 else PERSONAL
    arrays = [d[names].to_numpy(float)]
    if zcols:
        arrays += [d[zcols].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(d.role_secretary,drop_first=True,dtype=float).to_numpy()]
    if m['model_id'] in [3,4,5]: arrays += [d[EC].to_numpy(float)]
    xx = np.column_stack(arrays)
    both = pd.DataFrame(np.column_stack([d.Y.to_numpy(),xx]))
    dm = both-both.groupby(d.py.to_numpy()).transform('mean')
    y = dm.iloc[:,0].to_numpy(); x = dm.iloc[:,1:].to_numpy()
    scale = np.linalg.norm(x,axis=0); live = scale>1e-10
    x = x[:,live]/scale[live]
    b,_,rank,_=lstsq(x,y,cond=1e-10)
    assert rank==x.shape[1], (m['model_id'],rank,x.shape)
    u=y-x@b;bread=np.linalg.inv(x.T@x)
    gc=pd.factorize(d.anchor_province)[0]; G=int(gc.max()+1);N=len(d)
    scores=np.zeros((G,x.shape[1]));np.add.at(scores,gc,x*u[:,None])
    V=bread@scores.T@scores@bread*G/(G-1)*(N-1)/(N-K)
    return b[:len(names)]/scale[:len(names)],np.sqrt(np.diag(V)[:len(names)])/scale[:len(names)]

def report():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d=pd.read_csv(O/'preinspection_panel.csv.gz',low_memory=False)
    r=pd.read_stata(O/'stata_results.dta').merge(pd.DataFrame(SPECS),on='model_id',validate='m:1')
    rates=pd.read_csv(O/'raw_pooled_rates.csv');annual=pd.read_csv(O/'raw_annual_rates.csv')
    checks=[]
    def ck(n,v,detail=''):
        checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
    ck('All eight target coefficients completed',len(r)==8 and r.model_id.nunique()==5)
    ck('All models use identical pre-inspection observations',r.N.eq(len(d)).all())
    ck('Source main DID sample is unchanged',all(sha(Path(x.path))==x.sha256 for x in pd.read_csv(O/'input_manifest.csv').itertuples()))
    ck('Strict pre-period only',d.k.between(-4,-1).all())
    ck('Promotion is known binary, not imputed',d.Y.isin([0,100]).all())
    ck('Fixed relation and anchor province per person',d.groupby('person_id').C0.nunique().eq(1).all() and d.groupby('person_id').anchor_province.nunique().eq(1).all())
    ck('Economics use the previous calendar year',d.economic_year.eq(d.year-1).all())
    ck('All target intervals finite',np.isfinite(r[['b','se','p','lo','hi']]).all().all())
    ck('Province clustered t degrees of freedom',r.df.eq(r.G-1).all())
    ck('All targets have residual support',r.residual_sd.gt(1e-8).all())
    ck('Full dummy OLS reproduces all points',np.allclose(r.b,r.dense_b,atol=1e-7))
    validations=[]
    for m in SPECS:
        q=r[r.model_id.eq(m['model_id'])]
        bb,ss=independent_fit(d,m,int(q.K.iloc[0]))
        for row,b,s in zip(q.itertuples(),bb,ss):
            validations.append(dict(model_id=m['model_id'],term=row.term,python_b=b,stata_b=row.b,python_se=s,stata_se=row.se))
        ck('Independent demeaned coefficients model '+str(m['model_id']),np.allclose(bb,q.b,atol=1e-7))
        ck('Independent clustered sandwich model '+str(m['model_id']),np.allclose(ss,q.se,atol=1e-7))
    ck('CIs use 95% t intervals',np.allclose(r.lo,r.b-t.ppf(.975,r.df)*r.se,atol=1e-8))
    ck('p-values reproduce t tests',np.allclose(r.p,2*t.sf(np.abs(r.b/r.se),r.df),atol=1e-8))
    csv(r,'adjusted_preinspection_results.csv');csv(pd.DataFrame(validations),'independent_verification.csv');csv(pd.DataFrame(checks),'validation_checks.csv')
    assert all(x['passed'] for x in checks), [x for x in checks if not x['passed']]
    main=r[r.model_id.eq(3)].iloc[0]
    exact=r[r.model_id.eq(4)].iloc[0]
    summary=json.loads((O/'sample_summary.json').read_text(encoding='utf8'))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#718093','#c08032','#247e9d']
    fig,axes=plt.subplots(1,2,figsize=(14.8,6.8),gridspec_kw={'width_ratios':[1,1.4]})
    ax=axes[0];q=rates.set_index('C0').loc[[0,1]]
    bars=ax.bar([0,1],q.promotion_rate_pct,color=['#8e9ba6','#247e9d'],width=.55)
    for bar,row in zip(bars,q.itertuples()):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.45,f'{row.promotion_rate_pct:.2f}%\n{int(row.promotion_events)}/{int(row.officer_years)}',ha='center',va='bottom')
    ax.set_xticks([0,1],['No baseline tie','Baseline tie']);ax.set_ylim(0,q.promotion_rate_pct.max()+6)
    ax.set_ylabel('Annual promotion rate (%)');ax.set_title('Observed promotion rates\nNo confidence intervals for descriptive counts');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    ax=axes[1];labels=['Province x year FE','+ Personal controls','+ City economics (main)']
    for i,mid in enumerate([1,2,3]):
        row=r[r.model_id.eq(mid)].iloc[0];y=2-i
        ax.errorbar(row.b,y,xerr=[[row.b-row.lo],[row.hi-row.b]],fmt='o',color=colors[i],capsize=5,ms=7,ls='none')
        ax.annotate(f'{row.b:+.2f} pp; p={row.p:.3f}',(row.b,y),xytext=(0,14),textcoords='offset points',ha='center',fontsize=10)
    ax.set_yticks([2,1,0],labels);ax.axvline(0,color='#888',ls='--',lw=1.2);ax.set_ylim(-.6,2.6)
    ax.set_xlabel('Conditional promotion gap: tied minus untied (pp)');ax.set_title('Pre-inspection association levels\n95% province-clustered t confidence intervals');ax.grid(axis='x',alpha=.15)
    fig.suptitle('Pre-inspection connection premium | Fixed baseline ties\nSame source sample as the main C08 event study; relative years -4 to -1',fontsize=17,y=.98)
    fig.text(.05,.035,f'N={len(d):,} officer-years; {summary["pre_people"]} officials; {summary["connected_people"]} tied officials; {summary["provinces"]} provinces. All three specifications use identical observations.\nPersonal: age and age squared, tenure and tenure squared, rank and role. Economics: lagged growth, log GDP per capita, log population in the official\'s appointment city.\nNo individual FE: a fixed tie is absorbed by individual FE. The cohort was selected at a later pre-inspection snapshot; earlier outcomes are retrospective. Descriptive associations.',fontsize=9)
    fig.subplots_adjust(top=.73,bottom=.23,left=.075,right=.98,wspace=.48)
    fig.savefig(O/'figures/01_preinspection_raw_and_adjusted.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(14.2,6.4))
    ax=axes[0]
    for c,color,marker,label,offset in [(0,'#8e9ba6','s','No baseline tie',-.08),(1,'#247e9d','o','Baseline tie',.08)]:
        q=annual[annual.C0.eq(c)].sort_values('k');ax.scatter(q.k+offset,q.promotion_rate_pct,color=color,marker=marker,s=42,label=label)
    ax.set_xticks([-4,-3,-2,-1]);ax.set_ylabel('Observed promotion rate (%)');ax.set_xlabel('Years relative to first inspection');ax.set_title('Observed rates by relative year');ax.legend(frameon=False);ax.grid(axis='y',alpha=.15)
    ax=axes[1];q=r[r.model_id.eq(5)].copy();q['k']=-q.term.str[3:].astype(int);q=q.sort_values('k')
    ax.errorbar(q.k,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt='o',ls='none',color='#247e9d',capsize=5)
    ax.axhline(0,color='#888',ls='--');ax.set_xticks([-4,-3,-2,-1]);ax.set_ylabel('Conditional promotion gap (pp)');ax.set_xlabel('Years relative to first inspection');ax.set_title('Full controls + province x year FE\n95% province-clustered confidence intervals');ax.grid(axis='y',alpha=.15)
    fig.suptitle('Pre-inspection levels | Fixed baseline tie to either provincial chief',fontsize=17,y=.97)
    fig.text(.055,.035,'Annual association levels, not differences normalized to k=-1. Each year, including -1, has an estimated coefficient and CI.\nIdentical source observations as the pooled pre-period model; no individual FE. Raw rates have no inferential CI.\nCoefficients and CIs are exploratory; the fixed cohort and baseline ties were selected after some of these retrospective outcomes.',fontsize=9)
    fig.subplots_adjust(top=.75,bottom=.23,left=.075,right=.98,wspace=.32)
    fig.savefig(O/'figures/02_preinspection_annual_levels.png',dpi=180);plt.close(fig)
    note=f'''# 当前固定关系组：巡视前描述性证据与条件差异

本轮只估计事前水平，不重新估计或改写主DID。输入为当前C08四FE对照共同样本（2807个人年、547人），只取k=-4至-1。所有规格相同{len(d)}个人年、{summary['pre_people']}人、{summary['connected_people']}名有关系官员、{summary['provinces']}省；实际日历年{summary['start']}—{summary['end']}。事前省年singleton删除{summary['pre_singletons']}行，单独导出。官员每年可观察风险集不平衡，逐期人数全部报告。

关系C0、基期名单、省份锚点和晋升完全沿用现有主样本。关系=2012年前形成、至少六个月共事的省委书记或省长任一关系。C0取k=-1年度行，而该行使用上年末快照：2013巡视省是2011-12-31；2014巡视省是2012-12-31。C0和锚点省不随年改变。未知晋升/关系不补0；保留现有晋升风险集，不填造晋升后续年份。

方程：100Promotion_it = delta C0_i + province×calendar-year FE + X_it gamma + error，仅k<0。没有个人FE，否则固定C0被吸收。主规格为个人+经济控制。由于移除了个人FE，恢复可识别的年龄线性项；另单列严格沿用原C08列（仅年龄平方）的敏感性，不按p值选模型。个人控制为年龄及平方、任期及平方、职级类别、书记/市长角色；经济为官员年度任职城市的上年GDP增长、对数人均GDP、对数人口。

主要完整控制delta={main.b:.6f}个百分点，SE={main.se:.6f}，95%CI=[{main.lo:.6f}, {main.hi:.6f}]，p={main.p:.6f}。严格原C08列delta={exact.b:.6f}，p={exact.p:.6f}。同时报告FE-only、个人控制和逐年完整控制，全部相同观测。逐年系数是绝对条件差异，-1不归零，因此也有CI。总体回归由可用个人年加权；不能称为等官员权重或每人四期平衡比较。

推断：Stata18 reghdfe，省聚类CR1与t(G-1)95%CI。省年FE嵌套于省聚类，按reghdfe原有限样本规则处理；独立显式虚拟变量OLS验证点估计（regress自己的自由度校正不同，因此其SE另存，不能混用）。Python省年去均值OLS和独立聚类sandwich验证全部系数/SE，有限样本校正K按Stata元数据核对。未进行新的bootstrap、窗口搜索或显著性筛选。

原始均值图只显示本样本真实晋升率、事件数与分母，不给描述性计数添加CI。调整后CI对应条件回归推断；CI跨0不证明关系无效或组间等效。各省年同时含两组的支持单独输出。

解释限制：固定名单在k=-1年度快照锚定，k=-4至-2较早观测属于回溯；早期晋升可能影响进入该名单，关系的早期真实形成也不一定早于每个回溯年份。控制和固定效应无法消除这种选择，不能声称已识别事前关系的因果优势。事前系数为正或不显著均如实报告，不能用旧动态省长关系结果替代固定C0证据。新后验描述不能追溯地消除更早规格探索。

可重跑：使用项目Python运行code/preinspection_fixed_C0_levels.py prepare，Stata执行code/run_preinspection.do，再运行Python report。prepare保护已完成结果不覆盖；需要重跑时选新输出目录。不生成PDF。
'''
    (O/'方法与结果.md').write_text(note,encoding='utf8')
    with pd.ExcelWriter(O/'巡视前固定关系_描述与条件回归.xlsx',engine='openpyxl') as x:
        for name,df in [('回归结果',r),('总体晋升率',rates),('逐期晋升率',annual),('省年比较支持',pd.read_csv(O/'province_year_identification_support.csv')),('名单时间核查',pd.read_csv(O/'retrospective_anchor_audit.csv')),('核验',pd.DataFrame(checks))]:df.to_excel(x,sheet_name=name,index=False)
    page='<html><meta charset="utf-8"><title>Pre-inspection connection premium</title><body style="max-width:1300px;margin:auto;font-family:Arial"><h1>Pre-inspection connection premium</h1>'
    for fn in ['01_preinspection_raw_and_adjusted.png','02_preinspection_annual_levels.png']:page+=f'<img style="width:100%" src="figures/{fn}">'
    page+='<pre style="white-space:pre-wrap">'+html.escape(note)+'</pre></body></html>'
    (O/'index.html').write_text(page,encoding='utf8')
    shutil.copy2(__file__,O/'code'/Path(__file__).name)
    print(r[['model_id','term','b','se','p','lo','hi','N','G']].to_string(index=False))
    print('Validation checks:',len(checks),'all passed')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','report']);args=ap.parse_args()
    prepare() if args.stage=='prepare' else report()
