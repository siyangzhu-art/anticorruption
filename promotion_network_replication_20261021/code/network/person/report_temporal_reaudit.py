import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from replication_config import PROJECT_ROOT, CPED_ZIP
from pathlib import Path
import pandas as pd,json,html,sys,shutil,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path((PROJECT_ROOT / 'result/network_reaudit_2026_10_20'))
N=Path((PROJECT_ROOT / 'result/cped_pre_anticorruption_person_network_20261019'))
source=json.loads((OUT/'original_source_recheck.json').read_text(encoding='utf8'))
temporal=pd.read_csv(OUT/'temporal_validation_checks.csv')
independent=pd.DataFrame(json.loads((OUT/'independent_completeness_checks.json').read_text(encoding='utf8')))
allchecks=pd.concat([temporal,pd.DataFrame(source['checks']),independent],ignore_index=True)
allchecks.to_csv(OUT/'all_validation_checks.csv',index=False,encoding='utf-8-sig')
assert allchecks.status.eq('PASS').all()
ann=pd.read_csv(OUT/'annual_network_counts.csv');ann=ann[(ann.cutoff=='pre2012')&(ann.relation=='cowork_6m')&(ann.timing=='asof')&(ann.year>=2012)]
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
axes[0].plot(ann.year,[8540]*len(ann),marker='o',color='#28759b');axes[0].set_ylim(0,10000);axes[0].set_title('Fixed pre-2012 personal coworker graph\n2,771 ever-city principals')
axes[1].plot(ann.year,ann.positive_person_edges,marker='o',color='#cc8530');axes[1].set_ylim(0,500);axes[1].set_title('Edges among observed active city principals\nNational; distinct cities; both roles')
for ax in axes:
 ax.set_xlabel('January 1 roster year');ax.set_ylabel('Unique person-pair edges');ax.set_xticks(ann.year);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2)
fig.suptitle('A fixed relationship graph can produce a changing active subgraph',fontsize=15)
fig.text(.06,.025,'No post-2011 ties are added. Right-panel changes reflect officeholder rosters and locations, not deletion of personal ties.\nThese are descriptive counts, not estimates of an anticorruption effect.',fontsize=9)
fig.subplots_adjust(left=.075,right=.98,top=.78,bottom=.22,wspace=.3);fig.savefig(OUT/'fixed_relationships_vs_active_subgraph.png',dpi=180);plt.close(fig)

flags=json.loads((OUT/'measurement_sensitivity_summary.json').read_text(encoding='utf8'))
report=f'''# 官员个人网络：2026-10-20重新核验

结论：在目前定义、原始CPED包和既有任职映射范围内，没有发现“同一对人今年connected、明年变成不connected”的错误。共计{len(allchecks)}项记录核验全部通过。通过的是包内来源和程序一致性，不是外部人物事实认证。

## 为什么每年看起来不一样

1. 固定个人关系表 W_ab^0 不含年份，达到六个月共事或同期校友门槛后保持1；主截止点为2012-01-01之前。2,771名曾任市级主官之间有8,540条共事边、2,375条同期校友边、15,076条同乡边，合并去重25,233条。这些不是每年重建、每年过期的边。
2. 年度图只显示当年1月1日在包内有效市长/书记任期中的人。原市长升任省委职务、退任、任期记录缺失，都可能不再出现在当年市级图；其个人边仍保留在固定关系表中。
3. 城市间暴露 C_cd,t=W^0_[a(c,t),a(d,t)] 会随任职人变化。甲城原市长A与乙城市长B有关系，A调任丙城后，关系转为丙城—乙城；甲城继任者不会继承A的关系。
4. 查看器按市长/市委书记分开显示。A由市长转书记，会退出市长图，进入书记图；与B的关系不消失，但可能成为跨职务配对。
5. 只看同省时，跨省调动会让边退出同省图，全国关系仍在；两人都调入同一城市，则退出跨城图，但不是失去关系。
6. asof版本还要求关系在当年快照前已经形成：2009年才达到六个月共事门槛，2007年不能记1，之后一直保留。frozen版本把截至2011年末的全体关系固定；它在更早年份只是固定暴露，不应称为当时已形成。主截止点下，2012—2018两列完全一致。

## 实际检查结果

- 146,823条同省城市职务配对年全部检查；同一对人1变0或1变缺失均为0。
- 相邻年同一城市职务配对有130,654个可比较连接。共事已知状态变化3,900次：3,876次两端官员至少一人改变，24次同一对人在截止前达到形成门槛，全部0变1。
- 对两个截止日期、四类关系、每年全国在任映射，按固定个人边独立重构应出现的边：没有少边或多边。所有年度显示边的消失都能用在任名单、职务筛选或同城排除解释。
- 从分类后经历重新枚举203,640个同单位经历候选配对，得到24,056条全体人员共事边；重新枚举26,366个同校经历候选配对，得到5,569条同期校友边。与已发布关系表完全一致，首次形成日期也一致。不是只抽查少数名字。
- 原包全部73,487条经历及两个截止版共167,531条正向证据重新核对原工作表行、人员ID、单位/学校键和起止时间。
- 既有政策分析面板46,873条配对记录，其人员身份和四类关系均与核验后源表一致。这次没有重跑回归。
- 既有网络、查看器、回归输入均保留原样，没有自动删除或修改关系。

## 真正需要注意的测量和研究设计问题

### 共事不全是私人密友
市级主官8,540条共事边中，{flags['city_principal_cowork_only_broad_collective']:,}条（{flags['city_principal_cowork_only_broad_collective']/8540:.1%}）的全部支持证据仅来自同一党委常委会/政治局、人大常委会或政协常委会，且没有更细部门记录。这里仍保留具体地理单位与同时任职六个月，不是仅仅同省。共同领导班子可能是真实工作接触，所以不能据此说这3,732条是假边；但它们与同一办公室的工作关系强度不同，不能统称私人小圈子。新增标记文件供后续敏感性分析，本次未改主关系。

### 名册与日期覆盖
名册是年初快照，不是全年任职最长者、巡视进驻日现任者或文件发布日期现任者。对具体政策文件应按发布日重做任职匹配。2008年书记名册278条、2009年330条，说明覆盖并非平衡；差异不能自动解释为政治机制。4个直辖市未混入普通地级市映射，其余27省份都有观察。
原始经历中3,706条缺起止端点，111条终止不晚于起始；按原规则不能建立该条时间关系。另有179个同日同职多人组、6个一人多城人年已在主年度映射中保守排除。它们是资料或映射待核验，不是确认官员断交。

### 0和缺失
0只表示在最低比较基础下未检出该类关系，不证明现实无关系。未知未补0。正向边表缺少的人员对不可直接补0。同乡只表示籍贯属性相同；同期校友只表示同校时间重叠，均不是确认相识。

### 不能把年度边数下降当作反腐效果
固定事前网络不再添加事后新关系，而在任官员会更替，年度在任子图边数本身可能下降。主官共事图2012年423条、2018年203条是这种在任映射的描述，不是“220对人断交”。考察巡视是否削弱政策影响，应固定个人关系定义，把当年的城市政策接到实际任职人，估计网络关系与政策相似性的关联是否改变；不能仅用边数下降证明中央集权。

## 建议之后统一名称
“反腐前固定个人网络”用于完整边表；“当年在任官员的事前关系子图”用于年度图；“城市当年主官的网络暴露”用于城市配对回归。分别描述，避免把关系消失和人员退出样本混为一谈。

文件：all_validation_checks.csv为全部检查；actual_persistent_relationship_examples.csv为真实调任保持关系例子；annual_edge_loss_reasons.csv按年和筛选范围分解退出原因（跨年重复出现的人对可能多次计数，不是唯一人对总数）；cowork_collective_membership_sensitivity_flags.csv为待做敏感性标记；年度counts表的person_edges和office_edges分别按不同人对和职务组合计数。
'''
(OUT/'README_网络为什么逐年变化_详细核验.md').write_text(report,encoding='utf8')

