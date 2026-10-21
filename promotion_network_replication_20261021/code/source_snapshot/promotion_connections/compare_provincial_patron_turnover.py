"""Symmetric pre/post inspection retention; no career records are overwritten."""
from pathlib import Path
import pandas as pd
BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
OUT=BASE/'patron_retention_audit_2026_10_21';OUT.mkdir(exist_ok=True)
p=pd.read_csv(BASE/'province_principal_spells.csv',parse_dates=['start','end'])
dates=pd.read_csv(BASE/'cumulative_promotion_TWFE_12_24_36m/inspection_dates_official_sources.csv',parse_dates=['inspection_date'])
def roster(prov,date):
    return p[p.province_code.eq(prov)&p.start.le(date)&p.end.gt(date)]
def clear(q):
    # One person temporarily holding both offices is not an ambiguous roster.
    return len(q)==2 and q.role.nunique()==2
rows=[];checks=[]
for r in dates.itertuples():
    for h in [12,24,36]:
        inspect=r.inspection_date
        schedules={'Before':(inspect-pd.DateOffset(months=h),inspect-pd.Timedelta(days=1)),
                   'After':(inspect,inspect+pd.DateOffset(months=h)-pd.Timedelta(days=1))}
        good=True;rec=[]
        for phase,(lo,hi) in schedules.items():
            start=roster(r.province_code,lo);end=roster(r.province_code,hi)
            ok=clear(start) and clear(end);good=good and ok
            checks.append(dict(province=r.province,horizon_months=h,phase=phase,start_date=lo,end_date=hi,
                start_names='; '.join(f'{x.name}:{x.role}' for x in start.itertuples()),
                end_names='; '.join(f'{x.name}:{x.role}' for x in end.itertuples()),
                clear_start=clear(start),clear_end=clear(end)))
            for z in start.itertuples():
                rec.append(dict(province=r.province,province_code=r.province_code,horizon_months=h,
                    phase=phase,start_date=lo,end_date=hi,leader_id=z.person_id,leader_name=z.name,
                    start_role=z.role,retained_either_S_G=int(z.person_id in set(end.person_id)),
                    retained_same_role=int(((end.person_id==z.person_id)&(end.role==z.role)).any()),
                    clear_phase_roster=ok))
        for z in rec:z['paired_province_eligible']=good
        rows.extend(rec)
rows=pd.DataFrame(rows);checks=pd.DataFrame(checks)
summary=[]
for sample,q in [('Paired clear rosters',rows[rows.paired_province_eligible]),('All recorded rosters (provisional)',rows)]:
    for (h,phase),g in q.groupby(['horizon_months','phase']):
        n=len(g);k=int(g.retained_either_S_G.sum())
        summary.append(dict(sample=sample,horizon_months=h,phase=phase,provinces=g.province.nunique(),
            baseline_leaders=n,retained_S_or_G=k,not_recorded_S_or_G=n-k,retention_pct=100*k/n))
summary=pd.DataFrame(summary)
for n,f in [('symmetric_retention_summary',summary),('symmetric_retention_leader_records',rows),('symmetric_retention_roster_checks',checks)]:
    f.to_csv(OUT/(n+'.csv'),index=False,encoding='utf-8-sig')
with pd.ExcelWriter(OUT/'巡视前后省级领导留任对比.xlsx') as w:
    summary.to_excel(w,sheet_name='Summary',index=False)
    rows.to_excel(w,sheet_name='Leader_records',index=False)
    checks.to_excel(w,sheet_name='Roster_checks',index=False)
assert not rows.duplicated(['province_code','horizon_months','phase','start_role']).any()
for h in [12,24,36]:
    g=rows[rows.horizon_months.eq(h)&rows.paired_province_eligible]
    assert set(g[g.phase.eq('Before')].province_code)==set(g[g.phase.eq('After')].province_code)
print(summary.to_string(index=False))
print('EXCLUDED PROVINCES BY HORIZON')
for h in [12,24,36]:print(h,rows.loc[rows.horizon_months.eq(h)&~rows.paired_province_eligible,'province'].unique().tolist())
