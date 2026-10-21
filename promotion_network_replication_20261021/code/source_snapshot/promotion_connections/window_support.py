"""Add whole-year/cohort support diagnostics without refitting or changing any estimate."""
from estimate import OUT,sample
import pandas as pd,shutil,json
BASE={u:pd.read_csv(OUT/f,low_memory=False) for u,f in [('annual','annual_official_panel.csv.gz'),('term','term_destination_panel.csv.gz')]}
S=pd.read_csv(OUT/'model_status.csv');cache={};rows=[]
for r in S[S.kind.eq('rolling')].itertuples():
 key=(r.unit,r.role,r.outcome,r.relation,r.timing,r.controls,r.sampling)
 if key not in cache:cache[key]=sample(BASE[r.unit][BASE[r.unit].role.eq(r.role)],r.outcome,r.relation,r.timing,r.controls,r.sampling)
 d=cache[key];timecol='year' if r.axis=='calendar' else 'k';q=d[d[timecol].between(r.requested_lo,r.requested_hi)]
 assert len(q)==r.N
 nt=int(q[timecol].nunique());bycohort=q.groupby('first_inspection_year')[timecol].nunique();minimum=int(bycohort.min()) if len(bycohort) else 0
 rows.append(dict(model_id=r.model_id,observed_time_points=nt,observed_time_levels='|'.join(map(str,sorted(q[timecol].dropna().astype(int).unique()))),incomplete_window=bool(nt<r.width or (r.axis=='inspection_relative' and (len(bycohort)<2 or minimum<r.width))),inspection_cohorts=len(bycohort),minimum_cohort_time_points=minimum))
D=pd.DataFrame(rows);D.to_csv(OUT/'window_support_details.csv',index=False,encoding='utf-8-sig')
for f in ['all_estimates.csv','all_estimates_validated.csv','model_status.csv']:
 d=pd.read_csv(OUT/f,low_memory=False).drop(columns=[c for c in D if c!='model_id'],errors='ignore');d=d.merge(D,on='model_id',how='left',validate='m:1');d.to_csv(OUT/f,index=False,encoding='utf-8-sig')
print(json.dumps({'rolling_models':len(D),'incomplete_nominal_window_models':int(D.incomplete_window.sum()),'no_estimates_changed':True}));shutil.copy2(__file__,OUT/'code/window_support.py');shutil.copy2(__file__.replace('window_support.py','estimate.py'),OUT/'code/estimate.py')
