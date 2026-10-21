"""CPED-only city--province connections. No external inputs/network calls."""
from pathlib import Path
from collections import defaultdict
from itertools import combinations
import io,zipfile,json,hashlib,re,math,shutil
import numpy as np
import pandas as pd

ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\data\cped_connections_20261019')
SRC=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')
OUT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\cped_city_province_connections_20261019')
OUT.mkdir(parents=True,exist_ok=True)
START=pd.Timestamp('1980-01-01'); STOP=pd.Timestamp('2019-01-01')
def say(*a): print(*a,flush=True)
def clean(x):
 if pd.isna(x): return ''
 return re.sub(r'\s+','',str(x)).replace('（','(').replace('）',')').strip()
def code(x):
 try:return str(int(float(x)))
 except:return clean(x)
def csv(d,n): d.to_csv(OUT/n,index=False,encoding='utf-8-sig')

with zipfile.ZipFile(SRC) as z:
 bio=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all')
 raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
 geo=pd.read_excel(io.BytesIO(z.read('基本码表-20200606.xlsx')),sheet_name='地区关键词').dropna(how='all')
 schools=pd.read_excel(io.BytesIO(z.read('基本码表-20200606.xlsx')),sheet_name='学校关键词').dropna(how='all')
 orgs=pd.read_excel(io.BytesIO(z.read('基本码表-20200606.xlsx')),sheet_name='职务关键词').dropna(how='all')
say('Loaded',len(bio),len(raw))
assert bio['Unnamed: 0'].is_unique
assert set(raw['用户编码'])<=set(bio['Unnamed: 0'])
bio=bio.rename(columns={'Unnamed: 0':'person_id'}).set_index('person_id',drop=False)
persons={int(k):r for k,r in bio.to_dict('index').items()}
school_alias={code(r['编码']):code(r['别名编码']) or code(r['编码']) for r in schools.to_dict('records')}
school_names={code(r['编码']):clean(r['名称']) for r in schools.to_dict('records')}
org_alias={code(r['编码']):code(r['别名']) or code(r['编码']) for r in orgs.to_dict('records')}
def canonical(k,m):
 seen=set()
 while k in m and m[k]!=k and k not in seen:
  seen.add(k);k=m[k]
 return min(seen|{k}) if k in seen else k
province_names={code(r['编码']):clean(r['名称']) for r in geo.to_dict('records') if clean(r['级别'])=='省'}
valid_provs=set()
for r in raw.to_dict('records'):
 if '省' in clean(r['标志位']) and code(r['一级关键词编码']) in province_names:valid_provs.add(code(r['一级关键词编码']))
