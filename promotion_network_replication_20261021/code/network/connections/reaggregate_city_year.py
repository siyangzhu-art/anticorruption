import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from replication_config import PROJECT_ROOT, CPED_ZIP
"""Keep ambiguous county/district records separate from ordinary prefecture units."""
import pandas as pd

def reaggregate(A,out):
 agg=[]
 for (year,p,c,scope),g in A.groupby(['year','province_code','city_code','scope']):
  z={'year':year,'province_code':p,'province':g.province.iloc[0],'city_code':c,'city':g.city.iloc[0],'scope':scope,
     'n_observed_city_leaders':g.city_id.nunique(),'n_observed_provincial_leaders':g.province_id.nunique(),'n_dyads':len(g)}
  for label,sub in [('all',g),('top',g[g.top_four.eq(1)]),('city_secretary_to_province_secretary',g[g.city_is_secretary.eq(1)&g.province_is_secretary.eq(1)]),('city_secretary_to_governor',g[g.city_is_secretary.eq(1)&g.province_is_governor.eq(1)]),('mayor_to_province_secretary',g[g.city_is_mayor.eq(1)&g.province_is_secretary.eq(1)]),('mayor_to_governor',g[g.city_is_mayor.eq(1)&g.province_is_governor.eq(1)])]:
   z[label+'_n_dyads']=len(sub)
   for typ in ['hometown_prefecture','classmate_6m','cowork_6m','connected']:
    v=sub[typ].dropna();z[label+'_'+typ]=1 if (v==1).any() else (0 if len(sub)>0 and len(v)==len(sub) else None)
   z[label+'_n_recorded_connected_province_people']=sub.loc[sub.any_recorded_tie.eq(1),'province_id'].nunique() if len(sub)>0 else None
  agg.append(z)
 C=pd.DataFrame(agg)
 C.to_csv(out/'city_year_connections.csv',index=False,encoding='utf-8-sig')
 C[C.scope.eq('prefecture')].to_csv(out/'prefecture_city_year_connections.csv',index=False,encoding='utf-8-sig')
 assert not C.duplicated(['year','province_code','city_code','scope']).any()
 return C
