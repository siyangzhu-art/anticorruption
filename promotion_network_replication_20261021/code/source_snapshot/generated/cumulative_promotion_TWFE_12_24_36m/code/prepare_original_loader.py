"""CPED-only promotion outcomes and predetermined city--province ties.
Wang--Yang labels validate outcomes, never overwrite CPED outcomes.
"""
from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np,json,zipfile,io,re,hashlib,shutil
from functools import lru_cache

ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
NET=ROOT/'result/cped_pre_anticorruption_person_network_20261019'
OLD=ROOT/'result/cped_city_province_connections_20261019'
OUT=ROOT/'result/promotion_connections_rolling_2026_10_20';OUT.mkdir(exist_ok=True)
ZIP=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')
JPE=ROOT/'data/raw/policy_implementation_search_20261019/JPE_policy_experimentation'
RANK={'小于副处':0,'副处':1,'正处':2,'副厅':3,'正厅':4,'副部':5,'正部':6,'副国':7,'正国':8}
REL=['cowork_6m','hometown_prefecture','classmate_6m','connected']
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
def say(*a):print(*a,flush=True)
def iso(x):return pd.Timestamp(x).strftime('%Y-%m-%d') if pd.notna(x) else ''
def clean(x):return '' if pd.isna(x) else re.sub(r'\s+','',str(x)).replace('（','(').replace('）',')')
def corepos(x):return re.sub(r'\([^)]*\)','',clean(x))
def canon(a,b):return tuple(sorted([int(a),int(b)]))
with zipfile.ZipFile(ZIP) as z:
 raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
 bio=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all')
raw['row_id']=np.arange(2,len(raw)+2);raw['person_id']=raw['用户编码'].astype(int)
raw['start']=pd.to_datetime(raw['起始时间（YYYY-MM-DD）'],errors='coerce');raw['end']=pd.to_datetime(raw['终止时间（（YYYY-MM-DD））'],errors='coerce')
raw['rank']=raw['级别'].map(RANK);raw['pos_core']=raw['具体职务'].map(corepos)
raw['valid_interval']=raw.start.notna()&raw.end.notna()&raw.start.lt(raw.end)
raw['generic_membership']=raw.pos_core.isin(['委员','候补委员','常委','常务委员','常委会委员','代表','人大代表','政协委员'])&~raw['标志位'].isin(['省常委(其他)','市委副书记(专职)','市委书记','省委书记','省长','市长'])
raw['terminal']=raw.pos_core.str.contains(r'^(退休|离休|被免职|被撤职|被查处|接受调查|免职|撤职|开除|去世|逝世|因.*(免职|撤职))',regex=True)
eligible_work=pd.read_csv(OLD/'workplace_classification.csv.gz',usecols=['row_id','work_eligible']);eligible_rows=set(eligible_work.loc[eligible_work.work_eligible,'row_id'])
raw['substantive']=raw.row_id.isin(eligible_rows)&raw.pos_core.ne('')&~raw.generic_membership&~raw.terminal&~raw.pos_core.str.contains('待分配|待安排|待业|失业')
raw['second_line']=raw['基本大类别'].isin(['人大','政协'])
BY={int(k):g.sort_values(['start','end']).copy() for k,g in raw.groupby('person_id')}
B=bio.rename(columns={'Unnamed: 0':'person_id'}).set_index('person_id');B['birth']=pd.to_datetime(B['出生日期(YYYY-MM-DD)'],errors='coerce')
R=pd.read_csv(OLD/'leadership_roles_all.csv',keep_default_na=False,low_memory=False)
for c in ['start','end']:R[c]=pd.to_datetime(R[c],errors='coerce')
R=R.merge(raw[['row_id','rank']],on='row_id',validate='1:1')
C=R[R.roster_issue.eq('')&R.side.eq('city')&R.scope.eq('prefecture')&R.flag.isin(['市长','市委书记'])].copy()
P=R[R.roster_issue.eq('')&R.side.eq('province')&R.flag.isin(['省委书记','省长'])].copy()
SROWS=set(C.loc[C.flag.eq('市委书记'),'row_id'])

