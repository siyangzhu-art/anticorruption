"""Positive city--province-role person edges, including different provinces/periods.
This is an ever-role candidate graph, not a contemporaneous leadership network.
"""
from pathlib import Path
from collections import defaultdict
import pandas as pd,json

O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\cped_city_province_connections_20261019')
R=pd.read_csv(O/'leadership_roles_all.csv').fillna('')
R=R[R.roster_issue.eq('')]
C=set(R[R.side.eq('city')].person_id);P=set(R[R.side.eq('province')].person_id)
B=pd.read_csv(O/'people_and_hometowns.csv',keep_default_na=False) if (O/'people_and_hometowns.csv').exists() else None
if B is None:
 import io,zipfile
 with zipfile.ZipFile(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip') as z:
  B=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all').rename(columns={'Unnamed: 0':'person_id'}).fillna('')
ED=pd.read_csv(O/'education_classification.csv',keep_default_na=False)
J=pd.read_csv(O/'workplace_classification.csv.gz',keep_default_na=False)
first={}
def put(a,b,typ,dt,ar,br,key,sheet):
 if a==b:return
 k=(a,b,typ)
 if k not in first or dt<first[k]['formed']:
  first[k]={'city_id':a,'province_id':b,'relation':typ,'formed':dt,'city_evidence_row':ar,'province_evidence_row':br,'match_key':key,'source_sheet':sheet}
for cols,typ in [(['籍贯省','籍贯市'],'hometown_prefecture'),(['籍贯省','籍贯市','籍贯县/区'],'hometown_county'),(['籍贯省'],'hometown_province')]:
 g=B[B[cols].ne('').all(axis=1)].copy();g['key']=g[cols].apply(lambda r:'|'.join(str(v).strip() for v in r),axis=1)
 for key,d in g.groupby('key'):
  aa=d[d.person_id.isin(C)].person_id;bb=d[d.person_id.isin(P)].person_id
  for a in aa:
   for b in bb:put(a,b,typ,pd.Timestamp('1900-01-01'),None,None,key,'基本信息')
for frame,keycol,typ in [(ED[ED.ordinary_student_eligible], 'school_key','classmate_6m'),(J[J.work_eligible], 'workplace_key','cowork_6m')]:
 q=frame[frame.dates_valid].copy()
 q['start']=pd.to_datetime(q.start);q['end']=pd.to_datetime(q.end)
 for key,g in q.groupby(keycol,sort=False):
  aa=g[g.person_id.isin(C)].to_dict('records');bb=g[g.person_id.isin(P)].to_dict('records')
  for a in aa:
   for b in bb:
    if a['person_id']==b['person_id']:continue
    s=max(a['start'],b['start']);e=min(a['end'],b['end'])
    if s>=e:continue
    formed=s+pd.DateOffset(months=6)
    if formed<=e:put(a['person_id'],b['person_id'],typ,formed,a['row_id'],b['row_id'],key,'全部经历')
 print('Done',typ,len(first),flush=True)
D=pd.DataFrame(first.values())
names=B.set_index('person_id')['姓名'].to_dict()
D['city_official']=D.city_id.map(names);D['province_official']=D.province_id.map(names)
basic_rows={pid:i+2 for i,pid in enumerate(B.person_id)}
home=D.source_sheet.eq('基本信息')
D.loc[home,'city_evidence_row']=D.loc[home,'city_id'].map(basic_rows)
D.loc[home,'province_evidence_row']=D.loc[home,'province_id'].map(basic_rows)
D['scope_note']='ever-city-role versus ever-province-role; not necessarily simultaneous or same jurisdiction'
D.to_csv(O/'不限同省同期_曾任省市官员正向关系.csv.gz',index=False,encoding='utf-8-sig')
Q=D[D.relation.isin(['hometown_prefecture','classmate_6m','cowork_6m'])]
W=Q.pivot_table(index=['city_id','city_official','province_id','province_official'],columns='relation',values='formed',aggfunc='min').reset_index()
W.columns.name=None
W['any_tie_first_formed']=W[[c for c in ['hometown_prefecture','classmate_6m','cowork_6m'] if c in W]].min(axis=1)
W.to_csv(O/'不限同省同期_三类主关系首次形成.csv',index=False,encoding='utf-8-sig')
report={'positive_relation_type_rows':len(D),'distinct_positive_main_pairs':len(W),'by_type':D.relation.value_counts().to_dict(),'city_role_people':len(C),'province_role_people':len(P),'warning':'An ever-role candidate graph only. Filter actual roles and event time before use; absent edges are not confirmed zeros.'}
(O/'all_role_positive_network_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
