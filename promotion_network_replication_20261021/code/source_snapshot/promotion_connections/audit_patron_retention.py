"""Read-only audit of original provincial patrons in the cumulative TWFE cohort."""
from pathlib import Path
import pandas as pd

BASE=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
SRC=BASE/'cumulative_promotion_TWFE_12_24_36m'
OUT=BASE/'patron_retention_audit_2026_10_21';OUT.mkdir(exist_ok=True)
a=pd.read_csv(SRC/'cohort_anchor_all.csv.gz')
d=pd.read_csv(SRC/'all_estimation_panels.csv.gz')
ids=set(d.loc[d['sample'].eq('common_all_H'),'person_id'])
a=a[a.person_id.isin(ids)].copy()
p=pd.read_csv(BASE/'province_principal_spells.csv',parse_dates=['start','end'])
assert len(a)==422 and a.C0.eq(1).sum()==45
rows=[];dyads=[]
for r in a[a.C0.eq(1)].itertuples():
    anchor=pd.Timestamp(r.anchor_snapshot);inspection=pd.Timestamp(r.inspection_date)
    tied=[]
    for role in ['S','G']:
        if getattr(r,'legacy_cowork_6m_'+role)!=1:continue
        pid=int(getattr(r,role+'_person_id'));name=getattr(r,role+'_name')
        q=p[p.person_id.eq(pid)&p.province_code.eq(r.province_code)]
        assert ((q.start<=anchor)&(q.end>anchor)&q.role.eq(role)).any()
        tied.append((role,pid,name,q))
        dyads.append(dict(person_id=r.person_id,name=r.name,province=r.province,
                          patron_id=pid,patron_name=name,anchor_role=role,
                          anchor_snapshot=anchor,inspection_date=inspection,
                          province_spells='; '.join(f'{x.role}:{x.start.date()} to {x.end.date()}' for x in q.itertuples())))
    for h in [0,12,24,36]:
        # At inspection entry or immediately before the cumulative window ends.
        date=inspection if h==0 else inspection+pd.DateOffset(months=h)-pd.Timedelta(days=1)
        same=[];either=[]
        for role,pid,name,q in tied:
            active=q[q.start.le(date)&q.end.gt(date)]
            same.append(active.role.eq(role).any());either.append(len(active)>0)
        rows.append(dict(person_id=r.person_id,name=r.name,province=r.province,
                         province_code=r.province_code,months_after_entry=h,
                         assessment_date=date,anchor_snapshot=anchor,
                         inspection_date=inspection,any_original_patron_same_role=int(any(same)),
                         any_original_patron_S_or_G=int(any(either)),
                         original_patrons='; '.join(f'{z[2]} ({z[0]})' for z in tied),
                         source_scope='Recorded S/G office spells only; absence does not establish loss of all influence or corruption'))
out=pd.DataFrame(rows);dyads=pd.DataFrame(dyads)
summary=out.groupby('months_after_entry').agg(connected_officials=('person_id','nunique'),
     any_patron_same_role=('any_original_patron_same_role','sum'),
     any_patron_still_S_or_G=('any_original_patron_S_or_G','sum')).reset_index()
summary['no_original_patron_recorded_S_or_G']=summary.connected_officials-summary.any_patron_still_S_or_G
assert len(out)==45*4 and not out.duplicated(['person_id','months_after_entry']).any()
for name,frame in [('official_patron_retention',out),('original_tied_patron_dyads',dyads),('retention_summary',summary)]:
    frame.to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
with pd.ExcelWriter(OUT/'原联系省级领导任职持续性核查.xlsx') as w:
    summary.to_excel(w,sheet_name='Summary',index=False)
    out.to_excel(w,sheet_name='Officials_dates',index=False)
    dyads.to_excel(w,sheet_name='Original_dyads',index=False)
print(summary.to_string(index=False))
print('Distinct original patrons:',dyads.patron_id.nunique(),'distinct patron-province pairs:',len(dyads[['patron_id','province']].drop_duplicates()))
print('Already absent at entry:')
print(out[out.months_after_entry.eq(0)&out.any_original_patron_S_or_G.eq(0)][['name','province','original_patrons']].to_string(index=False))
print('Output:',OUT)