municipalities={p for p in valid_provs if province_names[p].endswith('市')}
PROV={'省委书记','省长','省委副书记(非省长)','省常委(其他)','副省长(常委)','副省长(非常委)','省组织部长'}
CITY={'市委书记','市长','市委副书记(专职)','市常委(其他)','副市长(常委)','副市长(非常委)','市组织部长'}
e=[];roles=[];education=[];job=[];issues=[]
for i,r in enumerate(raw.to_dict('records')):
 q={'row_id':i+2,'person_id':int(r['用户编码']),'name':clean(r['姓名']),
    'episode_seq':r['经历序号'],'start':pd.to_datetime(r['起始时间（YYYY-MM-DD）'],errors='coerce'),
    'end':pd.to_datetime(r['终止时间（（YYYY-MM-DD））'],errors='coerce'),
    'province_code':code(r['一级关键词编码']),'province':clean(r['地方一级关键词']),
    'city_code':code(r['二级关键词编码']),'city':clean(r['地方二级关键词']),
    'county':clean(r['地方三级关键词']),'area_level':clean(r['地区级别']),
    'category':clean(r['基本大类别']),'org_code':code(r['职务一级关键词编码']),
    'org':clean(r['职务一级关键词']),'subunit':clean(r['职务二级关键词']),
    'subunit2':clean(r['职务三级关键词']),'position':clean(r['具体职务']),
    'flag':clean(r['标志位']),'degree_raw':clean(r['学历']),
    'national':clean(r['是否全国性组织']),'central_dispatch':clean(r['是否中央派出']),
    'location_note':clean(r['录入信息备注']),'org_note':clean(r['录入信息备注.1'])}
 q['dates_valid']=pd.notna(q['start']) and pd.notna(q['end']) and q['start']<q['end']
 q['date_issue']='' if q['dates_valid'] else ('missing_endpoint' if pd.isna(q['start']) or pd.isna(q['end']) else 'end_not_after_start')
 e.append(q)
 if q['date_issue']:issues.append({'row_id':q['row_id'],'person_id':q['person_id'],'issue':q['date_issue']})
 if q['flag'] in PROV|CITY:
  rr=q.copy();rr['side']='province' if q['flag'] in PROV else 'city'
  rr['top_office']=q['flag'] in {'省委书记','省长','市委书记','市长'}
  rr['scope']='province' if rr['side']=='province' else ('municipality_district' if q['province_code'] in municipalities else ('direct_county' if q['area_level']=='省直辖县' else ('county_or_district_flag_conflict' if q['county'] or re.search('县长|县委|区长|区委',q['position']) else 'prefecture')))
  rr['roster_issue']=''
  if q['province_code'] not in valid_provs:rr['roster_issue']='province_not_in_local_provincial_roster'
  elif rr['side']=='city' and (not q['city_code'] or not q['city']):rr['roster_issue']='missing_city_key'
  elif rr['side']=='province' and q['city_code']:rr['roster_issue']='provincial_flag_with_city_location_requires_review'
  elif not q['dates_valid']:rr['roster_issue']=q['date_issue']
  roles.append(rr)
 if q['category']=='学校':
  qq=q.copy();qq['school_key']=canonical(q['org_code'],school_alias)
  qq['school_name_canonical']=school_names.get(qq['school_key'],q['org'])
  txt='|'.join([q['org'],q['subunit'],q['subunit2'],q['position'],q['org_note']])
  pos=q['position'];qtxt=q['subunit']+'|'+q['subunit2']+'|'+q['org_note']
  explicit=bool(re.search('学生|学员|研究生|博士生|硕士生|^(博士|硕士)$|学习|就读|攻读|在职函授|读书',pos))
  mixed=bool(re.search('教师|教员|讲师|教授|助教|研究实习员|研究员|文书|秘书|辅导员',pos))
  party=bool(re.search('党校|行政学院|干部学院|团校|社会主义学院|干部学校',q['org']))
  military=bool(re.search('军|国防|解放军|武警|海军|空军|陆军',q['org']))
  short=bool(re.search('培训|研修|进修|中青班|研讨|研究班|短期|考察|赴.{0,6}学习|访问|博士后|函授|在职|业余|远程|自考|网络教育|广播电视|电大',txt))
  higher=bool(re.search('大学|学院|专科|研究生院|社会科学院|中国科学院',q['org'])) and not bool(re.search('中学|小学|职业学校|中等|中专|技工|技校',q['org'])) and q['org'] not in {'大学','学院','师范学院','工学院','医学院','不详'}
  dur=(q['end']-q['start']).days if q['dates_valid'] else np.nan
  ordinary=explicit and not mixed and not party and not military and not short and higher and (pd.isna(dur) or dur>=365) and q['date_issue']!='end_not_after_start'
  qq.update(student_explicit=explicit,mixed_student_employee=mixed,party_school=party,military_school=military,
            nonstandard_or_training=short,higher_education_name=higher,ordinary_student_eligible=ordinary,
            duration_days=dur)
  qq['education_class']='ordinary_student_proxy' if ordinary else ('party_training_student' if explicit and party and not mixed else ('other_student_or_training' if explicit and not mixed else 'employment_or_ambiguous'))
  education.append(qq)
  # School employment is eligible only if clearly an employee, not a student or ambiguous term.
  if explicit or not re.search('教师|教员|讲师|教授|助教|研究员|校长|院长|处长|科长|书记|主任|辅导员|秘书|干事|干部|编辑|工程师',pos):continue
 # Build exact structured workplace key, retaining all levels of subunit and geography.
 if q['org'] and q['category'] not in {'其他'}:
  jj=q.copy();orgkey=canonical(q['org_code'],school_alias if q['category']=='学校' else org_alias)
  if q['category']=='学校':scope='SCHOOL' if q['org'] not in {'科学院','社科院','中科院','大学','学院','学校','不详'} else 'SCHOOL|'+q['province_code']+'|'+q['city_code']
  else:scope='|'.join([q['province_code'] or q['province'],q['city_code'] or q['city'],q['county']])
  jj['workplace_key']='|'.join([q['category'],scope,orgkey or q['org'],q['subunit'],q['subunit2']])
  # Generic job descriptions at a broad government root cannot establish a concrete workplace.
  coarse=(q['org'] in {'党委常委会/政治局','政府/国务院(综合)','革命委员会'} and not q['subunit'] and not q['subunit2'] and bool(re.search('干事|干部|工作人员|历任|^工作$|^秘书$',q['position'])))
  jj['work_eligible']=bool(q['org'] not in {'不详','未知','无','其他','工作单位不详'} and q['position'] and not coarse and (q['province_code'] or q['category']=='学校') and not re.search('待分配|待安排|待业|退休|离休|失业|学习|学员|学生|访问学者',q['position']))
  jj['coarse_workplace_excluded']=coarse
  job.append(jj)
