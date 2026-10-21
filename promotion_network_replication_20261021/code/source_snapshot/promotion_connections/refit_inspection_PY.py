"""Include inspection main effect when additive province/year FE do not absorb it."""
import pandas as pd,json,shutil
from estimate import OUT,sample,support,reason,fit
S=pd.read_csv(OUT/'model_status.csv');R=pd.read_csv(OUT/'all_estimates.csv');mask=S.kind.eq('pooled')&S.fe.eq('PY')&S.axis.isin(['inspection_main','inspection_drop_entry']);ids=set(S.loc[mask,'model_id']);new=[];failed=[]
base={u:pd.read_csv(OUT/f,low_memory=False) for u,f in [('annual','annual_official_panel.csv.gz'),('term','term_destination_panel.csv.gz')]}
for i,r in S[mask].iterrows():
 d=sample(base[r.unit][base[r.unit].role.eq(r.role)],r.outcome,r.relation,r.timing,r.controls,r.sampling);d=d[d.first_inspection_year.notna()].copy()
 if r.axis=='inspection_drop_entry':d=d[d.k.ne(0)].copy()
 d['post']=d.year.ge(d.first_inspection_year).astype(float);assert len(d)==r.N
 why=reason(support(d,True))
 if not why:
  try:
   rr=fit(d,r.controls,r.fe,True)
   meta={c:r[c] for c in ['kind','unit','role','outcome','relation','timing','controls','fe','sampling','axis','width','center','mixed','model_id']}
   for x in rr:new.append({**meta,**x,'primary_test':0})
  except Exception as ex:why=str(ex)
 S.at[i,'status']=why or 'OK'
 if why:failed.append({'model_id':r.model_id,'status':why})
R=pd.concat([R[~R.model_id.isin(ids)],pd.DataFrame(new)],ignore_index=True).sort_values(['model_id','leader','estimand']);R.to_csv(OUT/'all_estimates.csv',index=False,encoding='utf-8-sig');S.to_csv(OUT/'model_status.csv',index=False,encoding='utf-8-sig')
est=json.loads((OUT/'estimation_summary.json').read_text(encoding='utf8'));est.update(models_ok=int(S.status.eq('OK').sum()),status_counts=S.status.value_counts().to_dict(),estimates=len(R),inspection_main_effect='Explicit nuisance regressor in additive province+year FE; absorbed in province*year FE')
(OUT/'estimation_summary.json').write_text(json.dumps(est,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'inspection_PY_refit_summary.json').write_text(json.dumps({'models_revisited':len(ids),'models_success':len(new)//6,'failed':failed,'primary_models_unchanged':True},ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(__file__,OUT/'code/refit_inspection_PY.py');shutil.copy2(__file__.replace('refit_inspection_PY.py','estimate.py'),OUT/'code/estimate.py');print('Revisited',len(ids),'supplementary models')
