"""Read-only audit of source data; isolated estimation reruns, never rewrite old results."""
from pathlib import Path
import sys, json, hashlib, zipfile, io, re
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
ROOT=B.parent.parent
O=B/'audit_main_page_methods_2026_10_21'
PAGE=B/'organized_main_results_corruption_checks_2026_10_21/index.html'
for p in [O,O/'data',O/'code']:p.mkdir(parents=True,exist_ok=True)
def save(d,n):d.to_csv(O/'data'/n,index=False,encoding='utf-8-sig')
sources=[PAGE,B/'control_FE_sensitivity_post4/fixed_panel.csv.gz',B/'control_FE_sensitivity_post4/level_results.dta',B/'all_methods_C08_event_study_gallery/annual_C08_all_contrasts.csv',B/'preinspection_fixed_C0_levels_2026_10_21/preinspection_panel.csv.gz',B/'cumulative_promotion_TWFE_12_24_36m/cumulative_outcome_audit.csv.gz',B/'cumulative_promotion_TWFE_12_24_36m/all_estimation_panels.csv.gz',B/'cumulative_promotion_TWFE_12_24_36m/promotion_event_evidence_all_careers.csv',B/'exclude_corruption_leader_provinces_2026_10_21/province_exclusion_evidence.csv',Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')]
manifest=pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources]);save(manifest,'inputs_before_audit.csv')

