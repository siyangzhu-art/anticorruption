from pathlib import Path
import pandas as pd,zipfile,json,re,hashlib,shutil
from PIL import Image
from estimate_revised import OUT
checks=[]
def ck(n,v):checks.append({'check':n,'passed':bool(v)})
page=(OUT/'index.html').read_text(encoding='utf8')
links=re.findall(r'(?:src|href)="([^"]+)"',page)
ck('HTML references resolve',all((OUT/x).is_file() for x in links))
figs=list((OUT/'figures').glob('*.png'))
for x in figs:
 with Image.open(x) as im:im.verify()
ck('All 26 planned figures readable and present in gallery',len(figs)==26 and len(re.findall(r'<img ',page))==26)
xl=pd.ExcelFile(OUT/'晋升合并样本_2006_2017_修订结果.xlsx')
ck('Excel 13 sheets',len(xl.sheet_names)==13)
ck('Excel annual rows',len(pd.read_excel(xl,sheet_name='Annual_panel'))==7749)
ck('No PDF output',not list(OUT.rglob('*.pdf')))
ck('Primary 12 change tests',len(pd.read_csv(OUT/'primary_pooled_estimates_validated.csv').query("estimand=='change'"))==12)
ck('All data checks passed',pd.read_csv(OUT/'data_validation_checks.csv').passed.all())
ck('All numerical checks passed',pd.read_csv(OUT/'numerical_validation_checks.csv').passed.all())
ck('No lower-grade role-up events',not len(pd.read_csv(OUT/'annual_promotion_event_registry.csv').query("promotion==1 and base_rank>4 and event_rank=='正厅'")))
assert all(x['passed'] for x in checks)
(OUT/'delivery_validation.json').write_text(json.dumps({'checks':checks,'figures':len(figs),'passed':True},ensure_ascii=False,indent=2),encoding='utf8')
shutil.copy2(__file__,OUT/'code/delivery_revised_qc.py')
inputs=[OUT.parent/'promotion_connections_rolling_2026_10_20/annual_official_panel.csv.gz',OUT.parent/'promotion_connections_rolling_2026_10_20/term_destination_panel.csv.gz',Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')]
pd.DataFrame([dict(path=str(x),bytes=x.stat().st_size,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in inputs]).to_csv(OUT/'input_manifest.csv',index=False,encoding='utf-8-sig')
pd.DataFrame([dict(file=x.relative_to(OUT).as_posix(),bytes=x.stat().st_size,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in sorted(OUT.rglob('*')) if x.is_file() and x.name!='file_manifest.csv']).to_csv(OUT/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=OUT.parent/'省市关系与晋升_2006_2017_合并修订版.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for x in OUT.rglob('*'):
  if x.is_file():z.write(x,OUT.name+'/'+x.relative_to(OUT).as_posix())
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
print(json.dumps({'all_passed':True,'delivery_checks':len(checks),'figures':len(figs),'zip_bytes':zp.stat().st_size},ensure_ascii=False))
