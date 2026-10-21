from pathlib import Path
import sys,json,html,shutil,hashlib,zipfile
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimate import OUT
R=pd.read_csv(OUT/'all_estimates_validated.csv',low_memory=False);STATUS=pd.read_csv(OUT/'model_status.csv');PRIMARY=pd.read_csv(OUT/'primary_pooled_estimates_validated.csv')
for d in [R,STATUS]:d['incomplete_window']=d.incomplete_window.astype(str).str.lower().eq('true')
PREP=json.loads((OUT/'preparation_summary.json').read_text(encoding='utf8'));EST=json.loads((OUT/'estimation_summary.json').read_text(encoding='utf8'));V=json.loads((OUT/'validation_summary.json').read_text(encoding='utf8'));assert V['all_passed']
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
ROLES={'mayor':'Mayors','secretary':'City party secretaries'};LEAD={'S':'Provincial party secretary','G':'Governor'}
COL={'pre':'#287c9e','post':'#cf8735','change':'#a9537e'};gallery=[]
def qselect(**kw):
 q=R
 for k,v in kw.items():q=q[q[k].eq(v)]
 return q
def pval(v):return 'NA' if pd.isna(v) else ('<0.001' if v<.001 else f'{v:.3f}')
def export(fig,name,title):
 fig.savefig(FIG/name,dpi=165);plt.close(fig);gallery.append(dict(file='figures/'+name,title=title))
def rolling(name,axis='calendar',width=None,unit='annual',outcome='promotion',relation='cowork_6m',timing='legacy',compare=None,fe='PXY',controls='C1',sampling='common'):
 width=width or (5 if axis=='calendar' else 3)
 fig,axes=plt.subplots(2,2,figsize=(13,8.3));groups=['C0','C1','C2'] if compare=='controls' else ['PY','PXY','CITY_PXY'] if compare=='fe' else [controls]
 colors=['#9a9a9a','#287c9e','#c98235'];marks=['s','o','D']
 for ir,role in enumerate(ROLES):
  for il,lead in enumerate(LEAD):
   ax=axes[ir,il];ax.axhline(0,color='grey',ls='--',lw=1)
   cutoff=2012 if axis=='calendar' else 0;h=width//2;ax.axvspan(cutoff-h-.35,cutoff+h+.35,color='#eeeeee',zorder=0);ax.axvline(cutoff+.5 if axis=='calendar' else 0,color='#ad934f',ls=':',lw=1)
   allq=[]
   for j,g in enumerate(groups):
    qq=qselect(kind='rolling',unit=unit,outcome=outcome,role=role,leader=lead,relation=relation,timing=timing,controls=g if compare=='controls' else controls,fe=g if compare=='fe' else fe,sampling=sampling,axis=axis,width=width).sort_values('center');allq.append(qq)
    if len(qq):
     ax.errorbar(qq.center+(j-(len(groups)-1)/2)*.14,qq.b,yerr=[qq.b-qq.lo,qq.hi-qq.b],fmt=marks[j] if compare else 'o',ls='none',ms=3.5,capsize=2,color=colors[j] if compare else '#287c9e',label=g)
     incomplete=qq[qq.incomplete_window.eq(True)]
     ax.plot(incomplete.center+(j-(len(groups)-1)/2)*.14,incomplete.b,marker=marks[j] if compare else 'o',ls='none',ms=3.5,markerfacecolor='white',markeredgecolor=colors[j] if compare else '#287c9e')
   if not any(len(z) for z in allq):ax.text(.5,.5,'Not estimable under support rules',ha='center',transform=ax.transAxes)
   ax.set_title(ROLES[role]+' | Tie to '+LEAD[lead],fontsize=10.5);ax.set_ylabel('Promotion probability difference (pp)');ax.set_xlabel('Window center year' if axis=='calendar' else 'Window center relative to first inspection');ax.grid(axis='y',alpha=.15)
   if compare:ax.legend(fontsize=8,loc='best')
 title=f'{"Annual promotion" if unit=="annual" else "Next-post promotion"} | {width}-year rolling windows'
 if outcome=='rank_promotion':title='Administrative-rank promotion only | '+str(width)+'-year windows'
 fig.suptitle(title+'\n'+('Calendar time' if axis=='calendar' else 'Years relative to first central inspection')+' | 95% confidence intervals',fontsize=14,y=.98)
 fig.subplots_adjust(top=.85,bottom=.19,hspace=.48,wspace=.28)
 txt=('Age, tenure and baseline-rank controls; province-by-year FE.' if not compare else ('Common observations across C0/C1/C2; province-by-year FE.' if compare=='controls' else 'Common observations; age, tenure and baseline-rank controls.'))
 txt+=(' Maximal available C1 sample.' if sampling=='maximal' else ' Common full-control sample.')
 timingnote='Ties formed before 2012 and before joint appointment.' if timing=='legacy' else 'Comparison: ties formed before joint appointment; no pre-2012 restriction.'
 fig.text(.065,.035,txt+'\nBoth provincial-leader indicators enter together. '+timingnote+'\nShading: windows include 2012 / inspection year. Hollow: nominal window has whole-year / cohort gaps.\nPointwise province-clustered t intervals; no connecting lines. Coverage details are saved for every window.\nAnnual outcome uses prior-year-end officeholders. Follow-up ends in 2017. Associations, not causal effects.',fontsize=8)
 export(fig,name,title+' | '+axis+' | '+relation+' / '+timing+(' | '+compare+' comparison' if compare else ''))

