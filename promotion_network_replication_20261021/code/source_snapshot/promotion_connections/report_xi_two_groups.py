from pathlib import Path
import sys,json,html,shutil,zipfile,hashlib,re
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'Xi_two_groups_any_connection'
R=pd.read_csv(OUT/'all_window_estimates.csv');ST=pd.read_csv(OUT/'all_window_support.csv')
V=pd.read_stata(OUT/'stata_window_validation.dta',convert_categoricals=False)
Q=R.merge(V,on='model_id',suffixes=('_python','_stata'),validate='1:1')
checks=pd.read_csv(OUT/'pre_stata_validation.csv').to_dict('records')
for c in ['b','se','p','lo','hi','N','K','G','df']:
 checks.append(dict(check='Independent Stata '+c,passed=bool(np.allclose(Q[c+'_python'],Q[c+'_stata'],atol=2e-6,rtol=2e-6)),detail=float(abs(Q[c+'_python']-Q[c+'_stata']).max())))
assert len(Q)==24 and all(x['passed'] for x in checks)
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')
M=R[R.sampling.eq('maximal_union')].copy();M.to_csv(OUT/'main_12_coefficients.csv',index=False,encoding='utf-8-sig')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
def panel(ax,xi):
 q=M[M.Xi_group.eq(xi)].sort_values('center');color='#b15d48' if xi else '#287c9e'
 ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1);ax.axvspan(-1.3,1.3,color='#eeeeee',zorder=0)
 ax.errorbar(q.center,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt='o',ls='none',ms=5,color=color,capsize=4)
 ax.set_title('Province: '+('Xi-connected' if xi else 'No observed Xi connection'),fontsize=13)
 if xi:ax.text(.5,.96,'Exploratory: 2-4 province clusters',ha='center',va='top',transform=ax.transAxes,color='#8c3c30',fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.9))
 ax.set_xlim(-3.4,2.4);ax.set_xticks(range(-3,3));ax.set_xlabel('Window center relative to first inspection');ax.set_ylabel('Promotion probability difference (pp)');ax.grid(axis='y',alpha=.15)
 ns='; '.join(f'{int(r.center):+d}: {int(r.N)} / {int(r.G)}' for r in q.itertuples())
 ax.text(.5,-.27,'Center: N / provinces\n'+ns,ha='center',transform=ax.transAxes,fontsize=7.5)
foot='One regressor: a pre-existing city-official tie to EITHER the governor OR the provincial party secretary.\nProvince Xi-connected: EITHER provincial leader has a documented pre-2012 local coworking tie to Xi.\nThree-year windows; centers -3 to +2; gray windows contain inspection year; edge windows include k=-4 and +3.\nPooled mayors / city secretaries; personal and role controls; province-by-year FE. 95% CR1 t(G-1) CIs; no connecting lines.\nNo minimum-province screen. Full CIs shown; y scales differ. Xi-connected estimates rely on only 2-4 provinces.'
fig,axes=plt.subplots(1,2,figsize=(14,7.5))
for ax,xi in zip(axes,[0,1]):panel(ax,xi)
fig.suptitle('Promotion advantage from a tie to either provincial leader\nTwo province-year Xi groups | Three-year rolling regressions | 95% CIs',fontsize=15,y=.98)
fig.subplots_adjust(top=.80,bottom=.35,wspace=.25)
fig.text(.065,.035,foot,fontsize=8.2)
fig.savefig(OUT/'figures/01_two_groups_any_connection.png',dpi=180);plt.close(fig)
names=[]
for xi in [0,1]:
 fig,ax=plt.subplots(figsize=(10,7.5));panel(ax,xi)
 fig.suptitle('Tie to either provincial leader: promotion advantage\nThree-year rolling windows | Centers -3 to +2 | 95% CIs',fontsize=14,y=.98)
 fig.subplots_adjust(top=.79,bottom=.38,left=.13,right=.96)
 fig.text(.065,.025,foot,fontsize=7.4)
 fn='03_Xi_connected.png' if xi else '02_No_observed_Xi_connection.png';fig.savefig(OUT/'figures'/fn,dpi=180);plt.close(fig);names.append(fn)
