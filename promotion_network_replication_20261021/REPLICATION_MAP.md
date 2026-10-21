# 模型、数据与复现入口对应

| 部分 | 执行入口 | 冻结输入 | 输出检查点 |
|---|---|---|---|
| 年度TWFE和Sun–Abraham，四种FE；事前关系优势 | `replicate.py estimates --jobs main` | control_FE_sensitivity_post4/fixed_panel.dta；preinspection_fixed_C0_levels.../preinspection_panel.dta；旧累计输入 | expected/main.csv（78条） |
| 腐败省排除，历史数值审查 | `--jobs corruption` | 年度Strict与旧累计排省面板 | expected/corruption.csv（11条） |
| 当前12/24/36月独立样本及其同步排省检查 | `--jobs cumulative` | cumulative_horizon_specific_samples.../data/panel_*.dta | expected/cumulative.csv；wild_tests.dta |
| 同乡、同期校友，两组FE两种方法 | `--jobs hometown_school` | hometown_classmate_fixed_event_study.../data/*.dta | expected/hometown_school.csv |
| 同乡或同期校友合并 | `--jobs union_ties` | union_hometown_school_event_study.../data/*.dta | expected/union_ties.csv |
| 个人网络 | `replicate.py network` | 原始CPED ZIP | 源记录、边持久性和完整性核验；network统计 |

## Outcome / relation construction provenance

Original CPED loading and annual/term outcome classification: `code/source_snapshot/promotion_connections/prepare.py`. The explicitly requested promotion revision (new vice-governor appointment including same-grade move): `revise_2006_2017.py`. Annual economics follow appointment city: `add_city_economics.py`. Fixed pre-inspection cohort, covariates and FE comparisons: `sun_abraham_post4.py`, `control_fe_multiverse.py`. The current cumulative sample change: `cumulative_horizon_specific_samples.py`; original horizon outcomes and censoring: `cumulative_twfe_prepare.py`. Corruption province definitions and official sources: `exclude_corruption_provinces.py` and the delivered evidence CSV.

The source_snapshot also retains exploratory/earlier routines for transparency. They are not all current main specifications and can refer to superseded outputs. The executable estimation templates are the exact previously audited final jobs with relocated paths. LP-DiD and DoubleML historical result tables, scripts and controls are retained with the gallery, but are not part of the main five-job numerical validation launcher.

## Models

Pre-inspection association: 100 Promotion_it = province×year FE + b C0_i + X_it gamma + error. No individual FE: a fixed C0 cannot be separately estimated with it.

Annual event model: 100 Promotion_it = individual FE + year FE (or province×year FE) + sum[k != -1] b_k C0_i 1(event=k) + X_it gamma + error. Event main effects enter when not absorbed. City FE is an additional additive FE sensitivity, not city×year FE.

Cumulative H-month paired model: 100 Y_is(H) = individual FE + province×pre/post FE + theta_H C0_i Post_s + X_i0×Post_s gamma + error. C0 and Post main effects are absorbed. The 12/24/36 month samples are distinct; no equality of post gap is inferred from an insignificant p-value.

Sun–Abraham estimates cohort-specific event interactions and aggregates using the original routine. C0=0 is a comparison group for the relationship-gap contrast, not literally uninspected provinces. See KNOWN_ISSUES.md for limitations.