def pooled(name,axis,unit='annual',outcome='promotion',relation='cowork_6m',timing='legacy'):
 q=qselect(kind='pooled',unit=unit,outcome=outcome,relation=relation,timing=timing,controls='C1',fe='PXY',sampling='common',axis=axis)
 fig,axes=plt.subplots(2,2,figsize=(12.5,8.3))
 for ir,role in enumerate(ROLES):
  for il,lead in enumerate(LEAD):
   ax=axes[ir,il];qq=q[q.role.eq(role)&q.leader.eq(lead)].set_index('estimand').reindex(['pre','post','change']);ax.axhline(0,color='grey',ls='--',lw=1)
   for j,est in enumerate(['pre','post','change']):
    if est in qq.index and pd.notna(qq.loc[est,'b']):
     r=qq.loc[est];ax.errorbar(j,r.b,yerr=[[r.b-r.lo],[r.hi-r.b]],fmt=['o','s','D'][j],color=COL[est],capsize=4,ms=6)
   ax.set_xticks([0,1,2],['Before','After','Change']);ax.set_xlim(-.5,2.5);ax.set_ylabel('Percentage points');ax.grid(axis='y',alpha=.15);ax.set_title(ROLES[role]+' | Tie to '+LEAD[lead],fontsize=10.5)
   pp=' / '.join(pval(x) for x in qq.p);wild=pval(qq.loc['change','p_wild']) if 'p_wild' in qq else 'NA';ax.text(.5,-.17,'p: '+pp+'\nChange wild p: '+wild,transform=ax.transAxes,ha='center',va='top',fontsize=8)
 fig.suptitle(('Annual' if unit=='annual' else 'Term destination')+' promotion | Before / after / change\n'+('National anticorruption split' if axis=='national_main' else 'First provincial inspection')+' | 95% CIs',fontsize=14,y=.98)
 fig.subplots_adjust(top=.85,bottom=.22,hspace=.64,wspace=.30)
 fig.text(.065,.045,'Main specification: pre-2012 coworking ties; both leaders jointly; personal controls; province-by-year FE.\nCommon full-control sample. National split omits 2012; inspection Post begins in entry year.\nPointwise province-clustered t intervals. Primary annual changes: 9,999-rep Webb wild bootstrap, seed 20261015.\nInsignificance after the cutoff is not evidence of zero effect. No causal inspection effect is identified by this comparison.',fontsize=8.5)
 export(fig,name,'Before / after: '+axis+' | '+unit)

