import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from replication_config import PROJECT_ROOT, CPED_ZIP
"""Readable delivery, descriptive network summaries and interactive viewer.
Run after build_person_network.py and audit_person_network.py.
"""
from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json,shutil,zipfile,html,math
import numpy as np
import pandas as pd
O=Path((PROJECT_ROOT / 'result/cped_pre_anticorruption_person_network_20261019'))
WORK=Path(__file__).parent
S=json.loads((O/'build_summary.json').read_text(encoding='utf-8'))
V=json.loads((O/'validation.json').read_text(encoding='utf-8'))
assert V['status'].startswith('PASS')
def save(d,n):d.to_csv(O/n,index=False,encoding='utf-8-sig')
def read(n,**kw):return pd.read_csv(O/n,**kw)
types=['cowork_6m','classmate_6m','hometown_prefecture','connected']
N=read('person_nodes_pre2012.csv');A=read('city_officeholder_year_start.csv',dtype={'province_code':str,'city_code':str})
annualcoverage=read('annual_pair_coverage.csv'); graphstats=[];activenodes=[];movers=[]
all_view={};degree_rows=[]
for label in ['pre2012','pre2012Nov15']:
 E=read(f'person_edges_{label}.csv.gz'); EP=E[E.both_eligible_city_principals_2000_2018.eq(1)]
 # Components describe observed ties, not identified factions; isolates retained.
 people=set(N.loc[N.eligible_city_principal_2000_2018.eq(1),'person_id'])
 comp_columns={};degree_columns={}
 for typ in types:
  adj={int(a):set() for a in people}
  for r in EP[EP[typ].eq(1)].itertuples():adj[r.person_a].add(r.person_b);adj[r.person_b].add(r.person_a)
  seen=set();sizes=[];comp={}
  for a in sorted(people):
   if a in seen:continue
   group=[];stack=[a];seen.add(a)
   while stack:
    u=stack.pop();group.append(u)
    for b in adj[u]:
     if b not in seen:seen.add(b);stack.append(b)
   root=min(group)
   for b in group:comp[b]=root
   sizes.append(len(group))
  comp_columns[typ+'_component_observed_city_principals']=comp
  degree_columns[typ+'_degree_city_principals']={a:len(b) for a,b in adj.items()}
  graphstats.append({'cutoff_label':label,'relation':typ,'city_principal_nodes':len(people),'positive_edges':int(EP[typ].eq(1).sum()),
    'nodes_with_positive_edges':sum(bool(x) for x in adj.values()),'isolates_no_recorded_positive_edges':sum(not bool(x) for x in adj.values()),
    'connected_components_including_isolates':len(sizes),'largest_component':max(sizes),'largest_component_share':max(sizes)/len(people)})
 nodes=read(f'person_nodes_{label}.csv')
 for k,m in comp_columns.items():nodes[k]=nodes.person_id.map(m)
 for k,m in degree_columns.items():nodes[k]=nodes.person_id.map(m)
 save(nodes,f'person_nodes_{label}.csv')
 all_view[label]=[]
 PP=read(f'annual_positive_links_national_{label}.csv.gz',dtype={'city_a':str,'city_b':str,'province_a':str,'province_b':str})
 for y,aa in A.groupby('year',sort=True):
  links=PP[PP.year.eq(y)]
  # unique peer people, not number of office combinations
  dsets=defaultdict(set)
  for r in links.itertuples():
   for t in types:
    for v in ['frozen','asof']:
     if getattr(r,t+'_'+v)==1:
      for a,b in [(r.person_a,r.person_b),(r.person_b,r.person_a)]:
       dsets[(a,t,v,'national')].add(b)
       if r.same_province:dsets[(a,t,v,'same_province')].add(b)
  for r in aa.itertuples():
   z={'cutoff_label':label,'year':int(y),'person_id':r.person_id,'name':r.name,'office':r.office,
      'city_code':r.city_code,'city':r.city,'province_code':r.province_code,'province':r.province}
   for t in types:
    for v in ['frozen','asof']:
     for scope in ['national','same_province']:z[t+'_'+v+'_recorded_degree_'+scope]=len(dsets[(r.person_id,t,v,scope)])
   degree_rows.append(z)
  # Compact viewer embeds same-office links only; full cross-office links remain in CSV.
  for office,g in aa.groupby('office'):
   nl=[[int(r.person_id),r.name,r.city_code,r.city,r.province_code,r.province] for r in g.itertuples()]
   ll=[]
   ss=links[links.office_a.eq(office)&links.office_b.eq(office)].drop_duplicates(['person_a','person_b'])
   for r in ss.itertuples():
    flags=[int(getattr(r,t+'_asof')==1) for t in types]
    frozen=[int(getattr(r,t+'_frozen')==1) for t in types]
    ll.append([int(r.person_a),int(r.person_b),int(r.same_province),flags,frozen])
   all_view[label].append({'year':int(y),'office':office,'nodes':nl,'links':ll})
 # Track actual movers; show pre-cutoff relation evidence persists through moves.
 node_names=nodes.set_index('person_id').name.to_dict()
 lookup={(int(r.person_a),int(r.person_b)):r for r in EP.itertuples()}
 for pid,g in A.groupby('person_id'):
  if g.city_code.nunique()<2:continue
  gs=g.sort_values(['year','office']).drop_duplicates(['year','city_code'])
  for i in range(1,len(gs)):
   prev=gs.iloc[i-1];cur=gs.iloc[i]
   if cur.year!=prev.year+1 or cur.city_code==prev.city_code:continue
   peers=defaultdict(list)
   for (a,b),e in lookup.items():
    if pid not in (a,b):continue
    other=b if a==pid else a
    if e.cowork_6m!=1:continue
    if pd.Timestamp(e.cowork_6m_first_formation)>=pd.Timestamp(int(prev.year),1,1):continue
    before=A[A.year.eq(prev.year)&A.person_id.eq(other)]
    after=A[A.year.eq(cur.year)&A.person_id.eq(other)]
    if len(before) and len(after):peers['cowork'].append((other,e,before.iloc[0],after.iloc[0]))
   if peers['cowork']:
    other,e,bef,aft=sorted(peers['cowork'],key=lambda x:x[0])[0]
    movers.append({'cutoff_label':label,'moving_person_id':int(pid),'moving_person':node_names[pid],
       'before_year':int(prev.year),'before_city':prev.city,'before_office':prev.office,
       'after_year':int(cur.year),'after_city':cur.city,'after_office':cur.office,
       'peer_id':int(other),'peer':node_names[other],'peer_city_before':bef.city,'peer_city_after':aft.city,
       'frozen_cowork_relation_before':1,'frozen_cowork_relation_after':1,
       'relationship_formation_date':e.cowork_6m_first_formation,'evidence_id':e.cowork_6m_evidence_id})
