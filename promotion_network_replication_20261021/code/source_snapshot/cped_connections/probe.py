from pathlib import Path
import pandas as pd
p=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\data\cped_connections_20261019')
e=pd.read_pickle(p/'全部经历.pkl').fillna('')
b=pd.read_pickle(p/'基本信息.pkl').fillna('')
for col in ['标志位','基本大类别','地区级别','级别']:
 print('\nCOUNTS',col,e[col].value_counts().to_string())
for term in ['省','市']:
 x=e[e['标志位'].str.contains(term)]
 print('\nROLE',term,len(x));print(x[['标志位','地区级别','基本大类别','职务一级关键词','具体职务']].value_counts().head(60).to_string())
 print(x.head(15).to_string(index=False))
print('\nEDUCATION positions');print(e.loc[e['基本大类别']=='学校','具体职务'].value_counts().to_string())
print('\nSCHOOL SAMPLE');print(e.loc[e['基本大类别']=='学校'].sample(25,random_state=20261015).to_string(index=False))
print('\nMissing hometown',b[['籍贯省','籍贯市','籍贯县/区']].replace('',pd.NA).isna().sum().to_dict())
print('\nNATIONAL');print(e[['是否全国性组织','是否中央派出']].value_counts().to_string())
