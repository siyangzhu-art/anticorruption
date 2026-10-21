"""Same officials, fixed ties, equal-length pre/post cumulative promotion TWFE."""
from pathlib import Path
import sys,hashlib,shutil,json
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
BASE=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20';OUT=BASE/'cumulative_promotion_TWFE_12_24_36m'
for p in [OUT,OUT/'code',OUT/'data',OUT/'figures']:p.mkdir(exist_ok=True)
def save(d,n):d.to_csv(OUT/n,index=False,encoding='utf-8-sig')
# These are reported inspection START dates, not news publication or feedback dates.
date_rows=[
('内蒙古','2013-06-03','https://www.ccdi.gov.cn/special/zyxszt/2013dyl_zyxs/xsjz_dyl_zyxs/'),
('江西','2013-05-27','https://m.ccdi.gov.cn/content/13/f6/5178.html'),
('湖北','2013-06-02','https://www.ccdi.gov.cn/special/zyxszt/2013dyl_zyxs/xsjz_dyl_zyxs/'),
('重庆','2013-05-29','https://www.ccdi.gov.cn/toutiaon/201402/t20140221_90373.html'),
('贵州','2013-05-29','https://politics.people.com.cn/n/2013/0927/c1001-23057615.html'),
('山西','2013-10-30','https://www.gov.cn/xinwen/2014-06/07/content_2696041.htm'),
('吉林','2013-10-30','https://politics.people.com.cn/n/2014/0609/c1001-25119553.html'),
('安徽','2013-10-31','https://politics.people.com.cn/n/2014/0609/c1001-25121485.html'),
('湖南','2013-11-01','https://www.sxfj.gov.cn/xun_shi_xun_cha/10942563.shtml'),
('广东','2013-10-29','https://qzlx.people.com.cn/n/2014/0606/c364565-25112498.html'),
('云南','2013-10-30','https://www.ccdi.gov.cn/special/zyxszt/2013del_zyxs/zgls_del_zyxs/201407/t20140715_25187.html'),
('北京','2014-03-31','https://fanfu.people.com.cn/n/2014/1126/c64371-26096467.html'),
('天津','2014-03-28','https://m.ahjjjc.gov.cn/android/p/44024.html'),
('辽宁','2014-03-30','https://news.sina.com.cn/c/2014-07-07/180830482288.shtml'),
('福建','2014-03-27','https://news.12371.cn/2014/10/10/ARTI1412934167046733.shtml'),
('山东','2014-03-29','https://news.12371.cn/2014/10/10/ARTI1412910263272618.shtml'),
('河南','2014-03-28','https://fanfu.people.com.cn/n/2014/0707/c64371-25249817.html'),
('海南','2014-03-24','https://fanfu.people.com.cn/n/2014/1010/c64371-25803383.html'),
('甘肃','2014-03-27','https://politics.people.com.cn/n/2014/1010/c1001-25807918.html'),
('宁夏','2014-03-31','https://politics.people.com.cn/ywkx/n/2014/1010/c363762-25805104-2.html'),
('新疆','2014-03-30','https://cpc.people.com.cn/n/2014/0713/c64094-25274525.html'),
('广西','2014-07-28','https://www.xinhuanet.com/politics/2015-01/31/c_1114202468.htm'),
('上海','2014-07-30','https://politics.people.com.cn/n/2014/0730/c1001-25372187.html'),
('青海','2014-07-27','https://www.ccdi.gov.cn/special/zyxszt/2014del_zyxs/xsjz_2014del_zyxs/'),
('西藏','2014-07-25','https://www.ccdi.gov.cn/special/zyxszt/2014del_zyxs/xsjz_2014del_zyxs/'),
('浙江','2014-07-29','https://epaper.neamco.com/gmrb/html/2016-01/04/nw.D110000gmrb_20160104_4-03.htm'),
('河北','2014-07-29','https://www.ccdi.gov.cn/special/zyxszt/2014del_zyxs/fkqk_2014del_zyxs/201411/t20141117_30677.html'),
('陕西','2014-07-30','https://www.xinhuanet.com/politics/2015-01/28/c_1114162376.htm'),
('黑龙江','2014-07-28','https://fanfu.people.com.cn/n/2015/0202/c64371-26490530.html'),
('四川','2014-07-28','https://www.ccdi.gov.cn/yaowen/201501/t20150129_134710.html'),
('江苏','2014-07-28','https://www.ccdi.gov.cn/special/zyxszt/2014del_zyxs/fkqk_2014del_zyxs/201411/t20141117_30676.html')]
calendar=pd.read_csv(ROOT/'result/inspection_hometown_design_2026_10_16/first_provincial_inspection_years_with_official_province_codes.csv')
dates=pd.DataFrame(date_rows,columns=['province','inspection_date','date_source_url']).merge(calendar[['province','province_code','first_inspection_year']],on='province',validate='1:1')
dates.province_code=dates.province_code.astype(int)*10000;dates['inspection_date']=pd.to_datetime(dates.inspection_date);dates['date_definition']='Official reported start / entry date; not mobilization date';dates['verified_on']='2026-10-20'
assert len(dates)==31 and dates.inspection_date.dt.year.eq(dates.first_inspection_year).all();save(dates,'inspection_dates_official_sources.csv')

