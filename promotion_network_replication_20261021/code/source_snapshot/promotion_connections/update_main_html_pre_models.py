"""Update the user's existing gallery in place, from verified result CSVs only."""
from pathlib import Path
import hashlib, shutil, json, re, sys
from html import escape
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from html.parser import HTMLParser

B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'organized_main_results_corruption_checks_2026_10_21'
page=O/'index.html'
backup=O/'code/index_before_preinspection_and_two_FE_groups.html'
if not backup.exists():shutil.copy2(page,backup)
original=backup.read_text(encoding='utf-8')
sources={
 'preinspection_levels':B/'preinspection_fixed_C0_levels_2026_10_21/adjusted_preinspection_results.csv',
 'preinspection_raw':B/'preinspection_fixed_C0_levels_2026_10_21/raw_pooled_rates.csv',
 'preinspection_FE':B/'preinspection_FE_combinations_2026_10_21/all_FE_results.csv',
 'annual_events':B/'all_methods_C08_event_study_gallery/all_methods_full_controls_event_coefficients.csv',
 'annual_contrasts':B/'all_methods_C08_event_study_gallery/annual_C08_all_contrasts.csv',
}
hashes={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in sources.items()}
D={k:pd.read_csv(v) for k,v in sources.items()}
P=D['preinspection_levels']; E=D['annual_events']; A=D['annual_contrasts']
for k,v in D.items():v.to_csv(O/'data'/f'{k}_page_update.csv',index=False,encoding='utf-8-sig')
for src,name in [
 (B/'preinspection_fixed_C0_levels_2026_10_21/figures/01_preinspection_raw_and_adjusted.png','07_preinspection_raw_and_adjusted.png'),
 (B/'preinspection_FE_combinations_2026_10_21/figures/02_absolute_levels_and_absorption.png','08_preinspection_city_FE_sensitivity.png'),
 (B/'preinspection_FE_combinations_2026_10_21/figures/01_preinspection_individual_city_FE_changes.png','09_preinspection_individual_FE_changes.png')]:
 shutil.copy2(src,O/'figures'/name)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':16,'axes.labelsize':12,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
COLORS={'TWFE_fixed':'#cb8432','Sun_Abraham':'#237fa0'}
LABELS={'TWFE_fixed':'TWFE: fixed baseline ties','Sun_Abraham':'Sun-Abraham: fixed baseline ties'}
eqs={
 'pre_level':r'$100\,Promotion_{it}=\delta C_i^0+\lambda_{pt}+X_{it}^{\prime}\gamma+\varepsilon_{it},\quad k\in\{-4,-3,-2,-1\}$',
 'twfe_year':r'$100\,Promotion_{it}=\alpha_i+\lambda_t+\sum_{k\ne-1}\beta_k C_i^0 D_{pt}^{k}+\sum_{k\ne-1}\rho_k D_{pt}^{k}+X_{it}^{\prime}\gamma+\varepsilon_{it}$',
 'twfe_pxy':r'$100\,Promotion_{it}=\alpha_i+\lambda_{pt}+\sum_{k\ne-1}\beta_k C_i^0 D_{pt}^{k}+X_{it}^{\prime}\gamma+\varepsilon_{it}$',
 'sun':r'$100\,Promotion_{it}=F+\sum_g\sum_{k\ne-1}\delta_{gk}C_i^0\,1(G_p=g)D_{pt}^{k}+X_{it}^{\prime}\gamma+u_{it},\quad\beta_k^{SA}=\sum_g w_{gk}\delta_{gk}$',
 'cumulative':r'$100\,Y_{is}(H)=\alpha_i+\lambda_{p,s}+\theta_H C_i^0 Post_s+(X_{i0}\!\times Post_s)^{\prime}\gamma_H+u_{is}$',
 'pre_change':r'$100\,Promotion_{it}=\alpha_i+F+\sum_{k=-4}^{-2}\eta_k C_i^0 D_{pt}^{k}+X_{it}^{\prime}\gamma+\varepsilon_{it},\quad k\in\{-4,-3,-2,-1\}$',
}
for key,eq in eqs.items():
 fig=plt.figure(figsize=(14,1.05));fig.text(.015,.48,eq,va='center',fontsize=18);fig.savefig(O/'figures'/f'model_{key}.svg',bbox_inches='tight',pad_inches=.12);plt.close(fig)

