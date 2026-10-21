"""User-requested promotion revision; existing source and results are read-only.
Run with the bundled Python. Reuses documented network exposures, not outcome labels.
"""
from pathlib import Path
import sys, json, shutil, hashlib
import pandas as pd
import numpy as np

HERE=Path(__file__).parent
ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
OLDOUT=ROOT/'result/promotion_connections_rolling_2026_10_20'
OUT=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'
OUT.mkdir(exist_ok=True);(OUT/'code').mkdir(exist_ok=True)

def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')

# Read the same raw workbook and validated city/province roles. Stop before
# loading/building any network, so the original relation graph is never mutated.
src=(HERE/'prepare.py').read_text(encoding='utf8')
prefix=src.split('# Edge tables:')[0]
prefix=prefix.replace("OUT=ROOT/'result/promotion_connections_rolling_2026_10_20'", "OUT=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'")
ns={};exec(compile(prefix,'prepare_source_loader','exec'),ns)
for key in ['raw','BY','B','CS','PS','SROWS','baseline_rank','classify']:
 if key in ns:globals()[key]=ns[key]
functions=src[src.index('def baseline_rank('):src.index('def add_connections(')]
exec(compile(functions,'original_outcome_functions','exec'),ns)
baseline_rank=ns['baseline_rank'];classify=ns['classify']

# Source-coded provincial vice-governor flags also cover autonomous regions
# and directly administered municipalities; rank must be vice-ministerial.
flags=raw['标志位'].map(ns['clean'])
raw['vice_governor']=flags.isin(['副省长(常委)','副省长(非常委)']) & raw['rank'].eq(5) & raw.substantive
VROWS=set(raw.loc[raw.vice_governor,'row_id'])
save(raw[raw.vice_governor][['row_id','person_id','姓名','start','end','地方一级关键词','地方二级关键词','具体职务','级别','标志位']], 'vice_governor_source_rows.csv')

def vice_events(pid,lo,hi,base_rank):
 q=BY[pid]
 q=q[q.row_id.isin(VROWS)&q.start.gt(lo)&q.start.le(hi)]
 if pd.isna(base_rank) or base_rank>5:return q.iloc[0:0]
 keep=[]
 for r in q.itertuples():
  # Consecutive entries/renewals of an already held vice-governor position
  # do not create a second appointment event.
  prior=BY[pid]
  prior=prior[prior.row_id.isin(VROWS)&prior.start.lt(r.start)&prior.end.ge(r.start)]
  if not len(prior):keep.append(r.row_id)
 return q[q.row_id.isin(keep)]

A=pd.read_csv(OLDOUT/'annual_official_panel.csv.gz',low_memory=False)
A=A[A.year.between(2006,2017)].copy()
changes=[]
for idx,r in A.iterrows():
 pid=int(r.person_id);dt=pd.Timestamp(r.baseline_date);end=pd.Timestamp(int(r.year),12,31)
 original=classify(pid,dt,end,r.base_rank,r.role,r.city_code)
 new=vice_events(pid,dt,end,r.base_rank)
 A.loc[idx,'promotion_previous']=r.promotion
 A.loc[idx,'rank_promotion']=original['rank_promotion']
 A.loc[idx,'same_grade_vice_governor_event']=int(len(new)>0 and r.base_rank==5)
 for key,value in original.items():A.loc[idx,key]=value
 if len(new):
  er=new.sort_values('start').iloc[0]
  A.loc[idx,'promotion']=1.
  A.loc[idx,'status']='observed_promotion_including_vice_governor'
  if original['promotion']!=1:
   A.loc[idx,'event_date']=ns['iso'](er.start);A.loc[idx,'event_row']=int(er.row_id)
   A.loc[idx,'event_job']=er['具体职务'];A.loc[idx,'event_rank']=er['级别'];A.loc[idx,'second_line']=0
 if pd.isna(r.promotion)!=pd.isna(A.loc[idx,'promotion']) or (pd.notna(r.promotion) and r.promotion!=A.loc[idx,'promotion']):
  changes.append(dict(unit='annual',person_id=pid,name=r['name'],year=int(r.year),role=r.role,old=r.promotion,new=A.loc[idx,'promotion'],reason='new_vice_governor_appointment',event_row=A.loc[idx,'event_row'],event_date=A.loc[idx,'event_date'],event_job=A.loc[idx,'event_job']))

