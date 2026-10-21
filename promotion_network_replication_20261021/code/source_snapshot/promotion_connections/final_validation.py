from pathlib import Path
import sys,json,shutil,hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
from scipy.linalg import lstsq
from scipy.stats import t
from estimate import OUT,sample,fit,holm,C1,ECON
R=pd.read_csv(OUT/'all_estimates.csv');V=pd.read_stata(OUT/'stata_primary_validation.dta',convert_categoricals=False)
primary=R[R.primary_test.eq(1)];q=primary.merge(V,on=['model_id','leader','estimand'],suffixes=('_python','_stata'),validate='1:1');checks=[]
def ck(name,ok,detail):checks.append(dict(check=name,passed=bool(ok),detail=str(detail)))
for c in ['b','se','p','lo','hi','N','K','G','df']:
 error=float(abs(q[c+'_python']-q[c+'_stata']).max());ck('Independent Stata primary '+c,np.allclose(q[c+'_python'],q[c+'_stata'],atol=2e-7,rtol=2e-7),error)
ck('All eight primary change bootstraps completed',len(V[V.estimand.eq('change')])==8 and V.loc[V.estimand.eq('change'),'boot_rc'].eq(0).all(),V.loc[V.estimand.eq('change'),'boot_rc'].tolist())
R=R.merge(V[['model_id','leader','estimand','p_wild']],on=['model_id','leader','estimand'],how='left',validate='1:1');R['holm_eight_wild_changes']=np.nan
mask=R.primary_test.eq(1)&R.estimand.eq('change');R.loc[mask,'holm_eight_wild_changes']=holm(R.loc[mask,'p_wild'])
R.to_csv(OUT/'all_estimates_validated.csv',index=False,encoding='utf-8-sig');R[R.primary_test.eq(1)].to_csv(OUT/'primary_pooled_estimates_validated.csv',index=False,encoding='utf-8-sig')

# Independent explicit FE-dummy regression, including rank and clustering corrections.
A=pd.read_csv(OUT/'annual_official_panel.csv.gz',low_memory=False);tests=[]
for role,center,fe in [('mayor',2005,'PXY'),('mayor',2015,'PXY'),('secretary',2010,'PY'),('secretary',2015,'CITY_PXY')]:
 d=sample(A[A.role.eq(role)],'promotion','cowork_6m','legacy','C1','common');d=d[d.year.between(center-2,center+2)].copy()
 ref=R[R.kind.eq('rolling')&R.unit.eq('annual')&R.role.eq(role)&R.outcome.eq('promotion')&R.relation.eq('cowork_6m')&R.timing.eq('legacy')&R.controls.eq('C1')&R.fe.eq(fe)&R.sampling.eq('common')&R.axis.eq('calendar')&R.width.eq(5)&R.center.eq(center)]
 if len(ref)!=2:continue
 chunks=[np.ones((len(d),1)),d[['CS','CG',*C1]].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy()]
 for col in (['province_code','year'] if fe=='PY' else ['provyear'] if fe=='PXY' else ['city_code','provyear']):chunks.append(pd.get_dummies(d[col],drop_first=True,dtype=float).to_numpy())
 X=np.column_stack(chunks);norm=np.linalg.norm(X,axis=0);Xn=X/norm;beta,_,rank,_=lstsq(Xn,d.Y.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');b=beta/norm;res=d.Y.to_numpy()*100-X@b
 bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10);codes=pd.factorize(d.province_code)[0];G=int(codes.max()+1);score=np.zeros((G,X.shape[1]));np.add.at(score,codes,Xn*res[:,None]);VV=(bread@(score.T@score)@bread)*G/(G-1)*(len(d)-1)/(len(d)-rank);VV=VV/norm[:,None]/norm[None,:]
 for lead,col in [('S',1),('G',2)]:
  row=ref[ref.leader.eq(lead)].iloc[0];se=float(np.sqrt(max(0,VV[col,col])));errb=abs(b[col]-row.b);errs=abs(se-row.se);ok=errb<1e-6 and errs<2e-5
  tests.append(dict(role=role,center=center,fe=fe,leader=lead,b_dense=b[col],b_saved=row.b,se_dense=se,se_saved=row.se,error_b=errb,error_se=errs,passed=ok,N=len(d),K_dense=int(rank),K_saved=int(row.K)))
