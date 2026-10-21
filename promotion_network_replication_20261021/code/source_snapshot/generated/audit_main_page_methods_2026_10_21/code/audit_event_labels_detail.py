from pathlib import Path
import sys,zipfile,io,json
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd,numpy as np
B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20');O=B/'audit_main_page_methods_2026_10_21'
with zipfile.ZipFile(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip') as z:r=pd.read_excel(io.BytesIO(z.read('全部经历-20200606.xlsx')),sheet_name='全部经历').dropna(how='all')
r['row_id']=np.arange(2,len(r)+2);r['source_second_line']=r['基本大类别'].isin(['人大','政协'])
a=pd.read_csv(B/'with_officer_city_economics/annual_economics_rematched.csv.gz');p=a[a.promotion.eq(1)].merge(r[['row_id','source_second_line','基本大类别','标志位','具体职务','姓名','地方一级关键词']],left_on='event_row',right_on='row_id',validate='m:1')
p['flag_mismatch']=p.second_line.ne(p.source_second_line.astype(int));p.to_csv(O/'data/annual_event_label_details.csv',index=False,encoding='utf-8-sig')
print('annual second_line flag != first event source category',int(p.flag_mismatch.sum()));print(p[p.flag_mismatch][['name','year','event_job','基本大类别','second_line','source_second_line']].to_string(index=False))
bad=r[r['标志位'].astype(str).str.contains('副省长')&r.source_second_line]
bad.to_csv(O/'data/vice_governor_flag_vs_category_conflicts.csv',index=False,encoding='utf-8-sig');print('Contradictory vicegovernor and CPPCC/NPC fields',bad[['row_id','姓名','起始时间（YYYY-MM-DD）','终止时间（（YYYY-MM-DD））','具体职务','标志位','基本大类别','地方一级关键词']].to_string(index=False))
f=pd.read_csv(B/'control_FE_sensitivity_post4/fixed_panel.csv.gz');pp=p.merge(f[['person_id','year']],on=['person_id','year'],validate='1:1');print('main mismatch',pp[pp.flag_mismatch][['name','year','event_job','基本大类别','second_line','source_second_line']].to_string(index=False))
print('main positives first source second line',pp.source_second_line.sum(),'annual any source flag',pp.second_line.sum())