used=[]
for fe,key,title in [
 ('I_YEAR','10_event_TWFE_individual_year','Group A | Individual + year fixed effects'),
 ('I_PXY','11_event_individual_province_year','Group B | Individual + province-by-year fixed effects')]:
 fig,ax=plt.subplots(figsize=(13,6.5));fig.subplots_adjust(left=.085,right=.98,bottom=.25,top=.81)
 fig.suptitle(title+'\nFixed pre-inspection ties | 95% province-clustered t CIs',fontsize=18,y=.98)
 for method,offset,marker in [('TWFE_fixed',-.085,'s'),('Sun_Abraham',.085,'o')]:
  q=E[E.method.eq(method)&E.fe.eq(fe)].sort_values('k').copy()
  assert len(q)==9 and set(q.k)==set(range(-4,5))
  assert q.N_model.dropna().eq(2807).all() and q.G_model.dropna().eq(26).all()
  used.append(q)
  r=q[q.k.ne(-1)]
  ax.errorbar(r.k+offset,r.b,yerr=[r.b-r.lo,r.hi-r.b],fmt=marker,ls='none',color=COLORS[method],capsize=4,ms=6,lw=1.4,label=LABELS[method])
  ax.scatter([-1+offset],[0],s=42,facecolors='white',edgecolors=COLORS[method],marker=marker,zorder=5)
 ax.axhline(0,color='#888',ls='--',lw=1);ax.axvline(0,color='#c29445',ls=':',lw=1.4)
 ax.set_xticks(range(-4,5));ax.set_xlim(-4.5,4.5);ax.set_ylim(-65,65)
 ax.set_xlabel('Years relative to first provincial inspection (reference k = -1)')
 ax.set_ylabel('Change in the connection-related promotion gap (pp)')
 ax.grid(axis='y',alpha=.15);ax.legend(loc='upper left',frameon=False)
 fig.text(.085,.09,'Identical N = 2,807 officer-years; 547 officials; 26 province clusters; full C08 controls.\nEconomics follow each official\'s appointment city (lagged one year). Reference is normalized; no estimated CI.\nAt k = +4, only 4 baseline-connected officials remain. Points are not connected.',fontsize=10.5,va='bottom')
 for suffix in ['png','svg']:fig.savefig(O/'figures'/f'{key}.{suffix}',dpi=180)
 plt.close(fig)
pd.concat(used).to_csv(O/'data/annual_event_two_FE_groups.csv',index=False,encoding='utf-8-sig')

def image(name,alt):return f'<figure><img loading="lazy" src="figures/{name}" alt="{escape(alt)}"></figure>'
def equation(name,alt):return f'<div class="equation"><img src="figures/model_{name}.svg" alt="{escape(alt)}"></div>'
def avgtable(fe):
 rows=[]
 for meth,lab in [('TWFE_fixed','TWFE'),('Sun_Abraham','Sun–Abraham')]:
  r=A[A.fe.eq(fe)&A.estimator.eq(meth)&A.term.eq('post_average')].iloc[0]
  rows.append(f'<tr><td>{lab}</td><td>{r.b:+.2f}</td><td>[{r.lo:.2f}, {r.hi:.2f}]</td><td>{r.p:.3f}</td></tr>')
 return '<table><thead><tr><th>估计方法</th><th>+1至+4平均变化（百分点）</th><th>95% CI</th><th>原始p值</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'

