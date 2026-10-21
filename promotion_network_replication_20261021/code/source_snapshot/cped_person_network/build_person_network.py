"""Pre-anticorruption person network, CPED ZIP only. No policy outcomes read.

Default build uses the bundled, audited CPED classifications. The original ZIP
is read for identity/row/date checks, not external biographies. See README.
"""
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import argparse, hashlib, io, json, shutil, zipfile
import numpy as np
import pandas as pd

DEFAULT_ROOT = Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result')
parser=argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=DEFAULT_ROOT/'cped_pre_anticorruption_person_network_20261019')
parser.add_argument('--inputs', type=Path, default=DEFAULT_ROOT/'cped_city_province_connections_20261019')
parser.add_argument('--zip', type=Path, default=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip'))
args=parser.parse_args(); OUT=args.output; IN=args.inputs
OUT.mkdir(parents=True,exist_ok=True)
CUTS={'pre2012':pd.Timestamp('2012-01-01'), 'pre2012Nov15':pd.Timestamp('2012-11-15')}
BAD={'','不详','未知','无','其他','不明','不详市','不详县'}
def say(*a): print(*a,flush=True)
def save(df,name): df.to_csv(OUT/name,index=False,encoding='utf-8-sig')
def read(name): return pd.read_csv(IN/name,keep_default_na=False,low_memory=False)
def asbool(s): return s.astype(str).str.lower().eq('true')|s.astype(str).eq('1')
def txt(x): return str(x).strip() if pd.notna(x) else ''
def iso(t): return pd.Timestamp(t).strftime('%Y-%m-%d') if pd.notna(t) else ''
def jsave(x,name): (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

B=read('people_and_hometowns.csv'); R=read('leadership_roles_all.csv')
E=read('normalized_experiences.csv.gz'); ED=read('education_classification.csv'); J=read('workplace_classification.csv.gz')
for d in [R,E,ED,J]:
 for c in ['start','end']:d[c]=pd.to_datetime(d[c],errors='coerce')
 for c in ['dates_valid','work_eligible','ordinary_student_broad','ordinary_student_eligible']:
  if c in d:d[c]=asbool(d[c])
 for c in ['province_code','city_code']:
  d[c]=d[c].astype(str).str.replace(r'\.0$','',regex=True)
B.person_id=B.person_id.astype(int); B['name']=B['姓名']; ids=set(B.person_id)
names=B.set_index('person_id').name.to_dict(); basic_rows={int(p):i+2 for i,p in enumerate(B.person_id)}

# Independent source identity/date checks, for all normalized experience rows.
sha=hashlib.sha256(args.zip.read_bytes()).hexdigest()
assert sha=='1427471e045e5e4f26b1ce39bb6f8ea024476d099b8478aaf984893c1cf24526'
with zipfile.ZipFile(args.zip) as z:
 raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
 bio=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all')
assert len(raw)==len(E) and len(bio)==len(B)
assert np.array_equal(raw['用户编码'].astype(int).to_numpy(),E.person_id.to_numpy())
assert np.array_equal(bio['Unnamed: 0'].astype(int).to_numpy(),B.person_id.to_numpy())
for c,rc in [('start','起始时间（YYYY-MM-DD）'),('end','终止时间（（YYYY-MM-DD））')]:
 assert pd.Series(pd.to_datetime(raw[rc],errors='coerce').to_numpy()).equals(pd.Series(E[c].to_numpy()))
assert np.array_equal(E.row_id.to_numpy(),np.arange(2,len(E)+2))
say('Verified supplied ZIP and all',len(E),'source experience row identities and dates')

role_ok=R.roster_issue.eq('') & R.side.eq('city') & R.scope.eq('prefecture') & R.flag.isin(['市长','市委书记'])
RO=R[role_ok].copy()
eligible=set(RO[(RO.start<pd.Timestamp('2019-01-01'))&(RO.end>pd.Timestamp('2000-01-01'))].person_id)
first_exp=E[E.dates_valid].groupby('person_id').start.min().to_dict()
roster=[]; conflicts=[]
for year in range(2000,2019):
 dt=pd.Timestamp(year,1,1);active=RO[(RO.start<=dt)&(RO.end>dt)]
 for (p,c,f),g in active.groupby(['province_code','city_code','flag'],sort=True):
  persons=sorted(set(g.person_id));rr=g.iloc[0]
  if len(persons)>1:
   conflicts.append({'year':year,'province_code':p,'city_code':c,'city':rr.city,'office':f,'person_ids':'|'.join(map(str,persons)),'names':'|'.join(names[a] for a in persons)})
   continue
  a=int(persons[0]); gg=g[g.person_id.eq(a)]
  roster.append({'year':year,'snapshot_date':iso(dt),'province_code':p,'province':rr.province,'city_code':c,'city':rr.city,
                 'office':'mayor' if f=='市长' else 'secretary','office_cn':f,'person_id':a,'name':names[a],
                 'appointment_start':iso(gg.start.min()),'appointment_end':iso(gg.end.max()),
                 'source_role_rows':'|'.join(map(str,sorted(set(gg.row_id))))})
A=pd.DataFrame(roster);assert not A.duplicated(['year','province_code','city_code','office']).any()
save(A,'city_officeholder_year_start_before_multicity_screen.csv')
multicity=[];bad_person_years=set()
for (year,pid),g in A.groupby(['year','person_id']):
 if g.city_code.nunique()>1:
  bad_person_years.add((year,pid))
  multicity.append({'year':int(year),'person_id':int(pid),'name':names[pid],
    'cities':'|'.join(sorted(set(g.city))),'city_codes':'|'.join(sorted(set(g.city_code))),
    'offices':'|'.join(sorted(set(g.office))),'handling':'exclude all ambiguous city assignments in main annual mapping; retain source spells'})
save(pd.DataFrame(multicity),'multicity_official_years_for_review.csv')
A=A[[((r.year,r.person_id) not in bad_person_years) for r in A.itertuples()]].copy()
save(A,'city_officeholder_year_start.csv');save(pd.DataFrame(conflicts),'ambiguous_office_years.csv')
save(RO,'eligible_city_leadership_spells.csv')
save(R[~role_ok],'other_or_excluded_roles.csv.gz')
say('Unique city office snapshots',len(A),'people',A.person_id.nunique(),'conflict office-years',len(conflicts))

all_summary=[]; evidence_all=[]; node_all=[]; edge_all=[]; pair_summaries=[]; annual_positive_all=[]; intra_all=[]
for label,cut in CUTS.items():
 say('Building',label,'strictly before',iso(cut))
 # Recompute concurrent employment using PRE-CUTOFF time only. A later job
 # must not retrospectively disqualify a pre-cutoff ordinary-school spell.
 jj=J[J.work_eligible].copy()
 jj['clipped_end']=jj.end.where(jj.end<cut,cut)
 jj.loc[jj.end.isna(),'clipped_end']=pd.NaT
 job_by=defaultdict(list)
 for r in jj[jj.dates_valid & (jj.start<cut)].to_dict('records'):
  if r['category']!='学校':job_by[r['person_id']].append(r)
 ed=ED[ED.ordinary_student_broad].copy(); cc=[]
 for r in ed.to_dict('records'):
  conflict=False
  if r['dates_valid'] and r['start']<cut:
   en=min(r['end'],cut)
   for w in job_by[r['person_id']]:
    st=max(r['start'],w['start']);end=min(en,w['clipped_end'])
    if st+pd.DateOffset(months=6)<=end:conflict=True;break
  cc.append(conflict)
 ed['concurrent_employment_before_cutoff']=cc
 save(ed.assign(cutoff_label=label),'school_eligibility_'+label+'.csv.gz')
 ed=ed[~ed.concurrent_employment_before_cutoff]
 first={}; evid=[]; ambiguous=defaultdict(set); coverage={t:set() for t in ['cowork_6m','classmate_6m','hometown_prefecture']}
 def put(a,b,typ,formed,ar,br,key,sheet,**kw):
  if a==b:return
  if a>b:a,b,ar,br=b,a,br,ar
  eid=f'{label}_{len(evid)+1}'
  row={'cutoff_label':label,'cutoff_exclusive':iso(cut),'evidence_id':eid,'person_a':int(a),'person_b':int(b),
       'name_a':names[a],'name_b':names[b],'relation':typ,'formation_date':iso(formed),
       'formation_date_kind':'six_month_threshold' if pd.notna(formed) else 'fixed_hometown_attribute_no_observed_meeting_date',
       'source_sheet':sheet,'source_row_a':int(ar),'source_row_b':int(br),'match_key':str(key),**kw}
  evid.append(row);k=(a,b,typ)
  dt=formed if pd.notna(formed) else pd.Timestamp.min
  if k not in first or dt<first[k][0]:first[k]=(dt,eid,row)
 for cols,typ in [(['籍贯省','籍贯市'],'hometown_prefecture')]:
  good=B[cols].apply(lambda s:s.astype(str).str.strip().map(lambda x:x not in BAD)).all(axis=1)
  h=B[good].copy();coverage[typ]=set(h.person_id)
  for key,g in h.groupby(cols,sort=True):
   for a,b in combinations(sorted(g.person_id),2):
    put(a,b,typ,pd.NaT,basic_rows[a],basic_rows[b],'|'.join(key),'基本信息')
 for frame,keycol,typ in [(jj,'workplace_key','cowork_6m'),(ed,'school_key','classmate_6m')]:
  # At least one valid six-month pre-cutoff episode is a MINIMUM comparison
  # basis; it is not a claim that the biography is complete.
  valid=frame.dates_valid & (frame.start<cut)
  for r in frame[valid].to_dict('records'):
   if r['start']+pd.DateOffset(months=6)<cut and r['start']+pd.DateOffset(months=6)<=r['end']:
    coverage[typ].add(r['person_id'])
  candidates=frame[(frame.start.isna())|(frame.start<cut)]
  for key,g in candidates.groupby(keycol,sort=True):
   if str(key).strip() in BAD:continue
   rows=g.to_dict('records')
   for a,b in combinations(rows,2):
    pa,pb=int(a['person_id']),int(b['person_id'])
    if pa==pb:continue
    if not (a['dates_valid'] and b['dates_valid']):
     ambiguous[typ].add(tuple(sorted([pa,pb])));continue
    st=max(a['start'],b['start']);en=min(a['end'],b['end'],cut)
    formed=st+pd.DateOffset(months=6)
    if formed<=en and formed<cut:
     put(pa,pb,typ,formed,a['row_id'],b['row_id'],key,'全部经历',overlap_start=iso(st),overlap_end_censored=iso(en))
  say(label,typ,'positive person pairs',sum(k[2]==typ for k in first))
 types=['cowork_6m','classmate_6m','hometown_prefecture']
 pospairs=sorted({(a,b) for a,b,t in first}); e_lookup={}
 def status(a,b,asof=None):
  if a>b:a,b=b,a
  d={};valid_components=0;nties=0
  for t in types:
   hit=first.get((a,b,t));positive=bool(hit and (asof is None or t=='hometown_prefecture' or hit[0]<asof))
   comparable=(a in coverage[t] and b in coverage[t] and (a,b) not in ambiguous[t])
   # For earlier annual years, verify each side had some six-month episode
   # by that snapshot, rather than borrowing later pre-cutoff coverage.
   if asof is not None and t!='hometown_prefecture':
    comparable=comparable and min_qual[t].get(a,pd.Timestamp.max)<asof and min_qual[t].get(b,pd.Timestamp.max)<asof
   d[t]=1 if positive else (0 if comparable else None)
   valid_components+=d[t] is not None;nties+=positive
  d['connected']=1 if nties else (0 if valid_components==3 else None)
  d['n_positive_relation_types']=nties;d['components_comparable']=valid_components
  return d
 min_qual={}
 for f,t in [(jj,'cowork_6m'),(ed,'classmate_6m')]:
  m={}
  for r in f[f.dates_valid & (f.start<cut)].to_dict('records'):
   dt=r['start']+pd.DateOffset(months=6)
   if dt<=r['end'] and dt<cut:m[r['person_id']]=min(m.get(r['person_id'],pd.Timestamp.max),dt)
  min_qual[t]=m
 for a,b in pospairs:
  q={'cutoff_label':label,'person_a':a,'person_b':b,'name_a':names[a],'name_b':names[b],
     'both_eligible_city_principals_2000_2018':int(a in eligible and b in eligible)}
  q.update(status(a,b))
  for t in types:
   hit=first.get((a,b,t));q[t+'_first_formation']=iso(hit[0]) if hit and t!='hometown_prefecture' else ''
   q[t+'_evidence_id']=hit[1] if hit else ''
  edge_all.append(q);e_lookup[(a,b)]=q
 edges=pd.DataFrame([r for r in edge_all if r['cutoff_label']==label])
 save(edges,'person_edges_'+label+'.csv.gz')
 save(edges[edges.both_eligible_city_principals_2000_2018.eq(1)],'city_principal_person_edges_'+label+'.csv')
 ev=pd.DataFrame(evid);save(ev,'relationship_evidence_'+label+'.csv.gz');evidence_all.extend(evid)
 ambrows=[{'cutoff_label':label,'relation':t,'person_a':a,'person_b':b} for t,v in ambiguous.items() for a,b in sorted(v)]
 save(pd.DataFrame(ambrows,columns=['cutoff_label','relation','person_a','person_b']),'date_ambiguous_pairs_'+label+'.csv.gz')
 nodes=B[['person_id','name','籍贯省','籍贯市','籍贯县/区','has_experience']].copy()
 nodes['cutoff_label']=label;nodes['eligible_city_principal_2000_2018']=nodes.person_id.isin(eligible).astype(int)
 nodes['observed_experience_before_cutoff']=nodes.person_id.map(lambda a:int(first_exp.get(a,pd.Timestamp.max)<cut))
 for t in types:nodes[t+'_minimum_comparison_basis']=nodes.person_id.isin(coverage[t]).astype(int)
 for t in types+['connected']:
  cnt=Counter()
  for r in edges[edges[t].eq(1)].itertuples(index=False):cnt[r.person_a]+=1;cnt[r.person_b]+=1
  nodes[t+'_degree_all_people']=nodes.person_id.map(lambda a:cnt[a])
 node_all.extend(nodes.to_dict('records'));save(nodes,'person_nodes_'+label+'.csv')
 # Same-province city pairs: same-office mayor--mayor and secretary--secretary,
 # plus cross-office pairs. Every covered pair is kept, including unknowns.
 annual=[];positive=[];intracity=[]
 for year,ay in A.groupby('year',sort=True):
  dt=pd.Timestamp(int(year),1,1)
  # National positive person links mapped to current cities, irrespective of
  # province; does NOT require a provincial leader observation.
  by_person=defaultdict(list)
  for r in ay.to_dict('records'):by_person[r['person_id']].append(r)
  for (a,b),edge in e_lookup.items():
   if a not in by_person or b not in by_person:continue
   st=status(a,b,min(dt,cut))
   for ra in by_person[a]:
    for rb in by_person[b]:
     if ra['city_code']==rb['city_code']:continue
     zz={'cutoff_label':label,'year':int(year),'person_a':a,'name_a':names[a],'person_b':b,'name_b':names[b],
       'city_a':ra['city_code'],'city_name_a':ra['city'],'province_a':ra['province_code'],'office_a':ra['office'],
       'city_b':rb['city_code'],'city_name_b':rb['city'],'province_b':rb['province_code'],'office_b':rb['office'],
       'same_province':int(ra['province_code']==rb['province_code'])}
     for t in types+['connected']:
      zz[t+'_frozen']=edge[t];zz[t+'_asof']=st[t]
     positive.append(zz)
  for p,g in ay.groupby('province_code',sort=True):
   rows=sorted(g.to_dict('records'),key=lambda r:(r['city_code'],r['office']))
   for ra,rb in combinations(rows,2):
    a,b=ra['person_id'],rb['person_id']
    if a==b:continue
    d=status(a,b);now=status(a,b,min(dt,cut))
    typ=(ra['office']+'_to_'+rb['office']) if ra['office']==rb['office'] else 'mayor_to_secretary'
    z={'cutoff_label':label,'year':int(year),'snapshot_date':iso(dt),'province_code':p,'province':ra['province'],
      'city_a':ra['city_code'],'city_name_a':ra['city'],'office_a':ra['office'],'person_a':a,'name_a':names[a],
      'city_b':rb['city_code'],'city_name_b':rb['city'],'office_b':rb['office'],'person_b':b,'name_b':names[b],
      'pair_type':typ,'same_city':int(ra['city_code']==rb['city_code'])}
    for t in types+['connected','n_positive_relation_types','components_comparable']:
     z[t+'_frozen']=d[t];z[t+'_asof']=now[t]
    if z['same_city']:intracity.append(z)
    else:annual.append(z)
  say(label,'year',year,'within-province cumulative pairs',len(annual))
 pairs=pd.DataFrame(annual);save(pairs,'city_pairs_same_province_'+label+'.csv.gz')
 save(pd.DataFrame(positive),'annual_positive_links_national_'+label+'.csv.gz')
 save(pd.DataFrame(intracity),'within_city_secretary_mayor_'+label+'.csv.gz')
 for (year,typ),g in pairs.groupby(['year','pair_type']):
  z={'cutoff_label':label,'year':int(year),'pair_type':typ,'pairs':len(g),'provinces':g.province_code.nunique()}
  for t in types+['connected']:
   for ver in ['frozen','asof']:
    v=g[t+'_'+ver];z[t+'_'+ver+'_positive']=int(v.eq(1).sum());z[t+'_'+ver+'_recorded_zero']=int(v.eq(0).sum());z[t+'_'+ver+'_unknown']=int(v.isna().sum())
  pair_summaries.append(z)
 all_summary.append({'cutoff_label':label,'cutoff_exclusive':iso(cut),'all_people':len(B),'city_principal_people_2000_2018':len(eligible),
  'all_person_positive_edges':len(edges),'city_principal_positive_edges':int(edges.both_eligible_city_principals_2000_2018.sum()),
  'positive_edges_by_relation':{t:int(edges[t].eq(1).sum()) for t in types},
  'city_principal_edges_by_relation':{t:int(edges.loc[edges.both_eligible_city_principals_2000_2018.eq(1),t].eq(1).sum()) for t in types},
  'evidence_rows':len(ev),'same_province_city_pair_years':len(pairs),'national_positive_office_pair_years':len(positive),
  'within_city_pair_years':len(intracity),'school_rows_reincluded_after_precut_employment_check':int((~ED.ordinary_student_eligible & ED.row_id.isin(ed.row_id)).sum())})
save(pd.DataFrame(pair_summaries),'annual_pair_coverage.csv');save(pd.DataFrame(node_all),'person_nodes_all_cutoffs.csv')
save(pd.DataFrame(edge_all),'person_edges_all_cutoffs.csv.gz')
jsave({'source_zip':str(args.zip),'source_zip_sha256':sha,'network_timing':'formation date strictly before cutoff; no post-cutoff ties added',
       'no_outcome_data_used':True,'annual_year_range':[2000,2018],'annual_assignment':'January 1, unique officeholder, does not require province leadership data',
       'ambiguous_office_years':len(conflicts),'multicity_official_years_excluded':len(multicity),'summary':all_summary},'build_summary.json')
inputs_dir=OUT/'inputs';inputs_dir.mkdir(exist_ok=True)
for n in ['people_and_hometowns.csv','leadership_roles_all.csv','normalized_experiences.csv.gz','education_classification.csv','workplace_classification.csv.gz']:
 target=inputs_dir/n
 if (IN/n).resolve()!=target.resolve():shutil.copy2(IN/n,target)
provenance=[{'file':n,'sha256':hashlib.sha256((inputs_dir/n).read_bytes()).hexdigest(),'derived_only_from_supplied_zip':1} for n in sorted(x.name for x in inputs_dir.iterdir() if x.is_file())]
save(pd.DataFrame(provenance),'input_provenance.csv')
code=OUT/'code';code.mkdir(exist_ok=True)
if Path(__file__).resolve()!=(code/Path(__file__).name).resolve():shutil.copy2(__file__,code/Path(__file__).name)
say(json.dumps(all_summary,ensure_ascii=False,indent=2))