def merge_spells(frame,rolemap,side):
 rows=[]
 for (pid,pc,cc,flag),g in frame.groupby(['person_id','province_code','city_code','flag'],dropna=False):
  cur=None
  for r in g.sort_values(['start','end']).to_dict('records'):
   if cur is not None and r['start']<=cur['end']:
    cur['end']=max(cur['end'],r['end']);cur['source_rows'].append(int(r['row_id']))
   else:
    if cur:rows.append(cur)
    cur=dict(person_id=int(pid),name=r['name'],province_code=int(float(pc)),province=r['province'],city_code=int(float(cc)) if cc!='' else 0,city=r['city'],role=rolemap[flag],start=r['start'],end=r['end'],source_rows=[int(r['row_id'])],side=side)
  if cur:rows.append(cur)
 d=pd.DataFrame(rows).sort_values(['person_id','start','end','role']).reset_index(drop=True);d['spell_id']=[side+str(i+1) for i in range(len(d))]
 return d
CS=merge_spells(C,{'市长':'mayor','市委书记':'secretary'},'city');PS=merge_spells(P,{'省委书记':'S','省长':'G'},'province')
for d,f in [(CS,'city_principal_spells.csv'),(PS,'province_principal_spells.csv')]:save(d.assign(source_rows=d.source_rows.map(lambda v:'|'.join(map(str,v)))),f)

# Edge tables: the full 4,603-person frozen graph includes provincial leaders.
E=pd.read_csv(NET/'person_edges_pre2012.csv.gz');edges={canon(r.person_a,r.person_b):r for r in E.itertuples()}
N=pd.read_csv(NET/'person_nodes_pre2012.csv').set_index('person_id')
J=pd.read_csv(OLD/'workplace_classification.csv.gz',low_memory=False);ED=pd.read_csv(OLD/'education_classification.csv',low_memory=False)
ED0=pd.read_csv(NET/'school_eligibility_pre2012.csv.gz',low_memory=False)
for d in [J,ED,ED0]:
 for c in ['start','end']:d[c]=pd.to_datetime(d[c],errors='coerce')
F=pd.read_csv(OLD/'pair_first_connection_dates.csv');F['first_formed']=pd.to_datetime(F.first_formed,errors='coerce')
FF={}
for r in F[F.relation.isin(REL[:3])].itertuples():FF[(canon(r.city_id,r.province_id),r.relation)]=r.first_formed
amb={}
for timing in ['legacy','preassignment']:
 if timing=='legacy':
  a=pd.read_csv(NET/'date_ambiguous_pairs_pre2012.csv.gz');amb[timing]={t:{canon(x.person_a,x.person_b) for x in a[a.relation.eq(t)].itertuples()} for t in REL[:3]}
 else:
  # Pairs with same-unit/date ambiguity from existing provincial-dyad classifications.
  amb[timing]={t:set() for t in REL[:3]}
  for frame,keycol,typ in [(J[J.work_eligible],'workplace_key','cowork_6m'),(ED[ED.ordinary_student_eligible],'school_key','classmate_6m')]:
   for _,g in frame.groupby(keycol):
    if not (~g.dates_valid).any():continue
    ids=g.person_id.to_numpy();bad=~g.dates_valid.to_numpy()
    for i in range(len(g)):
     for j in range(i+1,len(g)):
      if ids[i]!=ids[j] and (bad[i] or bad[j]):amb[timing][typ].add(canon(ids[i],ids[j]))
qual={}
for timing in ['legacy','preassignment']:
 for frame,typ in [(J[J.work_eligible],'cowork_6m'),(ED0[ED0.ordinary_student_broad & ~ED0.concurrent_employment_before_cutoff] if timing=='legacy' else ED[ED.ordinary_student_eligible],'classmate_6m')]:
  q=frame[frame.dates_valid].copy();q['threshold']=q.start+pd.DateOffset(months=6);q=q[q.threshold.le(q.end)]
  qual[(timing,typ)]=q.groupby('person_id').threshold.min().to_dict()

