"""Curate verified existing results; no regression or new inferential search."""
from pathlib import Path
import sys,shutil,html,json
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
E=B/'exclude_corruption_leader_provinces_2026_10_21';P=B/'patron_retention_audit_2026_10_21'
O=B/'organized_main_results_corruption_checks_2026_10_21'
for p in [O,O/'figures',O/'data',O/'code']:p.mkdir(exist_ok=True)
A=pd.read_csv(E/'annual_all_results.csv');C=pd.read_csv(E/'cumulative_all_results.csv')
T=pd.read_csv(P/'symmetric_retention_summary.csv');T=T[T['sample'].eq('Paired clear rosters')].copy()
N=pd.read_csv(P/'departed_leaders/departed_comparison.csv')
T['departure_pct']=100*T.not_recorded_S_or_G/T.baseline_leaders
AM=A[A.variant.eq('Original')&A.term.eq('post_average')].copy()
CM=C[C.variant.eq('Original')&C.fe.eq('I_PXY')&C.control.eq('full')].copy()
AC=A[A.term.eq('post_average')].copy();CC=C[C.fe.eq('I_PXY')&C.control.eq('full')].copy()
SF=pd.read_csv(E/'sample_flow.csv');EV=pd.read_csv(E/'province_exclusion_evidence.csv')
RS=pd.read_csv(P/'retention_summary.csv')
raw=pd.read_csv(B/'cumulative_promotion_TWFE_12_24_36m/raw_group_promotion_rates.csv')
tables={'main_annual':AM,'main_cumulative':CM,'corruption_checks_annual':AC,'corruption_checks_cumulative':CC,
        'sample_flow':SF,'exclusion_evidence':EV,'descriptive_turnover':T,'descriptive_network_sizes':N,
        'original_patron_retention':RS,'raw_promotion_rates':raw,
        'cumulative_control_sensitivity':C[C.variant.eq('Original')&C.fe.eq('I_PXY')]}
for name,q in tables.items():q.to_csv(O/'data'/f'{name}.csv',index=False,encoding='utf-8-sig')
with pd.ExcelWriter(O/'主结果与腐败官员检查_汇总.xlsx') as w:
    for name,q in tables.items():q.to_excel(w,sheet_name=name[:31],index=False)
figures=[
 (B/'all_methods_C08_event_study_gallery/figures/01_Sun_Abraham_TWFE_fixed_four_FE.png','01_main_annual_four_FE.png'),
 (B/'cumulative_promotion_TWFE_12_24_36m/figures/01_cumulative_TWFE_three_horizons.png','02_main_cumulative.png'),
 (B/'cumulative_promotion_TWFE_12_24_36m/figures/02_control_sensitivity_same_sample.png','03_main_cumulative_controls.png'),
 (E/'figures/02_four_FE_Strict.png','04_corruption_exclusion_annual.png'),
 (E/'figures/03_cumulative_TWFE_full_controls.png','05_corruption_exclusion_cumulative.png')]
for src,name in figures:assert src.exists();shutil.copy2(src,O/'figures'/name)
# Descriptive chart: deliberately NO bootstrap intervals on fixed administrative records.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(14,6.8));colors={'Before':'#287f9d','After':'#ce8730'}
for phase,offset in [('Before',-.18),('After',.18)]:
    t=T[T.phase.eq(phase)].sort_values('horizon_months');n=N[N.phase.eq(phase)].sort_values('horizon_months')
    bars=axs[0].bar(np.arange(3)+offset,t.departure_pct,width=.30,color=colors[phase])
    for bar,r in zip(bars,t.itertuples()):axs[0].text(bar.get_x()+.15,bar.get_height()+1.2,f'{r.departure_pct:.1f}%\n({r.not_recorded_S_or_G}/{r.baseline_leaders})',ha='center',va='bottom',fontsize=9)
    bars=axs[1].bar(np.arange(3)+offset,n.mean_connections,width=.30,color=colors[phase])
    for bar,r in zip(bars,n.itertuples()):axs[1].text(bar.get_x()+.15,bar.get_height()+.055,f'{r.mean_connections:.2f}\n(n={r.leaders})',ha='center',va='bottom',fontsize=9)
