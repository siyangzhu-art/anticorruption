from pathlib import Path
import sys,json,hashlib,shutil,html
from html.parser import HTMLParser
sys.path.append(r'C:\Users\siyang zhu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages')
import pandas as pd,numpy as np
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'audit_main_page_methods_2026_10_21';P=B/'organized_main_results_corruption_checks_2026_10_21/index.html';W=Path(__file__).parent
compare=pd.read_csv(O/'data/isolated_rerun_comparison.csv');rr=pd.read_stata(O/'corruption_rerun.dta')
ca=pd.read_csv(P.parent/'data/corruption_checks_annual.csv');cc=pd.read_csv(P.parent/'data/corruption_checks_cumulative.csv');extra=[]
for r in rr.itertuples():
 q=cc[cc.variant.eq(r.variant)&cc.H.eq(24)].iloc[0] if r.method=='cumulative24m' else ca[ca.variant.eq(r.variant)&ca.estimator.eq(r.method)&ca.fe.eq(r.fe)].iloc[0]
 extra.append(dict(variant=r.variant,method=r.method,fe=r.fe,**{col:float(getattr(r,col)-q[col]) for col in ['b','se','p','lo','hi']}))
extra=pd.DataFrame(extra);extra.to_csv(O/'data/corruption_rerun_comparison.csv',index=False,encoding='utf-8-sig');assert extra[['b','se','p','lo','hi']].abs().max().max()<5e-6
wild=pd.read_stata(O/'wild24_rerun.dta');baseline=pd.read_csv(P.parent/'data/main_cumulative.csv');q=wild.merge(pd.concat([baseline.assign(variant='Original'),cc]).query('H==24')[['variant','p_wild']].drop_duplicates('variant'),on='variant',suffixes=('_rerun','_original'),validate='1:1');q['error']=q.p_wild_rerun-q.p_wild_original;assert q.error.abs().max()<1e-12 and wild.rc.eq(0).all();q.to_csv(O/'data/wild24_rerun_comparison.csv',index=False,encoding='utf-8-sig')
support=pd.read_csv(O/'data/annual_support.csv');selection=pd.read_csv(O/'data/cumulative_observation_selection.csv');retention=pd.read_csv(O/'data/cumulative_retention_by_C0.csv');exclusion=pd.read_csv(O/'data/strict_exclusion_which_group.csv')
raw=pd.read_csv(O/'data/annual_raw_positive_event_checks.csv');assert raw[['source_id_matches','date_matches','date_in_outcome_year','substantive']].all().all() and not raw.generic.any()
primary_url='https://github.com/lsun20/EventStudyInteract'
review_url='https://www.jonathandroth.com/assets/files/DiD_Review_Paper.pdf'
def code(file,line):return str(W/file)+':'+str(line)
issues=[
 dict(id='A01',priority='P1｜识别',title='累计24／36个月的事前窗口晚选队列：不能将负θ直接解释为巡视削弱关系回报',
 evidence='队列取k=-1年度记录，采用该行上年末在任者。共同422人中，24和36个月事前窗全部422人的名单快照晚于窗口开始；12个月没有这一问题。对24个月前窗而言，关系组17/45=37.78%，对照组143/377=37.93%，原始率没有正的事前关系优势。',
 implication='事前晋升会改变是否进入较晚的市级主官名单、基期职务、职级及后续晋升空间。个人FE只能吸收不变水平，不能消除按先前结果选择队列与均值回归。基期控制还可能在较长事前窗口的结果之后测量。',
 action='把当前长前窗累计结果降为探索性。重新设计时，在整段比较窗口开始前定义官员风险集和关系，前瞻追踪同一批人的后续结果；同时区分预先定义队列中的职务变化与失访。不能靠再挑窗口解决选择问题。',
 source=code('cumulative_twfe_prepare.py',56)+'；'+code('cumulative_twfe_prepare.py',123)),
 dict(id='A02',priority='P1｜识别',title='年度风险集与累计完整样本均受事后可观察性影响',
 evidence='年度事前关系组逐期人数为25、34、51、60、46、36、30、16、4；+4总共42行、8省且全是2013批次。累计可用基期545人缩为共同422人：有关系保留45/64=70.31%，无关系377/481=78.38%。36个月后窗关系组15/64、对照81/481的结果未知。',
 implication='年度观察只覆盖仍在市级主官风险集且留在锚点省、变量完整的年份；晋升调离会影响后续入样。累计共同样本又要求三个期限的前后六条结果都已知。观察到正向晋升即能确认Y=1，而Y=0需完整覆盖；这种合理的测量规则仍可能产生与结果相关的完整样本选择。它不是缺失已被解决。',
 action='保留固定官员ID并建立月度风险集、离任与删失表；晋升后退出、退休等竞争事件和信息缺失分开。报告最大样本与共同样本的入样过程；对删失建模或作透明界限分析。不能把所有失访补0，也不能机械地将非市级主官后续年补0。',
 source=code('sun_abraham_post4.py',28)+'；'+code('cumulative_twfe_prepare.py',112)+'；'+code('cumulative_twfe_prepare.py',126)),
 dict(id='A03',priority='P1｜模型与命题',title='目前晋升指标含正式职级上升的人大／政协去向，未等同于行政实权晋升',
 evidence='年度主样本429条正向晋升中，second_line标志有46条；其中首条事件的原始类别明确为人大／政协的有44条。共同24个月样本首个正向事件中，无关系组的该类事件为事前26次、事后6次；关系组为事前1次、事后1次。',
 implication='这不是将普通委员一律算晋升：普通成员已排除。但将正厅升人大／政协副部计入总晋升，会把行政权力增强与正式职级／退出安排混合。若论文解释是关系帮助掌握行政权力，当前总Y不够贴合命题；若解释为正式职级晋升，则需明确写出。',
 action='保留已授权的广义晋升总指标，同时新增逐事件核验的行政实职晋升和人大／政协职级晋升两类结果作对照。不能只根据第一个岗位的简短名称或单个类别字段判断。',
 source=code('prepare.py',125)+'；'+code('revise_2006_2017.py',113)),
 dict(id='A04',priority='P1｜识别',title='Sun–Abraham命令调用可复现，但不是“无关系者从未被巡视”的标准ATT',
 evidence='代码定义never=(C0==0)，treated_cohort只在C0=1时赋巡视年。所有省都在2013／2014年接受本轮巡视。隔离重跑官方eventstudyinteract的数值与页面一致，未把普通TWFE改名。',
 implication='这里可以研究关系组与非关系组受巡视后的差异变化，不能把无关系组视为没有受到政策。个人＋省年FE能够吸收共同省年冲击，仍需无巡视时关系差距的反事实趋势假设；个人＋年份版本还对共同巡视响应作了较强限制。调用软件本身不自动赋予标准SA因果解释。',
 action='将估计对象统一写为“固定事前关系组的相对晋升差距变化”。主规格、假设、批次权重按该差异设计说明。保留两组FE，不因某组显著而更名为更好的因果结果。',
 source=code('sun_abraham_post4.py',33)+'；'+code('control_fe_multiverse.py',63)),
 dict(id='A05',priority='P1｜识别',title='上年GDP等虽正确跟随官员，但晚期控制可能已受巡视影响',
 evidence='经济匹配实际为结果t行对应的t-1年末任职城市，匹配该市t-1日历年GDP增长、log人均GDP、log人口。没有错配为固定旧城市。但在k=+1时，所用经济年已经是巡视年；任期、职级、现职和任职城市也会随晋升与调动改变。',
 implication='“滞后一期”不等于“处理前”。控制受巡视影响的经济、调动或职务变量，可能阻断总效应的渠道，或产生条件选择。城市FE也不是无条件更好：当任职地点本身会被巡视改变时，解释随之改变。',
 action='预先确定目标是总效应还是给定现职／任职城市的条件关联。报告无事后控制或固定事前特征的规格，将现行C08明确作为条件关联／敏感性。不要通过看p值决定控制是否纳入。',
 source=code('add_city_economics.py',14)+'；'+code('control_fe_multiverse.py',11)),
 dict(id='A06',priority='P1｜稳健性解释',title='严格排腐败省份并未移除关系组，不能据此排除支持者离任机制',
 evidence='Strict实际删河北、福建。年度删除178行、39人，其中关系组0人；累计删除58行、29人，关系组0人。相同模型从原面板独立删省重跑，八个年度平均及三种排省版24个月累计结果均复现。',
 implication='严格版主要改变对照组，对“被移除原支持者的旧部是否丧失优势”这一机制缺少直接检验力。正常调任仍会使支持关系失效，后续受查筛选也会改变总体。两项描述统计相近不证明离任机制不存在。',
 action='只保留窄表述：这些删省不改变当前数值。按基期具体联系领导的身份与退出日期核验风险，不把整省删样当作剔除了全部支持者退出。若限制领导持续在任，须同时说明这是事后条件选择，而非自动识别净效应。',
 source=code('exclude_corruption_provinces.py',19)+'；'+code('exclude_corruption_provinces.py',81)),
 dict(id='A07',priority='P2｜统计推断',title='长期信息稀疏、规格探索与小关系省数限制显著性解释',
 evidence='年度+4只有4名有关系者、来自4省，且没有2014批次支持；同乡版12名关系者在4省，校友版8名在4省，合并版19名在6省。24个月累计wild p=0.018902，三个期限Holm校正后0.056706；此前还探索了更多控制、FE、窗口。',
 implication='26个总省份不等于每一期有26个提供关系差异的省。单期显著或四期平均显著不能证明四期稳定。三期限Holm校正只覆盖这三个期限，未覆盖全部历史探索。',
 action='完整展示支持数、逐点区间与联合检验，晚期降为补充；保留原始和校正p。补充预先选定的省级重抽样／逐省影响诊断，但不要声称这些方法在4个有效关系省时自动可靠。',
 source=code('report_control_fe_multiverse.py',71)+'；'+code('cumulative_twfe_checks_prepare.py',12)),
 dict(id='A08',priority='P2｜数据与实现',title='two fields“副省长标志／人大政协类别”冲突，需建立源记录审查名单',
 evidence='CPED物理Excel第38928行：赖德荣，2013-01-01，职务副主席、类别政协，却标为副省长（非常委）。第48259行：和段琪，2017-01-01，副主任、人大，同样副省长标志。当前VROWS主要按标志位与副部级判定。',
 implication='程序可以忠实复现原数据错误。“新任副省长”机制标签不能只相信标志位。第一条进入累计事件表时同时有职级上升，不能仅凭这个冲突断言主Y必然改变；第二条是否进入具体样本须按ID核对。',
 action='把这两条及类似跨字段冲突列为待人工核验。用机构名称、类别、实际职位、前后经历联合判断，保留原字段和修订依据；原始ZIP不改。',
 source=code('revise_2006_2017.py',34)+'；'+code('cumulative_twfe_prepare.py',68)),
 dict(id='A09',priority='P2｜实现／披露',title='second_line按当年任一候选事件赋值，不能直接当作首个晋升事件类别',
 evidence='classify返回最早的event_row，但second_line取整个候选晋升事件集合的any()。完整年度1119个正例中有11条该标志与首个事件的源类别不一致；主样本有2条。原executive_promotion又将second_line==1的正例直接改0。',
 implication='该标志更接近“当年候选晋升含人大政协”，并非“最早晋升属于人大政协”，也不是“当年没有行政实职晋升”。11条类别不一致不证明11条都误分，因为党委岗位也可能位于政协党组；但现行掩码不能直接代表是否发生任何行政实职晋升。它不改变现行广义主Y，却影响该敏感性变量的解释。',
 action='保存每次事件的完整机构与职位，并分别构造any_executive、any_second_line、first_event_type。不要用any_second_line直接否定any_executive；人工核验后重做该特定敏感性。',
 source=code('prepare.py',132)+'；'+code('revise_2006_2017.py',113)),
 dict(id='A10',priority='P2｜时间与测量',title='固定基期关系与巡视时现任关系不同；少数早期行发生关系回填',
 evidence='C0取k=-1年度行的上年末快照。已纳入年度k=-1行的523人中，快照早于巡视448—671天。2014批次的快照是2012年底：早于首次巡视，但已经晚于全国反腐开始。事前170条有关系记录中2条，其最早支持边在当时尚未达到6个月；累计前窗关系组45人中，24月1人、36月4人的边在窗口开始后才形成。',
 implication='固定分组是合理的事前暴露定义，但不能写成每一事前年份实际已建立关系，或巡视当日仍有在任支持者。首次巡视的增量效应也不等于全国2012年反腐总效应。',
 action='明确区分边的形成时间、基期领导映射时间与巡视时间；保留主固定组，另做事前整窗已形成关系的测量敏感性。不要悄悄把基期挪到巡视前一刻，因为那可能已受全国反腐影响。0只能表述为具备包内比较基础但未检出证据，不是已证明现实无关系。',
 source=code('sun_abraham_post4.py',19)+'；'+code('prepare.py',163)),
 dict(id='A11',priority='P2｜报告',title='事前正关联不稳健于共同样本与城市FE，不能直接与事件系数相加',
 evidence='原始1562条事前样本：完整控制δ=+7.98pp，p=0.029。城市FE比较的共同1456条样本：省年FEδ=+7.11，p=0.058；城市＋省年FEδ=+2.49，p=0.719。固定C0在个人FE下被吸收，此点代码正确。',
 implication='可以报告条件关联，但不应只凭显著版本宣布稳健事前优势。事前水平δ与个人FE事件β使用不同投影和权重，不能简单相加证明事后绝对优势为零。',
 action='将无city与有city、共同样本与原样本分别展示。事件研究负责相对变化，绝对水平另行定义并在一致框架估计；不显著不等于等效。',
 source=code('preinspection_fixed_C0_levels.py',15)+'；'+code('preinspection_FE_combinations.py',1)),
 dict(id='A12',priority='P2｜软件推断与时间精度',title='官方SA方差和精确进驻日需要更细的技术脚注',
 evidence='本机eventstudyinteract.ado第85行的交互回归按省聚类，但第58行对估计权重的方差用avar robust；第65行仍有unbalanced panel的TODO。当前面板不平衡。累计窗口用精确日界，CPED许多任职日期为每月1日；首次正向事件落在边界月份的记录已导出。',
 implication='这不是自行实现了假SA，而是应区分官方IW V_iw与纯省聚类回归sandwich。不能笼统保证IW所有方差环节均已按省重抽样。日级窗口也不代表原始任职数据真有日级精度。年度k=0包含进驻前月份。',
 action='标签写明官方IW方差与省聚类的交互回归，补充按省重估整个IW流程的稳健性并说明有限省数局限；累计窗口另做月界／剔除边界月的日期敏感性，k=0视作部分暴露年。',
 source=r'C:\Users\siyang zhu\ado\plus\e\eventstudyinteract.ado:58'+'；'+code('cumulative_twfe_prepare.py',123)),
 dict(id='A13',priority='P1｜新关系版本',title='同乡、校友、合并版事前联合检验均拒绝，不能作为干净的巡视因果证据',
 evidence='同乡与同期校友的8个模型，三个事前交互项的联合检验均p<0.05。合并版4个模型也均拒绝，TWFE个人＋年份p=0.0308、个人＋省年p=0.0169；合并版+4没有关系组，同期校友+2起没有关系组。',
 implication='相对-1期的负系数可能反映基期高点、差距原有变化与风险集选择。样本少也影响检验可靠性；既不能忽略拒绝，也不能将未拒绝视为平行趋势已证实。',
 action='这些图保留为探索性对照，不作为支持“反腐消除关系”的主要识别证据。优先解决队列、风险集与结果定义，不能靠删事前年份或挑参照期让图通过。',
 source=code('hometown_classmate_event_study.py',1)+'；'+code('union_hometown_school_event_study.py',1)),
]
checks={
 '78_original_contrasts_reproduced':compare.filter(like='difference').abs().max().max()<5e-6,
 '11_corruption_contrasts_reproduced':extra[['b','se','p','lo','hi']].abs().max().max()<5e-6,
 '2_wild_tests_reproduced':q.error.abs().max()<1e-12,
 '1119_raw_positive_event_ID_date_checks':raw[['source_id_matches','date_matches','date_in_outcome_year','substantive']].all().all(),
 'ordinary_generic_memberships_not_positive':not raw.generic.any(),
}
manifest=pd.read_csv(O/'data/inputs_before_audit.csv');changed=[]
for row in manifest.itertuples():
 if Path(row.path)!=P and hashlib.sha256(Path(row.path).read_bytes()).hexdigest()!=row.sha256:changed.append(row.path)