pre='''<section id="preinspection"><h3>1.2 巡视前：关系是否对应更高晋升概率？</h3>
<p>只使用相对时间k=-4至-1，沿用主事件研究来源样本和固定关系C<sup>0</sup>。共1,562个官员年、542人，其中62人为关系组，26省。以下三个控制版本使用完全相同的观测。</p>
<h4>事前水平回归</h4>'''+equation('pre_level','100 Promotion_it = delta C0_i + province-by-year FE + X_it gamma + error; pre-inspection k=-4,...,-1')+'''
<p>δ是同一省份、同一年内，事前有关系与无关系官员的条件晋升概率差异。此处不加个人FE，因为固定C<sup>0</sup>会被个人FE完全吸收。依次展示仅省份×年份FE、加个人控制、再加官员任职城市经济控制；标准误按基期省份聚类。</p>'''+image('07_preinspection_raw_and_adjusted.png','巡视前原始晋升率与三个控制版本的条件关系差异')+'''
<p><strong>结果：</strong>原始年晋升率为17.06%（有关系，29/170）和14.44%（无关系，201/1392）。仅省份×年份FE的条件差异为+1.22个百分点（p=0.614）；加个人控制为+7.75（p=0.031）；完整控制为<strong>+7.98个百分点，95% CI [0.89, 15.07]，p=0.029</strong>。这是事前条件关联，并非关系的因果效应，也不是每个事前年份都显著。</p>
<details><summary>事前加入城市FE、个人FE的完整敏感性结果</summary>
<p>加入城市FE时，三个水平模型使用共同样本：1,456个官员年、441人、25省。省份×年份FE下为+7.11个百分点，95% CI [-0.25, 14.46]；城市＋年份FE为+0.98，CI [-13.44, 15.40]；城市＋省份×年份FE为+2.49，CI [-11.64, 16.61]。城市FE版本较不精确，不能只展示显著的原样本版本。</p>'''+image('08_preinspection_city_FE_sensitivity.png','事前水平回归城市FE敏感性与个人FE吸收固定关系指标')+equation('pre_change','Pre-only model with individual FE: estimate C0 x event-time relative to k=-1, not an absolute connection premium')+'''
<p>个人FE版本估计η<sub>k</sub>：早期关系差距相对于k=-1的变化，不能再解释为绝对关系优势。上式F分别取年份、省份×年份、城市＋年份、城市＋省份×年份；年份FE版本另含未被吸收的事件时间主效应。</p>'''+image('09_preinspection_individual_FE_changes.png','仅事前个人固定效应：相对于-1期的差距变化')+'''
</details><p class="note">事前名单由较晚的巡视前快照固定，早期晋升可能影响进入名单，存在回溯入样选择。该部分与后面的个人FE事件研究估计对象和样本不同，不能把+7.98与事件系数直接相加推算巡视后的绝对优势，也不能用“不显著”宣布无差异。</p></section>'''

event='''<section id="event-study"><h3>1.3 年度event study：两组固定效应明确分开</h3>
<p>定义D<sub>pt</sub><sup>k</sup>=1(t-G<sub>p</sub>=k)，G<sub>p</sub>为基期任职省的首次巡视年。两组都保留<strong>个人FE</strong>，固定C<sup>0</sup>，使用完全相同的2,807个官员年、547人、26省及C08控制；展示k=-4至+4，k=-1为参照。因变量为100×年度晋升指标。</p>
<p><strong>β<sub>k</sub>的含义：</strong>关系组与非关系组的晋升差距，较巡视前一年改变了多少个百分点；负数表示差距相对下降。它不是当期绝对关系优势，也不是全体官员的巡视效应。</p>
<h4 id="event-A">A组：标准two-way fixed effects——个人＋年份FE</h4>'''+equation('twfe_year','100 Promotion_it = individual FE + year FE + sum beta_k C0_i Event_k + sum rho_k Event_k + controls + error')+'''
<p>α<sub>i</sub>吸收官员不随时间变化的特征；λ<sub>t</sub>吸收全国同年共同冲击。巡视相对时间主效应D<sup>k</sup>另行进入回归。该规格允许利用更广的跨省时间比较，尚未吸收各省各年独有的晋升共同冲击。</p>'''+image('10_event_TWFE_individual_year.png','A组：个人与年份固定效应，TWFE与Sun-Abraham')+avgtable('I_YEAR')+'''
<h4 id="event-B">B组：加强时间冲击控制——个人＋省份×年份FE</h4>'''+equation('twfe_pxy','100 Promotion_it = individual FE + province-by-year FE + sum beta_k C0_i Event_k + controls + error')+'''
<p>λ<sub>pt</sub>允许每省每年都有自己的共同晋升环境。它已经包含年份FE；因此不是再估计一套独立年份效应。各事件时间主效应也被吸收。比较依赖同省同年关系组与非关系组的差异及其随时间的变化，同时净化个人固定差异。</p>'''+image('11_event_individual_province_year.png','B组：个人与省份乘年份固定效应，TWFE与Sun-Abraham')+avgtable('I_PXY')+'''
<p><strong>两组解读：</strong>没有加入城市FE的这两组，事后+1至+4平均变化均为负，但95%区间跨零。不能称为四期稳定显著。+4期只有4名事前有关系官员，长期支持有限；图中-1期为空心归一化参照，没有估计的置信区间。平均区间使用完整系数协方差计算，并非四条逐点CI求平均。</p>
<details><summary>Sun–Abraham对应模型与识别含义</summary>'''+equation('sun','Sun-Abraham: cohort by event-time interactions in the fixed-C0 group, aggregated by cohort weights')+'''
<p>F取A组或B组的固定效应，未被吸收的事件时间主效应同时纳入。先估计巡视批次g与事件时间k的关系组交互系数，再按相应权重聚合。C<sup>0</sup>=0官员在该关系差异设计中充当对照，但其所在省也接受巡视；因此结果是巡视前后关系差距的变化，仍需相应的条件差异趋势假设。</p></details>
<details><summary>补充：城市FE敏感性（与上面两组主图分开）</summary>
<p>以下旧图保留四种FE用于透明对照：个人＋年份，个人＋省份×年份，个人＋城市＋年份，个人＋城市＋省份×年份。城市FE是加法效应，不是城市×年份FE。城市＋年份版本的显著平均下降，在加入省份×年份共同冲击后减弱，说明结果依赖FE结构。</p>'''+image('01_main_annual_four_FE.png','四种固定效应敏感性对照')+'''
</details><p class="note">这两组图的系数、区间均直接来自已核验CSV。本次更新只整理模型和图，没有重新估计、挑选窗口或改变显著性阈值。</p></section>'''