ck('Four predefined rolling models explicit FE-dummy coefficients and SEs',len(tests)==8 and all(x['passed'] for x in tests),{'contrasts':len(tests),'max_b_error':max(x['error_b'] for x in tests),'max_se_error':max(x['error_se'] for x in tests)})
pd.DataFrame(tests).to_csv(OUT/'explicit_dummy_rolling_validation.csv',index=False,encoding='utf-8-sig')
# Additive province/year FE inspection specification also needs the Post main effect.
d=sample(A[A.role.eq('mayor')],'promotion','cowork_6m','legacy','C1','common');d['post']=d.year.ge(d.first_inspection_year).astype(float)
target=np.column_stack([d.CS,d.CG,d.CS*d.post,d.CG*d.post]);chunks=[np.ones((len(d),1)),target,d[['post',*C1]].to_numpy(float),pd.get_dummies(d.base_rank,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(d.province_code,drop_first=True,dtype=float).to_numpy(),pd.get_dummies(d.year,drop_first=True,dtype=float).to_numpy()]
X=np.column_stack(chunks);norm=np.linalg.norm(X,axis=0);Xn=X/norm;bb,_,rank,_=lstsq(Xn,d.Y.to_numpy()*100,cond=1e-10,lapack_driver='gelsd');bb=bb/norm;err=d.Y.to_numpy()*100-X@bb;bread=np.linalg.pinv(Xn.T@Xn,rcond=1e-10);codes=pd.factorize(d.province_code)[0];G=int(codes.max()+1);score=np.zeros((G,X.shape[1]));np.add.at(score,codes,Xn*err[:,None]);cov=bread@(score.T@score)@bread*G/(G-1)*(len(d)-1)/(len(d)-rank);cov=cov/norm[:,None]/norm[None,:]
reference=R[R.kind.eq('pooled')&R.unit.eq('annual')&R.role.eq('mayor')&R.outcome.eq('promotion')&R.relation.eq('cowork_6m')&R.timing.eq('legacy')&R.controls.eq('C1')&R.fe.eq('PY')&R.sampling.eq('common')&R.axis.eq('inspection_main')]
extra=[]
for lead,j in [('S',1),('G',2)]:
 for est in ['pre','post','change']:
  L=np.zeros(X.shape[1]);L[j]=int(est in ['pre','post']);L[j+2]=int(est in ['post','change']);b0=float(L@bb);s0=float(np.sqrt(L@cov@L));r=reference[reference.leader.eq(lead)&reference.estimand.eq(est)].iloc[0];extra.append(dict(leader=lead,estimand=est,b_dense=b0,b_saved=r.b,se_dense=s0,se_saved=r.se,passed=abs(b0-r.b)<1e-6 and abs(s0-r.se)<2e-5))
pd.DataFrame(extra).to_csv(OUT/'explicit_dummy_inspection_PY_validation.csv',index=False,encoding='utf-8-sig');ck('Inspection Post main effect: independent additive-FE pooled validation',all(x['passed'] for x in extra),len(extra))
ck('Every successful model has two leader coefficients / six pooled contrasts',all(g.leader.nunique()==2 and len(g)==(6 if g.kind.iloc[0]=='pooled' else 2) for _,g in R.groupby('model_id')),R.model_id.nunique())
ck('All CIs finite and ordered around estimate',np.isfinite(R[['b','se','lo','hi']]).all().all() and R.lo.le(R.b).all() and R.hi.ge(R.b).all(),len(R))
ck('Every coefficient retained regardless of sign or significance',len(R)==len(pd.read_csv(OUT/'all_estimates.csv')),len(R))
D=pd.read_csv(OUT/'data_validation_checks.csv');ck('All source/event/timing checks passed',D.passed.all(),len(D))
ROOT=OUT.parent.parent
prior=json.loads((ROOT/'result/network_reaudit_2026_10_20/temporal_audit_summary.json').read_text(encoding='utf8'))
for name,digest in prior['source_hashes'].items():ck('Original network file unchanged '+name,hashlib.sha256((ROOT/'result/cped_pre_anticorruption_person_network_20261019'/name).read_bytes()).hexdigest()==digest,name)
pd.DataFrame(checks).to_csv(OUT/'numerical_validation_checks.csv',index=False,encoding='utf-8-sig')
(OUT/'validation_summary.json').write_text(json.dumps({'checks':len(checks),'all_passed':all(x['passed'] for x in checks),'source_data_checks':len(D),'source_data_passed':bool(D.passed.all()),'primary_contrasts_stata':len(q),'independent_rolling_contrasts':len(tests),'independent_additive_FE_pooled_contrasts':len(extra)},ensure_ascii=False,indent=2),encoding='utf8')
print(pd.DataFrame(checks).to_string(index=False),flush=True);shutil.copy2(__file__,OUT/'code/final_validation.py')
assert all(x['passed'] for x in checks)