save(pd.DataFrame(graphstats),'network_summary_by_relation.csv');save(pd.DataFrame(degree_rows),'active_official_year_recorded_degrees.csv.gz')
M=pd.DataFrame(movers).drop_duplicates();save(M,'relations_follow_people_actual_move_examples.csv')
# Degree zero means no RECORDED positive tie among observed active city principals,
# not verified absence of personal connections; unknown comparability elsewhere.
example_edges=read('city_principal_person_edges_pre2012.csv').head(0)
examples=[]
for typ in types[:3]:
 e=read('city_principal_person_edges_pre2012.csv');examples.append(e[e[typ].eq(1)].head(20).assign(example_relation=typ))
EX=pd.concat(examples,ignore_index=True);save(EX,'readable_edge_examples.csv')

DESC={
 'person_id':'CPED人员唯一ID；关系跟随此ID，不随城市固定。','name':'CPED姓名。',
 'person_a':'人员对A的CPED ID；个人边表固定person_a < person_b；城市对年表按城市排序。','person_b':'人员对B的CPED ID。',
 'name_a':'A姓名。','name_b':'B姓名。','cutoff_label':'pre2012主口径；pre2012Nov15敏感性。',
 'eligible_city_principal_2000_2018':'包内2000—2018期间曾有有效普通地级市市长或市委书记任期；不代表2011年已任该职。',
 'both_eligible_city_principals_2000_2018':'两人均属于上述曾任市级主官集合。',
 'connected':'三类关系OR：任一1则为1；三项可比较且均未检出才为0；其余缺失。',
 'cowork_6m':'同具体单位且反腐前有至少六个月重叠；0仅为最低可比较但未检出；空为未知。',
 'classmate_6m':'普通高校明确学生经历、同期至少六个月；不证明同班或实际熟识。',
 'hometown_prefecture':'籍贯省和地级市相同；不是出生地、任职地，也没有可观察结识日期。',
 'components_comparable':'三项关系中可赋0或1的数量。','n_positive_relation_types':'已检出的主关系种类数量0—3。',
 'year':'任职映射年份2000—2018；年初快照，不代表全年主要任职人。','snapshot_date':'当年1月1日，start <= snapshot < end。',
 'office':'mayor市长；secretary市委书记。','office_cn':'原CPED主官标签。',
 'province_code':'任职省代码，保留包内历史口径。','province':'任职省名。','city_code':'任职城市代码，保留包内历史口径，未做外部区划统一。','city':'任职城市名。',
 'city_a':'A当年任职城市代码。','city_b':'B当年任职城市代码。','city_name_a':'A任职城市名。','city_name_b':'B任职城市名。',
 'office_a':'A当年主职。','office_b':'B当年主职。','pair_type':'mayor_to_mayor/secretary_to_secretary/跨主职配对。','same_city':'同一任职城市标记；主城市对文件为0。',
 'appointment_start':'覆盖快照的来源任期起点；重复来源按人合并仅用于快照信息。','appointment_end':'覆盖快照的来源任期终点。',
 'source_role_rows':'全部经历工作表物理Excel行号，用|分开。',
 'observed_experience_before_cutoff':'有至少一条有效经历起点早于截止点；不代表当时已任市级主官。',
 'has_experience':'包内有经历记录。','籍贯省':'基本信息原籍贯省。','籍贯市':'基本信息原籍贯市。','籍贯县/区':'基本信息原籍贯县区。',
}
def description(c):
 if c in DESC:return DESC[c]
 for suffix,exp in [('_frozen','固定事前关系：截至反腐前截止点冻结；早期年份可能尚未形成，不能当成当时已存在的联系。'),('_asof','实际已形成版本：同时早于快照日及固定截止点；不向反腐前较早年份回填后来形成的边。')]:
  if c.endswith(suffix):return DESC.get(c[:-len(suffix)],c[:-len(suffix)])+' '+exp
 for t in types:
  if c.startswith(t):
   base=DESC[t]
   if c.endswith('_first_formation'):return base+' 最早满足六个月的日期；同乡留空；不是实际结识日。'
   if c.endswith('_evidence_id'):return base+' 首次证据ID，对应relationship_evidence文件。'
   if c.endswith('_minimum_comparison_basis'):return base+' 至少一条可用记录；不是履历完整认证。'
   if '_degree_' in c:return base+' 已记录正向边的不同对方人数；0不等于现实无关系。'
   if '_component_' in c:return base+' 正向边连通分量的最小人员ID；连通不等于两两认识，也不等于派系。'
 return c+'；详见README对应文件定义。'
