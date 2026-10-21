# Data access and two delivery tiers

The GitHub repository is public. This release does not redistribute the CPED ZIP, individual career records, analytic officer panels, individual edge lists, or evidence workbooks. Permission to use a dataset is not assumed to include permission to redistribute it.

**Local full-input bundle:** `inputs/raw/rerequestforaccesstothecped.zip` and `inputs/project/result/...` contain the exact inputs used for reproduction. They remain on the user's computer and are excluded from GitHub. This local bundle is not a claim of public data availability.

**Public release:** source code, relocatable network code, executable estimation templates, aggregate expected coefficients, HTML, figures, aggregate tables, definitions and checks. An authorized replicator must supply the restricted inputs under `inputs/` or pass `--inputs` / set `CPED_ZIP`.

Original CPED archive SHA256:
`1427471e045e5e4f26b1ce39bb6f8ea024476d099b8478aaf984893c1cf24526`

The only raw input for network reconstruction is that ZIP (two workbooks). It contains 4,603 people and 73,487 experience rows. No external biographies are used to create edges. Economic controls come from the previously prepared officer-city economic panels; the public release does not download new economic data.

`manifests/local_input_manifest.csv` lists relative filenames, file sizes and SHA256 of the exact local inputs. It contains no person-level observations. `code/source_snapshot/` preserves the original scripts and original absolute paths for provenance; use the root launcher and portable network scripts for execution on another computer.

`replicate.py estimates` starts at the frozen processed inputs. Raw-to-outcome preparation scripts are retained in source_snapshot and the step map, but are NOT advertised as an independently validated one-command raw-to-all-models pipeline. Network reconstruction does have a raw-ZIP launcher.
