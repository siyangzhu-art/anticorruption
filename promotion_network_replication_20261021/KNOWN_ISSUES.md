# 已知问题与版本边界 / Known issues

This release reproduces the estimates reported on 2026-10-21; it does not assert that every source-coded promotion is externally verified.

1. **人大／政协不是一律省级，也不是一律不晋升。** Main Y includes source-coded rank rises, mayor→secretary and newly appointed vice governors (including same-grade appointments). The 44 main-sample positives whose first event is NPC/CPPCC all use a recorded rank rise. Zhang Shaojun's Qingdao CPPCC destination is municipal. Ding Dawei's Wuxi NPC deputy-director record has a source vice-ministerial rank label requiring verification; the current numerical results have NOT been recoded around this issue.
2. `second_line` means any qualifying event in the year is NPC/CPPCC, while the recorded event is the earliest event. Consequently the historical `executive_promotion` sensitivity is not a reliable event-level executive-only outcome. Main models use broad `promotion`, not this sensitivity.
3. Raw vice-governor flags conflict with the NPC/CPPCC category for Lai Derong (2013) and He Duanqi (2017). They need record-level review; not every conflict necessarily changes the broad main Y.
4. Annual +4 has only four baseline-connected officials. The annual panel is an unbalanced promotion risk set. Provincial clustering does not solve attrition.
5. Cumulative 12/24/36-month models now use their own paired samples (497/466/425 people), not the old common 422-person sample. The later roster snapshot and retrospective pre-windows can induce selection; individual FE cannot remove that selection.
6. Sun–Abraham uses the untied group as the comparison in a relationship-gap design. All provinces were inspected; it is not automatically an overall inspection ATT. Economic controls, role, rank and location can themselves be affected by inspection.
7. Hometown and school extensions have sparse support and reject the displayed pretrend tests. They are diagnostic associations, not established causal effects.
8. Historical specification searches exist. Current release preserves all four FE comparisons and the existing audit. No new significance search or promotion recoding is performed for this upload.

Official destination checks: [Wuxi NPC](https://rd.wuxi.gov.cn/doc/2016/11/22/1677835.shtml); [Qingdao municipal government](https://www.qingdao.gov.cn/ywdt/tpxw/202010/t20201013_339913.shtml).
