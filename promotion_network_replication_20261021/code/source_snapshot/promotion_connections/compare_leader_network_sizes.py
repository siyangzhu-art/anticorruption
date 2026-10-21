"""Provincial leaders' predetermined city-principal ties: composition audit."""
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized')
BASE=ROOT/'result/promotion_connections_revised_2006_2017_2026_10_20'
OUT=BASE/'patron_retention_audit_2026_10_21/network_sizes';OUT.mkdir(exist_ok=True)
NET=ROOT/'result/cped_pre_anticorruption_person_network_20261019'
OLD=ROOT/'result/cped_city_province_connections_20261019'
anchors=pd.read_csv(BASE/'cumulative_promotion_TWFE_12_24_36m/cohort_anchor_all.csv.gz',parse_dates=['city_spell_start'])
pan=pd.read_csv(BASE/'cumulative_promotion_TWFE_12_24_36m/all_estimation_panels.csv.gz',usecols=['person_id','sample'])
fixed=anchors[anchors.person_id.isin(pan.loc[pan['sample'].eq('common_all_H'),'person_id'])].copy()
assert len(fixed)==422
p=pd.read_csv(BASE/'province_principal_spells.csv',parse_dates=['start','end'])
c=pd.read_csv(BASE/'city_principal_spells.csv',parse_dates=['start','end'])
lead=pd.read_csv(BASE/'patron_retention_audit_2026_10_21/symmetric_retention_leader_records.csv',parse_dates=['start_date','end_date'])
e=pd.read_csv(NET/'person_edges_pre2012.csv.gz',usecols=['person_a','person_b','cowork_6m','cowork_6m_first_formation'])
e=e[e.cowork_6m.eq(1)];forms={(int(r.person_a),int(r.person_b)):pd.Timestamp(r.cowork_6m_first_formation) for r in e.itertuples()}
amb=pd.read_csv(NET/'date_ambiguous_pairs_pre2012.csv.gz');amb=set(tuple(sorted((int(r.person_a),int(r.person_b)))) for r in amb[amb.relation.eq('cowork_6m')].itertuples())
j=pd.read_csv(OLD/'workplace_classification.csv.gz',usecols=['person_id','start','end','dates_valid','work_eligible'],parse_dates=['start','end'])
j=j[j.work_eligible&j.dates_valid].copy();j['threshold']=j.start+pd.DateOffset(months=6);j=j[j.threshold.le(j.end)]
qual=j.groupby('person_id').threshold.min().to_dict()
def tie(a,b,joint,snapshot):
    if a==b:return np.nan
    key=tuple(sorted((int(a),int(b))));cut=min(joint,snapshot,pd.Timestamp('2012-01-01'))
    formed=forms.get(key,pd.NaT)
    if pd.notna(formed) and formed<cut:return 1.
    known=all(qual.get(int(x),pd.Timestamp.max)<cut for x in [a,b]) and key not in amb
    return 0. if known else np.nan
# Reproduce every old relation flag in the exact original anchor setup first.
checks=[]
for r in fixed.itertuples():
    for role in ['S','G']:
        pid=getattr(r,role+'_person_id')
        if pd.isna(pid):continue
        joint=pd.Timestamp(getattr(r,'joint_start_'+role));date=pd.Timestamp(r.anchor_snapshot)
        old=getattr(r,'legacy_cowork_6m_'+role);new=tie(r.person_id,int(pid),joint,date)
        checks.append((pd.isna(old) and pd.isna(new)) or old==new)
