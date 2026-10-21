from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,csv,re
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  self.links += [v for k,v in attrs if k in ['href','src'] and v]
def validate(root):
 root=Path(root);missing=[];count=0
 for p in (root/'results').rglob('*.html'):
  q=Links();q.feed(p.read_text(encoding='utf-8'))
  for link in q.links:
   u=urlsplit(link)
   if u.scheme or u.netloc or not u.path:continue
   count+=1
   if not (p.parent/unquote(u.path)).exists():missing.append({'page':str(p.relative_to(root)),'link':link})
 assert not missing,missing
 bad=[str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.suffix in ['.dta','.gz']]
 assert not bad,bad
 identifier_pattern=r'(person.*id|official.*id|leader_id|leader_name|official_name|row_id|^start_names$|^end_names$|姓名)'
 for p in (root/'results').rglob('*.csv'):
  with p.open(encoding='utf-8-sig',newline='') as f:
   cols=next(csv.reader(f),[])
  assert not any(re.search(identifier_pattern,c,re.I) for c in cols),str(p)
 import openpyxl
 for p in (root/'results').rglob('*.xlsx'):
  wb=openpyxl.load_workbook(p,read_only=True,data_only=True)
  for sheet in wb:
   cols=[str(c) for c in next(sheet.iter_rows(max_row=1,values_only=True),[]) if c is not None]
   assert not any(re.search(identifier_pattern,c,re.I) for c in cols),(str(p),sheet.title)
  wb.close()
 with (root/'manifests/public_files.csv').open(encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f):
   p=root/r['path'];assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
 result={'html_local_links_checked':count,'broken_links':len(missing),'public_individual_panel_files':len(bad),'manifest_hashes':'PASS'}
 print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':validate(Path(__file__).resolve().parent)
