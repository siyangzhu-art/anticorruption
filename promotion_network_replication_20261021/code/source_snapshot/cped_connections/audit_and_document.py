from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,zipfile,shutil

O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\cped_city_province_connections_20261019')
src=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')
E=pd.read_csv(O/'normalized_experiences.csv.gz',keep_default_na=False,dtype={'province_code':str,'city_code':str}).set_index('row_id')
EV=pd.read_csv(O/'connection_evidence.csv.gz',keep_default_na=False)
ED=pd.read_csv(O/'education_classification.csv',keep_default_na=False).set_index('row_id')
J=pd.read_csv(O/'workplace_classification.csv.gz',keep_default_na=False).set_index('row_id')
A=pd.read_csv(O/'city_province_dyad_year_start.csv.gz',dtype={'province_code':str,'city_code':str})
T=pd.read_csv(O/'top_leaders_dyad_year_start.csv',dtype={'province_code':str,'city_code':str})
F=pd.read_csv(O/'pair_first_connection_dates.csv',keep_default_na=False)
P=pd.read_csv(O/'people_and_hometowns.csv',keep_default_na=False).set_index('person_id')
stats=json.loads((O/'build_summary.json').read_text(encoding='utf-8'))
from reaggregate_city_year import reaggregate
C=reaggregate(A,O)
stats['city_year_rows']=len(C)
stats['prefecture_city_year_rows']=int(C.scope.eq('prefecture').sum())
stats['top_actual_year_range']=[int(T.year.min()),int(T.year.max())]
(O/'build_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
global_first=pd.read_csv(O/'不限同省同期_曾任省市官员正向关系.csv.gz',keep_default_na=False)
assert not global_first.duplicated(['city_id','province_id','relation']).any()
assert not global_first.city_id.eq(global_first.province_id).any()
ff=F[F.relation.isin(['hometown_prefecture','hometown_county','hometown_province','classmate_6m','cowork_6m'])]
ff=ff.merge(global_first[['city_id','province_id','relation','formed']],on=['city_id','province_id','relation'],how='left',validate='one_to_one')
assert ff.formed.notna().all()
assert pd.to_datetime(ff.first_formed).eq(pd.to_datetime(ff.formed)).all()
assert stats['sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
assert len(E)==73487 and len(P)==4603
assert not (A.city_id==A.province_id).any()
assert not A.duplicated(['year','province_code','city_code','city_id','province_id']).any()
assert not (EV.city_id==EV.province_id).any()
errors=[]
for r in EV.to_dict('records'):
 typ=r['relation'];a=int(r['city_id']);b=int(r['province_id'])
 if typ.startswith('hometown'):
  cols=['籍贯省']+(['籍贯市'] if typ!='hometown_province' else [])+(['籍贯县/区'] if typ=='hometown_county' else [])
  for c in cols:assert P.loc[a,c] and P.loc[a,c]==P.loc[b,c]
  continue
 x=E.loc[int(r['city_evidence_row'])];y=E.loc[int(r['province_evidence_row'])]
 assert x.person_id==a and y.person_id==b
 if typ.startswith('cowork'):
  assert J.loc[x.name,'work_eligible'] and J.loc[y.name,'work_eligible']
  assert J.loc[x.name,'workplace_key']==J.loc[y.name,'workplace_key']==r['match_key']
 elif typ.startswith('classmate') or typ=='alumni_ordinary':
  assert ED.loc[x.name,'ordinary_student_eligible'] and ED.loc[y.name,'ordinary_student_eligible']
  assert str(ED.loc[x.name,'school_key'])==str(ED.loc[y.name,'school_key'])
 if typ=='alumni_ordinary':continue
 st=max(pd.Timestamp(x.start),pd.Timestamp(y.start));en=min(pd.Timestamp(x.end),pd.Timestamp(y.end))
 assert st<en
 if typ.endswith('6m') or typ=='classmate_same_entry_year':assert st+pd.DateOffset(months=6)<=en
 if typ.endswith('12m'):assert st+pd.DateOffset(months=12)<=en
 if typ=='classmate_same_entry_year':assert pd.Timestamp(x.start).year==pd.Timestamp(y.start).year
 assert pd.Timestamp(r['formed'])<=en

# Recompute each main relationship against its cutoff via independent merge of first evidence.
checks=[]
for typ in ['hometown_prefecture','classmate_6m','cowork_6m']:
 f=F[F.relation.eq(typ)][['city_id','province_id','first_formed']]
 m=A.merge(f,on=['city_id','province_id'],how='left',validate='many_to_one')
 yes=(pd.to_datetime(m.first_formed)<pd.to_datetime(m.joint_spell_start)).fillna(False)
 assert (m[typ].eq(1)==yes).all(),typ
 now=(pd.to_datetime(m.first_formed)<pd.to_datetime(m.snapshot_date)).fillna(False)
 assert (m[typ+'_asof'].eq(1)==now).all()
 checks.append({'test':'all annual '+typ+' indicators','pass':True,'rows':len(A)})
main=A[['hometown_prefecture','classmate_6m','cowork_6m']]
assert A.any_recorded_tie.eq(main.eq(1).any(axis=1).astype(int)).all()
unknown=~main.eq(1).any(axis=1)&main.isna().any(axis=1)
assert A.connected.isna().eq(unknown).all()
assert set(T.scope)=={'prefecture'}
assert T.top_four.eq(1).all()
assert T[['city_is_secretary','city_is_mayor']].max(axis=1).eq(1).all()
assert T[['province_is_secretary','province_is_governor']].max(axis=1).eq(1).all()
# Detect ambiguous office assignment instead of silently selecting one incumbent.
office_conflicts=[]
for role,side in [('city_is_secretary','city'),('city_is_mayor','city'),('province_is_secretary','province'),('province_is_governor','province')]:
 cols=['year','province_code']+(['city_code'] if side=='city' else [])
 q=A[A[role].eq(1)][cols+[side+'_id',side+'_official']].drop_duplicates()
 for keys,g in q.groupby(cols):
  if g[side+'_id'].nunique()>1:
   office_conflicts.append(dict(zip(cols,keys if isinstance(keys,tuple) else [keys]))|{'role':role,'people':'|'.join(g[side+'_official'].astype(str)),'ids':'|'.join(g[side+'_id'].astype(str)),'n_people':g[side+'_id'].nunique()})
pd.DataFrame(office_conflicts,columns=['year','province_code','city_code','role','people','ids','n_people']).to_csv(O/'同日同职多名官员_待核验.csv',index=False,encoding='utf-8-sig')
for role,side in [('city_is_secretary','city'),('city_is_mayor','city'),('province_is_secretary','province'),('province_is_governor','province')]:
 cols=['year','province_code']+(['city_code'] if side=='city' else [])
 bad={tuple(str(z.get(c,'')) for c in cols) for z in office_conflicts if z['role']==role}
 T[role+'_assignment_ambiguous']=[int(bool(r[role]) and tuple(str(r[c]) for c in cols) in bad) for r in T.to_dict('records')]
ambcols=[c for c in T if c.endswith('_assignment_ambiguous')]
T['role_assignment_unambiguous']=~T[ambcols].eq(1).any(axis=1)
T.to_csv(O/'top_leaders_dyad_year_start.csv',index=False,encoding='utf-8-sig')
TC=T[T.role_assignment_unambiguous].copy()
TC.to_csv(O/'top_leaders_unique_officeholder_year_start.csv',index=False,encoding='utf-8-sig')
stats['top_unique_officeholder_rows']=len(TC)
(O/'build_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
checks.extend([{'test':'evidence identities, keys, school eligibility and interval overlap','pass':True,'rows':len(EV)},
               {'test':'no self-pairs or duplicate dyad-years','pass':True,'rows':len(A)},
               {'test':'unknowns propagated to connected','pass':True,'rows':int(unknown.sum())},
               {'test':'input ZIP hash unchanged; source only two supplied XLSX','pass':True,'rows':2}])
audit={'status':'PASS_internal_consistency_not_external_biography_verification','checks':checks,
       'global_positive_relation_type_rows':len(global_first),
       'multiple_incumbent_office_year_groups':len(office_conflicts),
       'source_hash':stats['sha256'],'limitations':['source biography completeness unknown','exact acquaintance not observed','end dates not extrapolated','Jan 1 snapshot is not a full-year officeholder assignment','same-province contemporaneous roster only']}
(O/'validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')

dictionary={
 'year':'年份，1980—2018；对应1月1日快照，并非全年主政官员',
 'snapshot_date':'实际测量日：当年1月1日',
 'province_code':'包内任职省代码，不用外部区划补全',
 'province':'任职省名称', 'city_code':'包内二级任职地区代码，保留历史编码', 'city':'任职城市/二级地区名',
 'scope':'prefecture=普通地级市/州/地区；municipality_district=直辖市区县；direct_county=省直辖县；county_or_district_flag_conflict=市级标签与县区信息不一致',
 'city_id':'市级官员CPED用户编码', 'city_official':'市级官员姓名', 'province_id':'省级官员CPED用户编码', 'province_official':'省级官员姓名',
 'city_roles':'快照日有效的市级标志位，兼任去重保留', 'province_roles':'快照日有效的省级标志位，兼任去重保留',
 'city_is_secretary':'该日市级官员有市委书记标志', 'city_is_mayor':'该日市级官员有市长标志',
 'province_is_secretary':'该日省级官员有省委书记标志','province_is_governor':'该日省级官员有省长标志',
 'joint_spell_start':'这两人在该省该城市连续同期任职的区间起点，合并重叠/相邻标志记录',
 'top_four':'市委书记/市长与省委书记/省长配对；主表另要求scope=prefecture',
 'hometown_prefecture':'同省且同籍贯市/地区；主同乡口径，不等同出生地',
 'hometown_county':'同省、同籍贯市且同县区；更严格同乡口径',
 'hometown_province':'同籍贯省；宽口径，不进入主connected',
 'classmate_6m':'普通高校明确就读记录、包内学校别名规范后同校、时间重叠至少六个日历月；同学代理而非同班或相识证明',
 'classmate_any':'上述合格就读记录同校，日期存在正重叠；敏感性口径',
 'classmate_same_entry_year':'classmate_6m且双方入学年份相同；不证明同班',
 'alumni_ordinary':'上述普通高校曾就读同一学校，双方入学已发生；不要求同时在校，也不据此认定毕业',
 'cowork_6m':'按地区、组织类别、包内机构别名、二/三级部门严格同键，任期重叠至少六个日历月',
 'cowork_any':'同一工作单位键且任期正重叠；敏感性口径',
 'cowork_12m':'同一工作单位键且任期重叠至少十二个日历月；严格敏感性',
 'training_same_program_overlap':'党校等其他学习同校同二/三级课程字段且正重叠；不进主connected；不保证同一期班次',
 'any_recorded_tie':'三项主关系任一有证据为1，否则0；0仅是没有检出的关系，可包含资料未知',
 'connected':'三项主关系任一1则1；三项均有比较基础且均0则0；否则缺失。0也仅表示包内无匹配',
 'main_components_observable':'三项主关系中有1/0编码的数量，0—3',
 'n_main_tie_types':'三项主关系检出为1的种类数，0—3',
}
rows=[]
for c in A.columns:
 base=c[:-5] if c.endswith('_asof') else c
 d=dictionary.get(base,'')
 if c.endswith('_asof'):d+='；此列截至当年1月1日，可能包含双方当前任期内形成的关系，属于替代时点口径。'
 elif base in ['hometown_prefecture','hometown_county','hometown_province','classmate_6m','classmate_any','classmate_same_entry_year','alumni_ordinary','cowork_6m','cowork_any','cowork_12m','training_same_program_overlap','connected','any_recorded_tie']:d+='；主列只计joint_spell_start之前已经形成的关系。'
 assert d,c
 s=A[c]
 rows.append({'variable':c,'description':d,'dtype':str(s.dtype),'nonmissing':int(s.notna().sum()),'missing':int(s.isna().sum()),'unique':int(s.nunique()),'top5':str(s.value_counts().head(5).to_dict())})
CB=pd.DataFrame(rows);CB.to_csv(O/'variable_codebook.csv',index=False,encoding='utf-8-sig')
summary={k:stats[k] for k in ['people','experience_rows','valid_role_rows','unique_city_province_pairs','annual_dyad_rows','top_prefecture_dyad_rows','city_year_rows','prefecture_city_year_rows','strict_ordinary_student_rows','top_annual_connected']}

readme=f'''# CPED包内信息：市级—省级官员关系

本轮只读取用户ZIP内的两个工作簿。未联网补充人物、学校沿革、区划、领导名册或关系信息。源文件SHA256：`{stats['sha256']}`。

## 先用哪份结果

- `市级与省级官员关系_结果.xlsx`：城市年、四种主要领导配对、关系首次形成、实例、覆盖、人物、待核验任职。
- `top_leaders_dyad_year_start.csv`：普通地级单位的市委书记/市长—省委书记/省长四种配对，1980—2018年1月1日快照。
- `top_leaders_unique_officeholder_year_start.csv`：再排除快照日同一主职对应多人、无法仅凭包内记录裁定者；用于需要唯一官员赋值的版本。未根据关系的有无选择人选。全表新增四个`*_assignment_ambiguous`和`role_assignment_unambiguous`标志。
- `city_province_dyad_year_start.csv.gz`：包括市、省副职/常委等数据库标志位的扩展配对。
- `city_year_connections.csv`：按城市年聚合，四种主要领导配对分别保留；主地级样本另存`prefecture_city_year_connections.csv`。
- `dyad_spells_preexisting_connections.csv.gz`：完整同期任职区间，方便自定月/季度/年快照。
- `connection_evidence.csv.gz`：所有支持关系的两方源工作表与Excel行号；人物ID不等于Excel行号。
- `pair_first_connection_dates.csv`：每一类包内关系最早达到规则的日期和证据ID。仅对本次同省同期配对人物集合计算，不是全中国官员任意两人的普查网络。
- `不限同省同期_三类主关系首次形成.csv`：另提供整个包内曾任市级、曾任省级角色人物之间的三类正向关系及首次形成日；没有同省或同期任职限制。用于寻找跨省或未来调动联系，但必须在研究时再筛当年职务，不可直接当作当年在任网络。不存在的边不代表已核实的0。
- `不限同省同期_曾任省市官员正向关系.csv.gz`：上述全包正向关系，另含宽严同乡类型、两方原始行号。
- `education_classification.csv`、`workplace_classification.csv.gz`、`leadership_roles_all.csv`：可复核的分类过程。

## 三项主定义

1. **同乡**：双方基本信息的籍贯省、籍贯市都非空且完全相同。并列保留同县、同省；主指标不使用仅同省。籍贯不是出生地，任职地也不参与同乡判断。不做外部或模糊地名匹配，未把缺失市县猜出来。包内地名粒度可能不一致。
2. **同学代理**：双方都在普通高等教育机构有明确学生/学员等就读表述，使用学校码表自身的别名对应，起止时间重叠至少六个日历月。不以“学校”类别本身或最高学历断定就读；排除教师、校长等工作经历、党校/干部培训、军校、短训、访问、博士后、明确在职/函授/业余等记录。另排除与包内非学校工作记录重叠至少六个月的就读记录：这只能说明就读性质不确定，不证明没上学。同校不同期单列`alumni_ordinary`；不能称已确认同班、同专业或实际相识。
3. **曾经共事代理**：双方有相同具体单位键（组织类别＋任职省/市/县＋机构码表自身别名＋二/三级部门），且起止时间重叠至少六个日历月。同省、同市、行政上下级本身不构成共事。同一学校两名工作人员可以形成共事，但学生不与教师算共事。单位细分字段严格匹配，不将上下属部门自动合并，所以会漏掉真实关系；若两人都缺部门细节，也不能证明实际接触。军队等按原机构键保留，未推断真实指挥链。另保留任意重叠和十二个月版本。

`connected = 同地级籍贯 OR 同学6个月 OR 曾经共事6个月`。主列要求关系**严格在该两人连续同期省市任职区间开始之前形成**。达到六个月阈值的当天作为形成日；该日必须早于任职区间开始。`*_asof`为截至快照日的替代口径，可能包含当前任期形成的关系，不能直接解释为事前关系。时期改变不使用后来才出现的学校/工作关系回填。

## 0、1、缺失必须分清

- 1：包内有符合上述规则的证据。
- 0：有最低比较基础，但包内未发现符合规则的关系；不证明现实中没有关系，也不证明履历完整。
- 缺失：双方籍贯关键字段缺失，或缺少可比较的合格就读/工作经历；匹配到同单位/学校但关键日期缺失也保留未知。若其中一种关系为1，合并connected仍为1；如果都没检出1且有未知，connected缺失。
- `any_recorded_tie=0`可以包含未知；务必同时使用`connected`和`main_components_observable`，不要不加说明地把未知填0。

## 任职与年份

主研究对象是**同一任职省、同期在任**的市级—省级官员；不同人才能配对。省委书记、省长分别列，市委书记、市长分别列，省级领导不再混为此前的职业Local。本次是人与人关系，不是“上任前在本省有低层和高层经历”的Local。同日同职多名官员的记录组单列，不擅自选一人。不同地理层级/冲突记录分开聚合，不让县区标签记录混入普通地级市的城市年指标。

按包内标志位构造领导集合，保留兼任。普通地级市/州/地区与直辖市区县、省直辖县、标签冲突县区分别标记，主四配对表只含普通地级单位。不将所有正厅级或在省会工作者当作省级领导。有市地点的省级标志位等未决记录单列，不擅自确认。

源起止日期用左闭右开区间`[start,end)`。不把缺失结束时间视为仍在任，不把2018年6月的记录延长至2018年末。大量日期落在每月1日，不能将其解释为精确到日的真实交接时间；月边界敏感性应在正式实证前复核。使用**每年1月1日**快照保证2018也能使用已记载任职，不代表当年全年官员。需要全年主要任职者时，应用任职区间按在任时长另作赋值。

1980—2018是本次测量日范围，不代表各年官员覆盖完整。未有有效同期任职的城市年根本不造行，不填成没关系。市县代码保持包内历史口径，没有外部行政区跨年统一。2011年固定关系可以从`year=2011`取出，但须说明该日为1月1日。

## 实测规模

```json
{json.dumps(summary,ensure_ascii=False,indent=2)}
```

逐年城市数、人物数、配对数、三项可比较数见`annual_coverage.csv`。`validation.json`记录全量自环、重复、证据身份、学校/机构键、重叠和时点核对；其PASS仅是程序内部一致，不是外部履历事实认证。本轮未跑回归，未根据后续结果筛选关系。

**同乡关系没有包内观察到的“形成日期”。**证据与首次关系表中同乡行的`1900-01-01`仅是程序排序/比较用的固定属性占位值，不是源数据日期，也不表示1900年结识；新增`formation_date_kind`明确标记此类行。`formed_date_observed`在同乡行留空。任何基于首次形成日的事件分析应排除该占位值。

## 重跑

依次运行`code/build_connections.py`（从原ZIP重建主表）、`code/build_candidate_network.py`（全包正向关系）、`code/audit_and_document.py`（独立一致性检查、生成文档和打包）。需要Python、pandas、numpy、openpyxl；输入和输出位置在脚本开头。原始ZIP始终不修改。
'''
(O/'定义与使用说明.md').write_text(readme,encoding='utf-8')
codebook='# 市级—省级官员关系变量目录\n\n'+f'配对年主扩展表：{len(A):,}行，{len(A.columns)}列。统计为当前完整输出，原始输入只读。\n\n'
for r in rows:codebook+=f"## `{r['variable']}`\n\n{r['description']}\n\n类型：{r['dtype']}；非缺失：{r['nonmissing']:,}；缺失：{r['missing']:,}；不同值：{r['unique']:,}。\n\n"
(O/'变量说明.md').write_text(codebook,encoding='utf-8')
with pd.ExcelWriter(O/'市级与省级官员关系_结果.xlsx',mode='a',engine='openpyxl',if_sheet_exists='replace') as w:
 C.to_excel(w,sheet_name='城市年关系',index=False)
 T.to_excel(w,sheet_name='书记市长对书记省长',index=False)
 TC.to_excel(w,sheet_name='同日主职唯一的配对',index=False)
 CB.to_excel(w,sheet_name='变量说明',index=False)
 pd.DataFrame(checks).to_excel(w,sheet_name='内部核验',index=False)
 pd.DataFrame(office_conflicts).to_excel(w,sheet_name='同日同职多人待核',index=False)
# Human-readable examples with the actual source fields on both sides.
ex=[]
for typ in ['hometown_prefecture','classmate_6m','cowork_6m']:
 elig=T[T[typ].eq(1)].sort_values(['year','city_code']).drop_duplicates(['city_id','province_id']).head(8)
 for r in elig.to_dict('records'):
  f=F[(F.city_id==r['city_id'])&(F.province_id==r['province_id'])&(F.relation==typ)].iloc[0]
  v=EV[EV.evidence_id.eq(int(f.first_evidence_id))].iloc[0]
  d={k:r[k] for k in ['year','province','city','city_official','province_official','city_roles','province_roles','joint_spell_start']}
  d.update(relation=typ,formed=f.first_formed,evidence_id=int(v.evidence_id),city_excel_row=v.city_evidence_row,province_excel_row=v.province_evidence_row,source_sheet=v.evidence_sheet,match_key=v.match_key)
  for side,pid,er in [('city',r['city_id'],v.city_evidence_row),('province',r['province_id'],v.province_evidence_row)]:
   if typ.startswith('hometown'):
    q=P.loc[pid];d[side+'_source_detail']='|'.join(str(q[k]) for k in ['籍贯省','籍贯市','籍贯县/区'])
   else:
    q=E.loc[int(er)];d[side+'_source_detail']='|'.join(str(q[k]) for k in ['start','end','province','city','county','org','subunit','subunit2','position'])
  ex.append(d)
pd.DataFrame(ex).to_csv(O/'可读关系证据实例.csv',index=False,encoding='utf-8-sig')
# Label computational hometown-date sentinels explicitly; never present them as observed dates.
for file,datecol in [('connection_evidence.csv.gz','formed'),('pair_first_connection_dates.csv','first_formed'),('不限同省同期_曾任省市官员正向关系.csv.gz','formed')]:
 tab=pd.read_csv(O/file,keep_default_na=False)
 hh=tab.relation.str.startswith('hometown_')
 tab['formation_date_kind']=np.where(hh,'time_invariant_hometown_sort_sentinel','qualifying_recorded_overlap_or_enrollment')
 tab['formed_date_observed']=tab[datecol].where(~hh,'')
 tab.to_csv(O/file,index=False,encoding='utf-8-sig')
(O/'code').mkdir(exist_ok=True)
for name in ['build_connections.py','build_candidate_network.py','reaggregate_city_year.py','audit_and_document.py']:
 shutil.copy2(Path(__file__).parent/name,O/'code'/name)
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='file_manifest.csv':manifest.append({'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
pd.DataFrame(manifest).to_csv(O/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=O.parent/'CPED_市级与省级官员关系_数据代码与说明.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(O)))
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps(audit,ensure_ascii=False,indent=2))
print('PACKAGE',zp,'BYTES',zp.stat().st_size)
print(pd.DataFrame(ex).head(6).to_string(index=False))
