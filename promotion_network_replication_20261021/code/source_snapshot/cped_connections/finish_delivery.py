from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,zipfile,shutil
O=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\cped_city_province_connections_20261019')
F=pd.read_csv(O/'pair_first_connection_dates.csv')
W=pd.read_csv(O/'不限同省同期_三类主关系首次形成.csv')
if 'hometown_prefecture' in W:
 home=W['hometown_prefecture'].notna()
 W['has_recorded_hometown_prefecture']=home.astype(int)
 W=W.rename(columns={'hometown_prefecture':'hometown_time_invariant_sort_sentinel','any_tie_first_formed':'any_tie_first_formed_sort_key'})
 W['first_formed_date_observed']=W['any_tie_first_formed_sort_key'].where(~home,'')
 W['formation_date_kind']=np.where(home,'includes_time_invariant_hometown_no_observed_date','recorded_school_or_work_overlap')
 W.to_csv(O/'不限同省同期_三类主关系首次形成.csv',index=False,encoding='utf-8-sig')
notes=[('数据来源','仅用户ZIP内两个工作簿；未补充外部资料。'),
 ('同乡主口径','同一籍贯省及地级市；同县、同省作为替代列。'),
 ('同学主口径','普通高校明确就读且同时在校至少六个日历月；不是同班或实际相识的证明。'),
 ('共事主口径','同一地区、机构及部门单位键，任期重叠至少六个日历月；不把同省或上下级本身当成共事。'),
 ('时间','年度为当年1月1日快照；主关系在双方连续同期任职区间开始前已形成。'),
 ('同乡日期','1900-01-01只作固定属性的程序排序占位，不是源文件日期；同乡没有观察到的形成日，formed_date_observed留空。'),
 ('编码','1=有包内证据；0=有比较基础但未检出，仍不证明现实无关系；空值=不足判断。'),
 ('任职冲突','同日同职多人另列待核验，并提供同日主职唯一的配对版本；不能外部裁定。'),
 ('地理范围','普通地级单位、直辖市区县、省直辖县、标签冲突县区分开；历史代码不靠外部区划统一。'),
 ('Local区别','本次是官员之间的关系，不是此前论文的career-Local。'),
 ('网络补充','不限同省同期的正向网络是曾任省市角色人物集合，须另按当年职务和关系形成时间过滤；无边不等于已核实的0。')]
with pd.ExcelWriter(O/'市级与省级官员关系_结果.xlsx',mode='a',engine='openpyxl',if_sheet_exists='replace') as w:
 F.to_excel(w,sheet_name='各关系首次形成',index=False)
 pd.DataFrame(notes,columns=['主题','说明']).to_excel(w,sheet_name='先读口径说明',index=False)
shutil.copy2(Path(__file__),O/'code'/'finish_delivery.py')
doc=O/'定义与使用说明.md'
txt=doc.read_text(encoding='utf-8')
addition='\n交付格式最后运行`code/finish_delivery.py`，将固定同乡属性的排序占位与真实记录日期区分、更新Excel阅读说明并重新打包。\n'
if addition not in txt:doc.write_text(txt+addition,encoding='utf-8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='file_manifest.csv':manifest.append({'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
pd.DataFrame(manifest).to_csv(O/'file_manifest.csv',index=False,encoding='utf-8-sig')
zp=O.parent/'CPED_市级与省级官员关系_数据代码与说明.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,str(p.relative_to(O)))
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
T=pd.read_csv(O/'top_leaders_unique_officeholder_year_start.csv')
print('ZIP',zp,zp.stat().st_size)
print('Unique officeholder rows',len(T),'cities',T.city_code.nunique(),'years',int(T.year.min()),int(T.year.max()))
print(T[['hometown_prefecture','classmate_6m','cowork_6m','connected']].apply(lambda x:x.value_counts(dropna=False)).to_string())
