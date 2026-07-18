# Anti-Corruption Inspection & Economic Outcomes in China

**Siyang Zhu** | [siyangzhu-art/anticorruption](https://github.com/siyangzhu-art/anticorruption)

This repository contains the full empirical pipeline for studying how China's central anti-corruption inspection campaign (2013-2020) affects local economic behaviour, environmental quality, fiscal governance, and data reporting incentives.

---

## Research Overview

The project investigates whether and how the staggered rollout of central inspection teams (中央巡视/督察) across Chinese provinces triggers changes in:

| Domain | Core Question |
|---|---|
| **GDP Reporting** | Do inspections reduce GDP data over-reporting by local officials? |
| **Fiscal Governance** | Do inspections improve fiscal transparency, debt sustainability, and budget discipline? |
| **Trust Financing & LGFV Debt** | How do inspections affect local government financing vehicles (城投) — volumes, disclosure delays, and industry composition? |
| **Environmental Quality** | Do inspections reduce air pollution (CO, NO₂, SO₂, PM₂.₅, PM₁₀) and CO₂ emissions, especially in Air Key Control Zones and Low-Carbon Pilot Cities? |
|| **Policy Supportive Intensity** | Are prefecture-level supportive policies (R&D subsidies, tax relief, etc.) responsive to anti-corruption shocks? |

The analysis uses a staggered Difference-in-Differences (DID) design, supplemented by modern causal estimators (CSDID, LP-DID, Synthetic DID) and machine-learning robustness checks.

---

## File Structure

`
anticorruption/
├── Environment_lowcarbon.do         # Alternative low-carbon environment spec (final version)
├── Province_fiscal.do               # Provincial fiscal indicators: DID on budget metrics
├── GDP over report.do               # GDP over-reporting detection (main analysis)
├── compliance.do                    # Compliance/city-level JS_Plan & Cosine_Plan analysis
│
├── robustness ML for GDP over report.R  # Machine-learning robustness (RF, XGBoost, SVR, MARS, GAM stacking)
│
├── data/                            # Cleaned panel datasets
│   ├── night_light.dta              # Nighttime light (NTL) panel 1992-2024
│   ├── replicate_GDP.dta            # Replicated GDP estimates
│   ├── city_string.dta              # City name mapping
│   └── 工作簿1                       #county social econ information
     └──..........

## How to Reproduce

1. **Set up file paths**: Update the global 
oot macro in each .do file to match your local directory structure.
2. **Prepare data**: Ensure all raw datasets (Excel, CSV, DTA) are placed under the expected paths (data sources listed above).
3. **Run in order**:
--For GDP over report
   -  1_ GDP over report.do  (1-207 line)   — Data cleanning basic regression  non parametric construction of GDP  over report 
   -  2  Run  robustness ML for GDP over report.R use ML for GDP over report then it as “anti corruption_with_ml.dta”
   -  3  Back to  GDP over report.do  from 207 on forward. ins13.dta contain infromation of provinical inspection(To county level)
--For Environment_lowcarbon.do 
  - 1  ins12.dta provincial inspection team at (city level. if county inspected then city also inspected)
--For compliance
 -  1. Use orignal government report data and use cleanfinal.m to construct policy similarity measure JS Cosine
 -  2. For.dta and D.dta are replicate GDP(base on night light) and econ and social information about cities
## Key Methodological Pipeline

### 1. Treatment Definition

The treatment variable  nti_shock is constructed from hand-collected inspection data. For each province-year, it equals 1 if a central inspection team entered that province in that year. "Review" inspections (回头看) are excluded to avoid treatment pollution.

The staggered treatment schedule follows the actual roll-out:

| Year | Provinces Inspected |
|---|---|
| 2013 | Inner Mongolia, Jiangxi, Hubei, Chongqing, Guizhou, Shanxi, Jilin, Anhui, Hunan, Guangdong, Yunnan |
| 2014 | Beijing, Tianjin, Liaoning, Fujian, Shandong, Henan, Hainan, Gansu, Ningxia, Xinjiang, Hebei, Heilongjiang, Shanghai, Jiangsu, Zhejiang, Guangxi, Sichuan, Tibet, Shaanxi, Qinghai |
| 2016 | Liaoning, Anhui, Shandong, Hunan, Tianjin, Jiangxi, Henan, Hubei, Beijing, Guangxi, Chongqing, Gansu |
| 2017 | Inner Mongolia, Jilin, Yunnan, Shaanxi |
| 2018 | Hebei, Shanxi, Liaoning, Heilongjiang, Jiangsu, Fujian, Shandong, Henan, Hunan, Guangdong, Hainan, Sichuan, Guizhou, Ningxia, Hubei, Gansu, Qinghai, Xinjiang |
| 2020 | Beijing, Tianjin, Inner Mongolia, Jilin, Shanghai, Zhejiang, Anhui, Jiangxi, Hubei, Guangxi, Chongqing, Yunnan, Tibet, Shaanxi, Gansu, Qinghai, Xinjiang |

### 2. Estimators

- **Two-Way Fixed Effects (TWFE)** — 
eghdfe with province × year and city fixed effects
- **CSDID (Callaway & Sant'Anna, 2021)** — csdid with DR-IMP estimator
- **LP-DID (Local Projections DID)** — lpdid for dynamic treatment effects
- **Stacked DID** — did_multiplegt_dyn (de Chaisemartin & D'Haultfœuille)
- **Event Study** — full pre/post trend visualization (csdid_plot, event_plot)

### 3. Outcome Variables

| Category | Variables |
|---|---|
| GDP & Growth | growth_gdp, growth_realgdp, growth_night (NTL-based), ln_gdp, ln_ntl, GDP/ntl ranking gap |
| Fiscal | 财政收入稳健指数, 债务可持续指数, 财政支出结构指数, 社保基金可持续指数, 预算管理指数, 透明度指数, 审计违规金额占比 |
| Environment | CO, NO₂, SO₂, PM₂.₅, PM₁₀ (monthly city-level), CO₂ emissions, 大气重点控制区, 低碳城市试点 |
| Policy | JS Cosine

### 4. Machine-Learning Robustness (
obustness ML for GDP over report.R)

A 5-fold cross-fitted stacking (Super Learner) framework to disentangle genuine GDP growth from NTL-predicted growth:

- **Regression Forest** (OOB predictions via grf)
- **XGBoost** (regularized gradient boosting)
- **SVR** (radial-kernel support vector regression)
- **MARS** (multivariate adaptive regression splines)
- **GAM** (generalized additive model with cubic regression splines)

Meta-learner weights are optimized via L-BFGS-B with non-negativity constraints, then exported to Stata as  nti_corruption_with_ml.dta.

## Software Dependencies

### Stata (≥ 16)
- 
eghdfe (ssc install reghdfe)
- csdid + csdid_plot (ssc install csdid)
- lpdid (ssc install lpdid)
- did_multiplegt_dyn (ssc install did_multiplegt_dyn)
- event_plot (ssc install event_plot)

### R (≥ 4.0)
- grf, xgboost, e1071, earth, mgcv, 
lme, haven

## License

This project is for academic research purposes. All code is shared for transparency and replicability. Please cite appropriately if using in derivative work.