tabs={'全部检查':allchecks,'年度网络规模':pd.read_csv(OUT/'annual_network_counts.csv'),'城市暴露变化原因':pd.read_csv(OUT/'city_pair_status_changes.csv'),'年度边退出原因':pd.read_csv(OUT/'annual_edge_loss_reasons.csv'),'调任关系保持例子':pd.read_csv(OUT/'actual_persistent_relationship_examples.csv'),'年度名册覆盖':pd.read_csv(OUT/'annual_roster_coverage.csv'),'共事机构较宽标记':pd.read_csv(OUT/'cowork_collective_membership_sensitivity_flags.csv'),'最大单位证据组':pd.read_csv(OUT/'largest_cowork_unit_evidence_groups.csv'),'原始日期缺陷':pd.read_csv(OUT/'invalid_experience_date_counts.csv'),'同职多人待核验':pd.read_csv(OUT/'source_ambiguous_office_years.csv'),'一人多城待核验':pd.read_csv(OUT/'source_multicity_official_years_for_review.csv')}
cb=[]
for tab,d in tabs.items():
 for c in d:
  s=d[c];cb.append(dict(table=tab,variable=c,dtype=str(s.dtype),rows=len(d),nonmissing=int(s.notna().sum()),missing=int(s.isna().sum()),unique=int(s.nunique()),minimum=str(s.min()) if pd.api.types.is_numeric_dtype(s) else '',maximum=str(s.max()) if pd.api.types.is_numeric_dtype(s) else '',measurement='See source variable_codebook.csv and audit report; candidate pairs are episodes, person edges are unique unordered person IDs.'))
codebook=pd.DataFrame(cb);codebook.to_csv(OUT/'audit_codebook.csv',index=False,encoding='utf-8-sig');tabs['核验字段目录']=codebook
with pd.ExcelWriter(OUT/'官员网络_逐年变化与完整性复核.xlsx',engine='openpyxl') as w:
 for name,d in tabs.items():
  q=d.copy()
  for c in q.select_dtypes('object'):
   q[c]=q[c].map(lambda x:str(x) if isinstance(x,(dict,list)) else x)
  q.to_excel(w,sheet_name=name,index=False);ws=w.sheets[name];ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
shutil.copy2(N/'variable_codebook.csv',OUT/'source_network_variable_codebook.csv')
ht='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>官员网络复核</title><style>body{max-width:1100px;margin:40px auto;font:16px/1.7 system-ui}img{max-width:100%}pre{white-space:pre-wrap}table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #ddd;padding:5px}</style><h1>固定个人关系与年度在任网络</h1><img src="fixed_relationships_vs_active_subgraph.png"><pre>'+html.escape(report)+'</pre><h2>全部核验结果</h2>'+allchecks.to_html(index=False,escape=True)+'</html>'
(OUT/'网络详细核验.html').write_text(ht,encoding='utf8')
shutil.copy2(Path(__file__).with_name('rerun_original_source_checks.py'),OUT/'rerun_original_source_checks.py')
shutil.copy2(__file__,OUT/Path(__file__).name)
files=[{'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in OUT.iterdir() if f.is_file() and f.name!='audit_file_manifest.csv']
pd.DataFrame(files).to_csv(OUT/'audit_file_manifest.csv',index=False,encoding='utf-8-sig')
print(json.dumps({'all_checks':len(allchecks),'failures':int(allchecks.status.ne('PASS').sum()),'workbook_sheets':len(tabs),'output':str(OUT)},ensure_ascii=False),flush=True)