rolling('01_main_calendar_5year.png');rolling('02_main_inspection_3year.png',axis='inspection_relative')
rolling('maximal_C1_calendar_5year.png',sampling='maximal');rolling('maximal_C1_inspection_3year.png',axis='inspection_relative',sampling='maximal')
pooled('03_main_national_pre_post_change.png','national_main');pooled('04_main_inspection_pre_post_change.png','inspection_main')
for axis in ['calendar','inspection_relative']:
 rolling('controls_'+axis+'.png',axis=axis,compare='controls');rolling('fixed_effects_'+axis+'.png',axis=axis,compare='fe')
 for w in [3,5,7]:
  if (axis=='calendar' and w==5) or (axis=='inspection_relative' and w==3):continue
  rolling('window_'+axis+'_'+str(w)+'.png',axis=axis,width=w)
 rolling('rank_only_'+axis+'.png',axis=axis,outcome='rank_promotion')
 rolling('term_'+axis+'.png',axis=axis,unit='term')
 rolling('preassignment_'+axis+'.png',axis=axis,timing='preassignment')
 for rel in ['hometown_prefecture','classmate_6m','connected']:rolling(rel+'_'+axis+'.png',axis=axis,relation=rel)
pooled('term_national.png','national_main',unit='term');pooled('term_inspection.png','inspection_main',unit='term')

