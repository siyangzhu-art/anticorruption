"""Audit network evidence against supplied original ZIP and annual assignments.
No policy outcomes are used. Assertions fail loudly; no repair by dropping ties.
"""
from pathlib import Path
from collections import Counter
import hashlib,io,json,zipfile,re
import numpy as np
import pandas as pd

O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\cped_pre_anticorruption_person_network_20261019')
Z=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')
S=json.loads((O/'build_summary.json').read_text(encoding='utf-8'))
checks=[]
def passed(label,rows):checks.append({'check':label,'status':'PASS','rows':int(rows)})
def clean(x):
 if pd.isna(x):return ''
 return re.sub(r'\s+','',str(x)).replace('（','(').replace('）',')').strip()
def code(x):
 try:return str(int(float(x)))
 except:return clean(x)
def canonical(k,m):
 seen=set()
 while k in m and m[k]!=k and k not in seen:seen.add(k);k=m[k]
 return min(seen|{k}) if k in seen else k
with zipfile.ZipFile(Z) as z:
 raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
 bio=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all')
 school=pd.read_excel(io.BytesIO(z.read('基本码表-20200606.xlsx')),sheet_name='学校关键词').dropna(how='all')
 org=pd.read_excel(io.BytesIO(z.read('基本码表-20200606.xlsx')),sheet_name='职务关键词').dropna(how='all')
sm={code(r['编码']):code(r['别名编码']) or code(r['编码']) for r in school.to_dict('records')}
om={code(r['编码']):code(r['别名']) or code(r['编码']) for r in org.to_dict('records')}
raw.index=np.arange(2,len(raw)+2);bio.index=np.arange(2,len(bio)+2)
assert hashlib.sha256(Z.read_bytes()).hexdigest()==S['source_zip_sha256']
passed('original ZIP hash unchanged',len(raw))
raws=raw.to_dict('index');bios=bio.to_dict('index')
J=pd.read_csv(O/'inputs'/'workplace_classification.csv.gz',keep_default_na=False).set_index('row_id')
ED=pd.read_csv(O/'inputs'/'education_classification.csv',keep_default_na=False).set_index('row_id')
EVS={}
for label in ['pre2012','pre2012Nov15']:
 cut=pd.Timestamp('2012-01-01' if label=='pre2012' else '2012-11-15')
 ev=pd.read_csv(O/f'relationship_evidence_{label}.csv.gz',keep_default_na=False)
 edges=pd.read_csv(O/f'person_edges_{label}.csv.gz')
 assert (edges.person_a<edges.person_b).all() and not edges.duplicated(['person_a','person_b']).any()
 assert edges.connected.eq(1).all()
 assert ev.evidence_id.is_unique
 assert set(edges.cowork_6m_evidence_id.dropna())<=set(ev.evidence_id)
 for r in ev.to_dict('records'):
  a,b=int(r['source_row_a']),int(r['source_row_b'])
  if r['relation']=='hometown_prefecture':
   aa,bb=bios[a],bios[b]
   assert int(aa['Unnamed: 0'])==r['person_a'] and int(bb['Unnamed: 0'])==r['person_b']
   assert all(clean(aa[c])==clean(bb[c]) and clean(aa[c]) for c in ['籍贯省','籍贯市'])
   assert r['formation_date']==''
  else:
   aa,bb=raws[a],raws[b]
   assert int(aa['用户编码'])==r['person_a'] and int(bb['用户编码'])==r['person_b']
   st=max(pd.Timestamp(aa['起始时间（YYYY-MM-DD）']),pd.Timestamp(bb['起始时间（YYYY-MM-DD）']))
   en=min(pd.Timestamp(aa['终止时间（（YYYY-MM-DD））']),pd.Timestamp(bb['终止时间（（YYYY-MM-DD））']),cut)
   assert st+pd.DateOffset(months=6)<=en and pd.Timestamp(r['formation_date'])==st+pd.DateOffset(months=6)<cut
   if r['relation']=='classmate_6m':
    assert canonical(code(aa['职务一级关键词编码']),sm)==canonical(code(bb['职务一级关键词编码']),sm)==str(r['match_key'])
    assert bool(ED.loc[a,'ordinary_student_broad']) and bool(ED.loc[b,'ordinary_student_broad'])
   else:
    assert J.loc[a,'workplace_key']==J.loc[b,'workplace_key']==r['match_key']
    # Reconstruct the exact structured key from ORIGINAL fields and ZIP aliases.
    for row in [aa,bb]:
     cat=clean(row['基本大类别']);orgname=clean(row['职务一级关键词']);pr=code(row['一级关键词编码']);ci=code(row['二级关键词编码'])
     if cat=='学校':scope='SCHOOL' if orgname not in {'科学院','社科院','中科院','大学','学院','学校','不详'} else 'SCHOOL|'+pr+'|'+ci
     else:scope='|'.join([pr or clean(row['地方一级关键词']),ci or clean(row['地方二级关键词']),clean(row['地方三级关键词'])])
     kk='|'.join([cat,scope,canonical(code(row['职务一级关键词编码']),sm if cat=='学校' else om) or orgname,clean(row['职务二级关键词']),clean(row['职务三级关键词'])])
     assert kk==r['match_key']
 passed(label+': all positive evidence checked against original workbook rows/keys/dates',len(ev))
 f=ev[ev.relation.ne('hometown_prefecture')].groupby(['person_a','person_b','relation']).formation_date.min().to_dict()
 for r in edges.to_dict('records'):
  for t in ['cowork_6m','classmate_6m']:
   dt=r[t+'_first_formation']
   if pd.notna(dt):assert dt==f[(r['person_a'],r['person_b'],t)]
 passed(label+': undirected unique edges, earliest threshold dates, no future ties',len(edges))
 EVS[label]=edges

