from pathlib import Path
import sys,shutil,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'with_officer_city_economics/LPDID_DoubleML_common_sample'
for p in [O,O/'code',O/'figures']:p.mkdir(exist_ok=True)
A=pd.read_csv(B/'sun_abraham_fixed_connection_post4/analysis_panel.csv.gz')
econ=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
rematched=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz',usecols=['person_id','year']+econ)
A=A.drop(columns=econ).merge(rematched,on=['person_id','year'],how='left',validate='1:1')
basecols=['person_id','C0','G0','anchor_province','age','age2','tenure','tenure2','base_rank','role_secretary','Y']+econ
S=A[A.k.eq(-1)][basecols].copy().rename(columns={'age':'base_age','age2':'base_age2','tenure':'base_tenure','tenure2':'base_tenure2','base_rank':'base_rank0','role_secretary':'base_role','Y':'base_Y','gdp_growth_lag':'base_growth','lngdppc_lag':'base_lngdppc','lnpop_lag':'base_lnpop'})
S=S.dropna(subset=['base_growth','base_lngdppc','base_lnpop']).copy()
assert not S.duplicated('person_id').any()
missingbase=A[~A.person_id.isin(S.person_id)][['person_id','name','C0','G0']].drop_duplicates();missingbase.to_csv(O/'excluded_without_complete_baseline.csv',index=False)
allq=[];manual=[];support_exclusions=[]
for h in [-4,-3,-2,0,1,2,3,4]:
 q=S.merge(A[A.k.eq(h)][['person_id','Y']],on='person_id',how='inner',validate='1:1');q['deltaY']=q.Y-q.base_Y;q['h']=h
 eligible=q.groupby('anchor_province').C0.min().eq(0)
 unsupported=q[~q.anchor_province.isin(eligible[eligible].index)].copy()
 if len(unsupported):support_exclusions.append(unsupported)
 q=q[q.anchor_province.isin(eligible[eligible].index)].copy()
 q['inspection2014']=q.G0.eq(2014).astype(float)
 allq.append(q)
 for spec in ['cohort','province','cohort_econ','province_econ']:
  controls=['base_age','base_age2','base_tenure','base_tenure2','base_role']+(['base_growth','base_lngdppc','base_lnpop'] if spec.endswith('_econ') else [])
  # Regression adjustment: fit the untreated outcome-change model, then
  # average treated residuals. This matches LP-DiD's rw+controls estimand.
  cat='anchor_province' if spec.startswith('province') else 'G0'
  z=np.column_stack([np.ones(len(q)),q[controls].to_numpy(),pd.get_dummies(q.base_rank0,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(q[cat],drop_first=True,dtype=float).to_numpy()])
  norm=np.linalg.norm(z,axis=0);z=z[:,norm>0]/norm[norm>0];ctl=q.C0.eq(0).to_numpy();bb=lstsq(z[ctl],q.deltaY.to_numpy()[ctl],cond=1e-10)[0];val=float((q.deltaY.to_numpy()-z@bb)[~ctl].mean())
  manual.append(dict(h=h,spec=spec,b=val,N=len(q),treated=int(q.C0.sum()),controls=int(ctl.sum()),provinces=q.anchor_province.nunique(),treated_provinces=q.loc[q.C0.eq(1),'anchor_province'].nunique()))
Q=pd.concat(allq,ignore_index=True);Q.to_csv(O/'horizon_pairs.csv.gz',index=False);Q.to_stata(O/'horizon_pairs.dta',write_index=False,version=118)
pd.DataFrame(manual).to_csv(O/'python_LPDID_RA_points.csv',index=False)
grid=[]
for r in S.itertuples(index=False):
 for k in range(-4,5):
  yr=int(r.G0+k)
  if yr<=2017:grid.append(dict(person_id=r.person_id,year=yr,k=k,G0=r.G0,anchor_province=r.anchor_province,C0=r.C0,base_age=r.base_age,base_age2=r.base_age2,base_tenure=r.base_tenure,base_tenure2=r.base_tenure2,base_rank=r.base_rank0,base_role=r.base_role,base_growth=r.base_growth,base_lngdppc=r.base_lngdppc,base_lnpop=r.base_lnpop))
T=pd.DataFrame(grid).merge(A[['person_id','year','Y']],on=['person_id','year'],how='left',validate='1:1')
excluded_support=pd.concat(support_exclusions,ignore_index=True) if support_exclusions else pd.DataFrame(columns=['person_id','h','G0'])
excluded_support.to_csv(O/'excluded_no_within_province_comparison.csv',index=False)
T['Y_source']=T.Y
for r in excluded_support.itertuples():T.loc[T.person_id.eq(r.person_id)&T.year.eq(r.G0+r.h),'Y']=np.nan
T['treatment']=(T.C0.eq(1)&T.year.ge(T.G0)).astype(int)
assert T.loc[T.Y.isna(),'Y'].isna().all()
T.to_stata(O/'lpdid_panel.dta',write_index=False,version=118);T.to_csv(O/'lpdid_panel.csv.gz',index=False)
lines=['version 18','clear all','set more off','set processors 2',f'local out "{O.as_posix()}"','capture log close','log using "`out\'/lpdid.log", text replace','which lpdid','tempname res','postfile `res\' str16 spec str16 term double b se stat p lo hi N using "`out\'/lpdid_results.dta", replace']
for spec in ['cohort','province','cohort_econ','province_econ']:
 lines+=['use "`out\'/lpdid_panel.dta", clear','isid person_id year']
 controls='base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role'+(' base_growth base_lngdppc base_lnpop' if spec.endswith('_econ') else '')
 absorb=' absorb(anchor_province)' if spec.startswith('province') else ''
 lines += [f'lpdid Y if year==G0, unit(person_id) time(year) treat(treatment) pre(4) post(4) nevertreated rw controls({controls}) cluster(anchor_province){absorb} level(95) nograph','matrix RR=e(results)','local rn: rownames RR','local nr=rowsof(RR)','forvalues i=1/`nr\' {','local nm: word `i\' of `rn\'',f'post `res\' ("{spec}") ("`nm\'") (RR[`i\',1]) (RR[`i\',2]) (RR[`i\',3]) (RR[`i\',4]) (RR[`i\',5]) (RR[`i\',6]) (RR[`i\',7])','}']
lines+=['postclose `res\'','log close','exit, clear']
(O/'code/run_lpdid.do').write_text('\n'.join(lines)+'\n',encoding='utf8')
shutil.copy2(__file__,O/'code'/Path(__file__).name)
pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [B/'sun_abraham_fixed_connection_post4/analysis_panel.csv.gz',Path(r'C:\Users\siyang zhu\ado\plus\l\lpdid.ado')]]).to_csv(O/'input_manifest.csv',index=False)
print('Baseline people',len(S),'excluded',len(missingbase));print(pd.DataFrame(manual).to_string(index=False))