start=original.index('<h3>1.2 年度事件研究')
end=original.index('<h3>1.3 固定同一批官员',start)
html=original[:start]+pre+event+original[end:]
html=html.replace('<h3>1.3 固定同一批官员','<h3>1.4 固定同一批官员')
anchor='<p>该数据每H只有两个聚合期。'
html=html.replace(anchor,equation('cumulative','Cumulative TWFE: individual FE + province-by-pre/post FE + C0 x Post + baseline controls x Post')+'<p>s∈{前期, 后期}；H=12、24、36个月，Y<sub>is</sub>(H)表示对应等长窗口内是否至少晋升一次。θ<sub>H</sub>比较关系组与非关系组累计晋升差距的前后变化。</p>'+anchor)
css='''h4{font-size:21px;margin-top:32px;color:#256783}.equation{background:#f3f7fa;border-left:4px solid #287f9d;padding:12px 16px;overflow-x:auto;margin:20px 0}.equation img{min-width:800px;width:100%;max-height:110px;object-fit:contain;object-position:left}.note{padding:14px 18px;background:#fff7e7;border-left:4px solid #d09b3a}details{margin:24px 0;padding:16px;border:1px solid #d6e0e8;border-radius:6px}summary{cursor:pointer;color:#256783;font-weight:600}nav{padding:15px 18px;background:#eef4f7;border-radius:6px}nav a{margin-right:22px}a{color:#146f93}'''
html=html.replace('</style>',css+'</style>')
html=html.replace('<h2>1．主结果</h2>','<nav><a href="#preinspection">事前关系优势与模型</a><a href="#event-A">A：个人＋年份</a><a href="#event-B">B：个人＋省份×年份</a><a href="#corruption">腐败官员检查</a></nav><h2>1．主结果</h2>')
html=html.replace('<h2>2．腐败相关领导更替的检查</h2>','<h2 id="corruption">2．腐败相关领导更替的检查</h2>')
html=html.replace('正文分两部分；图均为英文；不生成PDF。','正文加入事前证据、明确区分两组事件研究及模型方程，后接累计晋升和腐败更替检查；图均为英文。本次直接更新原HTML页面。')
footer='<p>本次页面更新：2026-10-21。事前原样本与城市FE共同样本分别报告；年度两组主图使用相同观测。<a href="data/annual_event_two_FE_groups.csv">下载两组事件研究系数</a>；<a href="code/update_main_html_pre_models.py">页面更新代码</a>。原页面备份保存在code/中。</p>'
html=html.replace('</html>',footer+'</html>')
page.write_text(html,encoding='utf-8')
shutil.copy2(Path(__file__),O/'code/update_main_html_pre_models.py')
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append(a['src'])
  if 'id' in a:self.ids.append(a['id'])
p=Parser();p.feed(html)
checks={
 'all_images_exist':all((O/src).is_file() for src in p.images),
 'two_main_FE_groups_present':all(x in p.ids for x in ['event-A','event-B']),
 'preinspection_section_present':'preinspection' in p.ids,
 '36_event_rows':sum(len(q) for q in used)==36,
 'source_hashes_unchanged':all(hashlib.sha256(v.read_bytes()).hexdigest()==hashes[k] for k,v in sources.items()),
 'corruption_checks_retained':'2.5 建议用于汇报的表述' in html,
 'cumulative_model_present':'model_cumulative.svg' in html,
 'no_missing_reference_CI':all(q[q.k.eq(-1)].lo.isna().all() for q in used),
}
assert all(checks.values()),checks
(O/'data/page_update_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'data/page_update_sources.json').write_text(json.dumps({k:dict(path=str(v),sha256=hashes[k]) for k,v in sources.items()},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(page=str(page),checks=checks,images=len(p.images)),ensure_ascii=False,indent=2))
