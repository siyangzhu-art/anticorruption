from pathlib import Path
import shutil
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'tenure_stage_role_all_methods';W=Path(__file__).parent
s=(W/'fit_doubleml_post4.py').read_text(encoding='utf-8-sig')
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("\\LPDID_DoubleML_fixed_connection_post4'","\\tenure_stage_role_all_methods'")
rep("O/'horizon_pairs.csv.gz'","O/'data/horizon_pairs.csv.gz'")
rep('def splits(q,h):',"quadratic_features=features+['base_growth','base_lngdppc','base_lnpop']\nstage_features=[x for x in features if x not in ['base_tenure','base_tenure2','base_role']]+['base_growth','base_lngdppc','base_lnpop']\nfor cell in range(1,12):\n nm='stage_role_'+str(cell);Q[nm]=Q.base_stage_role.eq(cell).astype(float);stage_features.append(nm)\nfeature_sets={'quadratic':quadratic_features,'stage_role':stage_features}\ndef splits(q,h):")
rep("for learner in ['Ridge_Logit','RandomForest']:","for tenure_spec in ['quadratic','stage_role']:\n  for base_learner in ['Ridge_Logit','RandomForest']:\n   pass\n for tenure_spec,base_learner in [(s,l) for s in ['quadratic','stage_role'] for l in ['Ridge_Logit','RandomForest']]:\n  learner=base_learner+'_'+tenure_spec\n  used_features=feature_sets[tenure_spec]")
# Remove the temporary syntactic loop; all fits use one explicit product loop.
rep(" for tenure_spec in ['quadratic','stage_role']:\n  for base_learner in ['Ridge_Logit','RandomForest']:\n   pass\n",'')
rep("if learner=='Ridge_Logit':","if base_learner=='Ridge_Logit':")
rep('x_cols=features','x_cols=used_features')
rep("dict(method='DoubleML_DID',learner=learner,","dict(method='DoubleML_DID',learner=learner,base_learner=base_learner,tenure_spec=tenure_spec,")
rep('features=features,cluster=','feature_sets=feature_sets,cluster=')
rep('len(rows)==16','len(rows)==32')
rep("shutil.copy2(__file__,O/'code'/Path(__file__).name)","if Path(__file__).resolve()!=(O/'code'/Path(__file__).name).resolve():shutil.copy2(__file__,O/'code'/Path(__file__).name)")
(W/'fit_tenure_stage_DML.py').write_text(s,encoding='utf8');shutil.copy2(W/'fit_tenure_stage_DML.py',O/'code/fit_tenure_stage_DML.py');shutil.copy2(__file__,O/'code'/Path(__file__).name)
print('Generated 32 DoubleML fits with the same seed, folds, repetitions and learner settings.')