A=pd.read_csv(OUT/'annual_official_panel.csv.gz',low_memory=False);T=pd.read_csv(OUT/'term_destination_panel.csv.gz',low_memory=False);W=pd.read_csv(OUT/'wang_yang_cross_validation.csv',low_memory=False)
annual=A.groupby(['year','role']).agg(risk_rows=('person_id','size'),observed_outcome=('promotion','count'),promotions=('promotion','sum'),rank_promotions=('rank_promotion','sum'),cowork_S=('legacy_cowork_6m_S','sum'),cowork_G=('legacy_cowork_6m_G','sum')).reset_index();annual.to_csv(OUT/'annual_descriptive_summary.csv',index=False,encoding='utf-8-sig')
methods=f'''# 省市官员关系与晋升：滚动LPM，2026-10-20

## 结果概况
年度风险集{len(A):,}个人年，{A.person_id.nunique():,}人，2000—2017年；主晋升结果有值{A.promotion.notna().sum():,}个，其中{int(A.promotion.sum()):,}个晋升年。任期版{len(T):,}段任期，{T.promotion.notna().sum():,}段去向可分类。两套结果不是重复贴标签：年度版为实际发生年的事件，任期版为首个后续职位。
预定{EST['models_requested']:,}个模型，{EST['models_ok']:,}个通过支持与可识别性规则，{EST['models_requested']-EST['models_ok']:,}个留空。所有系数、控制、固定效应、窗口和失败原因保留。没有按显著性选图。
八项年度主规格的前后变化没有形成一致的显著下降；详见primary_pooled_estimates_validated.csv。p值未经调整和八项Holm校正均保留，滚动区间是逐点区间，非同时置信带。

## 数据与晋升
只用用户CPED包重建任职、关系和晋升。以原始Excel物理行号和person_id追溯事件。年度基期是上一年12月31日，避免先把1月1日已晋升者排出当年的风险集；当年内首次及其他符合条件的明确新职位产生年度0/1事件，同一年度最多记1。同一人兼市长和书记按书记归类；同职多人和一人多城的未决基期不擅自裁定。
主晋升=普通地级市市长升任普通地级市市委书记，或实际行政级别上升；对照只算职级上升。基期级别取快照时已在任实职的最高已记录级别，不采用日后最高级别。普通代表、泛委员身份、学生经历不作为实职晋升，人大政协实职另标second_line。 source flag与地理层级矛盾的县委书记记录不得当作地级市书记晋升；修正留痕共{PREP['scope_corrections']}个年度／任期结果。
已观察完整职业区间、没有晋升者记0；明确的免职、退休等作为竞争去向记0。日期不完整、职业区间有空档、基期或新职级不足以判定者保留未知。2018年大量记录于6月截止，因此不当作完整年度。缺失职务结束日期不延长为在任。任期版合并连续同人同城同职，在离任后12个月内取首个明确去向；没有可确认后续职位者未知。年度版与任期版有不同估计对象。

## 关系
主关系为共事至少六个日历月，取完整4,603人网络，省级领导不要求曾任市级主官。legacy关系须严格早于2012-01-01和双方当前共同任职起点；preassignment对照不要求早于2012，但仍早于共同任职起点。以前的个人边不消失，当前领导更替改变的是任职关系暴露。省委书记S、省长G同时入模；市长和市书记分开。未知不补0；合并connected的三项都可比且无正边才记0。同乡和同期校友单列对照。共事可能仅反映同一领导班子或委员会，不是私人密友或腐败团伙认证。

## 估计与样本
Y=100×晋升0/1。窗口内LPM同时放CS和CG，系数为百分点差异。C0仅FE；C1加年龄/平方、职务任期/平方和基期级别类别；C2加精确上年的城市GDP增长、log人均GDP、log人口。控制比较的common样本要求全部C2字段可用。C0/C1另存maximal样本，避免隐藏额外控制导致的缩样。没有要求2011已在任。
PY=省份+年份；PXY=省份×年份，主FE；CITY_PXY=城市+省份×年份。lag GDP增长直接用现有城市年鉴面板old_gdp_growth_pct，未用代理或补缺值。城市控制匹配普通地级单位，全市口径。
日历滚动3/5/7年，五年为主；全国反腐分界Post=2013起，滚动图保留2012，包含2012的窗口涂灰。首次巡视用直接核验的31省原始日程表，按官方省代码匹配，不从旧市级结果间接继承，以补足西藏旧面板缺年问题。相对时间3年为主、5/7年为对照，窗口端点要求两批巡视省都有日历年覆盖，不外推到2018以后；包含进驻年者涂灰。五/七年窗末端可能没有严格事后的完整窗口。
pooled同时估计CS、CG、CS×Post、CG×Post，计算Pre、Post和Change，并使用完整协方差。national_main排除2012；national_include2012将2012纳入前期；inspection_main从进驻年起Post；inspection_drop_entry剔除进驻年。各版本均保留。
窗口至少10省、10个晋升事件、每位省级领导变量至少10个有关系与10个无关系观测；目标变量残差矩阵须满秩且CI有效。缺少支持或不能分别识别两个关系系数时不输出伪零。
主网格年度共事legacy涵盖三控制×三FE×三宽度×两时间轴；C0/C1另有最大样本。其他关系、关系时间、纯职级晋升和任期结果按C1/PXY及对应主宽度比较，避免无目的的全组合搜索。pooled保留各控制/FE及过渡年口径对照。

## 推断和核验
按基期任职省聚类，CR1有限样本修正和t(G-1)，95%逐点CI。四个年度主pooled模型、八个Change检验由Stata areg和boottest独立重估，Webb权重9,999次、种子20261015；前后优势的SE使用协方差，非把两个SE相加。八项主Change报告常规和wild p及各自Holm校正。{V['primary_contrasts_stata']}个主对比与独立Stata核对，{V['independent_rolling_contrasts']}个预定滚动对比另用显式FE虚拟变量求解核对。原网络文件哈希保持不变。

Wang–Yang仅用于交叉核验：作者代码晋升标签3/4为1，不是标签1；4,979条记录中唯一匹配4,100条。主期内两边均有可比结果{PREP['wy_both_known']}条，一致{PREP['wy_agree']}条、不同{PREP['wy_disagree']}条。差异可能来自任期边界、后续职位、源履历或晋升分类，逐条提供；不能说两库晋升结果完全一致。未用外部标签覆盖CPED。

## 解释边界
这是有控制的关系—晋升关联，不是外生关系的因果回报。2013全国换届、省级领导更替、反腐后的受查退出、晋升机会和样本构成都可能改变系数。前显著后不显著不是前后差异显著，后期区间跨0不是证明效应消失。滚动窗口重叠，不能将多次显著点当独立重复证据。跨库299条尚未消除的差异也限制强解释。

## 重跑与文件
Python依赖pandas、numpy、openpyxl、scipy、matplotlib；Stata18及既有boottest依赖。顺序：code/prepare.py → code/audit_data.py → code/estimate.py → Stata code/validate_primary.do → code/final_validation.py → code/report.py。原始输入路径在脚本开头，原网络不修改。核验记录为data_validation_checks.csv、numerical_validation_checks.csv及explicit_dummy_rolling_validation.csv；完整系数all_estimates_validated.csv，所有模型状态model_status.csv。index.html可交互浏览所有成功模型并查看失败信息；figures/为固定预定主图与对照图。无PDF。
'''
methods+='\n## 名义窗口与实际年份覆盖\n共同C2完整样本因滞后城市数据缺失，2000—2002、2006—2007等年份可能整体不可用；主common样本实际从2003年起。名义五年区间不是保证五个年份都有有效观察，一些早期相邻窗口使用相同观察，所以点估计相同。窗口仍全部保留，没有插值或按结果删点；缺整年或巡视批次覆盖不足的点标为空心，observed_time_levels和window_support_details.csv记录实际覆盖。另附C1 maximal五年日历图及三年巡视图，使用个人控制最大可用样本，不因C2城市变量缺失缩样。它们是预定样本敏感性，不替代主common规格。\n重跑可在final_validation.py之后运行window_support.py以单独生成覆盖明细；estimate.py也已直接写入这些元数据。\n'
methods+='\npooled始终包括Post主效应：在省份×年份及城市＋省份×年份中被吸收，在省份＋年份的巡视模型中单独估计。80个相关补充模型已按此重估，并另用显式虚拟变量独立核对6个对比；八项主检验不受影响。\n'
(OUT/'methods_中文.md').write_text(methods,encoding='utf8')