T=pd.read_csv(OLDOUT/'term_destination_panel.csv.gz',low_memory=False)
T=T[T.year.between(2006,2017)].copy()
term_evidence=[]
for idx,r in T.iterrows():
 pid=int(r.person_id);start=pd.Timestamp(r.city_spell_start);end=pd.Timestamp(r.city_spell_end)
 # A revised term outcome covers a promotion DURING the current city-role
 # spell, plus promotion at its first observed destination within 12 months.
 q=BY[pid];inside=q[q.substantive&q.start.gt(start)&q.start.lt(end)]
 events=[]
 for er in inside.itertuples():
  prior_rank,_=baseline_rank(pid,er.start-pd.Timedelta(days=1),None)
  up=pd.notna(prior_rank) and pd.notna(er.rank) and er.rank>prior_rank
  roleup=r.role=='mayor' and er.row_id in SROWS
  vup=len(vice_events(pid,er.start-pd.Timedelta(days=1),er.start,prior_rank))>0 and er.row_id in VROWS
  if up or roleup or vup:events.append((er.start,int(er.row_id),'within_term',bool(up)))
 nextq=q[q.start.ge(end)&q.start.le(end+pd.DateOffset(months=12))&(q.substantive|q.terminal)]
 exitpromotion=r.promotion;exitrank=r.rank_promotion
 if len(nextq):
  nd=nextq.start.min();n=nextq[nextq.start.eq(nd)]
  # Only the first distinct destination, not any promotion over a later year.
  vnew=vice_events(pid,end-pd.Timedelta(days=1),nd,r.base_rank)
  vnew=vnew[vnew.start.eq(nd)]
  if len(vnew):exitpromotion=1.
  if exitpromotion==1:
   rr=n.sort_values('rank',ascending=False).iloc[0]
   events.append((nd,int(rr.row_id),'first_destination',bool(exitrank==1)))
 T.loc[idx,'promotion_previous']=r.promotion
 T.loc[idx,'within_term_promotion']=float(any(e[2]=='within_term' for e in events))
 if events:
  events.sort();er=raw[raw.row_id.eq(events[0][1])].iloc[0]
  T.loc[idx,'promotion']=1.;T.loc[idx,'rank_promotion']=float(any(e[3] for e in events))
  T.loc[idx,'status']='promotion_during_term_or_first_destination'
  for key,value in dict(event_date=ns['iso'](events[0][0]),event_row=int(er.row_id),event_job=er['具体职务'],event_rank=er['级别'],second_line=int(er.second_line)).items():T.loc[idx,key]=value
 for date,rowid,kind,up in events:term_evidence.append(dict(city_spell_id=r.city_spell_id,person_id=pid,name=r['name'],event_date=ns['iso'](date),event_row=rowid,event_kind=kind,rank_up=int(up)))
 val=T.loc[idx,'promotion']
 if pd.isna(r.promotion)!=pd.isna(val) or (pd.notna(r.promotion) and r.promotion!=val):
  changes.append(dict(unit='term',person_id=pid,name=r['name'],year=int(r.year),role=r.role,old=r.promotion,new=val,reason='within_term_or_new_vice_governor',event_row=T.loc[idx,'event_row'],event_date=T.loc[idx,'event_date'],event_job=T.loc[idx,'event_job']))

# Keep the old main outcome, including grade-up second-line posts. An explicit
# executive-only sensitivity excludes positive years attributed to second-line.
for d in [A,T]:
 d['executive_promotion']=d.promotion.mask(d.promotion.eq(1)&d.second_line.eq(1),0.)
 d['role_secretary']=d.role.eq('secretary').astype(float)