meta=[];details=[]
for filename in ['person_nodes_pre2012.csv','person_edges_pre2012.csv.gz','city_officeholder_year_start.csv','city_pairs_same_province_pre2012.csv.gz']:
 d=read(filename);details.append(f'## {filename}\n\n{len(d):,}行，{len(d.columns)}列。\n')
 for c in d:
  s=d[c];num=pd.api.types.is_numeric_dtype(s)
  z={'dataset':filename,'variable':c,'dtype':str(s.dtype),'nonmissing':int(s.notna().sum()),'missing':int(s.isna().sum()),'unique_nonmissing':int(s.nunique()),'description':description(c)}
  if num:z.update(min=s.min(),max=s.max(),mean=s.mean(),median=s.median(),sd=s.std())
  else:z['top5']=json.dumps(s.value_counts().head(5).to_dict(),ensure_ascii=False,default=str)
  meta.append(z)
  details.append(f'### `{c}`\n\n{z["description"]}\n\n类型：{z["dtype"]}；非缺失：{z["nonmissing"]:,}；缺失：{z["missing"]:,}；不同非缺失取值：{z["unique_nonmissing"]:,}。\n')
  if num:details.append(f'范围 [{s.min()}, {s.max()}]；均值 {s.mean()}；中位数 {s.median()}；标准差 {s.std()}。\n')
  else:details.append(f'前五项频数：{z["top5"]}\n')