E=pd.DataFrame(e);R=pd.DataFrame(roles);ED=pd.DataFrame(education);J=pd.DataFrame(job)
# Unlabelled simultaneous employment makes a program's full-time nature uncertain.
# Keep it in the broad ordinary-school table but exclude it from the primary peer proxy.
employment_by_person=defaultdict(list)
for q in J[J.work_eligible & J.dates_valid].to_dict('records'):
 employment_by_person[q['person_id']].append(q)
concurrent=[]
for q in ED.to_dict('records'):
 flag=False
 if q['dates_valid'] and q['ordinary_student_eligible']:
  for w in employment_by_person[q['person_id']]:
   # Student committee posts within the same school need not be separate employment.
   if w['category']=='学校':continue
   st=max(w['start'],q['start']);en=min(w['end'],q['end'])
   if st+pd.DateOffset(months=6)<=en:flag=True;break
 concurrent.append(flag)
ED['concurrent_employment_ge6m']=concurrent
ED['ordinary_student_broad']=ED.ordinary_student_eligible
ED.loc[ED.concurrent_employment_ge6m,'ordinary_student_eligible']=False
ED.loc[ED.concurrent_employment_ge6m,'education_class']='ordinary_school_concurrent_work_uncertain'
csv(E,'normalized_experiences.csv.gz');csv(R,'leadership_roles_all.csv');csv(ED,'education_classification.csv');csv(J,'workplace_classification.csv.gz')
csv(pd.DataFrame(issues),'date_issues.csv')
csv(R[R.roster_issue.ne('')],'excluded_or_unresolved_leadership_roles.csv')
RR=R[R.roster_issue.eq('')].copy()
cr=RR[RR.side.eq('city')].to_dict('records');pr=RR[RR.side.eq('province')].to_dict('records')
pby=defaultdict(list)
for r in pr:pby[r['province_code']].append(r)
spells=[]
for c in cr:
 for p in pby[c['province_code']]:
  if c['person_id']==p['person_id']:continue
  s=max(c['start'],p['start'],START);t=min(c['end'],p['end'],STOP)
  if s>=t:continue
  spells.append({'city_id':c['person_id'],'province_id':p['person_id'],'province_code':c['province_code'],
    'city_code':c['city_code'],'city':c['city'],'province':c['province'],'scope':c['scope'],
    'city_role':c['flag'],'province_role':p['flag'],'city_role_row':c['row_id'],'province_role_row':p['row_id'],
    'city_role_start':c['start'],'province_role_start':p['start'],
    'joint_start':max(c['start'],p['start']),'start':s,'end':t,
    'top_four':c['top_office'] and p['top_office']})
S=pd.DataFrame(spells);pairs=set(zip(S.city_id,S.province_id)); city_ids=set(S.city_id);province_ids=set(S.province_id)
say('Valid roles',len(RR),'dyad role spells',len(S),'unique oriented pairs',len(pairs))

