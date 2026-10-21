from pathlib import Path
import sys,shutil
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\patron_retention_audit_2026_10_21\departed_leaders')
a=pd.read_csv(OUT/'leader_network_sizes.csv');pairs=pd.read_csv(OUT/'leader_city_dyads.csv')
assert not pairs.duplicated(['scope','horizon_months','phase','province','leader_id','leader_role','city_official_id']).any()
g=a[a.scope.eq('Current_city_principals')].copy();depart=g[g.retained.eq(0)]
s=depart.groupby(['horizon_months','phase']).agg(leaders=('leader_id','size'),
  distinct_leaders=('leader_id','nunique'),provinces=('province_code','nunique'),
  total_confirmed_connections=('connected_city_officials','sum'),
  mean_connections=('connected_city_officials','mean'),median_connections=('connected_city_officials','median'),
  known_pairs=('known_pairs','sum'),unknown_pairs=('unknown_pairs','sum'),
  mean_connected_share_pct=('connected_pct_known','mean')).reset_index()
s['pooled_connected_share_pct']=100*s.total_confirmed_connections/s.known_pairs
s['unknown_share_pct']=100*s.unknown_pairs/(s.known_pairs+s.unknown_pairs)
# Province-block percentile bootstrap of unadjusted group composition contrasts.
rng=np.random.default_rng(20261015);contrasts=[];intervals=[]
for h in [12,24,36]:
    q=g[g.horizon_months.eq(h)];provs=sorted(q.province_code.unique());P=len(provs)
    weights=rng.multinomial(P,np.full(P,1/P),size=9999)
    dist={}
    for phase in ['Before','After']:
        z=q[q.phase.eq(phase)&q.retained.eq(0)]
        stats=z.groupby('province_code').agg(n=('leader_id','size'),degree=('connected_city_officials','sum'),
                 edges=('connected_city_officials','sum'),known=('known_pairs','sum')).reindex(provs,fill_value=0)
        n=weights@stats.n.to_numpy();total=weights@stats.degree.to_numpy()
        deg=np.divide(total,n,out=np.full(9999,np.nan),where=n>0)
        known=weights@stats.known.to_numpy();edges=weights@stats.edges.to_numpy()
        share=np.divide(100*edges,known,out=np.full(9999,np.nan),where=known>0)
        dist[phase]=(deg,share)
        lo,hi=np.nanquantile(deg,[.025,.975]);s.loc[(s.horizon_months==h)&(s.phase==phase),['mean_ci_low','mean_ci_high']]=[lo,hi]
    before=s[(s.horizon_months==h)&s.phase.eq('Before')].iloc[0]
    after=s[(s.horizon_months==h)&s.phase.eq('After')].iloc[0]
    for field,idx in [('mean_connections',0),('pooled_connected_share_pct',1)]:
        diff=dist['After'][idx]-dist['Before'][idx];lo,hi=np.nanquantile(diff,[.025,.975])
        contrasts.append(dict(horizon_months=h,metric=field,after_minus_before=after[field]-before[field],
            ci95_low=lo,ci95_high=hi,valid_bootstraps=int(np.isfinite(diff).sum()),province_blocks=P))
contrasts=pd.DataFrame(contrasts)
roles=depart.groupby(['horizon_months','phase','leader_role']).agg(leaders=('leader_id','size'),
  mean_connections=('connected_city_officials','mean'),median_connections=('connected_city_officials','median'),
  known_pairs=('known_pairs','sum'),unknown_pairs=('unknown_pairs','sum')).reset_index()
for name,df in [('departed_comparison',s),('unadjusted_composition_contrasts',contrasts),('departed_by_role',roles)]:df.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
with pd.ExcelWriter(OUT/'离任省级领导_巡视前后关系人数比较.xlsx') as w:
    s.to_excel(w,sheet_name='Departed_groups',index=False);contrasts.to_excel(w,sheet_name='Descriptive_differences',index=False)
    roles.to_excel(w,sheet_name='By_S_G',index=False);a.to_excel(w,sheet_name='All_leaders',index=False)
    pairs.to_excel(w,sheet_name='Relation_evidence',index=False)
fig,ax=plt.subplots(figsize=(9,5.5))
for phase,offset,color,label in [('Before',-.12,'#287f9d','Departed before inspection'),('After',.12,'#ce8730','Departed after inspection')]:
    z=s[s.phase.eq(phase)].sort_values('horizon_months');x=np.arange(3)+offset
    ax.errorbar(x,z.mean_connections,yerr=[z.mean_connections-z.mean_ci_low,z.mean_ci_high-z.mean_connections],fmt='o',linestyle='none',capsize=4,color=color,label=label)
    for xx,r in zip(x,z.itertuples()):ax.annotate(f'n={r.leaders}',(xx,r.mean_connections),(0,8),textcoords='offset points',ha='center',fontsize=9)
ax.set_xticks(range(3),['12 months','24 months','36 months']);ax.set_ylabel('Confirmed city-official ties per departing leader')
ax.set_title('City-official network size of departing provincial leaders\nTies measured at the start of each pre/post window')
ax.legend(frameon=False);ax.grid(axis='y',alpha=.2);ax.set_ylim(bottom=0)
fig.text(.08,.025,'Pre-2012 prior cowork ties (at least 6 months); current city principals in the same province.\n95% province-block bootstrap percentile intervals; descriptive. Unknown ties are not coded zero.\nMunicipalities excluded; windows overlap across horizons. Not a corruption-removal classification.',fontsize=9)
fig.subplots_adjust(bottom=.24,top=.84);fig.savefig(OUT/'departed_leader_connection_comparison.png',dpi=180);plt.close(fig)
for filename in ['departed_leader_connections.py','report_departed_leaders.py']:
    shutil.copy2(Path(__file__).parent/filename,OUT/filename)
print(s.to_string(index=False));print(contrasts.to_string(index=False));print(roles.to_string(index=False))
