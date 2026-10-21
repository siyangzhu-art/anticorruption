from pathlib import Path
import os
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("REPLICATION_PROJECT", PACKAGE_ROOT / "rerun/network/project"))
CPED_ZIP = Path(os.environ.get("CPED_ZIP", PACKAGE_ROOT / "inputs/raw/rerequestforaccesstothecped.zip"))
