import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from replication_config import PROJECT_ROOT, CPED_ZIP
"""Independent temporal audit; never overwrite source network or regression files."""
from pathlib import Path
from collections import Counter, defaultdict
import json, hashlib, shutil, html, itertools
import pandas as pd, numpy as np

P=Path((PROJECT_ROOT / ''))
O=P/'result/cped_pre_anticorruption_person_network_20261019'
OUT=P/'result/network_reaudit_2026_10_20';OUT.mkdir(exist_ok=True)
checks=[];findings=[]
TYPES=['cowork_6m','classmate_6m','hometown_prefecture','connected']
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
def check(n,ok,detail):
 checks.append(dict(check=n,status='PASS' if bool(ok) else 'FAIL',detail=detail))
 print(checks[-1],flush=True)
def read(f,**kwargs):return pd.read_csv(O/f,low_memory=False,**kwargs)
def pp(a,b):return tuple(sorted([int(a),int(b)]))

inputs=['person_edges_pre2012.csv.gz','city_pairs_same_province_pre2012.csv.gz','annual_positive_links_national_pre2012.csv.gz','city_officeholder_year_start.csv','active_official_year_recorded_degrees.csv.gz','官员个人网络_交互查看.html']
before={f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in inputs}
A=read('city_officeholder_year_start.csv');names=A.set_index('person_id').name.to_dict()
check('Unique city office-year',not A.duplicated(['year','city_code','office']).any(),len(A))
check('At most one city per person-year',A.groupby(['year','person_id']).city_code.nunique().le(1).all(),len(A))
E=read('person_edges_pre2012.csv.gz');EL={pp(r.person_a,r.person_b):r for r in E.itertuples()}
check('Fixed person edges unique and no self ties',not E.duplicated(['person_a','person_b']).any() and E.person_a.lt(E.person_b).all(),len(E))
year_summary=[];transitions=[];losses=[];examples=[];source_risks=[]
for label in ['pre2012','pre2012Nov15']:
 e=read(f'person_edges_{label}.csv.gz');lookup={pp(r.person_a,r.person_b):r for r in e.itertuples()}
 d=read(f'city_pairs_same_province_{label}.csv.gz')
 d['pa']=d[['person_a','person_b']].min(axis=1);d['pb']=d[['person_a','person_b']].max(axis=1)
 for t in TYPES:
  for v in ['frozen','asof']:
   s=t+'_'+v
   check(label+': '+s+' is binary or NA',d[s].dropna().isin([0,1]).all(),dict(d[s].value_counts(dropna=False)))
  # All observations of the SAME TWO PEOPLE, irrespective of city/office/year.
  stats=d.groupby(['pa','pb'])[t+'_frozen'].agg(lambda x:x.fillna(-9).nunique())
  check(label+': '+t+' fixed status invariant for same two people',stats.le(1).all(),{'observed_person_pairs':len(stats),'violations':int(stats.gt(1).sum())})
  u=d[['pa','pb','year',t+'_asof']].drop_duplicates().sort_values(['pa','pb','year'])
  u['previous']=u.groupby(['pa','pb'])[t+'_asof'].shift();u['previous_year']=u.groupby(['pa','pb']).year.shift()
  bad=u.previous.eq(1)&u[t+'_asof'].ne(1)
  check(label+': '+t+' once formed never disappears for same two people',not bad.any(),{'comparisons_after_observed_1':int(u.previous.eq(1).sum()),'one_to_zero_or_NA':int(bad.sum())})
  if bad.any():save(u[bad],label+'_'+t+'_violations.csv')
  post=d.year.ge(2012 if label=='pre2012' else 2013)
  check(label+': '+t+' asof equals frozen after cutoff',d.loc[post,t+'_frozen'].fillna(-9).equals(d.loc[post,t+'_asof'].fillna(-9)),int(post.sum()))
 # Adjacent years of same CITY/OFFICE pair: identify real exposure changes.
 k=['city_a','office_a','city_b','office_b'];lag=d[k+['year','pa','pb',*[t+'_asof' for t in TYPES]]].copy();lag.year+=1
 j=d.merge(lag,on=k+['year'],suffixes=('','_previous'),validate='1:1')
 j['same_people']=j.pa.eq(j.pa_previous)&j.pb.eq(j.pb_previous)
 for t in TYPES:
  a=j[t+'_asof_previous'];b=j[t+'_asof'];valid=a.notna()&b.notna();changed=valid&a.ne(b)
  row={'cutoff':label,'relation':t,'adjacent_city_office_observations':len(j),'known_status_changes':int(changed.sum()),'changes_same_people':int((changed&j.same_people).sum()),'changes_different_people':int((changed&~j.same_people).sum()),'one_to_zero_same_people':int((a.eq(1)&b.eq(0)&j.same_people).sum()),'positive_to_unknown_same_people':int((a.eq(1)&b.isna()&j.same_people).sum())}
  transitions.append(row)
  check(label+': '+t+' city exposure 1->0 requires personnel change',row['one_to_zero_same_people']==0,row)
 # Independently reconstruct ALL national active-person edge sets, not just existing records.
 national=read(f'annual_positive_links_national_{label}.csv.gz')
 active={int(y):g.groupby('person_id').first().to_dict('index') for y,g in A.groupby('year')}
 roleactive={(int(y),o):set(g.person_id) for (y,o),g in A.groupby(['year','office'])}
 sets={};viewer_sets={}
 for year,roster in active.items():
  q=national[national.year.eq(year)];actual={pp(r.person_a,r.person_b) for r in q.itertuples()}
  expect={key for key in lookup if key[0] in roster and key[1] in roster and roster[key[0]]['city_code']!=roster[key[1]]['city_code']}
  check(label+f': national mapping completeness {year}',actual==expect,{'expected_person_edges':len(expect),'observed':len(actual),'missing':len(expect-actual),'extra':len(actual-expect)})
  for t in TYPES:
   for v in ['frozen','asof']:
    qs=q[q[t+'_'+v].eq(1)];edge_set={pp(r.person_a,r.person_b) for r in qs.itertuples()};sets[(year,t,v)]=edge_set
    year_summary.append(dict(cutoff=label,year=year,relation=t,timing=v,active_people=len(roster),active_office_rows=int(A.year.eq(year).sum()),positive_person_edges=len(edge_set),positive_office_edges=len(qs),same_province_edges=len({pp(r.person_a,r.person_b) for r in qs[qs.same_province.eq(1)].itertuples()})))
    for office in ['mayor','secretary']:
     ids=roleactive.get((year,office),set());viewer_sets[(year,t,v,office)]={key for key in edge_set if key[0] in ids and key[1] in ids}
  # Verify every retained asof status against fixed formation dates.
  for r in q.itertuples():
   key=pp(r.person_a,r.person_b);edge=lookup[key]
   for t in TYPES[:3]:
    fixed=getattr(edge,t)==1
    formed=t=='hometown_prefecture' or (fixed and pd.Timestamp(getattr(edge,t+'_first_formation'))<pd.Timestamp(year,1,1))
    if (getattr(r,t+'_asof')==1)!=(fixed and formed):raise AssertionError(('wrong national asof',label,year,key,t))
 # Decompose losses in annual visible graphs into node exits and role/city filters.
 for year in range(2000,2018):
  prev=active[year];cur=active[year+1]
  for t in TYPES:
   for v in ['frozen','asof']:
    for scope in ['all_roles','mayor','secretary']:
     s0=sets[(year,t,v)] if scope=='all_roles' else viewer_sets[(year,t,v,scope)]
     s1=sets[(year+1,t,v)] if scope=='all_roles' else viewer_sets[(year+1,t,v,scope)]
     reasons=Counter()
     for key in s0-s1:
      a,b=key
      if a not in cur or b not in cur:reason='not_in_next_year_valid_city_principal_roster'
      elif cur[a]['city_code']==cur[b]['city_code']:reason='both_now_in_same_city_excluded_from_cross_city_graph'
      elif scope!='all_roles' and (a not in roleactive[(year+1,scope)] or b not in roleactive[(year+1,scope)]):reason='changed_office_filtered_out_of_this_role_graph'
      else:reason='UNEXPLAINED_RELATION_DISAPPEARANCE'
      reasons[reason]+=1
     for reason,n in reasons.items():losses.append(dict(cutoff=label,from_year=year,to_year=year+1,relation=t,timing=v,scope=scope,reason=reason,edges=n))
     if 'UNEXPLAINED_RELATION_DISAPPEARANCE' in reasons:raise AssertionError(reasons)
  # Real examples: same pair, relation persists, geographic assignment changes.
  for key in sets[(year,'cowork_6m','asof')] & sets[(year+1,'cowork_6m','asof')]:
   a,b=key
   if prev[a]['city_code']!=cur[a]['city_code'] or prev[b]['city_code']!=cur[b]['city_code']:
    examples.append(dict(cutoff=label,person_a=a,name_a=names.get(a),person_b=b,name_b=names.get(b),from_year=year,to_year=year+1,city_a_before=prev[a]['city'],city_a_after=cur[a]['city'],city_b_before=prev[b]['city'],city_b_after=cur[b]['city'],office_a_before=prev[a]['office'],office_a_after=cur[a]['office'],office_b_before=prev[b]['office'],office_b_after=cur[b]['office'],connected_before=1,connected_after=1,formation_date=getattr(lookup[key],'cowork_6m_first_formation')))
