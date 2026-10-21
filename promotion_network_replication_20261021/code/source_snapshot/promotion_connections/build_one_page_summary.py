"""One A3 landscape PDF: all current model families, actual results, explicit estimands."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from pypdf import PdfReader
import pypdfium2 as pdfium

B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'one_page_complete_summary_2026_10_21'
for p in [O,O/'code',O/'data']:p.mkdir(parents=True,exist_ok=True)
PDF=O/'中央巡视_关系与晋升_完整模型与结果_一页A3.pdf'
CN=FontProperties(fname=r'C:\Windows\Fonts\simhei.ttf')
G=B/'all_methods_C08_event_study_gallery'
sources={
 'pre':B/'preinspection_fixed_C0_levels_2026_10_21/adjusted_preinspection_results.csv',
 'raw':B/'preinspection_fixed_C0_levels_2026_10_21/raw_pooled_rates.csv',
 'pre_FE':B/'preinspection_FE_combinations_2026_10_21/all_FE_results.csv',
 'pre_joint':B/'preinspection_FE_combinations_2026_10_21/joint_preperiod_change_tests.csv',
 'events':G/'all_methods_full_controls_event_coefficients.csv',
 'annual':G/'annual_C08_all_contrasts.csv',
 'cumulative':B/'organized_main_results_corruption_checks_2026_10_21/data/main_cumulative.csv',
 'exclusions':B/'organized_main_results_corruption_checks_2026_10_21/data/corruption_checks_cumulative.csv',
}
data={k:pd.read_csv(p) for k,p in sources.items()}
P=data['pre'];F=data['pre_FE'];J=data['pre_joint'];E=data['events'];A=data['annual'];C=data['cumulative'];X=data['exclusions'];RAW=data['raw']
assert len(P)==8 and len(F)==19 and len(E)==144
assert len(A[A.term.eq('post_average')])==12 and set(C.H)=={12,24,36}
for k,d in data.items():d.to_csv(O/'data'/f'{k}.csv',index=False,encoding='utf-8-sig')
manifest=pd.DataFrame([dict(dataset=k,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for k,p in sources.items()]);manifest.to_csv(O/'source_manifest.csv',index=False,encoding='utf-8-sig')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.65,'pdf.fonttype':42,'ps.fonttype':42,'mathtext.fontset':'dejavusans'})
fig=plt.figure(figsize=(420/25.4,297/25.4),facecolor='white')
BLUE='#247e9d';ORANGE='#c58232';GRAY='#74818c';PURPLE='#805789';INK='#233543'
def text(x,y,s,size=8.5,cn=False,**kw):
 if cn:s=s.replace('⁰','0').replace('−','-').replace('₀','0')
 return fig.text(x,y,s,fontsize=size,fontproperties=CN if cn else None,va='top',**kw)
def rule(y):fig.add_artist(plt.Line2D([.023,.978],[y,y],transform=fig.transFigure,color='#cad3d9',lw=.65))
def pstr(v):return '<.001' if v<.001 else f'{v:.3f}'
def est(r):return f'{r.b:+.2f} [{r.lo:.2f}, {r.hi:.2f}]'
def forest(ax,rows,labels,colors=None):
 for i,(r,lab) in enumerate(zip(rows,labels)):
  color=colors[i] if colors else BLUE;y=len(rows)-1-i
  ax.errorbar(r.b,y,xerr=[[r.b-r.lo],[r.hi-r.b]],fmt='o',ls='none',color=color,capsize=2.5,ms=3.7,lw=.9)
 ax.set_yticks(range(len(rows)-1,-1,-1),labels);ax.axvline(0,color='#999',ls='--',lw=.7);ax.grid(axis='x',alpha=.15);ax.set_ylim(-.5,len(rows)-.35)

text(.025,.975,'中央巡视、地方关系与官员晋升｜完整模型与结果',18,cn=True,color=INK)
text(.975,.97,'2026-10-21  |  ONE PAGE / A3 LANDSCAPE',8,ha='right',color=GRAY)
text(.025,.943,'当前结论：事前存在正向条件关联；巡视后关系差距的变化依赖FE，尚不足以确认“关系优势被消除”。',10.3,cn=True,color=BLUE)
text(.025,.917,'定义：Y=100×年度是否晋升；C⁰=事前与省委书记/省长任一人至少共事6个月；k=t−G，G为基期省首次巡视年，k=−1为参照。',8.7,cn=True)
rule(.899)

# Equations are vector math text; X and FE meanings are explicitly linked below.
text(.025,.887,'M1 事前水平（k=−4,…,−1）：固定C⁰的平均条件关联；无个人FE。',9,cn=True,color=INK)
text(.035,.865,r'$Y_{it}=\delta C_i^0+\lambda_{pt}+X_{it}^{\prime}\gamma+\varepsilon_{it}$',10)
text(.025,.839,'M2 事件研究：F∈{I+Y, I+P×Y, I+C+Y, I+C+P×Y}；主口径I+P×Y。',9,cn=True,color=INK)
text(.035,.817,r'$Y_{it}=F+\sum_{k\ne-1}\beta_k C_i^0\,1[t-G_p=k]+X_{it}^{\prime}\gamma+\varepsilon_{it}$',9.5)
text(.035,.791,r'Sun–Abraham: '+r'$\sum_g\sum_{k\ne-1}\delta_{gk}C_i^0 1[G_p=g]1[t-G_p=k]$'+r'$\ \rightarrow\ \beta_k=\sum_g w_{gk}\delta_{gk}$',8.8)
text(.035,.768,'动态关系TWFE另含C_it主项，并将交互项中的C⁰替换为C_it；事前个人FE只估计相对−1的变化。',8,cn=True)

text(.615,.887,'M3 LP-DiD：ΔhY=Y(G+h)-Y(G-1)；m0h为无关系组条件均值。',8.6,cn=True,color=INK)
text(.625,.866,r'$\tau_h^{RA}=E[\Delta_hY-m_{0h}(X,F)\mid C^0=1],\quad F=\mathrm{cohort/province}$',8.7)
text(.615,.841,'M4 DoubleML-DiD：交叉拟合m0h、e=P(C0=1|X)；π=E[C0]。',8.6,cn=True,color=INK)
text(.625,.821,r'$\tau_h=E\!\left[\left\{\frac{C^0}{\pi}-\frac{(1-C^0)e(X)}{\pi(1-e(X))}\right\}(\Delta_hY-m_{0h}(X))\right]$',8.7)
text(.615,.798,'M5 累计TWFE：H=12/24/36月，等长前后窗口是否至少晋升一次。',8.8,cn=True,color=INK)
text(.625,.779,r'$100Y_{is}(H)=\alpha_i+\lambda_{p,s}+\theta_H C_i^0Post_s+(X_{i0}\!\times\!Post_s)^{\prime}\gamma_H+u_{is}$',8.6)
rule(.751)

# A: observed pre-period and sensitivity. Distinct samples visibly separated.
text(.025,.742,'A  事前关联及城市FE敏感性',10,cn=True,color=INK)
text(.025,.721,'原始率：有关系17.06%，无关系14.44%（差2.62pp）。',8.3,cn=True)
ax=fig.add_axes([.112,.493,.173,.201])
pre_rows=[P[P.model_id.eq(i)].iloc[0] for i in [1,2,3]]+[F[F.model_id.eq(i)].iloc[0] for i in [1,2,3]]
forest(ax,pre_rows,['P×Y','+ Personal','+ Economics','P×Y (core)','C+Y (core)','C+P×Y (core)'],[GRAY,ORANGE,BLUE,GRAY,ORANGE,BLUE])
ax.axhline(2.5,color='#c8c8c8',lw=.7);ax.set_xlabel('Absolute pre-period gap (pp)');ax.tick_params(axis='y',labelsize=8)
text(.025,.452,'前3行：N=1,562，542人，26省；后3行共同FE样本：',8,cn=True)
text(.025,.438,'N=1,456，441人，25省。固定C⁰被个人FE吸收。',8,cn=True)

# B: every current fixed-C0 annual FE specification, both estimators.
text(.321,.742,'B  Sun–Abraham / 固定关系TWFE：四种FE',10,cn=True,color=INK)
text(.321,.721,'蓝圆=Sun–Abraham；橙方=TWFE；N=2,807，547人，26省。',8.2,cn=True)
FE=['I_YEAR','I_PXY','I_CITY_YEAR','I_CITY_PXY'];SHORT=['I+Y','I+P×Y','I+C+Y','I+C+P×Y']
for n,(fe,lab) in enumerate(zip(FE,SHORT)):
 x=.35+(n%2)*.192;y=.604 if n<2 else .476
 ax=fig.add_axes([x,y,.164,.090])
 for meth,color,marker,off in [('Sun_Abraham',BLUE,'o',-.09),('TWFE_fixed',ORANGE,'s',.09)]:
  q=E[E.method.eq(meth)&E.fe.eq(fe)].sort_values('k');q=q[q.k.ne(-1)]
  ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=marker,ls='none',ms=2.6,capsize=1.8,lw=.75,color=color)
  ax.scatter([-1+off],[0],s=13,facecolors='white',edgecolors=color,marker=marker,zorder=4)
 ax.axhline(0,color='#999',ls='--',lw=.65);ax.axvline(0,color='#c99745',ls=':',lw=.7);ax.set_xticks([-4,-2,-1,0,2,4]);ax.set_xlim(-4.5,4.5);ax.set_ylim(-65,65);ax.set_yticks([-40,0,40]);ax.set_title(lab,pad=3);ax.grid(axis='y',alpha=.13)
 if n%2==0:ax.set_ylabel('Gap change (pp)')
 if n>=2:ax.set_xlabel('Years to first inspection',labelpad=2)

# C: both LP-DiD FE choices and both DML learners; all post horizons.
text(.755,.742,'C  LP-DiD / DoubleML：事后四期',10,cn=True,color=INK)
ax=fig.add_axes([.793,.493,.178,.201])
series=[('LPDID | cohort',BLUE,'o',-.18,'LP: cohort'),('LPDID | province',ORANGE,'s',-.06,'LP: province'),('DoubleML | Ridge_Logit_econ',PURPLE,'^',.06,'DML: Ridge/Logit'),('DoubleML | RandomForest_econ',GRAY,'D',.18,'DML: forest')]
for s,color,marker,off,label in series:
 q=E[E.series.eq(s)&E.k.between(1,4)].sort_values('k');assert len(q)==4
 ax.errorbar(q.k+off,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=marker,ls='none',color=color,ms=3,capsize=2,lw=.8,label=label)
ax.axhline(0,color='#999',ls='--',lw=.7);ax.set_xticks([1,2,3,4]);ax.set_ylim(-85,85);ax.set_ylabel('Gap change (pp)');ax.set_xlabel('Post-inspection horizon h');ax.grid(axis='y',alpha=.13);ax.legend(fontsize=8,loc='upper center',frameon=False,ncol=1)
text(.755,.452,'各期N=340/274/168/43；有关系人数38/32/17/4。',8,cn=True)
text(.755,.438,'LP为回归调整；DML为3省折×5重复，无个人/省FE。',8,cn=True)

# Left bottom: pre-period-only FE results and exact CI numbers.
text(.025,.407,'A1 完整控制：系数 [95% CI]；p值',9,cn=True,color=INK)
for y,row,lab in zip([.386,.369,.352],[P[P.model_id.eq(3)].iloc[0],F[F.model_id.eq(1)].iloc[0],F[F.model_id.eq(3)].iloc[0]],['原样本P×Y','共同样本P×Y','共同样本C+P×Y']):
 text(.025,y,lab,8,cn=True);text(.125,y,est(row)+f'; p={pstr(row.p)}',8)
text(.025,.325,'A2 个人FE：平均(−4,−3,−2)相对−1的变化',9,cn=True,color=INK)
for n,(fe,lab) in enumerate(zip(FE,SHORT)):
 row=F[F.fe.eq(fe)&F.term.eq('pre_average_change')].iloc[0];jj=J[J.model_id.eq(row.model_id)].iloc[0]
 text(.025,.303-n*.021,lab,8.1);text(.115,.303-n*.021,est(row)+f'; p={pstr(row.p)}',8)
text(.025,.207,'三期联合检验p：0.591 / 0.360 / 0.498 / 0.096。',8,cn=True)
text(.025,.19,'以上是事前差距变化，不是绝对关系优势；不能判定等效。',8,cn=True)

# Annual full-covariance averages: do not replace CI by pointwise averaging.
text(.321,.425,'B1  +1至+4等权平均：β [95% CI]；原始p值',9,cn=True,color=INK)
text(.321,.407,'FE',8.2);text(.388,.407,'Sun–Abraham',8.2,color=BLUE);text(.566,.407,'TWFE fixed',8.2,color=ORANGE)
for n,(fe,lab) in enumerate(zip(FE,SHORT)):
 y=.389-n*.020;text(.321,y,lab,8)
 for xx,meth in [(.388,'Sun_Abraham'),(.566,'TWFE_fixed')]:
  row=A[A.estimator.eq(meth)&A.fe.eq(fe)&A.term.eq('post_average')].iloc[0]
  text(xx,y,est(row)+f'; {pstr(row.p)}',7.9)
text(.321,.232,'B2 动态C_it TWFE：四种FE，N=4,111；不同关系定义',8.7,cn=True,color=INK)
for n,(fe,lab) in enumerate(zip(FE,SHORT)):
 row=A[A.estimator.eq('TWFE_dynamic')&A.fe.eq(fe)&A.term.eq('post_average')].iloc[0]
 text(.321,.212-n*.017,lab,8);text(.405,.212-n*.017,est(row)+f'; p={pstr(row.p)}',8)

# Cumulative and exclusion check, every H plus all four 24-month exclusion definitions.
text(.755,.407,'D  累计晋升TWFE：I+省×前后期FE',9,cn=True,color=INK)
for n,row in enumerate(C.sort_values('H').itertuples()):
 text(.755,.386-n*.020,f'{int(row.H)}m  {est(row)}; wild p={pstr(row.p_wild)}',8)
text(.755,.319,'共同422人（45有关系）、24省；每H共844行。',8,cn=True)
text(.755,.302,'24月wild p=0.019；三期限Holm后p=0.057。',8,cn=True)
text(.755,.276,'D1 24月：剔除腐败/违纪领导更替省份',9,cn=True,color=INK)
for n,(v,lab) in enumerate([('Strict','Strict'),('Plus_discipline','+ Discipline'),('Plus_recent','+ Recent')]):
 row=X[X.variant.eq(v)&X.H.eq(24)].iloc[0];y=.254-n*.031
 text(.755,y,lab+': '+est(row),8);text(.755,y-.014,f'wild p={pstr(row.p_wild)}; Holm(3H)={pstr(row.p_wild_holm_three_H)}',8)

rule(.139)
notes=[
 '模型口径：I=个人FE；C=城市FE（加法，不是city×year）；Y=年份FE；P×Y=省份×年份FE。Y的晋升口径=职级上升、市长升书记或新任副省长（含同级副部）。',
 '控制：年龄及平方、现职任期及平方、职级、书记/市长角色；上年GDP增长、log人均GDP、log人口跟随官员当年任职城市。个人+时间FE吸收年龄线性项。',
 '时间与关系：年度结果取上年末在任者；C⁰锚在k=−1年度行，2013批次对应2011年末、2014批次对应2012年末；关系形成于2012年前且早于共同当前任职。',
 '解释限制：事前回溯名单有入样选择，不能把水平δ与事件β直接相加。两组都接受巡视，事件研究识别相对差距变化；巡视时点并非已证明随机。',
 '样本支持：年度+4仅4名有关系官员；LP/DML也仅4名且8省。12/24/36月为不同结果期限，长事前窗口可能早于名单形成。结果不等于每期稳定效应或优势消失。',
 '推断：图为95%逐点省聚类t区间，无连线；原始p值未覆盖此前规格搜索。累计wild bootstrap=Webb，9,999次，seed=20261015。不同模型样本与估计对象不完全相同。',
 '剔除口径：Strict实际影响河北/福建；+Discipline再剔四川；+Recent再剔辽宁/甘肃（离任后不久受查，不代表因腐败离任）。',
 '范围：本页覆盖当前完整控制下的事前模型、4种年度FE×3类年度估计器、LP两版、DML两版、累计3期限及腐败更替检查；历史控制/窗口网格未逐项堆放。',
 '核验与复跑：所有数字读取已核验CSV，未重新估计；随附data/、source_manifest.csv与build_one_page_summary.py。首次巡视不是全国反腐启动的统一断点。',
]
for n,line in enumerate(notes):text(.025,.126-n*.0125,line,8,cn=True,color=INK)

fig.savefig(PDF,format='pdf',metadata={'Title':'Central inspections, ties and promotion: complete current models','Author':'Research project summary','Subject':'One-page A3; actual estimates and model definitions; exploratory evidence'})
fig.savefig(O/'一页完整结果_预览.png',dpi=180)
reader=PdfReader(str(PDF));assert len(reader.pages)==1
page=reader.pages[0];w=float(page.mediabox.width);h=float(page.mediabox.height);assert abs(w-1190.55)<1 and abs(h-841.89)<1
pdf=pdfium.PdfDocument(str(PDF));im=pdf[0].render(scale=1.6).to_pil();im.save(O/'一页完整结果_PDF实际渲染.png');pdf.close()
checks=[dict(check='Exactly one PDF page',passed=len(reader.pages)==1),dict(check='A3 landscape page size',passed=abs(w-1190.55)<1 and abs(h-841.89)<1),dict(check='All fixed FE variants in annual table',passed=A[A.estimator.eq('TWFE_fixed')&A.term.eq('post_average')].fe.nunique()==4),dict(check='All 144 event method-period rows loaded',passed=len(E)==144),dict(check='All three cumulative horizons present',passed=set(C.H)=={12,24,36}),dict(check='Every input hash unchanged after rendering',passed=all(hashlib.sha256(Path(r.path).read_bytes()).hexdigest()==r.sha256 for r in manifest.itertuples()))]
pd.DataFrame(checks).to_csv(O/'PDF_validation_checks.csv',index=False,encoding='utf-8-sig');assert all(r['passed'] for r in checks)
shutil.copy2(__file__,O/'code'/Path(__file__).name)
with pd.ExcelWriter(O/'一页报告_完整源结果.xlsx',engine='openpyxl') as x:
 for k,df in data.items():df.to_excel(x,sheet_name=k[:31],index=False)
print(PDF);print('PDF pages:',len(reader.pages),'size pt:',w,h,'bytes:',PDF.stat().st_size)
