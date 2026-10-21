from pathlib import Path
import shutil
WORK=Path(__file__).parent
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'with_officer_city_economics'
def rep(s,a,b):
 assert a in s,a
 return s.replace(a,b)
s=(WORK/'prepare_lp_dml_post4.py').read_text(encoding='utf-8-sig')
s=rep(s,"O=B/'LPDID_DoubleML_fixed_connection_post4'","O=B/'with_officer_city_economics/LPDID_DoubleML_common_sample'")
s=rep(s,"basecols=['person_id'","econ=['gdp_growth_lag','lngdppc_lag','lnpop_lag']\nrematched=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz',usecols=['person_id','year']+econ)\nA=A.drop(columns=econ).merge(rematched,on=['person_id','year'],how='left',validate='1:1')\nbasecols=['person_id'")
s=rep(s,"'role_secretary','Y']","'role_secretary','Y']+econ")
s=rep(s,"'Y':'base_Y'})","'Y':'base_Y','gdp_growth_lag':'base_growth','lngdppc_lag':'base_lngdppc','lnpop_lag':'base_lnpop'})\nS=S.dropna(subset=['base_growth','base_lngdppc','base_lnpop']).copy()")
s=rep(s,"for spec in ['cohort','province']:","for spec in ['cohort','province','cohort_econ','province_econ']:")
s=rep(s,"spec=='province'","spec.startswith('province')")
s=rep(s,"controls=['base_age','base_age2','base_tenure','base_tenure2','base_role']","controls=['base_age','base_age2','base_tenure','base_tenure2','base_role']+(['base_growth','base_lngdppc','base_lnpop'] if spec.endswith('_econ') else [])")
s=rep(s,'allq=[];manual=[]','allq=[];manual=[];support_exclusions=[]')
s=rep(s," q['inspection2014']=q.G0.eq(2014).astype(float)"," eligible=q.groupby('anchor_province').C0.min().eq(0)\n unsupported=q[~q.anchor_province.isin(eligible[eligible].index)].copy()\n if len(unsupported):support_exclusions.append(unsupported)\n q=q[q.anchor_province.isin(eligible[eligible].index)].copy()\n q['inspection2014']=q.G0.eq(2014).astype(float)")
s=rep(s,"T['treatment']=", "excluded_support=pd.concat(support_exclusions,ignore_index=True) if support_exclusions else pd.DataFrame(columns=['person_id','h','G0'])\nexcluded_support.to_csv(O/'excluded_no_within_province_comparison.csv',index=False)\nT['Y_source']=T.Y\nfor r in excluded_support.itertuples():T.loc[T.person_id.eq(r.person_id)&T.year.eq(r.G0+r.h),'Y']=np.nan\nT['treatment']=")
s=rep(s,"base_role=r.base_role))","base_role=r.base_role,base_growth=r.base_growth,base_lngdppc=r.base_lngdppc,base_lnpop=r.base_lnpop))")
s=rep(s,"controls='base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role'","controls='base_age base_age2 base_tenure base_tenure2 i.base_rank i.base_role'+(' base_growth base_lngdppc base_lnpop' if spec.endswith('_econ') else '')")
(O/'code/prepare_economic_lp_dml.py').write_text(s,encoding='utf8')
s=(WORK/'fit_doubleml_post4.py').read_text(encoding='utf-8-sig')
s=rep(s,"\\LPDID_DoubleML_fixed_connection_post4'","\\with_officer_city_economics\\LPDID_DoubleML_common_sample'")
s=rep(s,"for learner in ['Ridge_Logit','RandomForest']:","for base_learner,use_econ in [('Ridge_Logit',False),('RandomForest',False),('Ridge_Logit',True),('RandomForest',True)]:\n  learner=base_learner+('_econ' if use_econ else '_base')\n  used_features=features+(['base_growth','base_lngdppc','base_lnpop'] if use_econ else [])")
s=rep(s,"if learner=='Ridge_Logit':","if base_learner=='Ridge_Logit':")
s=rep(s,"x_cols=features","x_cols=used_features")
s=rep(s,"dict(method='DoubleML_DID',learner=learner,","dict(method='DoubleML_DID',learner=learner,economic_controls=use_econ,")
s=rep(s,"len(rows)==16","len(rows)==32")
s=rep(s,"features=features,cluster=","features=features,economic_features=['base_growth','base_lngdppc','base_lnpop'],cluster=")
(O/'code/fit_economic_doubleml.py').write_text(s,encoding='utf8')
for name in ['prepare_lp_dml_post4.py','fit_doubleml_post4.py','sun_abraham_post4.py']:
 target=O/'code'/name
 if (WORK/name).resolve()!=target.resolve():shutil.copy2(WORK/name,target)
print('Materialized LP-DiD and DoubleML economic-control scripts')