checks['all_nonpage_inputs_unchanged']=not changed
assert all(checks.values()),checks
(O/'validation_summary.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},ensure_ascii=False,indent=2),encoding='utf-8')

intro='审查结论：当前代码主要估计可以复现，暂未发现把关系串到别人、把正向晋升放错结果年、把普通委员全部算晋升等错误；但存在重大识别和解释限制，以及两项需要处理的事件标签／源字段一致性问题。不能将现页面当作已完成因果识别的最终证据。'
scope='实际完成：隔离重跑四种FE下Sun–Abraham和TWFE的64个逐期系数及8个事后平均、3个事前水平、3个累计期限，共78项；从原始面板重新删省，复核8个Strict年度平均和3种排省24个月结果，共11项；重新运行原样本与Strict的24个月Webb wild bootstrap（9999次，seed=20261015）两项。逐条对照原ZIP核验完整年度1119个正向事件的ID、日期和成员身份筛选；累计927条事件重新核对即时前职，未发现“已知前职且不符合任何晋升规则”的候选，另有16条即时前职无法从日界连续记录确认，保留核验名单。未为显著性改窗口、控制或样本。'
limits='审查边界：本次没有对全部CPED履历做外部人物史实认证，没有逐省重新认证31个进驻日，也没有重跑历史126个控制／FE网格或所有9999次bootstrap。数值复现不是对识别有效性的认证。原始ZIP、网络、旧回归CSV和图未覆盖；HTML仅增补审查入口及限定性说明。'
check_table='| 检查项 | 通过 |\n| --- | --- |\n'+'\n'.join('| '+k+' | '+str(bool(v))+' |' for k,v in checks.items())
md=['# 原结果页面：代码与实证方法审查','日期：2026-10-21','',intro,'',scope,'',limits,'','## 已通过的计算与实现核验','',check_table,'','## 需要处理的问题']
for x in issues:
 md += ['','### '+x['id']+' '+x['priority']+'｜'+x['title'],'','证据：'+x['evidence'],'','影响：'+x['implication'],'','建议：'+x['action'],'','代码定位：'+x['source']]
md+=['','## 优先修改顺序','','1. 明确正式职级晋升与行政实职晋升；核验源字段冲突，先完成事件级分类。','2. 在全部比较窗开始前固定队列，建立前瞻跟踪及删失／竞争事件记录；当前24／36月结果只作探索。','3. 固定主估计对象为事前关系组的相对变化，保留个人＋年份与个人＋省年两组，不以显著性选主规格。','4. 将受处理影响的控制单列为条件关联敏感性；把+4、同乡／校友图及整省排除检查的证明范围写清楚。','5. 在新定义冻结后重跑一次完整分析；此前搜索所得p值仍应标注探索性。','','## 方法依据','',f'- [Sun的eventstudyinteract官方说明]({primary_url})：标准比较组及IW实现。此处的关系差异解释是对本项目设计的判断，不能直接借标准ATT保证。',f'- [Roth等，2023，DiD方法综述]({review_url})：事后控制、事前检验能力、少数处理聚类与推断。未拒绝事前检验不证明平行趋势成立。','','## 交付','','data/包含隔离重跑差异、原始正事件核验、入样／删失、窗口、关系形成日、源字段冲突、全部审查问题清单；code/包含本轮检查脚本和独立Stata重跑脚本。']
(O/'审查报告.md').write_text('\n'.join(md),encoding='utf-8')
pd.DataFrame(issues).to_csv(O/'data/issues.csv',index=False,encoding='utf-8-sig')
esc=html.escape
sections=''
for x in issues:
 sections+=f'<section id="{x["id"]}"><h2>{x["id"]} {esc(x["priority"])}｜{esc(x["title"])}</h2><p><strong>证据：</strong>{esc(x["evidence"])}</p><p><strong>影响：</strong>{esc(x["implication"])}</p><p><strong>建议：</strong>{esc(x["action"])}</p><p class="source">代码定位：{esc(x["source"])}</p></section>'
doc='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>代码与实证方法审查</title><style>body{max-width:1180px;margin:32px auto;padding:0 24px;font:17px/1.8 system-ui,"Microsoft YaHei",sans-serif;color:#263745}h1{font-size:29px}h2{margin-top:46px;font-size:22px;border-bottom:2px solid #337f99}.alert{background:#fff2d9;padding:20px;border-left:5px solid #bf8032}.source{font-size:13px;overflow-wrap:anywhere;color:#5e6e78}table{border-collapse:collapse;font-size:14px;width:100%;display:block;overflow:auto}td,th{padding:8px;border-bottom:1px solid #d4dee5;text-align:left}a{color:#226f90}nav{padding:18px;background:#edf4f7}section{scroll-margin-top:20px}</style><h1>代码与实证方法审查｜2026-10-21</h1>'''
doc+='<p class="alert">'+esc(intro)+'</p><p>'+esc(scope)+'</p><p>'+esc(limits)+'</p><nav><a href="#A01">累计队列选择</a> · <a href="#A03">晋升定义</a> · <a href="#A04">Sun模型</a> · <a href="#A06">腐败检查</a> · <a href="#A08">源字段冲突</a></nav><h2>数值复核通过项目</h2>'+pd.DataFrame([dict(check=k,passed=bool(v)) for k,v in checks.items()]).to_html(index=False)+sections
doc+='<h2>关键诊断表</h2><h3>逐期年度支持</h3>'+support[support['sample'].eq('main_annual')].to_html(index=False)+'<h3>累计样本保留率</h3>'+retention.to_html(index=False)+'<h3>累计结果可观察性</h3>'+selection.to_html(index=False)+'<h3>Strict究竟删除谁</h3>'+exclusion.to_html(index=False)
doc+='<h2>修订优先级</h2><ol><li>核验事件级行政／人大政协分类，再确定主Y。</li><li>在比较窗口之前选队列，重建前瞻风险集及删失；当前长窗结果降为探索。</li><li>固定估计对象、FE与事前控制规则后重跑；不通过继续搜窗口修复识别问题。</li><li>正确限制腐败排除、晚期支持与同乡／校友结果的证明范围。</li></ol>'
doc+=f'<h2>方法依据</h2><p><a href="{primary_url}">Sun官方eventstudyinteract说明</a>；<a href="{review_url}">Roth等2023 DiD方法综述</a>。本报告中关于项目的具体判断来自本地代码与数据。</p><p><a href="审查报告.md">Markdown报告</a> · <a href="审查证据_全部结果.xlsx">审查证据Excel</a> · <a href="data/issues.csv">问题清单CSV</a></p></html>'
(O/'index.html').write_text(doc,encoding='utf-8')
with pd.ExcelWriter(O/'审查证据_全部结果.xlsx') as w:
 for name,d in [('问题清单',pd.DataFrame(issues)),('78项重跑',compare),('排省11项重跑',extra),('wild重跑',q),('年度支持',support),('累计保留率',retention),('累计可观察性',selection),('严格排除组别',exclusion),('源字段冲突',pd.read_csv(O/'data/vice_governor_flag_vs_category_conflicts.csv')),('事件首条标签',pd.read_csv(O/'data/annual_event_label_details.csv')),('边形成时间',pd.read_csv(O/'data/retrospective_relation_dates.csv'))]:d.to_excel(w,sheet_name=name,index=False)
for name in ['audit_main_page_methods.py','audit_main_page_supplement.py','audit_event_labels_detail.py','audit_corruption_rerun.py','audit_bootstrap_24m.py','build_main_methods_audit_report.py']:shutil.copy2(W/name,O/'code'/name)
# Make the audit visible in the page the user specifically asked us to review.
backup=O/'index_before_audit.html'
if not backup.exists():shutil.copy2(P,backup)
h=P.read_text(encoding='utf-8');marker='<!-- METHODS_AUDIT_20261021 -->'
if marker not in h:
 banner=marker+'<div style="padding:18px 22px;background:#fff2d9;border-left:5px solid #bf8032;margin:24px 0"><strong>2026-10-21 方法与代码审查：</strong>主计算及腐败排除检查能复现，但累计队列选择、风险集变化、正式职级与行政实权晋升混合、少数关系省等限制尚未解决。Strict没有移除基期关系组成员，不能排除全部支持者离任机制。<a href="../'+O.name+'/index.html">查看完整审查报告、代码定位和原始记录核验</a>。</div>'
 pos=h.index('</h1>')+len('</h1>');h=h[:pos]+banner+h[pos:]
 P.write_text(h,encoding='utf-8')
print('Audit delivered',O/'index.html','issues=',len(issues),'numeric_checks=',checks)