@lru_cache(maxsize=None)
def ties(a,b,joint,timing):
 key=canon(a,b);cut=min(joint,pd.Timestamp('2012-01-01')) if timing=='legacy' else joint;edge=edges.get(key);ans={}
 for t in REL[:3]:
  if t=='hometown_prefecture':
   cols=['籍贯省','籍贯市'];bad={'','不详','未知','无','其他','不明','不详市','不详县'}
   aa=[clean(B.loc[a,c]) for c in cols];bb=[clean(B.loc[b,c]) for c in cols]
   ok=all(v not in bad for v in aa+bb);ans[t]=int(aa==bb) if ok else np.nan
   continue
  dt=(pd.Timestamp(getattr(edge,t+'_first_formation')) if edge is not None and getattr(edge,t)==1 else pd.NaT) if timing=='legacy' else FF.get((key,t),pd.NaT)
  yes=pd.notna(dt) and dt<cut
  comparable=all(qual[(timing,t)].get(x,pd.Timestamp.max)<cut for x in [a,b]) and key not in amb[timing][t]
  ans[t]=1. if yes else (0. if comparable else np.nan)
 vals=list(ans.values());ans['connected']=1. if 1 in vals else (0. if all(v==0 for v in vals) else np.nan)
 return ans

active_cache={}
def active_unique(spells,dt,key):
 cachekey=(id(spells),pd.Timestamp(dt),tuple(key))
 if cachekey in active_cache:return active_cache[cachekey]
 q=spells[spells.start.le(dt)&spells.end.gt(dt)].copy();bad=[]
 count=q.groupby(key).person_id.transform('nunique')
 for _,g in q[count.gt(1)].groupby(key):bad.append(dict(snapshot=iso(dt),key='|'.join(map(str,g.iloc[0][key])),person_ids='|'.join(map(str,sorted(g.person_id.unique())))))
 good=q[count.eq(1)].sort_values('start').drop_duplicates(key,keep='last')
 result=good,bad
 active_cache[cachekey]=result
 return result

def baseline_rank(pid,dt,source_rows):
 q=BY[pid];q=q[q.substantive&q.valid_interval&q.start.le(dt)&q.end.gt(dt)]
 values=q['rank'].dropna().unique()
 return (float(max(values)) if len(values) else np.nan),('conflicting_rank_records' if len(values)>1 else '')

def classify(pid,dt,end,base_rank,role,city,exit_mode=False):
 q=BY[pid];new=q[q.start.gt(dt)&q.start.le(end)&q.substantive&(q.end.isna()|q.end.gt(q.start))].copy()
 rankrise=new['rank'].gt(base_rank) if pd.notna(base_rank) else pd.Series(False,index=new.index)
 roleup=new.row_id.isin(SROWS) if role=='mayor' else pd.Series(False,index=new.index)
 # A missing/invalid end does not erase a documented new appointment start.
 ev=new[rankrise|roleup].copy()
 if len(ev):
  first=ev.sort_values(['start','rank'],ascending=[True,False]).iloc[0]
  r=int(bool(rankrise.loc[ev.index].any()));b=int(bool(roleup.loc[ev.index].any()) or r)
  return dict(promotion=b,rank_promotion=r if pd.notna(base_rank) else np.nan,status='observed_promotion',event_date=iso(first.start),event_row=int(first.row_id),event_job=first['具体职务'],event_rank=first['级别'],second_line=int(bool(ev.second_line.any())),followup='documented_new_appointment')
 # Explicit dated removal is an observed competing outcome, never a future-state inference.
 terminal=q[q.start.gt(dt)&q.start.le(end)&q.terminal]
 basic=B.loc[pid];removed=pd.to_datetime(basic.get('查处/罢黜时间'),errors='coerce')
 if (pd.notna(removed) and dt<removed<=end) or len(terminal):
  er=terminal.sort_values('start').iloc[0] if len(terminal) else None
  return dict(promotion=0.,rank_promotion=0. if pd.notna(base_rank) else np.nan,status='observed_terminal_or_removal',event_date=iso(removed if er is None else er.start),event_row=np.nan if er is None else int(er.row_id),event_job='dated_removal' if er is None else er['具体职务'],event_rank='',second_line=0,followup='dated_competing_exit')
 # Verify full annual observation by union of substantive dated career intervals.
 cov=q[q.valid_interval & q.substantive & q.end.gt(dt)&q.start.le(end)].sort_values('start')
 covered=dt;gap=False
 for rr in cov.itertuples():
  if rr.start>covered:gap=True;break
  covered=max(covered,rr.end)
  if covered>end:break
 known=(not gap) and covered>end and pd.notna(base_rank) and not new['rank'].isna().any()
 return dict(promotion=0. if known else np.nan,rank_promotion=(0. if known and pd.notna(base_rank) else np.nan),status='observed_no_promotion' if known else 'censored_or_career_gap',event_date='',event_row=np.nan,event_job='',event_rank='',second_line=0,followup='covered_through_year_end' if known else 'incomplete_followup')

