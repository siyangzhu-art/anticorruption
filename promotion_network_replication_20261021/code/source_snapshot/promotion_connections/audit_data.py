from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np,json,zipfile,io,ast,hashlib,shutil,re
ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized');OUT=ROOT/'result/promotion_connections_rolling_2026_10_20';OLD=ROOT/'result/cped_city_province_connections_20261019'
RANK={'小于副处':0,'副处':1,'正处':2,'副厅':3,'正厅':4,'副部':5,'正部':6,'副国':7,'正国':8}
checks=[];corrections=[]
if (OUT/'scope_corrections_before_estimation.csv').exists():
 previous=pd.read_csv(OUT/'scope_corrections_before_estimation.csv');corrections=previous.to_dict('records')
def iso(x):return pd.Timestamp(x).strftime('%Y-%m-%d') if pd.notna(x) else ''
def corepos(x):return re.sub(r'\([^)]*\)','',re.sub(r'\s+','',str(x)).replace('（','(').replace('）',')')) if pd.notna(x) else ''
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
def check(n,ok,detail):
 checks.append(dict(check=n,passed=bool(ok),detail=str(detail)))
 if not ok:print('FAIL',n,detail,flush=True)
with zipfile.ZipFile(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip') as z:
 raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all');bio=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='基本信息').dropna(how='all')
raw['row_id']=np.arange(2,len(raw)+2);raw['person_id']=raw['用户编码'].astype(int);raw['start']=pd.to_datetime(raw['起始时间（YYYY-MM-DD）'],errors='coerce');raw['end']=pd.to_datetime(raw['终止时间（（YYYY-MM-DD））'],errors='coerce');raw['rank']=raw['级别'].map(RANK);raw['pos_core']=raw['具体职务'].map(corepos)
raw['valid_interval']=raw.start.notna()&raw.end.notna()&raw.start.lt(raw.end);raw['generic_membership']=raw.pos_core.isin(['委员','候补委员','常委','常务委员','常委会委员','代表','人大代表','政协委员'])&~raw['标志位'].isin(['省常委(其他)','市委副书记(专职)','市委书记','省委书记','省长','市长'])
raw['terminal']=raw.pos_core.str.contains(r'^(?:退休|离休|被免职|被撤职|被查处|接受调查|免职|撤职|开除|去世|逝世|因.*(?:免职|撤职))',regex=True)
J=pd.read_csv(OLD/'workplace_classification.csv.gz',usecols=['row_id','work_eligible']);eligible=set(J.loc[J.work_eligible,'row_id'])
raw['substantive']=raw.row_id.isin(eligible)&raw.pos_core.ne('')&~raw.generic_membership&~raw.terminal&~raw.pos_core.str.contains('待分配|待安排|待业|失业');raw['second_line']=raw['基本大类别'].isin(['人大','政协'])
BY={int(k):g.sort_values(['start','end']).copy() for k,g in raw.groupby('person_id')};B=bio.rename(columns={'Unnamed: 0':'person_id'}).set_index('person_id')
roles=pd.read_csv(OLD/'leadership_roles_all.csv',keep_default_na=False);SROWS=set(roles[(roles.roster_issue=='')&(roles.scope=='prefecture')&(roles.flag=='市委书记')].row_id)
source=Path(__file__).with_name('prepare.py').read_text(encoding='utf8');tree=ast.parse(source);node=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='classify'][0];exec(compile(ast.Module(body=[node],type_ignores=[]),'audited_classify','exec'),globals())
A=pd.read_csv(OUT/'annual_official_panel.csv.gz',low_memory=False);T=pd.read_csv(OUT/'term_destination_panel.csv.gz',low_memory=False)
calendar=pd.read_csv(ROOT/'result/inspection_hometown_design_2026_10_16/first_provincial_inspection_years_with_official_province_codes.csv')
calendar['province_code']=calendar.province_code.astype(int)*10000;assert len(calendar)==31 and calendar.province_code.is_unique
imap=calendar.set_index('province_code').first_inspection_year.to_dict()
if not (OUT/'inspection_timing_original_city_panel.csv').exists():shutil.copy2(OUT/'inspection_timing.csv',OUT/'inspection_timing_original_city_panel.csv')
save(calendar,'inspection_timing.csv')
for d in [A,T]:d['first_inspection_year']=d.province_code.map(imap);d['k']=d.year-d.first_inspection_year
check('Direct verified 31-province inspection calendar covers annual and term panels',A.first_inspection_year.notna().all() and T.first_inspection_year.notna().all(),len(calendar))
# Resolve source flag/administrative-scope contradictions before any estimation.
for i,r in A[(A.role=='mayor')&(A.promotion==1)&(A.rank_promotion==0)].iterrows():
 if pd.notna(r.event_row) and int(r.event_row) not in SROWS:
  val=classify(int(r.person_id),pd.Timestamp(r.baseline_date),pd.Timestamp(int(r.year),12,31),r.base_rank,r.role,r.city_code)
  for key,value in val.items():A.at[i,key]=value
  corrections.append(dict(unit='annual',person_id=r.person_id,name=r['name'],year=r.year,source_row=r.event_row,old_y=r.promotion,new_y=val['promotion'],reason='source city-secretary flag conflicts with county/district scope; require valid prefectural secretary role'))
