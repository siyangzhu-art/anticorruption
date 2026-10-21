"""Add all FE-only benchmarks, without selecting by observed significance."""
from pathlib import Path
import pandas as pd,shutil
O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20\cumulative_promotion_TWFE_12_24_36m')
M=pd.read_csv(O/'model_design.csv');assert not M.control.eq('none').any()
extra=M[M.control.eq('personal')].copy();extra['model_id']=range(int(M.model_id.max())+1,int(M.model_id.max())+1+len(extra));extra['control']='none'
pd.concat([M,extra],ignore_index=True).to_csv(O/'model_design.csv',index=False,encoding='utf-8-sig')
L=[]
for m in extra.itertuples():
 L += [f'use "`out\'/data/{m.filename}", clear','isid person_id post',f'capture noisily reghdfe Y CP, absorb({m.absorb}) vce(cluster anchor_province)','local rc=_rc',f'if `rc\'!=0 post `ff\' ({m.model_id}) (`rc\')','if `rc\'==0 {',f'assert e(N)=={m.N}','assert _se[CP]>0','local NN=e(N)','local GG=e(N_clust)','local DD=e(df_r)','quietly lincom CP, level(95)',f'post `rr\' ({m.model_id}) (r(estimate)) (r(se)) (r(p)) (r(lb)) (r(ub)) (`NN\') (`GG\') (`DD\') (e(df_m)+e(df_a))','}']
p=O/'code/run_TWFE.do';s=p.read_text(encoding='utf8');needle="postclose `rr'";assert s.count(needle)==1;s=s.replace(needle,'\n'.join(L)+'\n'+needle);p.write_text(s,encoding='utf8');shutil.copy2(__file__,O/'code'/Path(__file__).name)
print('Added 18 FE-only benchmarks; total 54 TWFE models.')