def add_connections(row,person,cityspell,provroster):
 for leader in ['S','G']:
  q=provroster[(provroster.province_code==cityspell['province_code'])&(provroster.role==leader)]
  row[leader+'_person_id']=int(q.iloc[0].person_id) if len(q)==1 else np.nan
  row[leader+'_name']=q.iloc[0]['name'] if len(q)==1 else ''
  for timing in ['legacy','preassignment']:
   vals=ties(person,int(q.iloc[0].person_id),max(cityspell['start'],q.iloc[0].start),timing) if len(q)==1 and int(q.iloc[0].person_id)!=person else {t:np.nan for t in REL}
   for t,v in vals.items():row[timing+'_'+t+'_'+leader]=v
   row['joint_start_'+leader]=iso(max(cityspell['start'],q.iloc[0].start)) if len(q)==1 else ''
 return row

annual=[];ambiguities=[]
for year in range(2000,2018):
 # Last instant of the prior calendar year: do not condition on a Jan-1 promotion.
 dt=pd.Timestamp(year,1,1)-pd.Timedelta(days=1);end=pd.Timestamp(year,12,31)
 a,bad=active_unique(CS,dt,['province_code','city_code','role']);pr,pbad=active_unique(PS,dt,['province_code','role']);ambiguities+=bad+pbad
 badpid=set(a.groupby('person_id').city_code.nunique().loc[lambda x:x>1].index)
 a=a[~a.person_id.isin(badpid)].copy();a['priority']=a.role.map({'mayor':0,'secretary':1});a=a.sort_values('priority').drop_duplicates('person_id',keep='last')
 for s in a.to_dict('records'):
  pid=s['person_id'];rank,issue=baseline_rank(pid,dt,s['source_rows']);dob=B.loc[pid,'birth'];age=(dt-dob).days/365.2425 if pd.notna(dob) else np.nan
  row=dict(year=year,baseline_date=iso(dt),person_id=pid,name=s['name'],role=s['role'],city_code=s['city_code'],city=s['city'],province_code=s['province_code'],province=s['province'],city_spell_id=s['spell_id'],city_spell_start=iso(s['start']),city_spell_end=iso(s['end']),base_rank=rank,rank_issue=issue,age=age,age2=age**2,tenure=(dt-s['start']).days/365.2425)
  row['tenure2']=row['tenure']**2;row.update(classify(pid,dt,end,rank,s['role'],s['city_code']));row=add_connections(row,pid,s,pr);annual.append(row)
 say('Annual year',year,'rows',len(a))
A=pd.DataFrame(annual);save(pd.DataFrame(ambiguities),'ambiguous_baseline_assignments.csv')

