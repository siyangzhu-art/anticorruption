from pathlib import Path
import sys,json,html,shutil,zipfile,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimate_revised import OUT
R=pd.read_csv(OUT/'all_estimates_validated.csv',low_memory=False)
P=pd.read_csv(OUT/'primary_pooled_estimates_validated.csv')
A=pd.read_csv(OUT/'annual_official_panel.csv.gz',low_memory=False)
V=json.loads((OUT/'validation_summary.json').read_text(encoding='utf8'));assert V['all_passed']
S=json.loads((OUT/'preparation_summary.json').read_text(encoding='utf8'))
E=json.loads((OUT/'estimation_summary.json').read_text(encoding='utf8'))
R['incomplete_window']=R.incomplete_window.astype(str).str.lower().eq('true')
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
LEAD={'S':'Provincial party secretary','G':'Governor'}
ROLES={'all':'All city principals','mayor':'Mayors','secretary':'City party secretaries'}
gallery=[]
def pv(x):return 'NA' if pd.isna(x) else ('<0.001' if x<.001 else f'{x:.3f}')
def select(**kw):
 q=R
 for k,v in kw.items():q=q[q[k].eq(v)]
 return q
def export(fig,name,title):
 fig.savefig(FIG/name,dpi=165);plt.close(fig);gallery.append(dict(file='figures/'+name,title=title))