for p in (OUT/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()

methods='''# 仅两组：一个“市级官员与任一省级主官有关系”变量
用户明确选择：关系带来的晋升优势，把市级官员与省长或书记任一人的关系合并为一个connection。不是画两组原始晋升率，也不是把两个原系数取平均或相加。

定义 C_any=1：原legacy_cowork_6m_S或legacy_cowork_6m_G至少一个为1；只有两者都已知且为0才令C_any=0；一者未知且另一者为0则未知，不补0。有一条明确正关系时即记1，不受另一条未知影响。个人关系要求至少六个月、2012年前且双方共同任职前已经形成。
省份分组仍是省×年XiProvince：当期基期在任省长或省委书记至少一人与Xi有2012年前地方同单位共事关系=1；两人均可核实且均无这种关系=0；其他未知排除。不是把一省永久贴标签；省级领导更替可改变分组。排除中央同期任职和学校工作单位。它不是对政治忠诚或私人关系的观测。

分别在XiProvince=0、=1省份的各个三年滚动窗估计：
100 Promotion_it = beta_w C_any_it + rho Secretary_it + X_it gamma_w + province×year FE + error。
两个原CS/CG不再单独进入回归。Y沿用修订年度升迁（行政级别上升、市长升书记、同级副部市级主官新任副省长）；同人同年兼任归书记。控制年龄及平方、任期及平方、基期行政级别、当前市长/书记职务。主版使用新合并变量可用的最大C1完整样本；另存限于原CS与CG均观测到的样本作核验，全部保留。
原始年度面板仍为2006—2017。窗口中心-3到+2，每点用[s-1,s+1]，因此端点用到k=-4和+3。灰窗包含进驻年。系数是晋升概率百分点的条件差异，不是归零事件研究。
取消原至少10省筛选，所有可识别窗口展示。省聚类CR1及t(G-1)95%逐点CI，图不连线、区间不截断、两组纵轴独立。Xi组只有2—4省；G=2时自由度1，区间特别宽，小聚类推断不可靠，只作探索性计算。没有用正态临界值缩窄区间，没有重新进行wild bootstrap或正式前后/组间差异检验。
不能从一个窗口显著、另一个不显著推出差异显著，也不能凭这两张图认定反腐因果效应。全部24次拟合（12个主窗口+12个原完整关系样本对照）均以独立完整FE虚拟变量回归和Stata18 areg核验。
可重跑：code/xi_two_groups_any_connection.py → Stata code/validate_windows.do → code/report_xi_two_groups.py；本机路径保留，迁移时修改BASE。旧图和原网络不覆盖，不生成PDF。
'''
(OUT/'methods_中文.md').write_text(methods,encoding='utf8')
with pd.ExcelWriter(OUT/'两组Xi关系_合并connection回归.xlsx',engine='openpyxl') as w:
 for name,d in [('Main_12_windows',M),('All_with_sensitivity',R),('Window_support',ST),('Province_groups',pd.read_csv(OUT/'province_Xi_group_by_year.csv')),('Validation',pd.DataFrame(checks)),('Independent_FE',pd.read_csv(OUT/'independent_full_dummy_validation.csv')),('Stata_validation',V)]:
  d.to_excel(w,sheet_name=name,index=False);w.sheets[name].freeze_panes='A2';w.sheets[name].auto_filter.ref=w.sheets[name].dimensions
page='<!doctype html><meta charset="utf-8"><title>两组Xi省份：任一省级关系的晋升优势</title><style>body{max-width:1500px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}</style><h1>只分两组：Xi-connected与未识别出Xi关系的省份</h1><p>一个解释变量：市级官员与省长或省委书记至少一人有事前关系。纵轴为该关系对应的晋升概率条件差异，不是两组原始晋升率。</p><p><a href="两组Xi关系_合并connection回归.xlsx">Excel结果</a> · <a href="methods_中文.md">方法说明</a></p><img src="figures/01_two_groups_any_connection.png">'
for name in names:page+='<h2>'+html.escape(name)+'</h2><img src="figures/'+name+'">'
(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
links=re.findall(r'(?:src|href)="([^"]+)"',page);assert all((OUT/z).is_file() for z in links)
summary=dict(main_models=len(M),all_models=len(R),checks=len(checks),all_checks_passed=True,main_estimates=M.to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
pd.DataFrame([dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='file_manifest.csv']).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=BASE/'两组Xi关系_合并connection_数据图表代码.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps({'main_models':len(M),'all_models':len(R),'all_checks_passed':True,'validation_checks':len(checks),'figures':3,'zip_bytes':zp.stat().st_size},ensure_ascii=False),flush=True)
