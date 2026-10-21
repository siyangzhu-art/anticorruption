from pathlib import Path
import sys,json,html,shutil,zipfile,hashlib,re
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'Xi_province_union_no_min_provinces'
R=pd.read_csv(OUT/'all_window_coefficients.csv');ST=pd.read_csv(OUT/'window_support_and_status.csv')
V=pd.read_stata(OUT/'stata_window_validation.dta',convert_categoricals=False)
Q=R.merge(V,on=['model_id','leader'],suffixes=('_python','_stata'),validate='1:1')
checks=pd.read_csv(OUT/'pre_stata_validation.csv').to_dict('records')
for c in ['b','se','p','lo','hi','N','K','G','df']:
 checks.append(dict(check='Independent Stata '+c,passed=bool(np.allclose(Q[c+'_python'],Q[c+'_stata'],atol=2e-6,rtol=2e-6)),detail=float(abs(Q[c+'_python']-Q[c+'_stata']).max())))
assert len(Q)==24 and all(x['passed'] for x in checks),checks
pd.DataFrame(checks).to_csv(OUT/'validation_checks.csv',index=False,encoding='utf-8-sig')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
LEAD={'G':'Governor','S':'Provincial party secretary'}
def panel(ax,lead,xi):
 q=R[R.leader.eq(lead)&R.Xi_group.eq(xi)].sort_values('center')
 st=ST[ST.Xi_group.eq(xi)].sort_values('center')
 ax.axhline(0,color='gray',ls='--',lw=1);ax.axvline(0,color='#b58a34',ls=':',lw=1);ax.axvspan(-1.3,1.3,color='#eeeeee',zorder=0)
 color='#b15d48' if xi else '#287c9e'
 ax.errorbar(q.center,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt='o',ls='none',ms=4.7,color=color,capsize=4)
 low=q[q.low_connection_count.astype(str).str.lower().eq('true')]
 ax.plot(low.center,low.b,marker='o',ls='none',mfc='white',mec=color,ms=5)
 ax.set_title(LEAD[lead]+' | Province: '+('Xi-connected' if xi else 'No observed Xi connection'),fontsize=11)
 if xi:ax.text(.5,.96,'Exploratory: 2-4 province clusters',transform=ax.transAxes,ha='center',va='top',fontsize=8.5,color='#8c3c30',bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
 ax.set_xlim(-3.4,2.4);ax.set_xticks(range(-3,3));ax.set_xlabel('Window center relative to first inspection');ax.set_ylabel('Promotion probability difference (pp)');ax.grid(axis='y',alpha=.15)
 ns='; '.join(f'{int(r.center):+d}: {int(r.N)} / {int(r.G)}' for r in st.itertuples())
 ax.text(.5,-.33,'Center: N / provinces\n'+ns,transform=ax.transAxes,ha='center',fontsize=7.6)

foot='Three-year windows; centers -3 to +2 (edge windows use k=-4 and +3). Pooled mayors and city party secretaries.\nProvince connected = governor OR provincial secretary has a documented pre-2012 local coworking tie to Xi.\nBoth city-to-leader ties jointly; personal and role controls; province-by-year FE. 95% CR1 t(G-1) CIs, clustered by province.\nNo minimum-province screen. All identifiable windows shown. Hollow: fewer than 10 positive/negative observations for a tie regressor.\nFull intervals retained; panels have different y scales. With 2 clusters, t degrees of freedom = 1. Small-cluster inference is fragile.'
fig,axes=plt.subplots(2,2,figsize=(15,11))
for i,l in enumerate(['G','S']):
 for j,xi in enumerate([0,1]):panel(axes[i,j],l,xi)
fig.suptitle('City-principal promotion and ties to provincial leaders\nProvince-year Xi groups | No minimum-province screen | 95% confidence intervals',fontsize=16,y=.98)
fig.subplots_adjust(top=.86,bottom=.22,hspace=.88,wspace=.23)
fig.text(.065,.035,foot,fontsize=8.3)
fig.savefig(OUT/'figures/01_four_panels_no_min_provinces.png',dpi=180);plt.close(fig)
gallery=[]
for l in ['G','S']:
 for xi in [0,1]:
  fig,ax=plt.subplots(figsize=(10,7.5));panel(ax,l,xi)
  fig.suptitle('Three-year rolling regressions | Centers -3 to +2\nNo minimum-province screen | 95% province-clustered t CIs',fontsize=14)
  fig.subplots_adjust(top=.79,bottom=.41,left=.13,right=.97)
  fig.text(.065,.025,foot,fontsize=7.5)
  name=f'{l}_Xi{xi}_no_min_provinces.png';fig.savefig(OUT/'figures'/name,dpi=180);plt.close(fig);gallery.append(name)
for p in (OUT/'figures').glob('*.png'):
 with Image.open(p) as im:im.verify()

methods='''# 取消10省门槛后的四格图
用户明确要求不使用至少10省筛选。本轮展示所有可识别窗口：取消任意最低省数筛选（计算原省聚类CR1/t区间本身至少需要两个省），少于10个正/负关系观测也不机械删点，而以空心点标注。没有按符号、p值或CI宽度选择结果。晋升定义、分省定义、回归方程、控制与原省聚类推断完全不变。

省×年分组：基期当任省长或省委书记至少一人与习近平有2012年前且当时已经形成的同单位至少六个月地方共事关系，归XiProvince=1。两人均可判断且无这种关系才归0，其他未知不补0。排除中央共同任职、学校工作单位关系。分组随省级领导更替变化，两行使用同一分省结果。
Y=年度实际晋升，沿用原修订版：行政级别提升/市长转市委书记/副部级市级主官新任副省长也计晋升。市长与书记合并，加入当前职务指示、年龄与平方、任期与平方、基期行政级别；CS（与书记关系）、CG（与省长关系）同时进入，省×年FE。因变量乘100，系数为百分点。
三年居中滚动，中心-3到+2，使用[s-1,s+1]。因此两端使用k=-4及+3，与用户指定原图的显示范围口径一致。灰色窗包含巡视年，没有将-1归零。数据来自2006—2017原年度面板，不增删原始履历。
省聚类CR1标准误及t(G-1)的95%逐点区间，不连接点；不改用正态临界值缩窄CI。只有2省时自由度1，t临界值约12.706；3省时自由度2、约4.303；4省时自由度3、约3.182。Xi组省数2—4，区间可能极宽，线性概率模型系数/CI也可超出±100个百分点。图不截断区间，各格纵轴独立，不应用视觉高度直接跨格比较。
省数少时这些常规聚类区间不具有可靠的大样本保证，仅作为探索性计算；省份内更多城市不能替代独立省级样本。未声称Xi组/非Xi组效果存在显著差异，也未声称巡视因果效应；本轮没有重做wild bootstrap或分组差异检验。
所有12个分组窗口均可识别，共24项系数全部报告。与Xi无已识别关系省份组原系数、SE、p及CI逐项不变。所有模型用独立全FE虚拟变量回归和Stata18 areg各复核一次。所有程序、源数据哈希与结果保留；旧的10省门槛版本不覆盖。
可重跑：先运行code/xi_province_no_minimum.py，再以Stata运行code/validate_windows.do，最后运行code/report_xi_no_minimum.py。保留本机路径，迁移项目需调整ROOT/BASE。
'''
(OUT/'methods_中文.md').write_text(methods,encoding='utf8')
roster=pd.read_csv(OUT/'province_Xi_group_by_year.csv')
with pd.ExcelWriter(OUT/'取消10省门槛_四格回归.xlsx',engine='openpyxl') as w:
 for n,d in [('All_24_coefficients',R),('12_window_support',ST),('Province_groups',roster),('Validation',pd.DataFrame(checks)),('Independent_dummy',pd.read_csv(OUT/'independent_dummy_validation.csv')),('Stata_validation',V)]:
  d.to_excel(w,sheet_name=n,index=False);w.sheets[n].freeze_panes='A2';w.sheets[n].auto_filter.ref=w.sheets[n].dimensions
page='<!doctype html><meta charset="utf-8"><title>取消10省门槛：四格图</title><style>body{max-width:1500px;margin:auto;padding:22px;font:16px system-ui}img{width:100%;height:auto}</style><h1>取消10省门槛：全部可识别窗口</h1><p>四组均已绘出。右列每窗2—4省，完整保留95% CR1 t(G−1)区间；各图纵轴不同。空心点标注关系观测较少的窗口。</p><p><a href="取消10省门槛_四格回归.xlsx">Excel全部结果</a> · <a href="methods_中文.md">定义及推断说明</a></p><img src="figures/01_four_panels_no_min_provinces.png">'
for f in gallery:page+='<h2>'+html.escape(f)+'</h2><img src="figures/'+f+'">'
(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
links=re.findall(r'(?:src|href)="([^"]+)"',page);assert all((OUT/x).is_file() for x in links)
summary=dict(models=12,coefficients=len(R),all_validation_passed=True,independent_checks=len(checks),min_provinces=int(R.G.min()),max_provinces=int(R.G.max()),xi_positive_coefficients=R[R.Xi_group.eq(1)].to_dict('records'))
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
pd.DataFrame([dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='file_manifest.csv']).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=BASE/'取消10省门槛_按省级Xi关系分组.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps({'models':12,'coefficients':len(R),'all_validation_passed':True,'validation_checks':len(checks),'figures':5,'zip_bytes':zp.stat().st_size},ensure_ascii=False),flush=True)