# One record per completed city-role spell; last pre-exit leadership and connection exposure.
terms=[]
for s in CS[CS.end.ge('2000-01-01')&CS.end.lt('2018-01-01')].to_dict('records'):
 dt=s['end']-pd.Timedelta(days=1);pid=s['person_id'];year=s['end'].year
 # Do not retain mayor spells concurrently held by a secretary on this date.
 if s['role']=='mayor' and len(CS[(CS.person_id==pid)&CS.role.eq('secretary')&CS.start.le(dt)&CS.end.gt(dt)]):continue
 act,bad=active_unique(CS,dt,['province_code','city_code','role'])
 if not ((act.person_id==pid)&(act.city_code==s['city_code'])&(act.role==s['role'])).any():continue
 pr,_=active_unique(PS,dt,['province_code','role']);rank,issue=baseline_rank(pid,dt,s['source_rows'])
 q=BY[pid];nextq=q[q.start.ge(s['end'])&q.start.le(s['end']+pd.DateOffset(months=12))&(q.substantive|q.terminal)].copy()
 # A continuing record of exactly the same office was already merged, so select the first distinct substantive destination.
 if len(nextq):
  nd=nextq.start.min();n=nextq[nextq.start.eq(nd)].copy();valid=n.substantive
  rankup=bool(n.loc[valid,'rank'].gt(rank).any()) if pd.notna(rank) else False
  roleup=bool(n.loc[valid,'row_id'].isin(SROWS).any()) if s['role']=='mayor' else False
  rr=n.sort_values('rank',ascending=False).iloc[0]
  y=float(rankup or roleup);yr=float(rankup) if pd.notna(rank) else np.nan
  if not n.terminal.any() and not n.loc[valid,'rank'].notna().any() and not roleup:y=np.nan;yr=np.nan
  status='known_next_post' if pd.notna(y) else 'next_post_rank_unknown'
  dest=dict(event_date=iso(nd),event_row=int(rr.row_id),event_job=rr['具体职务'],event_rank=rr['级别'],second_line=int(bool(n.second_line.any())))
 else:
  y=yr=np.nan;status='no_observed_next_post_or_right_censored';dest=dict(event_date='',event_row=np.nan,event_job='',event_rank='',second_line=0)
 dob=B.loc[pid,'birth'];age=(dt-dob).days/365.2425 if pd.notna(dob) else np.nan
 row=dict(year=year,baseline_date=iso(dt),person_id=pid,name=s['name'],role=s['role'],city_code=s['city_code'],city=s['city'],province_code=s['province_code'],province=s['province'],city_spell_id=s['spell_id'],city_spell_start=iso(s['start']),city_spell_end=iso(s['end']),base_rank=rank,rank_issue=issue,age=age,age2=age**2,tenure=(dt-s['start']).days/365.2425,promotion=y,rank_promotion=yr,status=status,**dest)
 row['tenure2']=row['tenure']**2;row=add_connections(row,pid,s,pr);terms.append(row)
T=pd.DataFrame(terms)

# Existing city-yearbook controls, exact prior calendar year only.
city=pd.read_csv(ROOT/'result/city_outcomes_province_Local_2026_10_19/analysis_panel.csv.gz',usecols=['citycode','year','old_population_wan','old_gdp_per_capita_yuan','old_gdp_growth_pct','first_inspection_year']).sort_values(['citycode','year'])
city['population']=city.old_population_wan.where(city.old_population_wan>0);city['gdppc']=city.old_gdp_per_capita_yuan.where(city.old_gdp_per_capita_yuan>0)
city['gdp_growth_lag']=city.old_gdp_growth_pct;city['lngdppc_lag']=np.log(city.gdppc);city['lnpop_lag']=np.log(city.population)
city['city_code']=city.citycode.astype(int)*100;city.year+=1
controls=city[['city_code','year','gdp_growth_lag','lngdppc_lag','lnpop_lag']]
calendar= pd.read_csv(ROOT/'result/inspection_hometown_design_2026_10_16/first_provincial_inspection_years_with_official_province_codes.csv')
calendar['province_code']=calendar.province_code.astype(int)*10000
assert calendar.province_code.is_unique and len(calendar)==31
imap=calendar.set_index('province_code').first_inspection_year.to_dict();save(calendar,'inspection_timing.csv')
for d,name in [(A,'annual_official_panel.csv.gz'),(T,'term_destination_panel.csv.gz')]:
 d=d.merge(controls,on=['city_code','year'],how='left',validate='m:1');d['first_inspection_year']=d.province_code.map(imap);d['k']=d.year-d.first_inspection_year;d['provyear']=d.province_code*10000+d.year
 save(d,name)
 if name.startswith('annual'):A=d
 else:T=d
save(A[['person_id','name','year','role','base_rank','promotion','rank_promotion','status','followup','event_date','event_row','event_job','event_rank','second_line','city_spell_id']],'annual_promotion_event_registry.csv')
save(raw[raw.generic_membership|raw.terminal|~raw.valid_interval][['row_id','person_id','姓名','start','end','具体职务','级别','generic_membership','terminal','valid_interval']],'source_membership_terminal_date_review.csv.gz')