for i,r in T[(T.role=='mayor')&(T.promotion==1)&(T.rank_promotion==0)].iterrows():
 if pd.notna(r.event_row) and int(r.event_row) not in SROWS:
  q=raw[raw.row_id.eq(int(r.event_row))]
  if len(q) and q['标志位'].iloc[0]=='市委书记':
   T.at[i,'promotion']=0. if pd.notna(r.base_rank) and q['rank'].notna().any() else np.nan
   corrections.append(dict(unit='term',person_id=r.person_id,name=r['name'],year=r.year,source_row=r.event_row,old_y=r.promotion,new_y=T.at[i,'promotion'],reason='county/district secretary is not promotion to prefectural party secretary'))
save(pd.DataFrame(corrections,columns=['unit','person_id','name','year','source_row','old_y','new_y','reason']),'scope_corrections_before_estimation.csv')
save(A,'annual_official_panel.csv.gz');save(T,'term_destination_panel.csv.gz')
save(A[['person_id','name','year','role','base_rank','promotion','rank_promotion','status','followup','event_date','event_row','event_job','event_rank','second_line','city_spell_id']],'annual_promotion_event_registry.csv')
check('Annual person-year unique',not A.duplicated(['person_id','year']).any(),len(A));check('Term spell unique',T.city_spell_id.is_unique,len(T))
check('Annual exact years 2000-2017',A.year.between(2000,2017).all(),sorted(A.year.unique()))
check('Annual positive has dated original source evidence',A.loc[A.promotion.eq(1),'event_row'].notna().all(),int(A.promotion.eq(1).sum()))
check('No unknown/censored annual outcome filled zero',A.loc[A.status.eq('censored_or_career_gap'),'promotion'].isna().all(),int(A.status.eq('censored_or_career_gap').sum()))
rank_events=[];violations=[]
rr=raw.set_index('row_id')
for r in A.itertuples():
 if r.promotion==1:
  x=rr.loc[int(r.event_row)]
  ok=int(x.person_id)==r.person_id and pd.Timestamp(r.baseline_date)<x.start<=pd.Timestamp(r.year,12,31) and x.substantive and (x['rank']>r.base_rank or (r.role=='mayor' and int(r.event_row) in SROWS))
  if not ok:violations.append((r.person_id,r.year,'positive source evidence invalid'))
 if r.rank_promotion==1:
  q=BY[r.person_id];q=q[q.substantive&q.start.gt(pd.Timestamp(r.baseline_date))&q.start.le(pd.Timestamp(r.year,12,31))&q['rank'].gt(r.base_rank)&(q.end.isna()|q.end.gt(q.start))].sort_values('start')
  if not len(q):violations.append((r.person_id,r.year,'rank positive without higher-rank appointment'))
  else:
   x=q.iloc[0];rank_events.append(dict(person_id=r.person_id,name=r.name,year=r.year,baseline_rank=r.base_rank,event_row=int(x.row_id),event_date=iso(x.start),new_rank=x['级别'],new_job=x['具体职务']))