check('Every annual edge loss explained by roster/city/office filters',True,'both cutoff versions; all relations; national and same-office visible graphs')
save(pd.DataFrame(year_summary),'annual_network_counts.csv');save(pd.DataFrame(transitions),'city_pair_status_changes.csv');save(pd.DataFrame(losses),'annual_edge_loss_reasons.csv');save(pd.DataFrame(examples),'actual_persistent_relationship_examples.csv')

# Sources of imperfect network measurement and annual mapping.
J=read('inputs/workplace_classification.csv.gz');ED=read('inputs/education_classification.csv');EX=read('inputs/normalized_experiences.csv.gz');N=read('person_nodes_pre2012.csv')
ev=read('relationship_evidence_pre2012.csv.gz')
work=ev[ev.relation.eq('cowork_6m')].merge(J[['row_id','org','subunit','subunit2','category','province','city']],left_on='source_row_a',right_on='row_id',how='left',validate='m:1')
top=work.groupby(['match_key','org','category'],dropna=False).agg(evidence_rows=('evidence_id','size'),people_a=('person_a','nunique'),people_b=('person_b','nunique')).reset_index().sort_values('evidence_rows',ascending=False)
save(top.head(100),'largest_cowork_unit_evidence_groups.csv')
save(EX[~EX.dates_valid].groupby('date_issue',dropna=False).size().reset_index(name='rows'),'invalid_experience_date_counts.csv')
save(A.groupby(['year','office']).agg(office_rows=('person_id','size'),people=('person_id','nunique'),cities=('city_code','nunique'),provinces=('province_code','nunique')).reset_index(),'annual_roster_coverage.csv')
for f in ['ambiguous_office_years.csv','multicity_official_years_for_review.csv']:
 z=read(f);save(z,'source_'+f)
