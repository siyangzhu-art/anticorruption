from pathlib import Path
import pandas as pd
p=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\data\cped_connections_20261019')
e=pd.read_pickle(p/'全部经历.pkl').fillna('')
e.to_csv(p/'全部经历_raw.csv',index=False,encoding='utf-8-sig')
print('prov nonempty city');print(e.loc[e['标志位'].str.contains('省') & e['地方二级关键词'].ne(''),['用户编码','姓名','地方一级关键词','地方二级关键词','地方三级关键词','标志位','具体职务']].head(40).to_string(index=False))
print('role geography');print(e.loc[e['标志位'].str.contains('省|市'),['地方一级关键词','地区级别']].value_counts().tail(25).to_string())
print('school overlap positions top40');print(e.loc[e['基本大类别']=='学校','具体职务'].value_counts().head(40).to_string())
print('school aliases examples');s=pd.read_pickle(p/'学校关键词.pkl');print(s.loc[s['编码']!=s['别名编码']].head(20).to_string(index=False));print('alias diffs',sum(s['编码']!=s['别名编码']))
print('org aliases diff');s=pd.read_pickle(p/'职务关键词.pkl');print(s.loc[s['编码']!=s['别名']].head(15).to_string(index=False))
print('sub geo unknown');print(e.loc[e['地方三级关键词'].ne('') & e['地方二级关键词'].eq(''),['地方一级关键词','地方三级关键词','职务一级关键词','具体职务']].head(10).to_string(index=False))
print('gov central');print(e.loc[(e['是否全国性组织']=='是') & (e['基本大类别']!='学校'),['地方一级关键词','基本大类别','职务一级关键词','职务二级关键词','具体职务']].sample(20,random_state=20261015).to_string(index=False))