check('All positive broad/rank events independently supported by original rows',not violations,violations[:10]);save(pd.DataFrame(rank_events),'rank_promotion_event_registry.csv')
for unit,d in [('annual',A),('term',T)]:
 for timing in ['legacy','preassignment']:
  for lead in ['S','G']:
   for rel in ['cowork_6m','classmate_6m','hometown_prefecture','connected']:
    check(unit+' binary/unknown '+timing+' '+lead+' '+rel,d[timing+'_'+rel+'_'+lead].dropna().isin([0,1]).all(),len(d))
 # Main frozen cowork edges must be supported by full-network evidence and predate both assignment and 2012.
 edges=pd.read_csv(ROOT/'result/cped_pre_anticorruption_person_network_20261019/person_edges_pre2012.csv.gz');lookup={(int(r.person_a),int(r.person_b)):r for r in edges.itertuples()};bad=[]
 for lead in ['S','G']:
  for r in d[d['legacy_cowork_6m_'+lead].eq(1)].itertuples():
   p=int(getattr(r,lead+'_person_id'));key=tuple(sorted([r.person_id,p]));e=lookup.get(key);dt=pd.Timestamp(e.cowork_6m_first_formation) if e is not None else pd.NaT
   if e is None or e.cowork_6m!=1 or not dt<min(pd.Timestamp('2012-01-01'),pd.Timestamp(getattr(r,'joint_start_'+lead))):bad.append((r.person_id,r.year,lead))
 check(unit+' frozen cowork ties predate assignment and cutoff',not bad,len(bad))
 # Future provincial leaders can be present; do not require either person to hold office in 2011.
 no_self=True
 for lead in ['S','G']:
  selfrows=d[d[lead+'_person_id'].eq(d.person_id)]
  cols=[timing+'_'+rel+'_'+lead for timing in ['legacy','preassignment'] for rel in ['cowork_6m','classmate_6m','hometown_prefecture','connected']]
  no_self=no_self and selfrows[cols].isna().all().all()
 check(unit+' no self-connections when one person holds provincial and city offices',no_self,len(d))
M=pd.read_csv(OUT/'wang_yang_cross_validation.csv',low_memory=False);M=M.drop(columns=['promotion_cped','rank_promotion','status','event_date','event_job','second_line','both_known','agreement'],errors='ignore').merge(T[['city_spell_id','promotion','rank_promotion','status','event_date','event_job','second_line']],on='city_spell_id',how='left',validate='m:1').rename(columns={'promotion':'promotion_cped'})
M['both_known']=M.wy_promote.notna()&M.promotion_cped.notna();M['agreement']=np.where(M.both_known,M.wy_promote.eq(M.promotion_cped).astype(float),np.nan)
save(M,'wang_yang_cross_validation.csv');save(M[M.both_known&M.agreement.eq(0)],'wang_yang_disagreements.csv')
check('WY author promotion mapping 3/4, not code 1',M.loc[M.wy_promote.notna(),'wy_promote'].eq(M.loc[M.wy_promote.notna(),'promotion_wy_raw'].gt(2)).all(),M.wy_promote.notna().sum())
save(pd.DataFrame(checks),'data_validation_checks.csv')
summary=json.loads((OUT/'preparation_summary.json').read_text(encoding='utf8'));summary.update(annual_known_promotion=int(A.promotion.notna().sum()),annual_promotions=int(A.promotion.eq(1).sum()),annual_rank_promotions=int(A.rank_promotion.eq(1).sum()),term_promotions=int(T.promotion.eq(1).sum()),scope_corrections=len(corrections),wy_both_known=int(M.both_known.sum()),wy_agree=int(M.agreement.eq(1).sum()),wy_disagree=int(M.agreement.eq(0).sum()),data_checks=len(checks),data_failed_checks=sum(not x['passed'] for x in checks))
(OUT/'preparation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
shutil.copy2(Path(__file__).with_name('prepare.py'),OUT/'code/prepare.py');shutil.copy2(__file__,OUT/'code/audit_data.py')
assert all(x['passed'] for x in checks)