# Load the original CPED classifications without executing network reconstruction
# or writing any existing project outputs. The prefix saves role spell copies only here.
src=(BASE/'code/prepare.py').read_text(encoding='utf-8-sig');prefix=src.split('# Edge tables:')[0]
prefix=prefix.replace("OUT=ROOT/'result/promotion_connections_rolling_2026_10_20'",f"OUT=Path({str(OUT)!r})")
ns={};exec(compile(prefix,'CPED_source_loader','exec'),ns)
raw=ns['raw'];CS=ns['CS'];BY=ns['BY'];cutoff=pd.Timestamp('2018-01-01')
assert hashlib.sha256(ns['ZIP'].read_bytes()).hexdigest()=='1427471e045e5e4f26b1ce39bb6f8ea024476d099b8478aaf984893c1cf24526'
A=pd.read_csv(BASE/'with_officer_city_economics/annual_economics_rematched.csv.gz',low_memory=False)
anchor=A[A.k.eq(-1)].copy();ss=anchor[['legacy_cowork_6m_S','legacy_cowork_6m_G']];anchor['C0']=np.where(ss.eq(1).any(axis=1),1,np.where(ss.eq(0).all(axis=1),0,np.nan))
anchor=anchor.merge(dates[['province_code','inspection_date','date_source_url']],on='province_code',validate='m:1')
assert not anchor.duplicated('person_id').any();anchor['anchor_province']=anchor.province_code;anchor['anchor_snapshot']=pd.to_datetime(anchor.baseline_date)
assert (anchor.anchor_snapshot<anchor.inspection_date).all()
for col,new in [('age','age0'),('age2','age20'),('tenure','tenure0'),('tenure2','tenure20'),('base_rank','rank0'),('role_secretary','role0'),('gdp_growth_lag','growth0'),('lngdppc_lag','lngdppc0'),('lnpop_lag','lnpop0')]:anchor[new]=anchor[col]
ctrl=['age0','age20','tenure0','tenure20','rank0','role0','growth0','lngdppc0','lnpop0']
anchor['eligible_controls']=anchor[ctrl].notna().all(axis=1);anchor['eligible_relation']=anchor.C0.notna()
save(anchor,'cohort_anchor_all.csv.gz');eligible=anchor[anchor.eligible_controls&anchor.eligible_relation].copy();pids=set(eligible.person_id.astype(int))
save(anchor[~(anchor.eligible_controls&anchor.eligible_relation)],'cohort_anchor_exclusions.csv')

# Event history compares a new appointment with the actual prior active grade /
# role, rather than repeatedly comparing all future jobs to an old city rank.
VROWS=set(raw.loc[raw['标志位'].map(ns['clean']).isin(['副省长(常委)','副省长(非常委)'])&raw['rank'].eq(5)&raw.substantive,'row_id'])
SROWS=set(CS[CS.role.eq('secretary')].source_rows.explode().astype(int));CSP={int(p):q for p,q in CS.groupby('person_id')}
events=[];uncertain=[];rawcopies=[]
for pid in sorted(pids):
 q=BY[pid];city=CSP.get(pid,CS.iloc[:0]);rawcopies.append(q)
 starts=q[q.substantive&q.start.ge('2006-01-01')&q.start.lt(cutoff)&(q.end.isna()|q.end.gt(q.start))]
 for date,g in starts.groupby('start'):
  prev=q[q.substantive&q.valid_interval&q.start.lt(date)&q.end.ge(date)];pr=prev['rank'].dropna();prior=float(pr.max()) if len(pr) else np.nan
  oldcity=city[city.start.lt(date)&city.end.ge(date)];wasmayor=oldcity.role.eq('mayor').any() and not oldcity.role.eq('secretary').any()
  prevvg=prev.row_id.isin(VROWS).any()
  for er in g.itertuples():
   up=pd.notna(prior) and pd.notna(er.rank) and er.rank>prior
   mayorup=wasmayor and er.row_id in SROWS
   viceup=(er.row_id in VROWS) and not prevvg and pd.notna(prior) and prior<=5
   rec=dict(person_id=pid,event_date=date,event_row=int(er.row_id),event_job=getattr(er,'具体职务'),prior_rank=prior,new_rank=er.rank,rank_up=bool(up),mayor_to_secretary=bool(mayorup),new_vice_governor=bool(viceup),second_line=bool(er.second_line))
   if up or mayorup or viceup:events.append(rec)
   elif pd.isna(er.rank) or pd.isna(prior):uncertain.append(rec)