assert all(checks)
rows=[];pairrows=[]
for r in lead.itertuples():
    if not r.paired_province_eligible:continue
    # Use the source office spell active at the phase's start.
    ls=p[p.person_id.eq(r.leader_id)&p.province_code.eq(r.province_code)&p.role.eq(r.start_role)&p.start.le(r.start_date)&p.end.gt(r.start_date)]
    assert len(ls)==1
    for scope in ['Fixed422','Current_city_principals']:
        if scope=='Fixed422':
            pool=fixed[fixed.province_code.eq(r.province_code)][['person_id','name','city_spell_start']].rename(columns={'city_spell_start':'start'})
        else:
            pool=c[c.province_code.eq(r.province_code)&c.start.le(r.start_date)&c.end.gt(r.start_date)].copy()
            n=pool.groupby(['city_code','role']).person_id.transform('nunique');pool=pool[n.eq(1)]
            bad=pool.groupby('person_id').city_code.nunique();pool=pool[~pool.person_id.isin(bad[bad.gt(1)].index)]
            pool['priority']=pool.role.map({'mayor':0,'secretary':1})
            pool=pool.sort_values('priority').drop_duplicates('person_id',keep='last')[['person_id','name','start']]
        pool=pool[pool.person_id.ne(r.leader_id)]
        # A province absent from the fixed 422-person cohort is outside this
        # estimand, not a leader with a verified zero-size client network.
        if len(pool)==0:continue
        vals=[]
        for z in pool.itertuples():
            v=tie(z.person_id,r.leader_id,max(z.start,ls.iloc[0].start),r.start_date);vals.append(v)
            pairrows.append(dict(scope=scope,horizon_months=r.horizon_months,phase=r.phase,
                province=r.province,leader_id=r.leader_id,leader_name=r.leader_name,leader_role=r.start_role,
                city_official_id=z.person_id,city_official_name=z.name,connection=v,start_date=r.start_date))
        v=pd.Series(vals,dtype=float);known=int(v.notna().sum());positive=int(v.eq(1).sum())
        rows.append(dict(scope=scope,horizon_months=r.horizon_months,phase=r.phase,province=r.province,
            province_code=r.province_code,leader_id=r.leader_id,leader_name=r.leader_name,leader_role=r.start_role,
            start_date=r.start_date,end_date=r.end_date,retained=r.retained_either_S_G,
            city_pool=len(v),known_pairs=known,unknown_pairs=int(v.isna().sum()),connected_city_officials=positive,
            connected_pct_known=100*positive/known if known else np.nan))
rows=pd.DataFrame(rows);pairs=pd.DataFrame(pairrows)
summary=rows.groupby(['scope','horizon_months','phase']).agg(
    leaders=('leader_id','size'),provinces=('province_code','nunique'),
    connection_pairs=('connected_city_officials','sum'),mean_connections_per_leader=('connected_city_officials','mean'),
    known_pairs=('known_pairs','sum'),unknown_pairs=('unknown_pairs','sum')).reset_index()
summary['connection_pct_known']=100*summary.connection_pairs/summary.known_pairs
groups=rows.groupby(['scope','horizon_months','phase','retained']).agg(
    leaders=('leader_id','size'),connection_pairs=('connected_city_officials','sum'),
    mean_connections_per_leader=('connected_city_officials','mean'),known_pairs=('known_pairs','sum'),unknown_pairs=('unknown_pairs','sum')).reset_index()
groups['connection_pct_known']=100*groups.connection_pairs/groups.known_pairs
union=[]
for key,g in pairs.groupby(['scope','horizon_months','phase']):
    flags=g.groupby(['province','city_official_id']).connection.agg(lambda x:1. if x.eq(1).any() else (0. if len(x)==2 and x.eq(0).all() else np.nan))
    union.append(dict(scope=key[0],horizon_months=key[1],phase=key[2],city_officials=len(flags),
        any_connected=int(flags.eq(1).sum()),none_connected=int(flags.eq(0).sum()),unknown=int(flags.isna().sum())))
union=pd.DataFrame(union)
for name,frame in [('leader_network_sizes',rows),('leader_city_dyads',pairs),('network_size_summary',summary),('retained_vs_departed_connections',groups),('any_leader_connection_counts',union)]:
    frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
with pd.ExcelWriter(OUT/'巡视前后省级领导关系人数.xlsx') as w:
    summary.to_excel(w,sheet_name='Before_after',index=False)
    groups.to_excel(w,sheet_name='Retained_departed',index=False)
    union.to_excel(w,sheet_name='Unique_city_officials',index=False)
    rows.to_excel(w,sheet_name='Leader_counts',index=False)
    pairs.to_excel(w,sheet_name='Dyad_audit',index=False)
print('Original anchor flag checks:',len(checks),'all passed')
print(summary.to_string(index=False))
print('FIXED COHORT RETAINED VS DEPARTED:')
print(groups[groups.scope.eq('Fixed422')].to_string(index=False))
print('UNION:');print(union[union.scope.eq('Fixed422')].to_string(index=False))