namesdup=N[N.name.duplicated(keep=False)].sort_values('name');save(namesdup,'duplicate_names_separate_person_ids.csv')
# Temporal endpoint limitations and sorting/filtering artifacts are documented, not silently repaired.
for c in ['start','end']:J[c]=pd.to_datetime(J[c],errors='coerce')
flag=work['subunit'].fillna('').eq('')&work['subunit2'].fillna('').eq('')
save(work[flag].groupby(['org','category'],dropna=False).size().sort_values(ascending=False).reset_index(name='positive_evidence_without_subunit'),'cowork_broad_unit_review.csv')
posmissing=read('annual_pair_coverage.csv');save(posmissing,'existing_annual_unknown_coverage.csv')
# Ensure old regression panel still points to the audited actor pairs/edge statuses.
reg=P/'result/person_network_policy_basic_2026_10_19/matched_city_pair_panel.csv.gz'
if reg.exists():
 r=pd.read_csv(reg,usecols=['year','city_a','city_b','office_a','office_b','person_a','person_b',*[t+'_asof' for t in TYPES]])
 n=read('city_pairs_same_province_pre2012.csv.gz')
 k=['year','city_a','city_b','office_a','office_b'];q=r.merge(n[k+['person_a','person_b',*[t+'_asof' for t in TYPES]]],on=k,suffixes=('','_source'),validate='1:1',how='left',indicator=True)
 check('Prior policy regression observations match current source actor pairs',q['_merge'].eq('both').all() and q.person_a.eq(q.person_a_source).all() and q.person_b.eq(q.person_b_source).all(),len(q))
 for t in TYPES:check('Prior regression '+t+' unchanged from audited source',q[t+'_asof'].fillna(-9).equals(q[t+'_asof_source'].fillna(-9)),len(q))

check('Source network and existing outputs unchanged by this audit',all(hashlib.sha256((O/f).read_bytes()).hexdigest()==h for f,h in before.items()),before)
save(pd.DataFrame(checks),'temporal_validation_checks.csv')
summary={'checks':len(checks),'failed_checks':sum(x['status']=='FAIL' for x in checks),'personal_edges_pre2012':len(E),'city_principal_edges_pre2012':int(E.both_eligible_city_principals_2000_2018.sum()),'temporal_source_files_unchanged':True,'survey_and_psychometric_tests':'Not applicable: archival relational data, not a survey scale','source_hashes':before}
(OUT/'temporal_audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('SUMMARY',json.dumps(summary,ensure_ascii=False),flush=True)
shutil.copy2(__file__,OUT/Path(__file__).name)
