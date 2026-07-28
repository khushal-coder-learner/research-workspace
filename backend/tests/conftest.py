import os
import sys
import shutil
from pathlib import Path
from uuid import uuid4

import pytest


# The repository .env currently contains DEBUG=release, while the application
# setting is typed as bool. Keep test collection independent of that value.
os.environ["DEBUG"] = "true"
os.environ.setdefault("TMP", r"C:\tmp")
os.environ.setdefault("TEMP", r"C:\tmp")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def tmp_path() -> Path:
    root = PROJECT_ROOT / ".tmp" / "pytest"
    root.mkdir(parents=True, exist_ok=True)
    path = root / uuid4().hex
    path.mkdir()

    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