save(A,'annual_official_panel.csv.gz');save(T,'term_destination_panel.csv.gz')
save(pd.DataFrame(changes),'promotion_definition_changes.csv');save(pd.DataFrame(term_evidence),'term_promotion_event_evidence.csv')
save(A[['person_id','name','year','role','base_rank','promotion_previous','promotion','rank_promotion','same_grade_vice_governor_event','status','event_date','event_row','event_job','event_rank','second_line']], 'annual_promotion_event_registry.csv')
desc=A.groupby('role').agg(rows=('person_id','size'),known=('promotion','count'),promotion_old=('promotion_previous','sum'),promotion_new=('promotion','sum'),rank_only=('rank_promotion','sum'),people=('person_id','nunique')).reset_index()
save(desc,'sample_summary.csv')

checks=[]
def check(name,ok,detail=''):checks.append(dict(check=name,passed=bool(ok),detail=str(detail)))
check('annual_person_year_unique',not A.duplicated(['person_id','year']).any())
check('term_spell_unique',T.city_spell_id.is_unique)
check('years_2006_2017',A.year.between(2006,2017).all() and T.year.between(2006,2017).all())
for unit,d in [('annual',A),('term',T)]:
 check(unit+'_binary',d.promotion.dropna().isin([0,1]).all())
 check(unit+'_no_removed_previous_promotions',d.loc[d.promotion_previous.eq(1),'promotion'].eq(1).all())
 check(unit+'_rank_is_subset',d.loc[d.rank_promotion.eq(1),'promotion'].eq(1).all())
for r in pd.DataFrame(changes).query("unit=='annual'").itertuples():
 er=raw[raw.row_id.eq(r.event_row)].iloc[0]
 check('annual_changed_event_'+str(r.event_row),er.vice_governor and er.start.year==r.year)
oldA=pd.read_csv(OLDOUT/'annual_official_panel.csv.gz',low_memory=False).query('2006<=year<=2017')
relcols=[c for c in A if c.startswith(('legacy_','preassignment_'))]
check('network_exposure_values_unchanged',oldA[relcols].reset_index(drop=True).equals(A[relcols].reset_index(drop=True)))
check('original_zip_hash',hashlib.sha256(ns['ZIP'].read_bytes()).hexdigest()=='1427471e045e5e4f26b1ce39bb6f8ea024476d099b8478aaf984893c1cf24526')
save(pd.DataFrame(checks),'data_validation_checks.csv')
assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
profile=[]
for c in A:
 profile.append(dict(variable=c,dtype=str(A[c].dtype),missing=int(A[c].isna().sum()),nonmissing=int(A[c].notna().sum()),unique=int(A[c].nunique()),definition={'promotion':'Any grade increase, mayor to city secretary, or new provincial vice-governor appointment even at the same vice-ministerial rank','rank_promotion':'Administrative rank increase only','promotion_previous':'Previous outcome definition before this revision','role_secretary':'1 city secretary; 0 mayor; included in pooled-role models','same_grade_vice_governor_event':'New vice-governor appointment with baseline rank vice-ministerial'}.get(c,'')))
save(pd.DataFrame(profile),'variable_codebook.csv')
summary=dict(annual_rows=len(A),annual_people=int(A.person_id.nunique()),annual_known=int(A.promotion.notna().sum()),annual_promotions=int(A.promotion.sum()),annual_changes=sum(c['unit']=='annual' for c in changes),term_rows=len(T),term_changes=sum(c['unit']=='term' for c in changes),data_checks=len(checks),all_checks_passed=all(c['passed'] for c in checks))
(OUT/'preparation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name)
shutil.copy2(HERE/'prepare.py',OUT/'code/prepare.py')
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
print(desc.to_string(index=False),flush=True)
