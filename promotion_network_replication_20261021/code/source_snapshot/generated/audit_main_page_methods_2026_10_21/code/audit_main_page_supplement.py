from pathlib import Path
import sys,json
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'audit_main_page_methods_2026_10_21'
f=pd.read_csv(B/'control_FE_sensitivity_post4/fixed_panel.csv.gz');ev=pd.read_csv(O/'data/cumulative_raw_event_recheck.csv');a=pd.read_csv(O/'data/annual_raw_positive_event_checks.csv')
print('Main positive',len(f[f.promotion.eq(1)]),'second_line',len(f[f.promotion.eq(1)&f.second_line.eq(1)]))
print(f[f.promotion.eq(1)&f.second_line.eq(1)][['name','year','event_job','event_rank','role','C0']].head(10).to_string(index=False))
print('Secondline flags',ev[ev.second_line][['event_job','source_flag','source_category']].value_counts().to_string())
edges=pd.read_csv(O/'data/retrospective_relation_dates.csv');print('Not-yet-formed pre rows',edges[edges['sample'].eq('pre_only')&edges.edge_not_yet_formed].to_string(index=False))
print('Snapshot delay',pd.read_csv(O/'data/snapshot_to_inspection_gap.csv').lag_days.describe().to_string())
c=pd.read_csv(B/'cumulative_promotion_TWFE_12_24_36m/all_estimation_panels.csv.gz');c=c[(c['sample']=='common_all_H')&c.H.eq(24)]
d=c[c.Y.eq(100)].merge(ev,on=['person_id','event_row'],suffixes=('','_event'),validate='m:1');print('24m events',d.groupby(['post','C0']).agg(N=('person_id','size'),second_line=('second_line','sum')).to_string())
print('Source event checks',a[['source_id_matches','date_matches','date_in_outcome_year','substantive','generic']].sum().to_string())
cp=pd.read_csv(B/'cumulative_promotion_TWFE_12_24_36m/all_estimation_panels.csv.gz');cp=cp[cp['sample']=='common_all_H'].copy()
ee=edges[edges['sample'].eq('annual')].drop_duplicates('person_id')[['person_id','first_edge_threshold']]
z=cp[cp.C0.eq(1)&cp.post.eq(0)].merge(ee,on='person_id',how='left',validate='m:1');z['formed_after_window_start']=pd.to_datetime(z.first_edge_threshold)>pd.to_datetime(z.start)
z.to_csv(O/'data/cumulative_formation_dates.csv',index=False,encoding='utf-8-sig');print('Edges formed after pre-window start',z.groupby('H').formed_after_window_start.agg(['sum','size']).to_string())
cu=pd.read_csv(B/'cumulative_promotion_TWFE_12_24_36m/cumulative_outcome_audit.csv.gz');pos=cu[cu.Y.eq(100)].copy();pos['event_month_at_boundary']=(pd.to_datetime(pos.event_date).dt.to_period('M')==pd.to_datetime(pos.start).dt.to_period('M'))|(pd.to_datetime(pos.event_date).dt.to_period('M')==pd.to_datetime(pos.end_exclusive).dt.to_period('M'));print('positive first event month on boundary',pos.groupby(['H','post']).event_month_at_boundary.sum().to_string())
pos.to_csv(O/'data/cumulative_month_boundary_sensitivity_candidates.csv',index=False,encoding='utf-8-sig')
# Check whether page's source CSVs are current copies of the underlying estimates.
orig=pd.read_csv(B/'organized_main_results_corruption_checks_2026_10_21/data/main_annual.csv');true=pd.read_csv(B/'all_methods_C08_event_study_gallery/annual_C08_all_contrasts.csv');z=orig.merge(true[true.term.eq('post_average')],on=['estimator','fe','term'],suffixes=('_page','_source'),validate='1:1');assert np.allclose(z.b_page,z.b_source)
print('All eight displayed annual averages match underlying CSV')
if (O/'rerun_results.dta').exists():
 rr=pd.read_stata(O/'rerun_results.dta');out=[]
 for r in rr.itertuples():
  if r.family=='annual':q=true[true.estimator.eq(r.method)&true.fe.eq(r.fe)&true.term.eq(r.term)].iloc[0]
  elif r.family=='pre':q=pd.read_csv(B/'preinspection_fixed_C0_levels_2026_10_21/adjusted_preinspection_results.csv').query('model_id=='+r.method.replace('model','')).iloc[0]
  else:q=pd.read_csv(B/'organized_main_results_corruption_checks_2026_10_21/data/main_cumulative.csv').query('H=='+r.method.replace('m','')).iloc[0]
  out.append(dict(family=r.family,method=r.method,fe=r.fe,term=r.term,b_difference=r.b-q.b,se_difference=r.se-q.se,p_difference=r.p-q.p,lo_difference=r.lo-q.lo,hi_difference=r.hi-q.hi))
 out=pd.DataFrame(out);out.to_csv(O/'data/isolated_rerun_comparison.csv',index=False,encoding='utf-8-sig');print('Rerun',len(out),'rows. Max differences',out.filter(like='difference').abs().max().to_dict());assert out.filter(like='difference').abs().max().max()<5e-6