save(pd.DataFrame(meta),'variable_codebook.csv');(O/'变量说明与分布.md').write_text('# 官员事前个人网络变量说明\n\n'+'\n'.join(details),encoding='utf-8')
main=S['summary'][0]; alt=S['summary'][1]
README=f'''# 反腐前官员个人网络：关系跟人走

本轮仅构建网络与任职映射，没有读取政策Y、运行回归、筛选显著性或确认任何反腐效果。

## 主口径

- 人员ID为节点，不是城市，也不是是否共同关联省委领导。原包共{main['all_people']:,}人；其中{main['city_principal_people_2000_2018']:,}人在2000—2018期间有包内有效普通地级市市长/市委书记任期。这个集合包含后来才晋升者；不表示他们反腐前已经在任。
- `pre2012`：共事/同期校友的六个月阈值日期必须严格早于2012-01-01，即主图固定在2011年末。不是把2012年全国反腐前后直接混在一起。
- `pre2012Nov15`：阈值严格早于2012-11-15，只作为截止日期敏感性。两个版本都不加入之后才形成的工作/学校关系。
- 籍贯相同是固定个人属性，没有可观察结识日期。其formation_date为空，不能宣称两人已经于某日相识或腐败串联。研究事前交往时优先使用cowork_6m；同乡/校友分别检验。
- 身份和履历来自2020年版回溯记录；这里的事前是“经历发生时间早于截止点”，不是声称研究者在2011年已经拿到这些履历。

## 三类关系

1. 共事：组织类别、任职省/市/县、机构码表别名、二/三级部门组成的具体单位键完全一致，重叠至少六个日历月。不是同省/同市就算共事。沿用严格单位分类，学生不算学校工作人员；过泛单位和不详岗位不算。部门缺失或不同写法可能漏边；同单位也不证明熟识。
2. 同期校友：普通高校明确学生经历，同校（仅使用包内别名）且同期至少六个月；排除党校、干部培训、军校、短训、访问、博士后、明确在职/函授等。只用截止前非学校就业重叠重新核查全日制不确定性，避免事后工作经历回改早期分类。不是同班/同专业的确认。
3. 同乡：籍贯省与籍贯地级市相同；不采用仅同省，也不等同出生地。

每条正向边均有原工作簿、工作表和物理Excel行号，可追到原始两人经历。六个月“形成日”只是达到研究阈值，不是现实首次见面日。

## 已建规模（个人网络，不是每年同时在任网络）

|范围|共事|同期校友|同乡|任一种的去重边|
|---|---:|---:|---:|---:|
|全部4603人|{main['positive_edges_by_relation']['cowork_6m']:,}|{main['positive_edges_by_relation']['classmate_6m']:,}|{main['positive_edges_by_relation']['hometown_prefecture']:,}|{main['all_person_positive_edges']:,}|
|两端均曾任2000—2018市级主官|{main['city_principal_edges_by_relation']['cowork_6m']:,}|{main['city_principal_edges_by_relation']['classmate_6m']:,}|{main['city_principal_edges_by_relation']['hometown_prefecture']:,}|{main['city_principal_positive_edges']:,}|

各类可能重叠，不能相加。全体个人网络保留跨省和非同期关系；城市映射再限制实际在任和样本层级。

## 关系怎样跟人走

`person_edges_pre2012.csv.gz`保存固定个人边W_ab；`city_officeholder_year_start.csv`保存每年人—城市—职务。A从甲市调到乙市，只改变任职地点，不改变A—B的事前边；甲市接任者不会继承A的私人关系。官员不再在包内市级主职任期中出现，就不再进入当年市级映射；边本身不删除。

每年使用1月1日，start <= 当日 < end。它不是全年任职时长最多者，也不能直接解释为年中巡视时的现任者。已交付完整有效任期，可在以后改成巡视日/月度映射；不能凭空把2018年中止的履历延长到年末。不依赖同年省级领导名册覆盖。

`*_frozen`：全部截止前关系固定后回看各年，适合明确称作“事前固定网络暴露”的版本；例如2009年形成的关系在2007年并未真实存在，不得把该列误称为当年已形成。

`*_asof`：同时要求关系早于当年快照日，且早于固定反腐前截止点；用于严格避免把2009年的联系回填到2007年。反腐截止后两列一致，任职变化只改变映射。早期可比较性仍仅为最低包内基础，不是完整履历；涉及未决日期的同单位配对保守设未知。

## 0与缺失

关系1=有包内证据。0=双方有最低比较基础且未检出该类关系，不是现实无关系的证明。空=缺少比较基础或同单位/学校存在日期歧义。connected任一类为1则1，三类都可比较且未检出才0，其余空。正向边表没有的人员对不能直接补0；请用包含0和空的城市对年表，或者结合nodes的可比较性与date_ambiguous_pairs。

节点degree/连通分量仅描述已记录正边。degree=0不等于无关系；A—B—C连通也不意味着A认识C。没有运行派系识别，没有把connected component命名为小团伙。

## 文件使用顺序

- `官员事前个人网络_阅读版.xlsx`：说明、网络规模、人物、主官正向边、任职映射、年度支持、实际调任例子和待核验记录。完整城市对在CSV.gz，避免Excel大表失真。
- `官员个人网络_交互查看.html`：按年份/市长或书记/关系/省份查看。默认只显示当年已经形成的边；可切换冻结暴露。可点击节点看不同任职年份和相连官员；没有省级领导作为必要中介。边缺失不证明现实无关系。
- `city_principal_person_edges_pre2012.csv`：主官个人正向边，不要求两人同期或同省任职。
- `city_pairs_same_province_pre2012.csv.gz`：最直接用于下一轮同省城市政策相似性。包括市长—市长、书记—书记、跨主职配对；没有把缺失填0。{main['same_province_city_pair_years']:,}个城市主职配对年。
- `annual_positive_links_national_pre2012.csv.gz`：固定边映射到每年各自城市，保留跨省关系；它仅含冻结网络中的正向边，不能单独当作完整对照组。
- `within_city_secretary_mayor_pre2012.csv.gz`：同城书记—市长关系，单独保留，不混入两市政策距离。
- `active_official_year_recorded_degrees.csv.gz`：每人当年关联的不同在任市级主官人数，区分全国/同省、冻结/已形成。一个人兼两职不会重复计算同一对方。
- `relationship_evidence_*.csv.gz`：所有证据，不只最早一条；个人边表evidence_id指向最早支持记录。
- `relations_follow_people_actual_move_examples.csv`：真实的相邻年跨城调任例子，人员关系没有继承给原城市。
- `network_summary_by_relation.csv`与`annual_pair_coverage.csv`：网络及实际在任关系覆盖；不是全中国官员完整普查。
- `eligible_city_leadership_spells.csv`：完整有效任期；主映射仅普通地级市/州/地区。直辖市区县、省直辖县和标签冲突记录没有混入。
- `ambiguous_office_years.csv`：{S['ambiguous_office_years']}个同日同职多人组；`multicity_official_years_for_review.csv`：{S.get('multicity_official_years_excluded',0)}个人年对应多城市，主映射排除，不擅自裁定。源任期和排除前快照均保留。
- `变量说明与分布.md`、`variable_codebook.csv`：名称、解释、缺失、唯一值及分布。

## 检查与来源

唯一外部原始输入是用户提供的`rerequestforaccesstothecped.zip`，两工作簿为`基本码表-20200606.xlsx`和`全部经历-20200606.xlsx`。SHA256：`{S['source_zip_sha256']}`。没有下载新人物、关系、学校沿革、区划或政策数据。inputs是此前仅由此ZIP生成的标准化表，已核对全部73,487条原始人员ID和起止日期；本次全部正向关系证据再次对照原工作簿行及单位/学校键。

validation.json通过的是程序与包内原始来源一致性，不是对官员履历的外部事实认证。未识别“抱团腐败”，没有得到巡视的因果结论。

## 重跑

Python依赖：pandas、numpy、openpyxl。保留原ZIP路径。包内inputs可独立复用，无需修改旧项目：

```powershell
python -X utf8 code/build_person_network.py --inputs inputs --output . --zip 'C:/Users/siyang zhu/Downloads/rerequestforaccesstothecped.zip'
python -X utf8 code/audit_person_network.py
python -X utf8 code/finish_person_network.py
```

build脚本支持输入/输出参数；后两脚本开头O是本次绝对输出位置，迁移目录时同步修改。本次不生成PDF。
'''
(O/'README_网络定义与使用.md').write_text(README,encoding='utf-8')

