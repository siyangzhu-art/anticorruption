"""Audit city-year matching and build reproducible economic-control variants."""
from pathlib import Path
import sys,hashlib,json,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import numpy as np,pandas as pd
ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
BASE=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'
OUT=BASE/'with_officer_city_economics'
for p in [OUT,OUT/'code',OUT/'figures']:p.mkdir(exist_ok=True)
econ=['gdp_growth_lag','lngdppc_lag','lnpop_lag']
source=ROOT/'result/city_outcomes_province_Local_2026_10_19/analysis_panel.csv.gz'
C=pd.read_csv(source,usecols=['citycode','year','old_population_wan','old_gdp_per_capita_yuan','old_gdp_growth_pct'])
assert not C.duplicated(['citycode','year']).any()
C['city_code']=(C.citycode*100).astype(int);C['economic_year']=C.year.astype(int);C['year']=C.year+1
C['gdp_growth_lag']=C.old_gdp_growth_pct;C['lngdppc_lag']=np.log(C.old_gdp_per_capita_yuan.where(C.old_gdp_per_capita_yuan.gt(0)));C['lnpop_lag']=np.log(C.old_population_wan.where(C.old_population_wan.gt(0)))
A=pd.read_csv(BASE/'annual_official_panel.csv.gz',low_memory=False)
orig=A[econ].copy();A=A.drop(columns=econ).merge(C[['city_code','year','economic_year']+econ],on=['city_code','year'],how='left',validate='m:1',sort=False)
checks=[]
def ck(n,v,detail=''):checks.append(dict(check=n,passed=bool(v),detail=str(detail)))
for col in econ:ck('Independent rematch agrees with existing '+col,np.allclose(orig[col],A[col],equal_nan=True))
ck('Unique person-year',not A.duplicated(['person_id','year']).any());ck('Exact preceding calendar year',A.loc[A.economic_year.notna(),'economic_year'].eq(A.loc[A.economic_year.notna(),'year']-1).all())
A['economic_complete']=A[econ].notna().all(axis=1)
Z=A.sort_values(['person_id','year']).copy();Z['previous_city']=Z.groupby('person_id').city_code.shift();Z['previous_row_year']=Z.groupby('person_id').year.shift();Z['city_changed']=Z.previous_city.notna()&Z.city_code.ne(Z.previous_city)
for col in econ:Z['previous_row_'+col]=Z.groupby('person_id')[col].shift()
moves=Z[Z.city_changed].copy();moves.to_csv(OUT/'officer_city_change_audit.csv',index=False,encoding='utf-8-sig')
example=moves[moves.economic_complete].head(20)
example[['person_id','name','year','baseline_date','previous_city','previous_row_year','city_code','city','economic_year']+econ].to_csv(OUT/'moving_official_examples.csv',index=False,encoding='utf-8-sig')
A.to_csv(OUT/'annual_economics_rematched.csv.gz',index=False)
pd.DataFrame(checks).to_csv(OUT/'economic_matching_checks.csv',index=False,encoding='utf-8-sig');assert all(x['passed'] for x in checks)
pd.DataFrame([dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [source,BASE/'annual_official_panel.csv.gz']]).to_csv(OUT/'input_manifest.csv',index=False)

# Materialize full standalone estimator files from previously validated source.
# Every replacement asserts its expected source is present, and generated source
# is delivered for inspection. No old code, data or results are overwritten.
WORK=Path(__file__).parent
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b)
origscript=(WORK/'sun_abraham_post4.py').read_text(encoding='utf-8-sig')
s=replace(origscript,"OUT=BASE/'sun_abraham_fixed_connection_post4'","OUT=BASE/'with_officer_city_economics/SA_TWFE_common_sample'")
s=replace(s,"BASE/'annual_official_panel.csv.gz'","BASE/'with_officer_city_economics/annual_economics_rematched.csv.gz'")
s=replace(s,"required=['promotion','age2','tenure','tenure2','base_rank','role_secretary']","econ=['gdp_growth_lag','lngdppc_lag','lnpop_lag']\nrequired=['promotion','age2','tenure','tenure2','base_rank','role_secretary']+econ")
s=replace(s,"+dnames+['all_'+n for n in dnames]","+econ+dnames+['all_'+n for n in dnames]")
s=replace(s,"for mid,fe in [(1,'I_YEAR'),(2,'I_PXY')]:","for mid,fe,use_econ in [(1,'I_YEAR',False),(2,'I_PXY',False),(3,'I_YEAR',True),(4,'I_PXY',True)]:")
s=replace(s,'bb,V,meta=fit(D,fe,np.column_stack(values),E)','bb,V,meta=fit(D,fe,np.column_stack(values),np.column_stack([E,D[econ].to_numpy()]) if use_econ else E)')
s=replace(s,"cov='age2 tenure tenure2 i.base_rank i.role_secretary'+", "cov='age2 tenure tenure2 i.base_rank i.role_secretary'+(' '+' '.join(econ) if use_econ else '')+")
s=replace(s,"helper=Path(__file__).with_name('event_study_individual_FE.py')","helper=Path(__file__).with_name('event_study_individual_FE.py')")
sun_script=OUT/'code/estimate_SA_TWFE_economic.py';sun_script.write_text(s,encoding='utf8')
shutil.copy2(WORK/'event_study_individual_FE.py',OUT/'code/event_study_individual_FE.py')
print('Matching checks passed; city changes:',len(moves),'annual rows',len(A),'complete economies',int(A.economic_complete.sum()))
print(example[['name','year','previous_city','city','economic_year']].head(6).to_string(index=False))
