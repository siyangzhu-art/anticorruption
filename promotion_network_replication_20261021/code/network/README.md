# 市级领导个人网络复现

唯一原始输入是用户提供的CPED ZIP，SHA256见根目录DATA_ACCESS.md。运行 `python replicate.py network`。

## 执行顺序

1. `connections/build_connections.py`：读取两个原始Excel，标准化履历、地理与单位／学校别名，识别市级及省级任期。
2. `connections/build_candidate_network.py`：保留曾任省、市职务的完整人员候选关系，不能只取“市级主官两端”的子图替代它。
3. `connections/audit_and_document.py`、`finish_delivery.py`：核验及说明。
4. `person/build_person_network.py`：按2012-01-01及2012-11-15两个截止日重建固定个人边；不是按每年重新取消既有关系。
5. `person/audit_person_network.py`、`finish_person_network.py`：逐条正向证据检查、表格和交互图。
6. `rerun_original_source_checks.py`、`recheck_temporal_network.py`、`recheck_edge_completeness.py`、`report_temporal_reaudit.py`：独立源记录、时间与完整性核验。

## 关系定义

- 同乡：CPED籍贯省＋地级市一致，不能称作出生地一致。
- 同期校友：合格普通高校学习经历同校重叠至少6个月；不等于同班同专业。党校、培训及明确在职学习等按代码中的分类规则排除。
- 共事：同一标准化任职单位的有效经历重叠至少6个月；属于可记录的共同单位暴露，不保证私交或直接上下级关系。
- 主个人网络严格使用截止日前形成的关系。个人边始终保留；年度任职映射变化是人员调动、退出主官样本或展示筛选造成，不能解释为关系消失。
- 未知不补0；“没有记录到正边”和“证实没有真实关系”不是同一件事。

原网络规模：4,603人，主截止日前71,048条个人正向边；其中曾任普通地级主官2,771人，主官之间25,233条正向边。年度任职映射2000–2018。各关系数量可能重叠，不能直接相加为唯一边数。

`source_snapshot`为原始代码备份。`code/network`只更改输入输出路径和vendor环境引用，分类规则不变。新输出写到独立rerun目录。公开仓库不发布逐人边及履历；本地完整包中有原始网络及证据。