# Wang--Yang: pos 1=secretary, 2=mayor; author code promote=1 iff promotion>2.
with zipfile.ZipFile(JPE/'data.zip') as z:W=pd.read_excel(io.BytesIO(z.read('data/Pref_Secretary&Mayor_final.xlsx')))
W['wy_id']=np.arange(1,len(W)+1);W['role']=W.pos.map({1:'secretary',2:'mayor'});W['clean_name']=W.name.map(clean);W['wy_promote']=np.where(W.promotion.notna(),W.promotion.gt(2).astype(float),np.nan)
CS['clean_name']=CS.name.map(clean)
wy_candidates={k:g for k,g in CS.groupby(['clean_name','role','city_code'])}
matches=[]
for w in W.to_dict('records'):
 candidates=wy_candidates.get((w['clean_name'],w['role'],w['prefecture']),CS.iloc[:0]).copy()
 on=pd.to_numeric(w['on_yr'],errors='coerce');off=pd.to_numeric(w['off_yr'],errors='coerce')
 if pd.notna(on):candidates=candidates[candidates.start.dt.year.between(int(on)-1,int(on)+1)]
 if pd.notna(off):candidates=candidates[candidates.end.dt.year.between(int(off)-1,int(off)+1)]
 state='unique_exact_name_city_role_tenure_match' if len(candidates)==1 else ('no_match' if len(candidates)==0 else 'multiple_matches')
 row={k:w[k] for k in ['wy_id','name','prefname','prefecture','role','promotion','wy_promote','on_yr','off_yr','nextins','nextpos']};row.update(match_status=state,candidates=len(candidates))
 if len(candidates)==1:
  s=candidates.iloc[0];row.update(person_id=int(s.person_id),city_spell_id=s.spell_id,cped_start=iso(s.start),cped_end=iso(s.end))
 matches.append(row)
M=pd.DataFrame(matches);M=M.merge(T[['city_spell_id','promotion','rank_promotion','status','event_date','event_job','second_line']],on='city_spell_id',how='left',suffixes=('_wy_raw','_cped'),validate='m:1')
M['both_known']=M.wy_promote.notna()&M.promotion_cped.notna();M['agreement']=np.where(M.both_known,M.wy_promote.eq(M.promotion_cped).astype(float),np.nan)
save(M,'wang_yang_cross_validation.csv');save(M[M.both_known & M.agreement.eq(0)],'wang_yang_disagreements.csv')
save(A.groupby(['year','role','status'],dropna=False).size().reset_index(name='rows'),'annual_outcome_support.csv')
save(T.groupby(['year','role','status'],dropna=False).size().reset_index(name='rows'),'term_outcome_support.csv')
save(pd.DataFrame([dict(variable=c,dtype=str(A[c].dtype),missing=int(A[c].isna().sum()),nonmissing=int(A[c].notna().sum()),unique=int(A[c].nunique())) for c in A]),'panel_variable_profile.csv')
assert not A.duplicated(['person_id','year']).any();assert T.city_spell_id.is_unique
assert A.promotion.dropna().isin([0,1]).all() and A.rank_promotion.dropna().isin([0,1]).all()
for timing in ['legacy','preassignment']:
 for leader in ['S','G']:
  for rel in REL:assert A[timing+'_'+rel+'_'+leader].dropna().isin([0,1]).all()
summary={'annual_rows':len(A),'annual_known_promotion':int(A.promotion.notna().sum()),'annual_promotions':int(A.promotion.eq(1).sum()),'annual_known_rank':int(A.rank_promotion.notna().sum()),'annual_rank_promotions':int(A.rank_promotion.eq(1).sum()),'term_rows':len(T),'term_known_promotion':int(T.promotion.notna().sum()),'term_promotions':int(T.promotion.eq(1).sum()),'wy_match_status':M.match_status.value_counts().to_dict(),'wy_both_known':int(M.both_known.sum()),'wy_agree':int(M.agreement.eq(1).sum()),'wy_disagree':int(M.agreement.eq(0).sum()),'ambiguities':len(ambiguities),'baseline':'December 31 prior year, predict following calendar year','data_source_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),'no_existing_network_files_modified':True,'rank_order':RANK,'GDP_growth_note':'Exact prior-year old_gdp_growth_pct from existing city-yearbook panel; no proxy or gap filling'}
(OUT/'preparation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
code=OUT/'code';code.mkdir(exist_ok=True);shutil.copy2(__file__,code/'prepare.py')
say(json.dumps(summary,ensure_ascii=False,indent=2))
