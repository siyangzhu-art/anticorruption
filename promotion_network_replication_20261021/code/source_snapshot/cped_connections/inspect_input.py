from pathlib import Path
import zipfile,io,json
import pandas as pd

src=Path(r'C:\Users\siyang zhu\Downloads\rerequestforaccesstothecped.zip')
out=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\data\cped_connections_20261019')
out.mkdir(parents=True,exist_ok=True)
report={}
with zipfile.ZipFile(src) as z:
    print(z.namelist())
    for n in z.namelist():
        if not n.endswith('.xlsx'): continue
        xl=pd.ExcelFile(io.BytesIO(z.read(n)))
        report[n]={}
        for s in xl.sheet_names:
            df=xl.parse(s).dropna(how='all')
            report[n][s]={'shape':df.shape,'columns':df.columns.tolist(),'head':df.head(5).astype(str).to_dict('records')}
            df.to_pickle(out/(s+'.pkl'))
            print(n,s,df.shape,df.columns.tolist())
(out/'schema.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
