"""Atajo operativo: ejecuta los controles de tests/architecture."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    sys.exit(
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/architecture"], cwd=ROOT
        ).returncode
    )