# Workbook: readable positive city-principal edges, not millions of blank pairs.
with pd.ExcelWriter(O/'官员事前个人网络_阅读版.xlsx',engine='openpyxl') as w:
 pd.DataFrame({'说明':README.splitlines()}).to_excel(w,sheet_name='先读说明',index=False)
 pd.DataFrame(graphstats).to_excel(w,sheet_name='网络规模',index=False)
 read('person_nodes_pre2012.csv').to_excel(w,sheet_name='人物与可比较性',index=False)
 read('city_principal_person_edges_pre2012.csv').to_excel(w,sheet_name='市级主官事前正向边',index=False)
 A.to_excel(w,sheet_name='逐年人在何城何职',index=False)
 annualcoverage.to_excel(w,sheet_name='逐年关系支持',index=False)
 M.head(3000).to_excel(w,sheet_name='关系跟人走实际例子',index=False)
 EX.to_excel(w,sheet_name='三类关系实例',index=False)
 read('ambiguous_office_years.csv').to_excel(w,sheet_name='同职多人待核验',index=False)
 read('multicity_official_years_for_review.csv').to_excel(w,sheet_name='一人多城待核验',index=False)
 pd.DataFrame(meta).to_excel(w,sheet_name='变量目录',index=False)
 for sh in w.sheets.values():
  sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
  for col in sh.iter_cols(min_row=1,max_row=1):sh.column_dimensions[col[0].column_letter].width=min(48,max(15,len(str(col[0].value))*1.25))

