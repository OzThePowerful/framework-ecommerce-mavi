"""Valida las entradas del catálogo API en knowledge/catalog/api/.

Cada YAML debe declarar las claves mínimas del contrato de catálogo.
No autoriza consumo de APIs productivas.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "knowledge" / "catalog" / "api"
REQUIRED_KEYS = {"endpoint", "method", "purpose", "verification_status"}


def main() -> int:
    files = sorted(CATALOG_DIR.glob("*.yaml")) + sorted(CATALOG_DIR.glob("*.yml"))
    errors = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        missing = REQUIRED_KEYS - set(data)
        if missing:
            errors.append(f"{path.name}: faltan {sorted(missing)}")
    for error in errors:
        print(error)
    print(f"Catálogo API: {len(files)} archivo(s), {len(errors)} error(es)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