axs[0].set_title('A. Provincial leadership departure rates');axs[0].set_ylabel('Departure rate (%)');axs[0].set_ylim(0,78)
axs[1].set_title('B. Departing leaders: mean city-official ties');axs[1].set_ylabel('Confirmed ties per departing leader');axs[1].set_ylim(0,2.8)
for ax in axs:ax.set_xticks(range(3),['12 months','24 months','36 months']);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Leadership turnover and networks before / after first inspection\nDescriptive sample statistics; no sampling confidence intervals',fontsize=16)
fig.legend(handles=[Patch(facecolor=colors[p],label=p+' inspection') for p in ['Before','After']],loc='upper center',bbox_to_anchor=(.5,.86),ncol=2,frameon=False)
fig.subplots_adjust(top=.73,bottom=.24,left=.07,right=.98,wspace=.25)
fig.text(.06,.135,'All exit reasons combined, not a normal-exit-only comparison. Governor-to-secretary moves in the same province count as retained.\nTies measured at window start; pre-2012 prior cowork relationships (at least 6 months); unknown ties are not coded zero.\nProvince frames (12/24/36m): A=30/27/26; B=27/24/22. Municipalities lack a comparable city-principal pool in B.\nNo sampling intervals or significance/equivalence claims are made for these fixed-sample descriptive counts.',fontsize=9,va='top')
fig.savefig(O/'figures/06_descriptive_turnover_networks_no_CI.png',dpi=180,facecolor='white');plt.close(fig)
md=r'''# 结果整理：主结果与腐败相关领导更替检查

本文件汇总已有核验结果；本轮没有新增回归或挑选显著窗口。首次巡视按各省实际进驻日期对齐，不是所有省统一以2012年为断点。以下结果是关系组与非关系组晋升差异的变化，不是全体官员的巡视平均效应。

## 1．主结果

### 1.1 样本、变量与关系

- 主年度结果：2,807个官员年、547人、26省；固定事前关系组中63人。展示k=-4至+4，k=-1为参照。
- CPED重建晋升：行政级别上升，市长升市委书记，或新任副省长（包括已为副部级的市委书记转任副省长）。不把普通委员身份或同级平调自动算晋升。
- C0：与基期省委书记或省长任一人的事前至少六个月共事关系；形成于2012年前、早于双方当前共同任职。个人边保留；本轮不混入同乡和校友。
- 原年度滞后口径形成的关系快照较早：2013巡视省为2011年底，2014巡视省为2012年底，不是进驻前一刻。此次结果整理保留原口径，没有悄悄改变基期。
- C08沿用全部个人控制与经济控制：年龄特征、任期及平方、职级、现职身份，以及官员当年基期任职城市的上年GDP增长、对数人均GDP、对数人口。经济变量跟官员任职地走。个人加时间FE吸收线性年龄项。

### 1.2 年度事件研究：Sun–Abraham与TWFE

回归比较固定关系组与非关系组的年度晋升差异相对k=-1如何变化。TWFE形式：

100 Promotion_it = IndividualFE + Time/PlaceFE + Σ[k≠−1] θ_k C0_i × Event_k + X_it γ + Event主效应（未被FE吸收时）+ error。

Sun–Abraham加入巡视cohort与相对时间交互再聚合；C0=0是该差异设计的对照组，并非该省从未被巡视。两个估计量均要求相应的条件差异趋势假设。

事后+1至+4四期平均系数（单位：百分点；括号为原始p值）：

| 固定效应 | Sun–Abraham | TWFE |
|---|---:|---:|
| 个人＋年份 | −7.73（0.415） | −8.77（0.289） |
| 个人＋省份×年份 | −6.69（0.458） | −8.64（0.288） |
| 个人＋城市＋年份 | −18.66（0.0042） | −19.10（0.0030） |
| 个人＋城市＋省份×年份 | −8.99（0.174） | −11.18（0.093） |

核心解读：加入城市FE、用年份FE时，四期平均下降显著；允许省份×年份共同冲击后估计明显减弱。因此年度证据对FE结构敏感，不能表述为所有合理规格均稳健。四期平均显著也不等于四个单独事后系数都显著。+4期仅4名事前有关系官员，长期支持不足。统计显著性亦没有消除此前全控制/窗口网格探索的不确定性。

![年度事件研究](figures/01_main_annual_four_FE.png)

### 1.3 固定同一批官员的累计晋升：12、24、36个月

固定同一422人（45名有关系者）、24省；每个H分别构造巡视前H个月和后H个月各一条记录，Y为窗内是否至少晋升一次。每H为844行。主规格：个人FE＋省份×前后期FE＋C0×Post＋基期控制×Post。

该数据每H只有两个聚合期。省份×前后期FE不能冒称逐年年度省份×年份FE。负θ表示关系组的累计晋升差异在后期相对前期下降，不是关系组的总晋升率下降这么多。

| H | θ（百分点） | 95%省聚类CI | 常规p | wild bootstrap p |
|---|---:|---|---:|---:|
| 12个月 | −15.03 | [−30.17，0.12] | 0.052 | 0.082 |
| 24个月 | −32.71 | [−55.32，−10.10] | 0.0065 | 0.0189 |
| 36个月 | −13.92 | [−40.00，12.16] | 0.281 | 0.316 |

24个月最值得继续研究；12个月较边缘，36个月不显著。24个月wild p对三个期限作Holm校正后为0.0567，不应隐去这一结果。仅FE版24个月系数为−16.25、p=0.077，个人控制版−28.48、p=0.010，完整控制版−32.71、p=0.0065，说明量级和显著性也依赖控制设定。

关键限制：原始分组均值未显示普遍正的事前关系优势；负θ不能直接支持“事前关系有用、事后无用”。24/36个月事前窗口部分早于基期官员名单形成，前期晋升可能影响进入该名单，存在队列选择与均值回归问题，个人FE不自动消除。累计回归与年度事件研究使用不同风险集与结果定义，不能把二者当作同一估计量互证。

![累计晋升](figures/02_main_cumulative.png)

![累计晋升控制对照](figures/03_main_cumulative_controls.png)

当前可用的总表述：在部分固定效应规格和24个月累计窗口中，巡视后事前关系组的相对晋升表现下降；年度结果对省份×年份FE敏感，长期与选择问题尚待解决。当前不能宣布巡视因果性地消除关系作用，也不能单凭这些晋升结果宣布中央集权增强。

## 2．腐败相关领导更替的检查

### 2.1 要排查的解释

原支持者因查处退出，可能导致其旧部晋升表现下降，而不必意味着支持者仍在时关系回报降低。省份×年份FE可以吸收共同省级冲击，但不能吸收只影响该领导旧部的额外损失。若查处由巡视引起，更替也可能是巡视机制而非普通遗漏因素。

### 2.2 原联系对象是否仍在：提示性核查

累计样本45名事前有关系者中，至少一名原联系对象仍任本省书记/省长的人数：巡视进驻时35，12个月末26，24个月末16，36个月末7。原联系对象均不再任这两个职位的人数相应为10、19、29、38。

这按市级官员计数，不是省级领导离任率；且原关系快照较早，有10人在巡视开始时原联系对象已离任。不能由此直接认定因反腐失去支持。

### 2.3 对称前后窗的总体更替与网络构成：只作描述

| 窗口 | 巡视前离任比例 | 巡视后离任比例 | 前期离任领导平均联系人数 | 后期离任领导平均联系人数 |
|---|---:|---:|---:|---:|
| 12个月 | 13.3%（8/60） | 13.3%（8/60） | 1.00（8位领导） | 2.14（7位领导） |
| 24个月 | 46.3%（25/54） | 29.6%（16/54） | 1.86（22位领导） | 2.00（16位领导） |
| 36个月 | 63.5%（33/52） | 63.5%（33/52） | 1.69（29位领导） | 1.52（29位领导） |

总体更替未显示巡视后普遍加快；离任者网络规模的差异方向随期限变化。离任包含正常调任与查处等所有原因，不能称为“正常离任率相同”。左右统计的省份范围不同：网络部分没有直辖市的可比地级市主官关系池；但各H内前后使用匹配省份框架。关系未知不补0。

修正先前表达：这些是固定样本的描述统计。本轮不展示其bootstrap区间，不用此前人为重抽样的区间断言“差异不显著”或“前后等效”。描述性模式不能排除特定旧部群体更容易失去支持者。

![离任与网络描述统计，无抽样CI](figures/06_descriptive_turnover_networks_no_CI.png)

### 2.4 整省排除后重跑主回归

各版均保留原结果定义、C0、控制、FE和日期，只删除省份全部年份：

- Strict：排除样本期内任内腐败查处相关书记/省长更替省份河北、福建、上海、天津、重庆。后三个直辖市本来不在主地级市样本中，实际删河北福建。
- Plus_discipline：再排四川，魏宏属于严重违纪撤职；不把该处分改写为受贿定罪。
- Plus_recent：再排辽宁、甘肃，王珉与王三运离任后12个月内被查。保守扩大排除，但不据此认定离任当时已由案件导致。

原年度547人/2807行 → 严格版508人/2629行；原累计422人 → 严格版393人。严格版没有删除原基期关系组成员，主要删除对照组。扩大到三项补充后，累计关系组45→44→33人。

| 样本 | 年度城市＋年份FE：Sun平均系数（p） | 同规格TWFE（p） | 累计24个月主规格θ | wild p |
|---|---:|---:|---:|---:|
| 原样本 | −18.66（0.0042） | −19.10（0.0030） | −32.71 | 0.0189 |
| 严格排除 | −18.84（0.0045） | −19.58（0.0031） | −33.32 | 0.0184 |
| 再排四川 | −18.60（0.0063） | −19.31（0.0051） | −32.87 | 0.0296 |
| 再排辽宁、甘肃 | −19.11（0.0037） | −20.71（0.0008） | −33.69 | 0.0163 |

上述年度城市＋年份FE仍含个人FE、C08全部控制。年度加入省份×年份FE后的平均结果，各排除版仍不显著；不能因排除结果稳健，就忽略原有FE敏感性。累计严格版24个月95%CI为[−56.45，−10.18]，wild p的三期限Holm校正为0.0552；再排四川为0.0888，再排辽宁甘肃为0.0489，三者全部保留，不按校正后的显著性选择版本。

![排除省份后的年度对照](figures/04_corruption_exclusion_annual.png)

![排除省份后的累计对照](figures/05_corruption_exclusion_cumulative.png)

这一检查支持：目前的24个月负向关联，以及城市＋年份FE下的年度平均下降，并非由已核实的这些领导查处相关更替省份单独驱动。但不等于已经识别出“在领导仍在任时关系回报降低”。正常调任和退休仍可能切断实际支持；按事后查处筛选省份也会改变研究总体和选择机制，因此作为稳健性检查而非净因果效应。

### 2.5 建议用于汇报的表述

“巡视后，事前关系组的相对晋升表现，在部分年度固定效应规格及24个月累计窗口内下降。排除省级主要领导腐败查处相关更替省份后，估计量级保持接近，削弱了结果仅由这些省份领导查处退出驱动的解释。与此同时，年度估计对省份×年份固定效应敏感，累计长窗存在队列选择问题，因此结果仍作为条件关联解释。”

## 文件与核验

正文分两部分；图均为英文；不生成PDF。汇总Excel保留原始系数、95%区间、常规/wild/校正p及排除证据。有关显著性的描述来自原回归推断；离任率/人数仅作描述统计。既有23项排省重估核验全部通过，原结果可精确复现、累计点由一阶差分复核；本轮没有重跑或覆盖它们。
'''
(O/'结果整理.md').write_text(md,encoding='utf-8')
# Render a self-contained reading page with local figures and original values.
def render(text):
    out=[];lines=text.splitlines();i=0
    while i<len(lines):
        line=lines[i]
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].startswith('|'):block.append(lines[i]);i+=1
            cells=[[c.strip() for c in z.strip('|').split('|')] for z in block]
            out.append('<table><thead><tr>'+''.join('<th>'+html.escape(c)+'</th>' for c in cells[0])+'</tr></thead><tbody>')
            for row in cells[2:]:out.append('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in row)+'</tr>')
            out.append('</tbody></table>');continue
        if line.startswith('!['):
            alt,path=line[2:].split('](',1);out.append(f'<figure><img src="{html.escape(path[:-1])}" alt="{html.escape(alt)}"></figure>')
        elif line.startswith('#'):
            lev=len(line)-len(line.lstrip('#'));out.append(f'<h{lev}>'+html.escape(line[lev:].strip())+f'</h{lev}>')
        elif line.startswith('- '):out.append('<p class="bullet">• '+html.escape(line[2:])+'</p>')
        elif line.strip():out.append('<p>'+html.escape(line)+'</p>')
        i+=1
    return '\n'.join(out)
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>主结果与腐败官员检查</title><style>body{max-width:1250px;margin:30px auto;padding:0 24px;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif;color:#22313b}h1{font-size:30px}h2{margin-top:50px;border-bottom:2px solid #287f9d}h3{margin-top:35px}p{max-width:1120px}img{width:100%;height:auto}figure{margin:24px 0}table{border-collapse:collapse;font-size:15px;width:100%;margin:20px 0}td,th{border-bottom:1px solid #d7e0e6;padding:10px;text-align:left}th{background:#eef4f7}.bullet{margin:8px 0}</style>'''+render(md)
page+='<h3>排除分类的官方来源</h3><ul>'
for r in EV.itertuples():page+=f'<li>{html.escape(r.province)} {html.escape(r.leader)}：<a href="{html.escape(r.source_url)}">官方证据</a>；{html.escape(r.classification_note)}</li>'
page+='</ul><p><a href="主结果与腐败官员检查_汇总.xlsx">下载汇总Excel</a></p></html>'
(O/'index.html').write_text(page,encoding='utf-8')
assert AM.shape[0]==8 and CM.shape[0]==3 and AC.shape[0]==32 and CC.shape[0]==12
assert (pd.read_csv(E/'validation_checks.csv').passed==True).all()
shutil.copy2(__file__,O/'code'/Path(__file__).name)
(O/'source_directories.json').write_text(json.dumps({'main_annual':str(B/'all_methods_C08_event_study_gallery'),'main_cumulative':str(B/'cumulative_promotion_TWFE_12_24_36m'),'corruption_checks':str(E),'turnover_descriptions':str(P)},ensure_ascii=False,indent=2),encoding='utf-8')
print(O);print('Curated 6 figures; 11 data tables; original regression outputs not modified.')
