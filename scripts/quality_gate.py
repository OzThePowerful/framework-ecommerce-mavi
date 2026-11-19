"""Quality gate inicial: compileall + ruff + architecture + collect-only."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("compileall", [sys.executable, "-m", "compileall", "-q", "."]),
    ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
    ("architecture", [sys.executable, "-m", "pytest", "tests/architecture", "-q"]),
    ("collect-only", [sys.executable, "-m", "pytest", "--collect-only", "-q"]),
]


def main() -> int:
    failed = []
    for name, command in STEPS:
        result = subprocess.run(command, cwd=ROOT, check=False)
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {name}")
        if result.returncode != 0:
            failed.append(name)
    if failed:
        print(f"Quality gate FALLÓ en: {failed}")
        return 1
    print("Quality gate OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