EV=pd.DataFrame(events);UN=pd.DataFrame(uncertain,columns=EV.columns)
EV['evidence_basis']='new_appointment_vs_immediately_prior_active_grade_or_role'
# Preserve the previously audited positive city-principal event registry. Some
# CPED month-coded end/start pairs leave a gap, preventing a daily prior-state
# lookup although the year-baseline promotion evidence is already verified.
# Such gaps are NOT filled for negative outcomes.
oldpos=A[A.person_id.isin(pids)&A.promotion.eq(1)&A.event_date.notna()]
extra=[]
for r in oldpos.itertuples():
 date=pd.Timestamp(r.event_date);er=raw[raw.row_id.eq(int(r.event_row))].iloc[0]
 assert int(er.person_id)==int(r.person_id) and er.start==date
 extra.append(dict(person_id=int(r.person_id),event_date=date,event_row=int(r.event_row),event_job=er['具体职务'],prior_rank=r.base_rank,new_rank=er['rank'],rank_up=bool(r.rank_promotion==1),mayor_to_secretary=bool(r.role=='mayor' and int(r.event_row) in SROWS),new_vice_governor=bool(int(r.event_row) in VROWS),second_line=bool(er.second_line),evidence_basis='previously_audited_annual_city_principal_promotion'))
EV=pd.concat([pd.DataFrame(extra),EV],ignore_index=True).drop_duplicates(['person_id','event_row'],keep='first')
save(EV,'promotion_event_evidence_all_careers.csv');save(UN,'unresolved_appointment_events.csv')
save(pd.concat(rawcopies,ignore_index=True),'source_career_records_cohort.csv.gz')
evby={int(p):g.sort_values(['event_date','event_row']) for p,g in EV.groupby('person_id')};unby={int(p):g for p,g in UN.groupby('person_id')}

def outcome(pid,lo,hi):
 assert lo<hi and hi<=cutoff
 q=BY[pid];ev=evby.get(pid,EV.iloc[:0]);ev=ev[ev.event_date.ge(lo)&ev.event_date.lt(hi)]
 bad=unby.get(pid,UN.iloc[:0]);bad=bad[bad.event_date.ge(lo)&bad.event_date.lt(hi)]
 cov=q[q.substantive&q.valid_interval&q['rank'].notna()&q.end.gt(lo)&q.start.lt(hi)].sort_values('start')
 reached=lo;gap=False
 for rr in cov.itertuples():
  if rr.start>reached:gap=True;break
  reached=max(reached,rr.end)
  if reached>=hi:break
 covered=(not gap) and reached>=hi
 term=q[q.terminal&q.start.ge(lo)&q.start.lt(hi)]
 if len(ev):
  first=ev.iloc[0];return dict(Y=100.,status='observed_at_least_one_promotion',event_date=first.event_date,event_row=first.event_row,event_job=first.event_job,covered=covered,coverage_through=reached,uncertain_appointments=len(bad),competing_exits=len(term),promotion_events=ev.event_date.nunique())
 if covered and len(bad)==0:return dict(Y=0.,status='covered_no_promotion',event_date=pd.NaT,event_row=np.nan,event_job='',covered=True,coverage_through=reached,uncertain_appointments=0,competing_exits=len(term),promotion_events=0)
 return dict(Y=np.nan,status='censored_gap_or_unknown_rank',event_date=pd.NaT,event_row=np.nan,event_job='',covered=covered,coverage_through=reached,uncertain_appointments=len(bad),competing_exits=len(term),promotion_events=0)

rows=[]
for a in eligible.itertuples():
 for H in [12,24,36]:
  g=a.inspection_date
  for post,lo,hi in [(0,g-pd.DateOffset(months=H),g),(1,g,g+pd.DateOffset(months=H))]:
   r=dict(person_id=a.person_id,name=a.name,anchor_province=a.anchor_province,anchor_city=a.city_code,anchor_snapshot=a.anchor_snapshot,C0=a.C0,inspection_date=g,H=H,post=post,start=lo,end_exclusive=hi,end_year=(hi-pd.Timedelta(days=1)).year,anchor_after_window_start=a.anchor_snapshot>lo,**{c:getattr(a,c) for c in ctrl});r.update(outcome(a.person_id,lo,hi));rows.append(r)