# Evidence only for city--province pairs that actually share a province during a documented leadership spell.
events=[]; ambiguous=defaultdict(set)
def event(a,b,typ,key,formed,rowa,rowb,**kw):
 if (a,b) not in pairs:return
 events.append({'city_id':a,'province_id':b,'relation':typ,'match_key':key,'formed':formed,'city_evidence_row':rowa,'province_evidence_row':rowb,**kw})
def candidate_matches(frame,keycol):
 for key,g in frame.groupby(keycol,sort=False):
  if not key:continue
  rows=g.to_dict('records');aa=[r for r in rows if r['person_id'] in city_ids];bb=[r for r in rows if r['person_id'] in province_ids]
  for a in aa:
   for b in bb:
    if (a['person_id'],b['person_id']) in pairs:yield key,a,b
def overlap(a,b):
 if not(a['dates_valid'] and b['dates_valid']):return None
 s=max(a['start'],b['start']);t=min(a['end'],b['end'])
 return (s,t) if s<t else False

for a,b in sorted(pairs):
 aa=persons[a];bb=persons[b]
 ap,ac,ad=[clean(aa[x]) for x in ['籍贯省','籍贯市','籍贯县/区']]
 bp,bc,bd=[clean(bb[x]) for x in ['籍贯省','籍贯市','籍贯县/区']]
 for typ,match,k in [('hometown_province',bool(ap and bp and ap==bp),ap),
                     ('hometown_prefecture',bool(ap and ac and bp and bc and (ap,ac)==(bp,bc)),ap+'|'+ac),
                     ('hometown_county',bool(ap and ac and ad and bp and bc and bd and (ap,ac,ad)==(bp,bc,bd)),ap+'|'+ac+'|'+ad)]:
  if match:event(a,b,typ,k,pd.Timestamp('1900-01-01'),a,b,city_basic_id=a,province_basic_id=b)
