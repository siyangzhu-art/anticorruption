from pathlib import Path
import shutil
W=Path(__file__).parent
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'with_officer_city_economics'
def rep(s,a,b):
 assert a in s,a
 return s.replace(a,b)
s=(W/'window_post4.py').read_text(encoding='utf-8-sig')
s=rep(s,"OUT=BASE/'event_study_window_sensitivity_post4'","OUT=BASE/'with_officer_city_economics/dynamic_TWFE_common_sample'")
s=rep(s,"assert len(A)==7249 and not A.duplicated(['person_id','year']).any()","assert len(A)==7249 and not A.duplicated(['person_id','year']).any()\necon=['gdp_growth_lag','lngdppc_lag','lnpop_lag']\nrematched=pd.read_csv(BASE/'with_officer_city_economics/annual_economics_rematched.csv.gz',usecols=['person_id','year']+econ)\nA=A.drop(columns=econ).merge(rematched,on=['person_id','year'],how='left',validate='1:1').dropna(subset=econ).copy()")
s=rep(s,'for L in range(3,9):','for L in [4]:')
s=rep(s,"for fe in ['I_YEAR','I_PXY']:\n  mid=(L-3)*2+(1 if fe=='I_YEAR' else 2)","for mid,(fe,use_econ) in enumerate([('I_YEAR',False),('I_PXY',False),('I_YEAR',True),('I_PXY',True)],1):")
s=rep(s,'fit(d,fe,XX,dd)','fit(d,fe,XX,np.column_stack([dd,d[econ].to_numpy()]) if use_econ else dd)')
s=rep(s,'meta.update(model_id=mid,L=L,fe=fe,','meta.update(model_id=mid,L=L,fe=fe,economic_controls=use_econ,')
s=rep(s,"'role_secretary','k']","'role_secretary','k']+econ")
s=rep(s,"' age2 tenure tenure2 i.base_rank i.role_secretary '+","' age2 tenure tenure2 i.base_rank i.role_secretary '+(' '.join(econ)+' ' if m.economic_controls else '')+")
s=rep(s,'len(M)==12','len(M)==4')
(O/'code/estimate_economic_dynamic_TWFE.py').write_text(s,encoding='utf8')
if (W/'window_post4.py').resolve()!=(O/'code/window_post4.py').resolve():shutil.copy2(W/'window_post4.py',O/'code/window_post4.py')
print('Materialized dynamic-TWFE economic-control estimator')