# Offline SVG explorer exposes all estimates and recorded failures, not just main figures.
data=R.to_json(orient='records',force_ascii=False);statuses=STATUS.to_json(orient='records',force_ascii=False)
template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>省市关系与晋升：全部结果</title><style>body{font:15px/1.65 system-ui;max-width:1450px;margin:25px auto;padding:0 18px;color:#243544}header{background:#eef5f8;padding:20px;border-radius:10px}select{padding:5px;max-width:220px}label{display:inline-block;margin:5px 12px 5px 0}#plots{display:grid;grid-template-columns:1fr 1fr;gap:16px}.panel{border:1px solid #d8e1e7;border-radius:8px;padding:10px}svg{width:100%;height:auto}.gallery{display:grid;grid-template-columns:1fr 1fr;gap:15px}.gallery img{width:100%}details{margin:12px 0}pre{white-space:pre-wrap;font:14px/1.7 system-ui}table{border-collapse:collapse;font-size:12px}td,th{border:1px solid #ddd;padding:5px}#failure{max-height:220px;overflow:auto}</style><header><h1>省市官员关系与晋升：完整结果</h1><p>All pre-specified rolling windows and pooled comparisons. Pointwise 95% province-clustered CIs. No connecting lines. Results are associations.</p><p>年度／任期、关系类型、控制、固定效应、样本均可切换。主规格：annual / promotion / cowork_6m / legacy / C1 / PXY / common。全国比较Post从2013年起，主pooled排除2012；首次巡视按各省进驻年。无足够支持的窗口保留失败记录。</p></header><div id="filters"></div><p id="caption"></p><div id="plots"></div><details><summary>当前筛选的未估计模型及原因</summary><div id="failure"></div></details><h2>预定图片</h2><div class="gallery">__GALLERY__</div><details><summary>完整方法与限制</summary><pre>__METHODS__</pre></details><script>const DATA=__DATA__, STATUS=__STATUS__;
const keys=['kind','unit','outcome','relation','timing','controls','fe','sampling','axis','width'];
const defaults={kind:'rolling',unit:'annual',outcome:'promotion',relation:'cowork_6m',timing:'legacy',controls:'C1',fe:'PXY',sampling:'common',axis:'calendar',width:'5'};
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
keys.forEach(k=>{let vals=[...new Set(STATUS.map(x=>String(x[k])))];if(k==='width')vals.sort((a,b)=>+a-+b);const s=document.createElement('select');s.id=k;vals.forEach(v=>s.add(new Option(v,v)));s.value=defaults[k];s.onchange=()=>{if(k==='kind'){document.getElementById('axis').value=s.value==='pooled'?'national_main':'calendar';document.getElementById('width').value=s.value==='pooled'?'0':'5';}if(k==='axis'&&document.getElementById('kind').value==='rolling')document.getElementById('width').value=s.value==='inspection_relative'?'3':'5';draw();};const l=document.createElement('label');l.textContent=k+' ';l.append(s);document.getElementById('filters').append(l);});
function draw(){const f=Object.fromEntries(keys.map(k=>[k,document.getElementById(k).value]));const match=x=>keys.every(k=>String(x[k])===f[k]);const rows=DATA.filter(match),fail=STATUS.filter(match).filter(x=>x.status!=='OK');document.getElementById('caption').textContent=`${rows.length} estimates; ${fail.length} unestimated models. Unit: percentage points. Gray: windows containing cutoff year.`;document.getElementById('failure').innerHTML=fail.length?'<pre>'+esc(JSON.stringify(fail.map(x=>({role:x.role,center:x.center,N:x.N,G:x.G,status:x.status})),null,2))+'</pre>':'No failed cells in this selection.';const box=document.getElementById('plots');box.innerHTML='';for(const role of ['mayor','secretary'])for(const lead of ['S','G']){let q=rows.filter(x=>x.role===role&&x.leader===lead);const div=document.createElement('div');div.className='panel';let h='<h3>'+esc(role==='mayor'?'Mayors':'City party secretaries')+' → '+esc(lead==='S'?'Provincial party secretary':'Governor')+'</h3>';if(!q.length){div.innerHTML=h+'<p>No estimable model for this selection.</p>';box.append(div);continue;}const pooled=f.kind==='pooled';const xv=r=>pooled?({pre:0,post:1,change:2})[r.estimand]:r.center;q.sort((a,b)=>xv(a)-xv(b));let xmin=Math.min(...q.map(xv))-.5,xmax=Math.max(...q.map(xv))+.5,ymin=Math.min(0,...q.map(r=>r.lo)),ymax=Math.max(0,...q.map(r=>r.hi));let pad=Math.max(1,(ymax-ymin)*.12);ymin-=pad;ymax+=pad;const xx=x=>65+(x-xmin)/(xmax-xmin)*490,yy=y=>280-(y-ymin)/(ymax-ymin)*245;let s='<svg viewBox="0 0 600 350" role="img">';if(!pooled){const cut=f.axis==='calendar'?2012:0,hw=+f.width/2-.5;s+=`<rect x="${xx(Math.max(xmin,cut-hw-.35))}" y="25" width="${Math.max(0,xx(Math.min(xmax,cut+hw+.35))-xx(Math.max(xmin,cut-hw-.35)))}" height="255" fill="#eee"/>`;}for(let j=0;j<5;j++){const y=ymin+(ymax-ymin)*j/4;s+=`<line x1="65" x2="555" y1="${yy(y)}" y2="${yy(y)}" stroke="#eee"/><text x="58" y="${yy(y)+4}" text-anchor="end" font-size="11">${y.toFixed(1)}</text>`;}s+=`<line x1="65" x2="555" y1="${yy(0)}" y2="${yy(0)}" stroke="#999" stroke-dasharray="5 4"/>`;for(const r of q){const x=xx(xv(r)),col=pooled?({pre:'#287c9e',post:'#cf8735',change:'#a9537e'})[r.estimand]:'#287c9e';s+=`<g><title>${esc('b='+r.b.toFixed(3)+'; 95% CI=['+r.lo.toFixed(3)+', '+r.hi.toFixed(3)+']; p='+r.p?.toFixed(4)+'; N='+r.N+'; provinces='+r.G+(r.p_wild!=null?'; wild p='+r.p_wild.toFixed(4):''))}</title><line x1="${x}" x2="${x}" y1="${yy(r.lo)}" y2="${yy(r.hi)}" stroke="${col}" stroke-width="2"/><line x1="${x-4}" x2="${x+4}" y1="${yy(r.lo)}" y2="${yy(r.lo)}" stroke="${col}"/><line x1="${x-4}" x2="${x+4}" y1="${yy(r.hi)}" y2="${yy(r.hi)}" stroke="${col}"/><circle cx="${x}" cy="${yy(r.b)}" r="4" fill="${col}"/></g>`;}const ticks=pooled?[0,1,2]:q.map(xv).filter((x,i)=>i%Math.max(1,Math.ceil(q.length/9))===0);for(const x of ticks)s+=`<text x="${xx(x)}" y="302" text-anchor="middle" font-size="11">${pooled?['Before','After','Change'][x]:x}</text>`;s+='<text x="310" y="330" text-anchor="middle" font-size="12">'+(pooled?'Pooled contrast':f.axis==='calendar'?'Window center year':'Window center relative to inspection')+'</text><text x="18" y="155" transform="rotate(-90 18 155)" text-anchor="middle" font-size="12">Percentage points</text></svg>';div.innerHTML=h+s;box.append(div);}}
draw();</script></html>'''
links=''.join('<figure><a href="'+x['file']+'"><img loading="lazy" src="'+x['file']+'"></a><figcaption>'+html.escape(x['title'])+'</figcaption></figure>' for x in gallery)
page=template.replace('__GALLERY__',links).replace('__METHODS__',html.escape(methods)).replace('__DATA__',data).replace('__STATUS__',statuses)
page=page.replace('r="4" fill="${col}"','r="4" fill="${r.incomplete_window?\'white\':col}" stroke="${col}"')
page=page.replace('No connecting lines. Results are associations.','No connecting lines. Hollow points have whole-year / cohort coverage gaps. Results are associations.')
page=page.replace("+' → '+","+' | Tie to '+")
(OUT/'index.html').write_text(page,encoding='utf8');(OUT/'figure_manifest.json').write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf8')

# Self-contained workbook; raw inputs are preserved at their original paths.
book={'主结果前后差异':PRIMARY,'全部系数':R,'全部模型及留空':STATUS,'年度晋升面板':A,'任期去向面板':T,'年度样本与事件数':annual,'WangYang核验':W,'跨库不一致':W[W.both_known&W.agreement.eq(0)],'晋升事件证据':pd.read_csv(OUT/'annual_promotion_event_registry.csv'),'纯职级晋升证据':pd.read_csv(OUT/'rank_promotion_event_registry.csv'),'数据核验':pd.read_csv(OUT/'data_validation_checks.csv'),'独立数值核验':pd.read_csv(OUT/'numerical_validation_checks.csv'),'县市层级修正':pd.read_csv(OUT/'scope_corrections_before_estimation.csv'),'巡视来源':pd.read_csv(OUT/'inspection_timing.csv')}
with pd.ExcelWriter(OUT/'省市关系与晋升_全部结果.xlsx',engine='openpyxl') as w:
 for name,d in book.items():
  d.to_excel(w,sheet_name=name,index=False);ws=w.sheets[name];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
dictionary=[]
for c in A:
 s=A[c];meaning={'promotion':'主晋升：普通市长升普通市委书记或行政级别上升','rank_promotion':'仅行政级别上升','year':'实际晋升观察年；2000–2017','baseline_date':'上一年12月31日，确定风险集及领导关系','base_rank':'基期已记录在任实职最高级别：0小于副处…8正国','k':'实际年份减首次中央巡视年份','status':'晋升结果是否观察完整及删失原因','gdp_growth_lag':'精确上年GDP增长率，既有城市年鉴变量','S_person_id':'基期省委书记CPED ID','G_person_id':'基期省长CPED ID'}.get(c,'见方法和脚本；关系列legacy/preassignment分别为事前旧关系/各时期事前关系，后缀S/G为省委书记/省长。')
 dictionary.append(dict(variable=c,definition=meaning,dtype=str(s.dtype),missing=int(s.isna().sum()),nonmissing=int(s.notna().sum()),unique=int(s.nunique())))
pd.DataFrame(dictionary).to_csv(OUT/'variable_codebook.csv',index=False,encoding='utf-8-sig')
shutil.copy2(__file__,OUT/'code/report.py')
files=[dict(path=str(f.relative_to(OUT)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in OUT.rglob('*') if f.is_file() and f.name!='file_manifest.csv'];pd.DataFrame(files).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
archive=OUT.parent/'省市官员关系与晋升_滚动回归_数据图表代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(OUT)))
print(json.dumps({'figures':len(gallery),'workbook_sheets':len(book),'archive':str(archive),'archive_bytes':archive.stat().st_size},ensure_ascii=False),flush=True)