say('Hometown events',len(events))
for key,a,b in candidate_matches(ED[ED.ordinary_student_eligible],'school_key'):
 ai,bi=a['person_id'],b['person_id']
 # Alumni exists only after both have documented enrollment dates; it does not assert graduation.
 if pd.notna(a['start']) and pd.notna(b['start']):
  event(ai,bi,'alumni_ordinary',key,max(a['start'],b['start']),a['row_id'],b['row_id'])
 else:ambiguous[(ai,bi)].add('alumni_ordinary')
 ov=overlap(a,b)
 if ov is None:ambiguous[(ai,bi)].update(['classmate_6m','classmate_any']);continue
 if not ov:continue
 s,t=ov
 event(ai,bi,'classmate_any',key,s+pd.Timedelta(days=1),a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
 f=s+pd.DateOffset(months=6)
 if f<=t:event(ai,bi,'classmate_6m',key,f,a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
 if a['start'].year==b['start'].year and f<=t:
  event(ai,bi,'classmate_same_entry_year',key,f,a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
say('After school events',len(events))
# Party schools/short programs do not contribute to the primary connection measure.
TR=ED[ED.student_explicit & ~ED.mixed_student_employee & ~ED.ordinary_student_eligible].copy()
TR['training_key']=TR['school_key']+'|'+TR['subunit']+'|'+TR['subunit2']
for key,a,b in candidate_matches(TR,'training_key'):
 ov=overlap(a,b)
 if ov is None or ov is False:continue
 s,t=ov
 if not(a['subunit'] or a['subunit2']):continue # generic central Party school is not enough for same program
 event(a['person_id'],b['person_id'],'training_same_program_overlap',key,s+pd.Timedelta(days=1),a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
say('After training events',len(events))
for key,a,b in candidate_matches(J[J.work_eligible],'workplace_key'):
 ov=overlap(a,b);ai,bi=a['person_id'],b['person_id']
 if ov is None:ambiguous[(ai,bi)].update(['cowork_6m','cowork_any','cowork_12m']);continue
 if ov is False:continue
 s,t=ov
 event(ai,bi,'cowork_any',key,s+pd.Timedelta(days=1),a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
 for months in [6,12]:
  f=s+pd.DateOffset(months=months)
  if f<=t:event(ai,bi,'cowork_'+str(months)+'m',key,f,a['row_id'],b['row_id'],overlap_start=s,overlap_end=t)
say('All evidence events',len(events))
EV=pd.DataFrame(events).drop_duplicates(['city_id','province_id','relation','city_evidence_row','province_evidence_row','match_key','formed'])
EV.insert(0,'evidence_id',range(1,len(EV)+1))
# Basic evidence uses explicit sheet and physical Excel row, not person ID as a row number.
basic_rows={int(pid):int(i)+2 for i,pid in enumerate(bio.person_id)}
is_home=EV.relation.str.startswith('hometown_')
EV.loc[is_home,'city_evidence_row']=EV.loc[is_home,'city_id'].map(basic_rows)
EV.loc[is_home,'province_evidence_row']=EV.loc[is_home,'province_id'].map(basic_rows)
EV['evidence_sheet']=np.where(is_home,'基本信息','全部经历')
csv(EV,'connection_evidence.csv.gz')
first={}
for r in EV.sort_values(['formed','evidence_id']).drop_duplicates(['city_id','province_id','relation']).itertuples(index=False):
 first[(r.city_id,r.province_id,r.relation)]=(r.formed,int(r.evidence_id))

# At least one observed eligible record on each side is required to code a no-recorded-match zero.
school_starts=defaultdict(list);work_starts=defaultdict(list)
for r in ED[ED.ordinary_student_eligible & ED.dates_valid].to_dict('records'):school_starts[r['person_id']].append(r['start'])
for r in J[J.work_eligible & J.dates_valid].to_dict('records'):work_starts[r['person_id']].append(r['start'])
school_min={k:min(v) for k,v in school_starts.items()};work_min={k:min(v) for k,v in work_starts.items()}
types=['hometown_prefecture','hometown_county','hometown_province','classmate_6m','classmate_any','classmate_same_entry_year','alumni_ordinary','cowork_6m','cowork_any','cowork_12m','training_same_program_overlap']
def coverage(a,b,typ,cut):
 if typ.startswith('hometown'):
  cols=['籍贯省']+(['籍贯市'] if typ!='hometown_province' else [])+(['籍贯县/区'] if typ=='hometown_county' else [])
  return all(clean(persons[i][c]) not in {'','不详','未知','无','其他'} for i in [a,b] for c in cols)
 if typ.startswith('cowork'):m=work_min
 elif typ=='training_same_program_overlap':return False
 else:m=school_min
 return a in m and b in m and m[a]<cut and m[b]<cut and typ not in ambiguous[(a,b)]
def indicators(a,b,cut):
 d={}
 for typ in types:
  hit=first.get((a,b,typ))
  yes=bool(hit and hit[0]<cut)
  d[typ]=1 if yes else (0 if coverage(a,b,typ,cut) else None)
 main=[d[t] for t in ['hometown_prefecture','classmate_6m','cowork_6m']]
 d['any_recorded_tie']=int(1 in main)
 d['connected']=1 if 1 in main else (0 if all(x==0 for x in main) else None)
 d['main_components_observable']=sum(x is not None for x in main)
 d['n_main_tie_types']=sum(x==1 for x in main)
 return d

# Union simultaneous/adjacent leadership records before defining dyad episodes.
# An official holding multiple provincial positions counts once, never as his/her own contact.
groups=['city_id','province_id','province_code','city_code','scope']
merged=[];current=None;lastkey=None
for r in S.sort_values(groups+['start','end']).itertuples(index=False):
 keys=tuple(getattr(r,k) for k in groups)
 if current is not None and keys==lastkey and r.start<=current['end']:
  current['end']=max(current['end'],r.end);current['joint_start']=min(current['joint_start'],r.joint_start)
 else:
  if current is not None:merged.append(current)
  current={**dict(zip(groups,keys)),'province':r.province,'city':r.city,'start':r.start,'end':r.end,'joint_start':r.joint_start}
 lastkey=keys
if current is not None:merged.append(current)
D=pd.DataFrame(merged)
say('Merged dyad spells',len(D))
details=[];precomputed={}
for r in D.to_dict('records'):
 a,b=r['city_id'],r['province_id'];r['city_official']=persons[a]['姓名'];r['province_official']=persons[b]['姓名']
 # Predetermined ties: formed strictly before the beginning of this concurrent leadership spell.
 pre=indicators(a,b,r['joint_start']);precomputed[(a,b,r['joint_start'])]=pre
 r.update(pre);details.append(r)
DS=pd.DataFrame(details);csv(DS,'dyad_spells_preexisting_connections.csv.gz')

# Year-start panel, exact dated appointments only: start <= January 1 < end.
# Jan 1 allows a genuine 2018 snapshot without projecting June 2018 end dates forward.
annual=[]
for year in range(1980,2019):
 dt=pd.Timestamp(year,1,1)
 active=S[(S.start<=dt)&(S.end>dt)]
 active_d=D[(D.start<=dt)&(D.end>dt)]
 active_lookup={k:v for k,v in active.groupby(['city_id','province_id','city_code','province_code'])}
 for r in active_d.to_dict('records'):
  a,b=r['city_id'],r['province_id'];g=active_lookup[(a,b,r['city_code'],r['province_code'])]
  z={'year':year,'snapshot_date':dt,'province_code':r['province_code'],'province':r['province'],'city_code':r['city_code'],'city':r['city'],
    'scope':r['scope'],'city_id':a,'city_official':persons[a]['姓名'],'province_id':b,'province_official':persons[b]['姓名'],
    'city_roles':'|'.join(sorted(set(g.city_role))),'province_roles':'|'.join(sorted(set(g.province_role))),
    'city_is_secretary':int('市委书记' in set(g.city_role)),'city_is_mayor':int('市长' in set(g.city_role)),
    'province_is_secretary':int('省委书记' in set(g.province_role)),'province_is_governor':int('省长' in set(g.province_role)),
    'joint_spell_start':r['joint_start']}
  z['top_four']=int(bool(z['city_is_secretary'] or z['city_is_mayor']) and bool(z['province_is_secretary'] or z['province_is_governor']))
  z.update(precomputed[(a,b,r['joint_start'])])
  now=indicators(a,b,dt)
  for t in types+['connected','any_recorded_tie']:z[t+'_asof']=now[t]
  annual.append(z)
 say('Annual',year,len(active_d))
A=pd.DataFrame(annual)
assert not A.duplicated(['year','province_code','city_code','city_id','province_id']).any()
csv(A,'city_province_dyad_year_start.csv.gz')
TOP=A[A.top_four.eq(1)&A.scope.eq('prefecture')].copy();csv(TOP,'top_leaders_dyad_year_start.csv')

# City-year summaries: observed officials/contacts, never a claim to complete leadership rosters.
agg=[]
for (year,p,c,scope),g in A.groupby(['year','province_code','city_code','scope']):
 z={'year':year,'province_code':p,'province':g.province.iloc[0],'city_code':c,'city':g.city.iloc[0],'scope':g.scope.iloc[0],
    'n_observed_city_leaders':g.city_id.nunique(),'n_observed_provincial_leaders':g.province_id.nunique(),'n_dyads':len(g)}
 for label,sub in [('all',g),('top',g[g.top_four.eq(1)]),('city_secretary_to_province_secretary',g[g.city_is_secretary.eq(1)&g.province_is_secretary.eq(1)]),('city_secretary_to_governor',g[g.city_is_secretary.eq(1)&g.province_is_governor.eq(1)]),('mayor_to_province_secretary',g[g.city_is_mayor.eq(1)&g.province_is_secretary.eq(1)]),('mayor_to_governor',g[g.city_is_mayor.eq(1)&g.province_is_governor.eq(1)])]:
  z[label+'_n_dyads']=len(sub)
  for typ in ['hometown_prefecture','classmate_6m','cowork_6m','connected']:
   v=sub[typ].dropna();z[label+'_'+typ]=1 if (v==1).any() else (0 if len(sub)>0 and len(v)==len(sub) else None)
  z[label+'_n_recorded_connected_province_people']=sub.loc[sub.any_recorded_tie.eq(1),'province_id'].nunique() if len(sub)>0 else None
 agg.append(z)
C=pd.DataFrame(agg);csv(C,'city_year_connections.csv')
csv(C[C.scope.eq('prefecture')],'prefecture_city_year_connections.csv')
P=bio[['person_id','姓名','性别','民族','出生日期(YYYY-MM-DD)','籍贯省','籍贯市','籍贯县/区']].copy()
P['has_experience']=P.person_id.isin(E.person_id).astype(int)
P['ever_city_flag']=P.person_id.isin(R[R.side.eq('city')].person_id).astype(int)
P['ever_province_flag']=P.person_id.isin(R[R.side.eq('province')].person_id).astype(int)
csv(P,'people_and_hometowns.csv')
firstrows=[]
for (a,b,typ),(formed,eid) in sorted(first.items()):firstrows.append({'city_id':a,'city_official':persons[a]['姓名'],'province_id':b,'province_official':persons[b]['姓名'],'relation':typ,'first_formed':formed,'first_evidence_id':eid})
F=pd.DataFrame(firstrows);csv(F,'pair_first_connection_dates.csv')
support=A.groupby(['year','scope']).agg(dyads=('city_id','size'),cities=('city_code','nunique'),provinces=('province_code','nunique'),city_people=('city_id','nunique'),province_people=('province_id','nunique'),any_recorded_ties=('any_recorded_tie','sum'),fully_comparable=('main_components_observable',lambda x:(x==3).sum())).reset_index();csv(support,'annual_coverage.csv')
samples=TOP[TOP.any_recorded_tie.eq(1)].sort_values(['year','city_code']).drop_duplicates(['city_id','province_id']).head(60)
csv(samples,'top_leader_examples.csv')
stats={'source_zip':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'only_input_files':['基本码表-20200606.xlsx','全部经历-20200606.xlsx'],'people':len(P),'experience_rows':len(E),
 'roles_source_rows':len(R),'valid_role_rows':len(RR),'role_exclusions':R[R.roster_issue.ne('')].roster_issue.value_counts().to_dict(),
 'source_provinces':len(valid_provs),'city_leader_people_ever':int(R[R.side.eq('city')].person_id.nunique()),'province_leader_people_ever':int(R[R.side.eq('province')].person_id.nunique()),
 'dyad_role_spells':len(S),'merged_dyad_spells':len(D),'unique_city_province_pairs':len(pairs),'evidence_rows':len(EV),'evidence_by_type':EV.relation.value_counts().to_dict(),
 'annual_dyad_rows':len(A),'top_prefecture_dyad_rows':len(TOP),'city_year_rows':len(C),'prefecture_city_year_rows':int(C.scope.eq('prefecture').sum()),
 'year_range':[1980,2018], 'snapshot':'January 1','top_prefecture_unique_city_codes':int(TOP.city_code.nunique()),
 'preexisting_ties_by_type_in_top_annual':{t:int(TOP[t].eq(1).sum()) for t in types},
 'top_annual_connected':TOP.connected.fillna('NA').value_counts().to_dict(),
 'top_annual_known_zero_is_only_no_documented_match':True,
 'strict_ordinary_student_rows':int(ED.ordinary_student_eligible.sum()),'dates_invalid':int((~E.dates_valid).sum()),
 'education_class_counts':ED.education_class.value_counts().to_dict(),
 'source_date_end_max':str(E.end.max()),'source_date_start_max':str(E.start.max())}
(OUT/'build_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
with pd.ExcelWriter(OUT/'市级与省级官员关系_结果.xlsx',engine='openpyxl') as w:
 C.to_excel(w,sheet_name='城市年关系',index=False)
 TOP.to_excel(w,sheet_name='书记市长对书记省长',index=False)
 F.to_excel(w,sheet_name='各关系首次形成',index=False)
 samples.to_excel(w,sheet_name='关系实例',index=False)
 support.to_excel(w,sheet_name='年份覆盖',index=False)
 P.to_excel(w,sheet_name='人物与籍贯',index=False)
 R[R.roster_issue.ne('')].to_excel(w,sheet_name='任职待核验',index=False)
say(json.dumps(stats,ensure_ascii=False,indent=2,default=str))