def rolling(name,axis='calendar',width=None,roles=['all'],compare=None,relation='cowork_6m',outcome='promotion',sampling='maximal'):
 width=width or (5 if axis=='calendar' else 3)
 groups=['C0','C1','C2'] if compare=='controls' else ['PY','PXY','CITY_PXY'] if compare=='fe' else ['C1']
 if compare=='controls':sampling='common'
 if relation!='cowork_6m' or outcome!='promotion':sampling='common'
 fig,axes=plt.subplots(len(roles),2,figsize=(13,4.5*len(roles)+1.8),squeeze=False)
 for i,role in enumerate(roles):
  for j,lead in enumerate(LEAD):
   ax=axes[i,j];ax.axhline(0,color='gray',ls='--',lw=1)
   cut=2012 if axis=='calendar' else 0;h=width//2
   ax.axvspan(cut-h-.3,cut+h+.3,color='#eeeeee',zorder=0)
   ax.axvline(2012.5 if axis=='calendar' else 0,color='#ac914c',ls=':',lw=1)
   shown=False
   for ig,g in enumerate(groups):
    q=select(kind='rolling',unit='annual',role=role,leader=lead,outcome=outcome,relation=relation,timing='legacy',controls=g if compare=='controls' else 'C1',fe=g if compare=='fe' else 'PXY',sampling=sampling,axis=axis,width=width).sort_values('center')
    if not len(q):continue
    shown=True;offset=(ig-(len(groups)-1)/2)*.12;color=['#287c9e','#cf8735','#a9537e'][ig]
    ax.errorbar(q.center+offset,q.b,yerr=[q.b-q.lo,q.hi-q.b],fmt=['o','s','D'][ig],ls='none',capsize=3,ms=4,color=color,label=g)
    gap=q[q.incomplete_window]
    ax.plot(gap.center+offset,gap.b,marker=['o','s','D'][ig],ls='none',mfc='white',mec=color,ms=4)
   if not shown:ax.text(.5,.5,'Not estimable under support rules',ha='center',transform=ax.transAxes)
   if compare:ax.legend(fontsize=8)
   ax.set_title(ROLES[role]+' | Tie to '+LEAD[lead],fontsize=11)
   ax.set_ylabel('Promotion probability difference (pp)')
   ax.set_xlabel('Window center year' if axis=='calendar' else 'Window center relative to first inspection')
   ax.grid(axis='y',alpha=.15)
   if axis=='calendar':ax.set_xticks(range(2006+width//2,2018-width//2))
 desc={'promotion':'Revised broad promotion','rank_promotion':'Administrative-rank promotion only','executive_promotion':'Sensitivity: exclude flagged second-line promotions'}[outcome]
 title=f'{desc} | 2006-2017 | {width}-year rolling windows'
 fig.suptitle(title+'\n95% province-clustered confidence intervals',fontsize=15,y=.98)
 fig.subplots_adjust(top=1-.15/(len(roles)**.5),bottom=.20/(len(roles)**.5),hspace=.48,wspace=.27)
 fig.text(.07,.025,'Both leader ties jointly; province-by-year FE unless compared. Pooled sample controls for mayor / secretary status.\n'+('C0 / C1 / C2 on common complete observations.' if compare=='controls' else ('Personal controls, maximal available sample.' if sampling=='maximal' else 'Personal controls, common full-control sample.'))+' Ties formed before 2012 and joint assignment.\nGray: windows include transition / inspection year. Hollow: incomplete year / cohort support. No connecting lines.\nNew vice-governor appointments count even without a rank increase. Conditional associations; no causal interpretation.',fontsize=8)
 export(fig,name,title+' | '+axis+(' | '+compare if compare else '')+' | '+relation)

def pooled(name,axis,roles=['all']):
 fig,axes=plt.subplots(len(roles),2,figsize=(13,5.0*len(roles)+2.0),squeeze=False)
 for i,role in enumerate(roles):
  for j,lead in enumerate(LEAD):
   ax=axes[i,j];ax.axhline(0,color='gray',ls='--',lw=1)
   q=P[P.axis.eq(axis)&P.role.eq(role)&P.leader.eq(lead)].set_index('estimand')
   for ix,est in enumerate(['pre','post','change']):
    r=q.loc[est];ax.errorbar(ix,r.b,yerr=[[r.b-r.lo],[r.hi-r.b]],fmt=['o','s','D'][ix],color=['#287c9e','#cf8735','#a9537e'][ix],capsize=4,ms=6)
    ax.annotate(f'{r.b:+.2f}',(ix,r.b),xytext=(9,5),textcoords='offset points',fontsize=9)
   ax.set_xticks([0,1,2],['Before','After','After - Before']);ax.set_xlim(-.45,2.55)
   ax.set_title(ROLES[role]+' | Tie to '+LEAD[lead],fontsize=11)
   ax.set_ylabel('Promotion probability difference (pp)');ax.grid(axis='y',alpha=.15)
   ax.text(.5,-.17,'Raw p: '+' / '.join(pv(q.loc[k,'p']) for k in ['pre','post','change'])+'\nChange wild-bootstrap p: '+pv(q.loc['change','p_wild']),transform=ax.transAxes,ha='center',va='top',fontsize=8.5)
 title='Revised broad promotion | 2006-2017 | '+('National anticorruption split' if axis=='national_main' else 'First provincial inspection')
 fig.suptitle(title+'\nBefore / after / change | 95% confidence intervals',fontsize=15,y=.98)
 fig.subplots_adjust(top=.83 if len(roles)==1 else .92,bottom=.31 if len(roles)==1 else .17,hspace=.78,wspace=.27)
 fig.text(.065,.03,'Personal controls; province-by-year FE; both leader ties jointly. Pooled models control for current mayor / secretary status.\nMaximal C1 sample. National split: 2006-2011 vs 2013-2017; 2012 omitted. Inspection split includes entry year as Post.\nProvince-clustered t CIs; Webb wild bootstrap: 9,999 repetitions, seed 20261015. No connecting lines.\nA nonsignificant post coefficient does not establish equality. A change must be tested directly.',fontsize=8)
 export(fig,name,title)

rolling('01_total_calendar_5year.png')
rolling('02_total_inspection_3year.png',axis='inspection_relative')
pooled('03_total_national_pre_post.png','national_main')
pooled('04_total_inspection_pre_post.png','inspection_main')
for axis in ['calendar','inspection_relative']:
 rolling('split_'+axis+'.png',axis=axis,roles=['all','mayor','secretary'])
 rolling('controls_'+axis+'.png',axis=axis,compare='controls')
 rolling('fixed_effects_'+axis+'.png',axis=axis,compare='fe')
 for w in [3,5,7]:
  if w==(5 if axis=='calendar' else 3):continue
  rolling(f'window_{axis}_{w}.png',axis=axis,width=w)
 for rel in ['hometown_prefecture','classmate_6m','connected']:
  rolling(rel+'_'+axis+'.png',axis=axis,relation=rel)
 for outcome in ['rank_promotion','executive_promotion']:
  rolling(outcome+'_'+axis+'.png',axis=axis,outcome=outcome)
pooled('split_national_pre_post.png','national_main',roles=['all','mayor','secretary'])
pooled('split_inspection_pre_post.png','inspection_main',roles=['all','mayor','secretary'])

annual=A.groupby(['year','role']).agg(rows=('person_id','size'),known=('promotion','count'),promotions=('promotion','sum'),rank_promotions=('rank_promotion','sum'),new_same_grade_vice_governor=('same_grade_vice_governor_event','sum')).reset_index()
annual.to_csv(OUT/'annual_descriptive_summary.csv',index=False,encoding='utf-8-sig')
key=P[P.role.eq('all')].pivot(index=['axis','leader'],columns='estimand',values=['b','p','lo','hi','p_wild']).reset_index()
key.columns=['_'.join(str(z) for z in c if z) for c in key.columns];key.to_csv(OUT/'total_main_results.csv',index=False,encoding='utf-8-sig')
methods=f'''# 2006—2017：修订晋升定义、市长与市委书记合并估计

## 本轮变更
仅使用原有CPED履历和已核验关系暴露，不增加外部履历。晋升主指标=行政级别上升，或市长转市委书记，或新任省级政府副职（副省长/自治区副主席/直辖市副市长等来源“副省长”标志）。最后一项允许原来已是副部级。原任副省长职务的连续记录/续任不重新计为晋升；行政级别下降不计这项新增晋升。同级转其他省委常委职务没有自动一律计为晋升。
保留原主指标对行政级别上升至人大/政协实职的编码，另提供排除被标记二线晋升的敏感性结果，以及仅行政级别上升的结果。不是把所有平级调动都当晋升。
年度版仍为上一年12月31日在任市长/书记，预测随后日历年的实际晋升事件；同人同年兼任两职归书记。未知不填0。原风险集不变，仅截取2006—2017。
新增{S['annual_changes']}个晋升事件年。年度风险集{S['annual_rows']:,}个人年、{S['annual_people']:,}人，已知Y {S['annual_known']:,}行、晋升{S['annual_promotions']:,}个事件年。promotion_definition_changes.csv逐条列出变化。

## “总的”估计
市长、书记合在同一回归，加入当前是否市委书记的指示变量；同时保留市长、书记各自结果。与省委书记CS、与省长CG两项关系同时进入，并未把两个系数加总。
窗口回归：100 Promotion = beta_S CS + beta_G CG + rho Secretary + X gamma + FE + error。
前后回归：在上述式子加入CS×Post和CG×Post；可识别时加入Post主效应，省×年FE下其被吸收。pre=beta；post=beta+theta；变化=theta。province/year FE 的补充回归明确包括Post主效应。
主关系：至少六个月的共事，形成于2012年以前且早于共同任职开始；同乡、同期校友、任一关系另报。与当年基期在任省级主官的暴露随人员变化，个人边不删除。

## 年份、控制、推断
主结果为2006—2017年、C1个人控制最大可用样本：年龄及平方、任期及平方、基期行政级别；合并样本额外控制职务。主FE为省×年。补充省+年、城市+省×年。
为保留2006、2007年，不再把主规格限制为城市经济控制完整样本。比较C0/C1/C2时使用同一完整样本；C2追加严格上年GDP增长、对数人均GDP、对数人口，并保存实际年份及缺口。C0/C1最大样本全部保留。这一调整先于查看回归结果确定。
全国前后主版：2006—2011 vs 2013—2017，2012过渡年从交互回归排除、滚动图保留。补充将2012归前。巡视主版各省首次进驻年起Post；另报剔除进驻年。
日历五年窗、巡视相对三年窗为主要图；另报3/5/7年完整名义窗口。灰色为含分界年的混合窗口；空心为实际整年/巡视批次覆盖不足，不补齐端点。所有支持窗口均展示，不按显著性挑选。
省聚类，95%逐点t(G-1)置信区间。12项主变化（3职务样本×2分界×2省级领导）的Webb wild bootstrap 9999次、种子20261015，并报告12项Holm校正。合并总样本主检验与分组检验并非相互独立。
至少10省、10晋升事件且每项关系至少10个有/无关系观测；不能识别则留空。共{E['models_requested']}个模型、{E['models_ok']}个成功，其余失败原因保留。

## 任期核验
另提供任期中晋升+离任后首个去向的修订事件核验表，修复只比较离任前后级别而漏记任内晋升的问题。该核验表不用于本轮回归：若把因变量扩展到整个任期，原来的离任时关系暴露可能晚于晋升，须先重新锚定任期起点的解释变量。本轮所有估计均为时间顺序明确的年度版。

## 解释边界
主结果考察关系与晋升的条件关联，不直接识别反腐/巡视因果效应。前期显著、后期不显著本身不代表系数下降；请看变化及其区间。不进行等效判断。新任副省长计为晋升是本轮用户明确采用的职务进阶口径，不声称所有同级岗位转换都是客观行政晋级。

## 可重跑
使用项目Python环境依次运行code/revise_2006_2017.py、code/estimate_revised.py；Stata18执行code/validate_revised.do；再运行code/validate_revised.py和code/report_revised.py。prepare.py仅作为原始载入函数来源，不单独运行。路径保留本机项目根目录，移动项目时修改ROOT/OUT。原始zip、原网络、上一轮结果均不覆盖。不生成PDF。
'''
(OUT/'methods_中文.md').write_text(methods,encoding='utf8')

tabs={'Total_main':key,'Primary_all_roles':P,'All_coefficients':R,'Model_status':pd.read_csv(OUT/'model_status.csv'),'Annual_panel':A,'Annual_events':pd.read_csv(OUT/'annual_promotion_event_registry.csv'),'Definition_changes':pd.read_csv(OUT/'promotion_definition_changes.csv'),'Term_audit_only':pd.read_csv(OUT/'term_destination_panel.csv.gz'),'Term_evidence':pd.read_csv(OUT/'term_promotion_event_evidence.csv'),'Annual_summary':annual,'Codebook':pd.read_csv(OUT/'variable_codebook.csv'),'Data_checks':pd.read_csv(OUT/'data_validation_checks.csv'),'Numerical_checks':pd.read_csv(OUT/'numerical_validation_checks.csv')}
with pd.ExcelWriter(OUT/'晋升合并样本_2006_2017_修订结果.xlsx',engine='openpyxl') as w:
 for name,d in tabs.items():
  d.to_excel(w,sheet_name=name,index=False);ws=w.sheets[name];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
  for col in list(ws.columns)[:12]:ws.column_dimensions[col[0].column_letter].width=min(36,max(12,len(str(col[0].value))+3))

cards=''.join('<section><h2>'+html.escape(g['title'])+'</h2><a href="'+g['file']+'"><img loading="lazy" src="'+g['file']+'" alt="'+html.escape(g['title'])+'"></a></section>' for g in gallery)
mainhtml=P[P.role.eq('all')][['axis','leader','estimand','b','lo','hi','p','p_wild','N','G']].round(4).to_html(index=False)
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>2006–2017 晋升与省市关系</title><style>body{font:16px system-ui;max-width:1400px;margin:auto;padding:25px;background:#fafafa;color:#222}section{background:white;padding:18px;margin:25px 0;border:1px solid #ddd}img{width:100%;height:auto}h2{font-size:19px}table{border-collapse:collapse;font-size:13px}td,th{padding:6px;border:1px solid #ddd}.note{padding:14px;background:#eef4f7}a{color:#176788}</style><h1>2006—2017：晋升定义修订与合并样本</h1>'''
page+='<p class="note">主指标包含同级副部市委书记新任副省长；市长、书记合并并控制职务。全部图为95%CI、无连线。灰色窗口跨分界，空心点表示覆盖不足。条件关联不能直接解释为巡视因果效应。</p>'
page+='<p><a href="晋升合并样本_2006_2017_修订结果.xlsx">Excel全部结果</a> · <a href="methods_中文.md">定义、样本与方法</a> · <a href="promotion_definition_changes.csv">逐条晋升变化</a> · <a href="all_estimates_validated.csv">全部回归CSV</a></p>'
page+=cards+'<section><h2>合并样本主结果数值</h2>'+mainhtml+'</section></html>'
(OUT/'index.html').write_text(page,encoding='utf8')
shutil.copy2(__file__,OUT/'code/report_revised.py')
for fn in ['make_revised_estimator.py','make_revised_validation.py']:
 shutil.copy2(Path(__file__).parent/fn,OUT/'code'/fn)
manifest=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='file_manifest.csv':manifest.append(dict(file=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
pd.DataFrame(manifest).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
archive=OUT.parent/'省市关系与晋升_2006_2017_合并修订版.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'figures':len(gallery),'excel_sheets':len(tabs),'zip':str(archive),'total_main':P[P.role.eq('all')].to_dict('records')},ensure_ascii=False,default=str),flush=True)