P=pd.DataFrame(rows);assert not P.duplicated(['person_id','H','post']).any();save(P,'cumulative_outcome_audit.csv.gz')
paired=P.groupby(['person_id','H']).Y.count().eq(2).unstack('H').fillna(False);common=set(paired.index[paired.all(axis=1)])
flow=[];panels=[];models=[];singleton_exclusions=[];mid=0
for mode in ['common_all_H','maximum_each_H']:
 for H in [12,24,36]:
  ids=common if mode=='common_all_H' else set(paired.index[paired[H]])
  d=P[P.H.eq(H)&P.person_id.isin(ids)].copy()
  # Province-period FE require >=2 officials in a province. Remove only
  # mathematical singleton cells, for every FE comparison on the same sample.
  counts=d[d.post.eq(0)].groupby('anchor_province').person_id.nunique()
  singleprovs=counts[counts.eq(1)].index
  singleton_exclusions.append(d[d.anchor_province.isin(singleprovs)].assign(sample=mode))
  d=d[~d.anchor_province.isin(singleprovs)].copy();ids=set(d.person_id)
  d['CP']=d.C0*d.post
  d['pid']=pd.factorize(d.person_id)[0]+1;d['pp']=pd.factorize(pd.MultiIndex.from_frame(d[['anchor_province','post']]))[0]+1
  filename=f'panel_{mode}_{H}m.dta';cols=['person_id','pid','anchor_province','anchor_city','H','post','end_year','pp','C0','CP','Y']+ctrl
  d[cols].to_stata(OUT/'data'/filename,write_index=False,version=118);panels.append(d.assign(sample=mode))
  flow.append(dict(sample=mode,H=H,people=len(ids),rows=len(d),connected_people=int(d[d.post.eq(0)].C0.sum()),G=d.anchor_province.nunique(),pre_promotions=int(d.loc[d.post.eq(0),'Y'].sum()/100),post_promotions=int(d.loc[d.post.eq(1),'Y'].sum()/100),anchor_after_pre_window_start=int(d.loc[d.post.eq(0),'anchor_after_window_start'].sum())))
  for fe,absorb in [('I_PERIOD','pid post'),('I_CALENDAR','pid end_year'),('I_PXY','pid pp')]:
   for ctype in ['personal','full']:
    mid+=1;models.append(dict(model_id=mid,sample=mode,H=H,fe=fe,absorb=absorb,control=ctype,filename=filename,N=len(d),people=len(ids),G=d.anchor_province.nunique()))
save(pd.DataFrame(flow),'sample_flow.csv');save(pd.DataFrame(models),'model_design.csv');save(pd.concat(panels),'all_estimation_panels.csv.gz')
save(pd.concat(singleton_exclusions,ignore_index=True),'province_period_singleton_exclusions.csv')
save(P[P.Y.isna()],'unknown_outcomes.csv')

L=['version 18','clear all','set more off','set processors 2',f'local out "{OUT.as_posix()}"','capture log close','log using "`out\'/TWFE.log", text replace','tempname rr ff',
'postfile `rr\' long model_id double(b se p lo hi N G df pretrend_placeholder) using "`out\'/TWFE_results.dta", replace',
'postfile `ff\' long model_id long rc using "`out\'/TWFE_failures.dta", replace']
for m in models:
 cov='c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0'
 if m['control']=='full':cov+=' c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0'
 L += [f'use "`out\'/data/{m["filename"]}", clear','isid person_id post','capture noisily reghdfe Y CP '+cov+f', absorb({m["absorb"]}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({m["model_id"]}) (`rc\')','if `rc\'==0 {',f'assert e(N)=={m["N"]}','assert _se[CP]>0','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','quietly lincom CP, level(95)',f'post `rr\' ({m["model_id"]}) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\') (`DD\') (.)','}']
L += ['postclose `rr\'','postclose `ff\'','log close','exit, clear'];(OUT/'code/run_TWFE.do').write_text('\n'.join(L)+'\n',encoding='utf8')
shutil.copy2(__file__,OUT/'code'/Path(__file__).name);shutil.copy2(BASE/'code/prepare.py',OUT/'code/prepare_original_loader.py')
save(pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [ns['ZIP'],BASE/'with_officer_city_economics/annual_economics_rematched.csv.gz',ROOT/'result/cped_city_province_connections_20261019/workplace_classification.csv.gz',ROOT/'result/cped_city_province_connections_20261019/leadership_roles_all.csv']]),'input_manifest.csv')
print('Anchor rows:',len(anchor),'eligible:',len(eligible),'known relation:',int(anchor.eligible_relation.sum()),flush=True);print(pd.DataFrame(flow).to_string(index=False),flush=True);print('Events',len(EV),'Uncertain',len(UN),'Models',len(models),flush=True)
