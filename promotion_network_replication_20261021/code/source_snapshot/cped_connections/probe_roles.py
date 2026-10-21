from pathlib import Path
import pandas as pd
p=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\data\cped_connections_20261019')
e=pd.read_pickle(p/'全部经历.pkl').fillna('')
for pat in ['省','市']:
 d=e[e['标志位'].str.contains(pat)]
 print(pat,'geos',d['地方一级关键词'].value_counts().to_string())
 print('bad-city',d[d['二级关键词编码'].eq('')].shape if pat=='市' else '')
print('school date duration')
q=e[e['基本大类别']=='学校'].copy();q['s']=pd.to_datetime(q['起始时间（YYYY-MM-DD）'],errors='coerce');q['e']=pd.to_datetime(q['终止时间（（YYYY-MM-DD））'],errors='coerce');q['days']=(q.e-q.s).dt.days
print(q[q['具体职务'].str.contains('学生|学员|研究生')]['days'].describe().to_string())
print('source row index preserved?',e.index.min(),e.index.max())
print(pd.read_pickle(p/'地区关键词.pkl').loc[lambda x:x['级别']=='省',['编码','名称']].to_string(index=False))
