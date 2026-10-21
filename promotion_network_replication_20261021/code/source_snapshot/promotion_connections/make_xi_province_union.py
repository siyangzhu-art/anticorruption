"""Generate the user-confirmed province-year OR classification analysis."""
from pathlib import Path
H=Path(__file__).parent
s=(H/'xi_stratified_rolling.py').read_text(encoding='utf8')
s=s.replace("OUT=BASE/'Xi_stratified_rolling'", "OUT=BASE/'Xi_province_union_rolling'")
s=s.replace("ROSTER=pd.DataFrame(roster);save(ROSTER,'province_leader_Xi_status_by_year.csv')", """ROSTER=pd.DataFrame(roster);save(ROSTER,'province_leader_Xi_status_by_year.csv')
A['Xi_province']=np.where(A.Xi_G.eq(1)|A.Xi_S.eq(1),1.,np.where(A.Xi_G.eq(0)&A.Xi_S.eq(0),0.,np.nan))
province_roster=A[['year','baseline_date','province_code','province','S_person_id','S_name','G_person_id','G_name','Xi_S','Xi_G','Xi_S_status','Xi_G_status','Xi_province']].drop_duplicates()
save(province_roster,'province_Xi_group_by_year.csv')
ck('Province connected iff at least one leader has a documented Xi tie',A.Xi_province.eq(1).equals(A.Xi_G.eq(1)|A.Xi_S.eq(1)))
ck('Province group zero requires both leader statuses known zero',A.loc[A.Xi_province.eq(0),['Xi_G','Xi_S']].eq(0).all().all())
ck('Unique classification within province-year',A.groupby(['province_code','year']).Xi_province.nunique(dropna=False).le(1).all())""")
s=s.replace("D['Xi_'+lead].eq(xi)", "D.Xi_province.eq(xi)")
s=s.replace("LEAD[lead]+' | '+('Pre-2012 local coworking tie to Xi' if xi else 'No observed pre-2012 local coworking tie to Xi')", "LEAD[lead]+' | Province: '+('Xi-connected' if xi else 'No observed Xi connection')")
s=s.replace("Stratified by the corresponding leader\\'s pre-2012 local coworking tie to Xi", "Province-year groups: governor OR secretary has a pre-2012 local coworking tie to Xi")
s=s.replace("Xi ties must predate the observation and 2012. Central co-membership and school workplaces excluded; unknown status excluded.", "Province connected = either leader has a pre-2012 local tie to Xi; group 0 requires both leader statuses known zero.")
s=s.replace("Group 0 means no documented qualifying tie with usable career coverage; it does not establish the absence of a private connection.", "Province groups can change with leadership turnover. Central co-membership and school work excluded; private ties are not observed.")
s=s.replace('01_four_panels_Xi_stratified.png','01_four_panels_Xi_province.png')
s=s.replace('Xi关系分组_四格滚动回归.xlsx','按省级Xi关系分组_四格回归.xlsx')
s=s.replace('Xi关系分组_数据图表代码.zip','按省级Xi关系分组_数据图表代码.zip')
s=s.replace("('Xi_leader_year',ROSTER),", "('Xi_leader_year',ROSTER),('Province_group_year',province_roster),")
start=s.index("method='''")
end=s.index("(OUT/'methods_中文.md')",start)
s=s[:start]+"""method='''# 按省份当年与Xi的关系分组：四格滚动回归

本轮依用户明确选择定义省份分组：该省当年（基期上一年12月31日）省委书记或省长至少一人与习近平有已形成的、2012年前地方共事关系，则XiProvince=1。只有两人的关系状态都可判断且均为0，才令XiProvince=0。一人未知且另一人为0，省份状态未知，不补0；一人有明确正关系即归1，不受另一人未知影响。
分组单位为省×年；同一省同一年所有市级官员采用完全相同分组。它不是把某省永久标为connected，也不是分别按书记自身/省长自身分组；人员更替可改变省份分组。province_Xi_group_by_year.csv逐年列出两位领导及其状态。

四格：两行分别估计市级官员与省长、省委书记关系的晋升系数；两列分别是XiProvince=0、=1。每一省份分组/窗口内，CS和CG同时进入同一回归，四格图只展示对应系数。XiProvince分组在两行完全相同。
因变量沿用修订后的年度实际晋升：行政级别提升/市长升市委书记/副部级市级主官新任副省长亦计晋升。市长和书记合并，控制当前职务、年龄及平方、任期及平方、基期行政级别，省×年FE。两类关系均为至少六个月、2012前且共同任职前形成的共事关系。
习近平关系仍严格依据CPED习近平person_id=406的全部同单位至少六个月地方共事证据；排除中央机构共同任职、学校工作单位。证据必须不晚于基期且早于2012。无正证据只有在具备可比地方履历且不存在同单位日期歧义时才记0；否则未知。它衡量履历关系，不声称观察私人关系或忠诚。

三年居中窗显示中心-3至+2；各点使用[s-1,s+1]，边缘实际包含k=-4和+3。省聚类95%t区间，不连线，灰色表示窗口含巡视年。主样本仍从2006—2017年度面板取符合窗口的观测。
沿用原至少10省、10晋升事件、CS/CG各10个有/无关系观测和系数可识别要求。XiProvince=1各窗只有2—4省，12个对应面板点不满足省数要求，因此不输出其系数或CI；这不是零效应或不显著，也不是两组没有差别。每格列出N/省数，全部失败记录保存。不能通过把省份内许多城市当成独立省级关系案例扩大有效样本。
两个行的同一分组/窗口使用同一回归设计，24个目标面板窗口实质对应12个分组窗口回归；其中XiProvince=0的6个回归可报告两项系数。脚本为核验每项面板分别复算，因此保留24条目标支持记录。
全部成功拟合由独立完整FE虚拟变量回归核验系数与SE。没有按显著性筛选、没有放宽阈值、没有重做wild bootstrap。不能凭当前图判断两类省份关系晋升回报是否不同，更不识别巡视的因果作用。
'''
"""+s[end:]
s=s.replace('右侧有Xi关系两格的窗口仅0—3省','右侧Xi-connected省份组每窗仅2—4省')
s=s.replace('省级领导与习近平关系：四组滚动回归','按省份与习近平关系分组：四组滚动回归')
s=s.replace('Xi关系分组四格图','按省级Xi关系分组四格图')
(H/'xi_province_union_rolling.py').write_text(s,encoding='utf8')
print('Generated province-year union grouping analysis')
