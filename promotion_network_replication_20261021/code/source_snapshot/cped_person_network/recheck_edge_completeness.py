from pathlib import Path
import pandas as pd,numpy as np,json,shutil
P=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result')
O=P/'cped_pre_anticorruption_person_network_20261019';OUT=P/'network_reaudit_2026_10_20'
cut=pd.Timestamp('2012-01-01');checks=[]
J=pd.read_csv(O/'inputs/workplace_classification.csv.gz',low_memory=False)
ED=pd.read_csv(O/'school_eligibility_pre2012.csv.gz',low_memory=False)
N=pd.read_csv(O/'person_nodes_pre2012.csv');E=pd.read_csv(O/'person_edges_pre2012.csv.gz')
for d in [J,ED]:
 for c in ['start','end']:d[c]=pd.to_datetime(d[c],errors='coerce')
work=J[J.work_eligible & J.dates_valid & J.start.lt(cut)].copy()
work_by={pid:q for pid,q in work[work.category.ne('学校')].groupby('person_id')}
# Recheck full-time-school exclusion using independent interval comparisons.
reasons=[]
for r in ED.itertuples():
 actual=False
 if r.dates_valid and r.start<cut and r.person_id in work_by:
  q=work_by[r.person_id]
  st=q.start.where(q.start>r.start,r.start)
  en=q.end.where(q.end<min(r.end,cut),min(r.end,cut))
  actual=bool((st+pd.DateOffset(months=6)<=en).any())
 if actual!=bool(r.concurrent_employment_before_cutoff):reasons.append({'row_id':r.row_id,'recomputed':actual,'released':r.concurrent_employment_before_cutoff})
checks.append(dict(check='Independent pre-cutoff concurrent-employment classification',status='PASS' if not reasons else 'FAIL',violations=len(reasons)))

def derive(frame,keycol):
 frame=frame[frame.dates_valid & frame.start.lt(cut)].copy()
 frame['threshold']=frame.start+pd.DateOffset(months=6)
 frame['clipped_end']=frame.end.where(frame.end<cut,cut)
 pairs={};candidate_pairs=0
 for key,g in frame.groupby(keycol):
  if len(g)<2:continue
  pid=g.person_id.to_numpy();st=g.start.to_numpy();th=g.threshold.to_numpy();en=g.clipped_end.to_numpy()
  ai,bi=np.triu_indices(len(g),k=1)
  astart=st[ai];bstart=st[bi];formation=np.where(astart>=bstart,th[ai],th[bi]);end=np.minimum(en[ai],en[bi])
  ok=(pid[ai]!=pid[bi])&(formation<=end)&(formation<np.datetime64(cut))
  candidate_pairs+=len(ai)
  for a,b,dt in zip(pid[ai[ok]],pid[bi[ok]],formation[ok]):
   k=tuple(sorted([int(a),int(b)]));pairs[k]=min(pairs.get(k,dt),dt)
 return pairs,candidate_pairs

for typ,frame,keycol in [('cowork_6m',work,'workplace_key'),('classmate_6m',ED[ED.ordinary_student_broad & ~ED.concurrent_employment_before_cutoff],'school_key')]:
 recomputed,n=derive(frame,keycol);released=E[E[typ].eq(1)]
 keys=set(zip(released.person_a,released.person_b));expected=set(recomputed)
 dates={tuple(sorted([int(r.person_a),int(r.person_b)])):pd.Timestamp(getattr(r,typ+'_first_formation')) for r in released.itertuples()}
 wrong_dates=[k for k in expected&keys if pd.Timestamp(recomputed[k])!=dates[k]]
 row=dict(check='Independent all-candidate '+typ+' edges and first formation dates',status='PASS' if expected==keys and not wrong_dates else 'FAIL',candidate_episode_pairs=n,recomputed_person_edges=len(expected),released_person_edges=len(keys),missing=len(expected-keys),extra=len(keys-expected),wrong_dates=len(wrong_dates));checks.append(row);print(row,flush=True)

expected=set()
bad={'','不详','未知','无','其他','不明','不详市','不详县'}
for _,g in N.fillna('').groupby(['籍贯省','籍贯市']):
 if str(g['籍贯省'].iloc[0]).strip() in bad or str(g['籍贯市'].iloc[0]).strip() in bad:continue
 ids=sorted(g.person_id)
 for i,a in enumerate(ids):
  for b in ids[i+1:]:expected.add((a,b))
q=E[E.hometown_prefecture.eq(1)];keys=set(zip(q.person_a,q.person_b))
checks.append(dict(check='Independent all hometown group combinations',status='PASS' if expected==keys else 'FAIL',recomputed_person_edges=len(expected),released_person_edges=len(keys),missing=len(expected-keys),extra=len(keys-expected)))

# Flag broad organizational membership as a measurement sensitivity, not a coding error.
ev=pd.read_csv(O/'relationship_evidence_pre2012.csv.gz');ev=ev[ev.relation.eq('cowork_6m')]
cols=['row_id','org','category','subunit','subunit2','position','province_code','city_code']
v=ev.merge(J[cols].add_suffix('_a'),left_on='source_row_a',right_on='row_id_a',validate='m:1').merge(J[cols].add_suffix('_b'),left_on='source_row_b',right_on='row_id_b',validate='m:1')
collective={'人大常委会','政协常委会','党委常委会/政治局'}
v['broad_collective']=v.org_a.isin(collective)&v.subunit_a.fillna('').eq('')&v.subunit2_a.fillna('').eq('')
g=v.groupby(['person_a','person_b']).agg(evidence_rows=('evidence_id','size'),broad_collective_evidence=('broad_collective','sum')).reset_index()
g['all_evidence_broad_collective']=g.evidence_rows.eq(g.broad_collective_evidence)
EP=E[E.both_eligible_city_principals_2000_2018.eq(1)&E.cowork_6m.eq(1)]
g=g.merge(E[['person_a','person_b','name_a','name_b','both_eligible_city_principals_2000_2018']],on=['person_a','person_b'],validate='1:1')
g.to_csv(OUT/'cowork_collective_membership_sensitivity_flags.csv',index=False,encoding='utf-8-sig')
v[v.broad_collective].head(250).to_csv(OUT/'broad_collective_evidence_review_examples.csv',index=False,encoding='utf-8-sig')
stats={'all_cowork_edges':len(g),'all_cowork_supported_only_by_broad_collective':int(g.all_evidence_broad_collective.sum()),'city_principal_cowork_edges':len(EP),'city_principal_cowork_only_broad_collective':int(g.loc[g.both_eligible_city_principals_2000_2018.eq(1),'all_evidence_broad_collective'].sum()),'warning':'Broad collective means same committee/body with no recorded lower subunit. Provincial standing leadership can be real coworkers; flag does not establish false ties. Do not automatically discard.'}
(OUT/'measurement_sensitivity_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'independent_completeness_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'checks':checks,'measurement_sensitivity':stats},ensure_ascii=False,indent=2),flush=True)
shutil.copy2(__file__,OUT/Path(__file__).name)
