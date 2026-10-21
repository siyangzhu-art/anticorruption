# Release validation

All five estimation jobs were run in a separate output tree on 2026-10-21.

- 183 stored coefficient contrasts checked against the frozen original numerical outputs.
- Twelve fixed-seed wild cluster bootstrap p-values reproduced (maximum difference 5.551115123125783e-17).
- Six network tables independently rebuilt from the original ZIP and compared by keys/contents, including both frozen cutoffs, nodes, officeholder mapping and city-pair exposure.
- 106 original-source, timing and completeness checks passed in the new network rerun.
- The tiny discrepancies in some school/hometown variance outputs fall within the documented relative/absolute comparison tolerance; numerical equality does not certify source rank labels.

See replication_run_summary.json for individual job counts and maximum errors; environment_used.json records the runtime. The public package is data-restricted and requires authorized inputs. The local full-input bundle includes these inputs. No original research estimate or original network file was overwritten.
