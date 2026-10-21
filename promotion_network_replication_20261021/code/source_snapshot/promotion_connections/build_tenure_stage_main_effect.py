"""User steering: stage main effects, no stage-by-role interactions."""
from pathlib import Path
import shutil
W=Path(__file__).parent
s=(W/'tenure_stage_prepare.py').read_text(encoding='utf-8-sig')
def rep(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
rep("O=B/'tenure_stage_role_all_methods'","O=B/'tenure_stage_main_effect_all_methods'")
rep("tenure_spec='stage_role'","tenure_spec='stage_only'")
rep('i.tenure_stage##i.role_secretary','i.tenure_stage i.role_secretary')
rep('i.base_stage##i.base_role','i.base_stage i.base_role')
rep("if config['tenure_spec']=='quadratic' else [])","if config['tenure_spec']=='quadratic' else ['base_role'])")
rep('pd.get_dummies(q.base_stage_role,drop_first=True','pd.get_dummies(q.base_stage,drop_first=True')
rep("if config['tenure_spec']=='stage_role'","if config['tenure_spec']=='stage_only'")
(W/'tenure_stage_main_prepare.py').write_text(s,encoding='utf8')
print('Built main-effect preparation script.')
