"""Inventario operativo del framework: archivos por capa."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYERS = (
    "api",
    "config",
    "core",
    "data",
    "data_providers",
    "docs",
    "domain",
    "fixtures",
    "knowledge",
    "pages",
    "repositories",
    "scripts",
    "test_cases",
    "tests",
    "workflows",
)


def main() -> int:
    for layer in LAYERS:
        directory = ROOT / layer
        count = len(list(directory.rglob("*.py"))) if directory.is_dir() else 0
        status = "ok" if directory.is_dir() else "AUSENTE"
        print(f"{layer:<16} {status:<8} {count} archivos .py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