def prepare():
 f=pd.read_csv(B/'control_FE_sensitivity_post4/fixed_panel.csv.gz');annual=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz');pre=pd.read_csv(B/'preinspection_fixed_C0_levels_2026_10_21/preinspection_panel.csv.gz')
 C=B/'cumulative_promotion_TWFE_12_24_36m';cu=pd.read_csv(C/'cumulative_outcome_audit.csv.gz');cp=pd.read_csv(C/'all_estimation_panels.csv.gz');common=cp[(cp['sample']=='common_all_H')&cp.H.eq(24)&cp.post.eq(0)].copy()
 # Baseline selection and event support.
 rows=[]
 for name,d in [('main_annual',f),('pre_only',pre)]:
  for k,g in d.groupby('k'):
   z=g[g.C0.eq(1)];rows.append(dict(sample=name,k=k,N=len(g),people=g.person_id.nunique(),connected_people=z.person_id.nunique(),provinces=g.anchor_province.nunique(),connected_provinces=z.anchor_province.nunique(),G2013=int((g.G0==2013).sum()),G2014=int((g.G0==2014).sum()),connected_promotions=z.promotion.sum()))
 save(pd.DataFrame(rows),'annual_support.csv')
 missing=cu.groupby(['H','post','C0']).agg(total=('Y','size'),known=('Y','count'),promotions=('Y',lambda x:x.eq(100).sum()),unknown=('Y',lambda x:x.isna().sum()),full_coverage=('covered','sum'),uncertain=('uncertain_appointments','sum')).reset_index();missing['unknown_pct']=100*(missing.total-missing.known)/missing.total;save(missing,'cumulative_observation_selection.csv')
 selected=set(common.person_id);elig=cu[(cu.H==24)&cu.post.eq(0)][['person_id','C0','anchor_province']].copy();elig['in_common_sample']=elig.person_id.isin(selected)
 retention=elig.groupby('C0').agg(eligible=('person_id','size'),retained=('in_common_sample','sum'));retention['retained_pct']=100*retention.retained/retention.eligible;save(retention.reset_index(),'cumulative_retention_by_C0.csv')
 window=cu[cu.person_id.isin(selected)].groupby(['H','post','C0']).agg(N=('person_id','size'),anchor_after_start=('anchor_after_window_start','sum'),raw_rate=('Y','mean'),positive_incomplete_coverage=('covered',lambda x:0)).reset_index();save(window,'common_cohort_windows.csv')
 # No confidence interval for these fixed-sample descriptive rates.
 g=cp[cp['sample'].eq('common_all_H')].groupby(['H','post','C0']).agg(N=('Y','size'),promotion_pct=('Y','mean')).reset_index();save(g,'cumulative_raw_rates.csv')
 # Backfill of pre-2012 edges to earlier retrospective observations.
 E=pd.read_csv(ROOT/'result/cped_pre_anticorruption_person_network_20261019/person_edges_pre2012.csv.gz')
 edges={(min(int(r.person_a),int(r.person_b)),max(int(r.person_a),int(r.person_b))):r for r in E.itertuples()}
 edge_audit=[]
 for dname,d in [('annual',f[f.C0.eq(1)]),('pre_only',pre[pre.C0.eq(1)])]:
  for r in d.itertuples():
   form=[]
   for leader in [r.anchor_S,r.anchor_G]:
    if pd.isna(leader):continue
    ee=edges.get(tuple(sorted([int(r.person_id),int(leader)])))
    if ee is not None and ee.cowork_6m==1:
     dt=pd.to_datetime(ee.cowork_6m_first_formation,errors='coerce')
     if pd.notna(dt):form.append(dt)
   first=min(form) if form else pd.NaT
   edge_audit.append(dict(sample=dname,person_id=r.person_id,year=r.year,k=r.k,baseline_date=r.baseline_date,first_edge_threshold=first,edge_not_yet_formed=pd.notna(first) and first>=pd.Timestamp(r.baseline_date)))
 edge_audit=pd.DataFrame(edge_audit);save(edge_audit,'retrospective_relation_dates.csv')
 # Independent raw-workbook event audit.
 with zipfile.ZipFile(sources[-1]) as z:raw=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
 raw['row_id']=np.arange(2,len(raw)+2);raw['person_id']=raw['用户编码'].astype(int);raw['start']=pd.to_datetime(raw['起始时间（YYYY-MM-DD）'],errors='coerce');raw['end']=pd.to_datetime(raw['终止时间（（YYYY-MM-DD））'],errors='coerce')
 ranks={'小于副处':0,'副处':1,'正处':2,'副厅':3,'正厅':4,'副部':5,'正部':6,'副国':7,'正国':8};raw['rank']=raw['级别'].map(ranks)
 W=pd.read_csv(ROOT/'result/cped_city_province_connections_20261019/workplace_classification.csv.gz',usecols=['row_id','work_eligible']);wk=set(W[W.work_eligible].row_id)
 clean=lambda s:'' if pd.isna(s) else re.sub(r'\s+','',str(s)).replace('（','(').replace('）',')')
 raw['pos']=raw['具体职务'].map(lambda s:re.sub(r'\([^)]*\)','',clean(s)))
 raw['generic']=raw.pos.isin(['委员','候补委员','常委','常务委员','常委会委员','代表','人大代表','政协委员'])&~raw['标志位'].isin(['省常委(其他)','市委副书记(专职)','市委书记','省委书记','省长','市长'])
 raw['terminal']=raw.pos.str.contains(r'^(?:退休|离休|被免职|被撤职|被查处|接受调查|免职|撤职|开除|去世|逝世|因.*(?:免职|撤职))',regex=True)
 raw['valid']=raw.start.notna()&raw.end.notna()&raw.start.lt(raw.end);raw['substantive']=raw.row_id.isin(wk)&raw.pos.ne('')&~raw.generic&~raw.terminal&~raw.pos.str.contains('待分配|待安排|待业|失业')
 raw['second_line']=raw['基本大类别'].isin(['人大','政协']);R=raw.set_index('row_id');by={p:d for p,d in raw.groupby('person_id')}
 pos=annual[annual.promotion.eq(1)].copy();evchecks=[]
 for r in pos.itertuples():
  er=R.loc[int(r.event_row)];dt=pd.Timestamp(r.event_date)
  evchecks.append(dict(person_id=r.person_id,year=r.year,event_row=r.event_row,source_id_matches=int(er.person_id)==r.person_id,date_matches=dt==er.start,date_in_outcome_year=dt.year==r.year,substantive=bool(er.substantive),generic=bool(er.generic),second_line=bool(er.second_line),event_job=er['具体职务'],source_flag=er['标志位'],event_rank=er['级别']))
 save(pd.DataFrame(evchecks),'annual_raw_positive_event_checks.csv')
 cev=pd.read_csv(C/'promotion_event_evidence_all_careers.csv');cs=pd.read_csv(C/'city_principal_spells.csv');cs.start=pd.to_datetime(cs.start);cs.end=pd.to_datetime(cs.end)
 candidates=[]
 vrows=set(raw[raw['标志位'].map(clean).isin(['副省长(常委)','副省长(非常委)'])&raw['rank'].eq(5)&raw.substantive].row_id)
 for rr in cev.itertuples():
  er=R.loc[int(rr.event_row)];date=pd.Timestamp(rr.event_date);q=by[rr.person_id];prev=q[q.substantive&q.valid&q.start.lt(date)&q.end.ge(date)];pr=prev['rank'].dropna();prior=pr.max() if len(pr) else np.nan
  c=cs[(cs.person_id==rr.person_id)&cs.start.lt(date)&cs.end.ge(date)];mayor=c.role.eq('mayor').any() and not c.role.eq('secretary').any()
  up=pd.notna(prior) and pd.notna(er['rank']) and er['rank']>prior
  roleup=mayor and clean(er['标志位'])=='市委书记'
  vup=int(rr.event_row) in vrows and not prev.row_id.isin(vrows).any() and pd.notna(prior) and prior<=5
  candidates.append(dict(person_id=rr.person_id,event_row=rr.event_row,event_date=date,event_job=rr.event_job,source_flag=er['标志位'],source_category=er['基本大类别'],prior_rank_rechecked=prior,new_rank=er['rank'],second_line=bool(er.second_line),evidence_basis=rr.evidence_basis,independently_confirmed=bool(up or roleup or vup),prior_unknown=pd.isna(prior),candidate_known_prior_no_promotion=pd.notna(prior) and not(up or roleup or vup)))
 candidates=pd.DataFrame(candidates);save(candidates,'cumulative_raw_event_recheck.csv');save(candidates[candidates.candidate_known_prior_no_promotion],'cumulative_event_candidates_for_review.csv')
 # Date resolution: annual precise lag vs actual within-year first inspection.
 anchor=f[f.k.eq(-1)][['person_id','anchor_snapshot','G0','C0']].copy();anchor=anchor.merge(pd.read_csv(C/'cohort_anchor_all.csv.gz')[['person_id','inspection_date']],on='person_id',how='left',validate='1:1');anchor['lag_days']=(pd.to_datetime(anchor.inspection_date)-pd.to_datetime(anchor.anchor_snapshot)).dt.days;save(anchor,'snapshot_to_inspection_gap.csv')
 # Exact isolated rerun of the displayed specifications.
 lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"',f'local base "{B.as_posix()}"','capture log close','log using "`out\'/isolated_rerun.log", text replace','tempname rr','postfile `rr\' str12 family str20 method str24 fe str24 term double(b se p lo hi N G) using "`out\'/rerun_results.dta", replace']
 terms=['d_m4','d_m3','d_m2','d_p0','d_p1','d_p2','d_p3','d_p4'];cov='age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag'
 for fe,absorb in [('I_YEAR','person_id year'),('I_PXY','person_id py'),('I_CITY_YEAR','person_id city_code year'),('I_CITY_PXY','person_id city_code py')]:
  lines+=['use "`base\'/control_FE_sensitivity_post4/fixed_panel.dta", clear','isid person_id year','egen py=group(anchor_province year)']
  for k,n in zip([-4,-3,-2,0,1,2,3,4],terms):lines+=[f'gen double {n}=(k=={k})*C0',f'gen double all_{n}=(k=={k})']
  covs=cov+(' '+' '.join('all_'+n for n in terms) if fe in ['I_YEAR','I_CITY_YEAR'] else '')
  for method in ['TWFE_fixed','Sun_Abraham']:
   cmd=('reghdfe Y '+' '.join(terms)+' '+covs+f', absorb({absorb}) vce(cluster anchor_province)') if method=='TWFE_fixed' else ('eventstudyinteract Y '+' '.join(terms)+f', cohort(treated_cohort) control_cohort(never) absorb({absorb}) covariates({covs}) vce(cluster anchor_province)')
   lines+=[cmd,'local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)']
   if method=='Sun_Abraham':lines+=['matrix BI=e(b_iw)','matrix VI=e(V_iw)','ereturn post BI VI, obs(`NN\') dof(`DD\')']
   for n,expression in [(n,n) for n in terms]+[('post_average','(d_p1+d_p2+d_p3+d_p4)/4')]:
    lines += [f'quietly lincom {expression}, level(95)',f'post `rr\' ("annual") ("{method}") ("{fe}") ("{n}") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\')']
 for mid,controls in [(1,''),(2,'age age2 tenure tenure2 i.base_rank i.role_secretary'),(3,'age age2 tenure tenure2 i.base_rank i.role_secretary gdp_growth_lag lngdppc_lag lnpop_lag')]:
  lines+=['use "`base\'/preinspection_fixed_C0_levels_2026_10_21/preinspection_panel.dta", clear',f'reghdfe Y C0 {controls}, absorb(py) vce(cluster anchor_province)','local NN=e(N)','local GG=e(N_clust)','quietly lincom C0, level(95)',f'post `rr\' ("pre") ("model{mid}") ("PXY") ("C0") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\')']
 for h in [12,24,36]:
  lines += [f'use "`base\'/cumulative_promotion_TWFE_12_24_36m/data/panel_common_all_H_{h}m.dta", clear','reghdfe Y CP c.post#c.age0 c.post#c.age20 c.post#c.tenure0 c.post#c.tenure20 i.rank0#c.post c.post#c.role0 c.post#c.growth0 c.post#c.lngdppc0 c.post#c.lnpop0, absorb(pid pp) vce(cluster anchor_province)','local NN=e(N)','local GG=e(N_clust)','quietly lincom CP, level(95)',f'post `rr\' ("cumulative") ("{h}m") ("I_PXY") ("CP") (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\')']
 lines+=['postclose `rr\'','log close','exit, clear'];(O/'code/isolated_rerun.do').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 diagnostics={'annual_N':len(f),'annual_people':f.person_id.nunique(),'annual_tied_people':f[f.C0.eq(1)].person_id.nunique(),'pre_N':len(pre),'cumulative_eligible':len(elig),'cumulative_common':len(common),'positive_annual_events':len(pos),'annual_events_second_line':int(pd.DataFrame(evchecks).second_line.sum()),'cumulative_positive_registry':len(candidates),'cumulative_second_line_events':int(candidates.second_line.sum()),'candidate_known_prior_no_promotion':int(candidates.candidate_known_prior_no_promotion.sum()),'registry_prior_unknown':int(candidates.prior_unknown.sum()),'pre_tied_rows_before_edge_formation':int(edge_audit[edge_audit['sample'].eq('pre_only')].edge_not_yet_formed.sum()),'pre_tied_rows':int((edge_audit['sample']=='pre_only').sum())}
 (O/'diagnostic_summary.json').write_text(json.dumps({k:int(v) for k,v in diagnostics.items()},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(diagnostics,ensure_ascii=False,indent=2));print(retention.to_string());print(candidates[candidates.candidate_known_prior_no_promotion].head(12).to_string(index=False))

if __name__=='__main__':prepare()