TEMPLATE='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>反腐前官员个人网络</title>
<style>body{font:15px system-ui;margin:24px;color:#203040}h1{font-size:25px}select{padding:7px;margin:5px}#wrap{display:flex;gap:18px}canvas{border:1px solid #ddd;background:#fbfcfe;width:76%;height:720px}#info{width:23%;max-height:720px;overflow:auto;line-height:1.6}small{color:#526070}button{padding:6px}table{border-collapse:collapse}td{padding:3px;border-bottom:1px solid #ddd}</style>
<h1>反腐前官员个人网络：关系跟人走</h1>
<p>节点是当年在任官员；线是反腐前已形成的个人关系。省份筛选指当年任职省，不是籍贯省。点击节点查看相连官员及本人任职变化。</p>
<label>截止点<select id="cut"><option value="pre2012">2011年末（主）</option><option value="pre2012Nov15">2012-11-15之前</option></select></label>
<label>年份<select id="year"></select></label><label>职务<select id="office"><option value="mayor">市长</option><option value="secretary">市委书记</option></select></label>
<label>关系<select id="rel"><option value="0">共事至少6个月</option><option value="1">同期校友至少6个月</option><option value="2">同乡：同地级市</option><option value="3">任一种</option></select></label>
<label>任职省<select id="province"><option value="all">全国（含跨省边）</option></select></label>
<label>时点<select id="timing"><option value="3">当年已形成（推荐）</option><option value="4">截止点冻结关系暴露</option></select></label>
<p id="stats"></p><div id="wrap"><canvas id="cv"></canvas><div id="info">点击一个节点。<p>同乡无可观察的结识日期；同校/共事不保证现实熟识。没有线不证明没有关系，关系未知另见完整CSV。</p></div></div>
<p><small>仅用户CPED ZIP。每年1月1日快照；排除同日同职多人和一人多城的未决映射。节点按任职省分组排列，坐标不是地理位置或派系识别。未估计任何反腐效果。</small></p>
<script id="data" type="application/json">__DATA__</script><script>
const DB=JSON.parse(document.getElementById('data').textContent);const $=id=>document.getElementById(id);
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
for(let y=2000;y<=2018;y++)$('year').add(new Option(y,y));$('year').value=2011;
const provinces=new Map();DB.pre2012.forEach(d=>d.nodes.forEach(n=>provinces.set(n[4],n[5])));[...provinces].sort().forEach(([k,v])=>$('province').add(new Option(v,k)));
let points=[],links=[],selected=null;const cv=$('cv'),ctx=cv.getContext('2d');let cw=1000,ch=720;
function draw(){const d=DB[$('cut').value].find(x=>x.year==$('year').value&&x.office==$('office').value);const p=$('province').value;const ns=d.nodes.filter(n=>p==='all'||n[4]===p);const idset=new Set(ns.map(n=>n[0]));const rel=+$('rel').value,tm=+$('timing').value;links=d.links.filter(e=>idset.has(e[0])&&idset.has(e[1])&&e[tm][rel]);
cw=cv.clientWidth;ch=720;cv.width=cw*devicePixelRatio;cv.height=ch*devicePixelRatio;ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);ctx.clearRect(0,0,cw,ch);points=[];
const gr=[...new Set(ns.map(n=>n[4]))].sort();gr.forEach((pr,gi)=>{const g=ns.filter(n=>n[4]===pr),cols=p==='all'?6:1,rows=Math.ceil(gr.length/cols),gw=cw/cols,gh=ch/rows,cx=(gi%cols+.5)*gw,cy=(Math.floor(gi/cols)+.5)*gh,rad=p==='all'?Math.min(gw,gh)*.34:Math.min(cw,ch)*.37;
ctx.fillStyle='#555';ctx.font='12px system-ui';ctx.textAlign='center';ctx.fillText(provinces.get(pr),cx,cy-rad-12);g.forEach((n,i)=>{const a=2*Math.PI*i/g.length;points.push({n,x:cx+rad*Math.cos(a),y:cy+rad*Math.sin(a),color:`hsl(${(gi*47)%360},55%,43%)`});});});
const mp=new Map(points.map(p=>[p.n[0],p]));ctx.lineWidth=1;links.forEach(e=>{const a=mp.get(e[0]),b=mp.get(e[1]);ctx.strokeStyle=selected&&(selected===e[0]||selected===e[1])?'#b12c40':'rgba(60,105,145,.24)';ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();});points.forEach(p=>{ctx.fillStyle=p.n[0]===selected?'#d32145':p.color;ctx.beginPath();ctx.arc(p.x,p.y,p.n[0]===selected?7:4,0,7);ctx.fill();if($('province').value!=='all'){ctx.font='12px system-ui';ctx.fillStyle='#203040';ctx.textAlign=p.x>cw/2?'left':'right';ctx.fillText(p.n[1]+' · '+p.n[3],p.x+(p.x>cw/2?7:-7),p.y);}});
const linked=new Set(links.flatMap(e=>[e[0],e[1]]));$('stats').textContent=`${d.year}年1月1日：${ns.length}位在任官员；${links.length}条已记录正向边；${linked.size}位至少有一条线。其余不等于现实无关系。`;
if(selected){const pt=points.find(p=>p.n[0]===selected);if(pt)show(pt.n,d);}}
function show(n,d){const peers=links.filter(e=>e[0]===n[0]||e[1]===n[0]).map(e=>e[0]===n[0]?e[1]:e[0]);let ht=`<b>${esc(n[1])}</b> · CPED ${n[0]}<p>${esc(n[5])} / ${esc(n[3])}</p><b>当前显示关系 ${peers.length} 人</b><ul>`;peers.forEach(id=>{const q=d.nodes.find(a=>a[0]===id);if(q)ht+=`<li>${esc(q[1])} · ${esc(q[3])}</li>`;});ht+='</ul><b>包内任职快照</b><table>';
const seen=new Set();DB[$('cut').value].forEach(g=>g.nodes.filter(q=>q[0]===n[0]).forEach(q=>{const k=g.year+'|'+q[2]+'|'+g.office;if(!seen.has(k)){seen.add(k);ht+=`<tr><td>${g.year}</td><td>${esc(q[3])}</td><td>${g.office==='mayor'?'市长':'市委书记'}</td></tr>`;}}));$('info').innerHTML=ht+'</table>';}
cv.addEventListener('click',e=>{const r=cv.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;let near=points.map(p=>[p,(p.x-x)**2+(p.y-y)**2]).sort((a,b)=>a[1]-b[1])[0];if(near&&near[1]<225){selected=near[0].n[0];draw();}});
['cut','year','office','rel','province','timing'].forEach(id=>$(id).onchange=()=>{selected=null;draw();});window.addEventListener('resize',draw);draw();
</script></html>'''
viewer=TEMPLATE.replace('__DATA__',json.dumps(all_view,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
(O/'官员个人网络_交互查看.html').write_text(viewer,encoding='utf-8')
# Save JavaScript separately for syntax checks.
script=viewer.split('<script>')[1].split('</script>')[0];(O/'code'/'viewer_syntax_check.js').write_text(script,encoding='utf-8')
for name in ['build_person_network.py','audit_person_network.py','finish_person_network.py']:
 src=WORK/name;dst=O/'code'/name
 if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='file_manifest.csv':manifest.append({'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
save(pd.DataFrame(manifest),'file_manifest.csv')
archive=O.parent/'反腐前官员个人网络_关系跟人走_数据代码.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,arcname=O.name+'/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'size_mb':round(archive.stat().st_size/1024**2,2),'files':len(manifest)+1,'move_examples':len(M),'status':'PASS'},ensure_ascii=False),flush=True)