A=pd.read_csv(O/'city_officeholder_year_start.csv',dtype={'province_code':str,'city_code':str,'source_role_rows':str})
assert not A.duplicated(['year','province_code','city_code','office']).any()
assert A.groupby(['year','person_id']).city_code.nunique().le(1).all()
spells=pd.read_csv(O/'eligible_city_leadership_spells.csv',keep_default_na=False,dtype={'province_code':str,'city_code':str}).set_index('row_id')
for r in A.to_dict('records'):
 dt=pd.Timestamp(r['snapshot_date']);rs=spells.loc[[int(x) for x in r['source_role_rows'].split('|')]]
 assert rs.person_id.eq(r['person_id']).all() and rs.city_code.eq(r['city_code']).all()
 assert ((pd.to_datetime(rs.start)<=dt)&(pd.to_datetime(rs.end)>dt)).any()
passed('unique actual city assignment on snapshot day; no province-leader matching required',len(A))
annual_lookup={(int(r.year),str(r.city_code),r.office):int(r.person_id) for r in A.itertuples()}
for label,edges in EVS.items():
 cut=pd.Timestamp('2012-01-01' if label=='pre2012' else '2012-11-15')
 lookup={(int(r.person_a),int(r.person_b)):r for r in edges.itertuples()}
 pairs=pd.read_csv(O/f'city_pairs_same_province_{label}.csv.gz',dtype={'city_a':str,'city_b':str,'province_code':str})
 assert not pairs.duplicated(['year','city_a','office_a','city_b','office_b']).any()
 assert pairs.city_a.ne(pairs.city_b).all() and pairs.person_a.ne(pairs.person_b).all()
 for r in pairs.itertuples():
  assert annual_lookup[(r.year,r.city_a,r.office_a)]==r.person_a
  assert annual_lookup[(r.year,r.city_b,r.office_b)]==r.person_b
  e=lookup.get(tuple(sorted([r.person_a,r.person_b])))
  for t in ['cowork_6m','classmate_6m','hometown_prefecture']:
   val=getattr(r,t+'_frozen');positive=e is not None and getattr(e,t)==1
   assert (val==1)==positive
   if getattr(r,t+'_asof')==1 and t!='hometown_prefecture':
    assert pd.Timestamp(getattr(e,t+'_first_formation'))<min(pd.Timestamp(r.snapshot_date),cut)
  vals=[getattr(r,t+'_frozen') for t in ['cowork_6m','classmate_6m','hometown_prefecture']]
  if 1 in vals:assert r.connected_frozen==1
  elif any(pd.isna(v) for v in vals):assert pd.isna(r.connected_frozen)
  else:assert r.connected_frozen==0
 passed(label+': full annual mapped pairs, correct people, fixed edges and unknown propagation',len(pairs))
 post=pairs[pairs.year.ge(2013)]
 for t in ['cowork_6m','classmate_6m','hometown_prefecture','connected']:
  assert post[t+'_frozen'].fillna(-1).equals(post[t+'_asof'].fillna(-1))
 passed(label+': after cutoff, as-of and frozen ties agree for every mapped person pair',len(post))

# Person graph can only gain edges with a later cutoff; minimum six-month
# support is checked against original sources above, not against a handpicked
# set of names or regression results.
for t in ['cowork_6m','classmate_6m','hometown_prefecture']:
 a=EVS['pre2012'];b=EVS['pre2012Nov15']
 assert set(zip(a.loc[a[t].eq(1),'person_a'],a.loc[a[t].eq(1),'person_b']))<=set(zip(b.loc[b[t].eq(1),'person_a'],b.loc[b[t].eq(1),'person_b']))
passed('nested cutoff graphs for all three relations',len(EVS['pre2012']))
report={'status':'PASS_internal_and_original_source_consistency_not_external_fact_verification','no_outcomes_read':True,'checks':checks}
(Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\network_reaudit_2026_10_20')/'original_source_recheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

