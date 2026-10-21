"""Run in a new output tree. Never overwrite the delivered estimates."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, shutil
ROOT=Path(__file__).resolve().parent
BN="promotion_connections_revised_2006_2017_2026_10_20"
JOBS=json.loads((ROOT/'code/estimation/jobs.json').read_text())

def network():
 from replication_config import PROJECT_ROOT, CPED_ZIP
 if not CPED_ZIP.exists():raise FileNotFoundError('Supply the authorized CPED zip; see DATA_ACCESS.md')
 (PROJECT_ROOT/'result/network_reaudit_2026_10_20').mkdir(parents=True,exist_ok=True)
 assert hashlib.sha256(CPED_ZIP.read_bytes()).hexdigest()=='1427471e045e5e4f26b1ce39bb6f8ea024476d099b8478aaf984893c1cf24526'
 scripts=[('connections','build_connections.py'),('connections','build_candidate_network.py'),('connections','audit_and_document.py'),('connections','finish_delivery.py'),('person','build_person_network.py'),('person','audit_person_network.py'),('person','finish_person_network.py'),('person','rerun_original_source_checks.py'),('person','recheck_temporal_network.py'),('person','recheck_edge_completeness.py'),('person','report_temporal_reaudit.py')]
 for folder,name in scripts:
  cmd=[sys.executable,'-X','utf8',str(ROOT/'code/network'/folder/name)]
  if name=='build_person_network.py':cmd+=['--output',str(PROJECT_ROOT/'result/cped_pre_anticorruption_person_network_20261019'),'--inputs',str(PROJECT_ROOT/'result/cped_city_province_connections_20261019'),'--zip',str(CPED_ZIP)]
  print('Running network:',name,flush=True);subprocess.run(cmd,check=True,cwd=ROOT)

def estimates(jobs,stata,inputs):
 base=inputs/'result'/BN
 if not base.exists():raise FileNotFoundError('Authorized processed inputs missing. See DATA_ACCESS.md; no individual CPED data are public.')
 stata=stata or os.environ.get('STATA_EXE') or shutil.which('stata-mp') or shutil.which('stata')
 if not stata:raise RuntimeError('Set STATA_EXE to Stata 18 executable')
 for job in jobs:
  output=ROOT/'rerun/estimation'/job;output.mkdir(parents=True,exist_ok=True)
  def stpath(p):
   # Stata on Windows can reject existing input paths longer than MAX_PATH.
   if os.name=='nt':
    import ctypes
    buf=ctypes.create_unicode_buffer(32768)
    if ctypes.windll.kernel32.GetShortPathNameW(str(p),buf,len(buf)):return Path(buf.value).as_posix()
   return p.as_posix()
  s=(ROOT/'code/estimation'/f'{job}.do.in').read_text(encoding='utf-8')
  s=s.replace('@OUTPUT@',stpath(output)).replace('@BASE@',stpath(base))
  missing=[]
  # Fail before estimation if the input panel list is incomplete.
  for raw in re.findall(r'^use "([^"]+)"',s,re.M):
   p=Path(raw.replace("`base'",base.as_posix()))
   if not p.exists():missing.append(str(p))
  if missing:raise FileNotFoundError(json.dumps(missing,indent=2))
  do=output/'run.do';do.write_text(s,encoding='utf-8')
  startup=None
  if os.name=='nt':
   startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
  print('Running estimation:',job,flush=True)
  cmd=[str(stata),'/e','do',str(do)] if os.name=='nt' else [str(stata),'-b','do',str(do)]
  proc=subprocess.run(cmd,cwd=output,startupinfo=startup)
  expected=output/JOBS[job][1]
  if not expected.exists():raise RuntimeError(f'{job} did not produce {expected.name}; inspect rerun logs. Return code={proc.returncode}')
  validate(job,expected)
  if job=='cumulative':
   import pandas as pd,numpy as np
   ref=pd.read_csv(ROOT/'expected/cumulative_wild.csv');new=pd.read_stata(output/'wild_tests.dta')
   q=ref.merge(new,on='model_id',suffixes=('_expected','_rerun'),validate='1:1')
   assert len(q)==12 and q.rc_rerun.eq(0).all() and np.allclose(q.p_wild_expected,q.p_wild_rerun,atol=1e-12,rtol=0)
   (output/'wild_replication_validation.json').write_text(json.dumps({'tests':12,'passed':True,'max_abs_difference':float((q.p_wild_expected-q.p_wild_rerun).abs().max())},indent=2),encoding='utf-8')
   print('12 fixed-seed wild-bootstrap tests: PASS',flush=True)

def validate(job,p):
 import pandas as pd,numpy as np
 old=pd.read_csv(ROOT/'expected'/f'{job}.csv');new=pd.read_stata(p)
 keys=[c for c in ['family','variant','method','fe','term','model_id','estimator'] if c in old and c in new]
 assert keys and not old.duplicated(keys).any() and not new.duplicated(keys).any()
 q=old.merge(new,on=keys,suffixes=('_expected','_rerun'),validate='1:1')
 assert len(q)==len(old)==len(new),(job,len(q),len(old),len(new))
 checks=[]
 for col in ['b','se','p','lo','hi','N','G']:
  if col+'_expected' in q:
   a=q[col+'_expected'].to_numpy(dtype=float);b=q[col+'_rerun'].to_numpy(dtype=float)
   assert np.allclose(a,b,atol=1e-7,rtol=1e-7,equal_nan=True),(job,col)
   checks.append(dict(column=col,max_abs_difference=float(np.nanmax(np.abs(a-b)))))
 result=dict(job=job,contrasts=len(q),passed=True,checks=checks)
 p.with_name('replication_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result),flush=True)

def integrity():
 from validate_package import validate
 validate(ROOT)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['network','estimates','check']);p.add_argument('--jobs',nargs='+',choices=list(JOBS),default=['main','corruption','cumulative','hometown_school','union_ties']);p.add_argument('--stata');p.add_argument('--inputs',type=Path,default=ROOT/'inputs/project');a=p.parse_args()
 if a.command=='network':network()
 elif a.command=='estimates':estimates(a.jobs,a.stata,a.inputs.resolve())
 else:integrity()
