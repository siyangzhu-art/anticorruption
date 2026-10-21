# 官员关系与晋升 / Promotion and official networks

2026-10-21 research snapshot. Existing repository contents are unchanged.

## 结果入口

- [HTML总结：模型、主结果、腐败领导检查和关系类型扩展](results/organized_main_results_corruption_checks_2026_10_21/index.html)
- [已知问题：请先读](KNOWN_ISSUES.md)
- [数据与本地完整包说明](DATA_ACCESS.md)
- [市级领导个人网络复现说明](code/network/README.md)
- [模型与文件对应](REPLICATION_MAP.md)

Download/clone the repository and open `index.html` locally to view the HTML report. GitHub's file viewer displays HTML source; this release does not enable GitHub Pages or change repository settings.

## 安装和运行

Python 3.12; Stata 18 for the estimation jobs. Run from this release directory:

```powershell
python -m pip install -r requirements.txt
python replicate.py check
$env:STATA_EXE = 'C:\Program Files\Stata18\StataMP-64.exe'
python replicate.py estimates --jobs main corruption cumulative hometown_school union_ties
python code/plot_rerun.py
```

Stata add-ons: `reghdfe`, `ftools`, `eventstudyinteract`, `avar`, `boottest` (install separately with `ssc install`, as applicable). The launcher stops on missing inputs or unmatched coefficients. It checks aggregate coefficients/SEs/CIs against the delivered expected results; newly generated output goes only under `rerun/`.

The default **main** job reproduces 72 annual contrasts, three pre-inspection association levels and three historical common-cohort cumulative contrasts. The **cumulative** job reproduces the NEW 18 horizon-specific models and 12 wild bootstrap tests. Historical common-422 estimates are retained as comparisons, not substituted for the newer samples. `corruption` is the historical 11-contrast audit; the NEW cumulative exclusion variants are included in the cumulative job. Hometown/school and union jobs reproduce 8 and 4 diagnostic models.

For the raw-to-network workflow:

```powershell
$env:CPED_ZIP = 'D:\authorized-data\rerequestforaccesstothecped.zip'
python replicate.py network
```

Network output defaults to `rerun/network/project/result/`, never to the original research folder. See its README for definitions and timing. The public archive intentionally needs authorized data; the user's local bundle includes the processed inputs.

## Interpretation

Annual event coefficients are changes in the connected–unconnected promotion gap relative to k=-1, not the absolute value of connections. The pre-inspection association models omit individual FE because fixed C0 is absorbed by individual FE. Cumulative coefficients use equal-length pre/post windows and individual plus province-by-pre/post FE. All reported uncertainty follows the original stored specification; no new window search was conducted to prepare this release.

Broad promotion still includes source-coded NPC/CPPCC grade rises. An unresolved source-rank issue is prominently flagged. Numerical replication is distinct from validating the underlying historical labels. No original estimate or source network was overwritten by this packaging operation.


## 本次实际重跑核验

[核验记录](validation/README.md)：183项系数对照、12项wild bootstrap，以及从原始ZIP重建的六张网络表和完整性检查均通过。人大／政协职级标签问题仍未修订，参见KNOWN_ISSUES.md。Windows建议解压到较短目录；启动器会尝试使用Windows短路径。
