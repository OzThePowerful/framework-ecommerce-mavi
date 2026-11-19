"""Utilidades AST que convierten las reglas arquitectónicas en controles."""

import ast
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FUNCTIONAL_TOP_LEVELS = frozenset({"pages", "workflows", "tests"})

# Acciones Playwright prohibidas dentro de archivos *_locators.py.
LOCATOR_ACTIONS = frozenset({
    "check",
    "click",
    "count",
    "dispatch_event",
    "evaluate",
    "fill",
    "hover",
    "inner_text",
    "input_value",
    "is_visible",
    "press",
    "screenshot",
    "select_option",
    "tap",
    "type",
    "uncheck",
    "wait_for_selector",
})

# Accesores que materializan locators; prohibidos en tests, steps y workflows.
LOCATOR_ACCESSORS = frozenset({
    "frame_locator",
    "get_by_alt_text",
    "get_by_label",
    "get_by_placeholder",
    "get_by_role",
    "get_by_test_id",
    "get_by_text",
    "get_by_title",
    "locator",
})

FRAMEWORK_DIRS = (
    "api",
    "core",
    "data_providers",
    "domain",
    "fixtures",
    "pages",
    "repositories",
    "scripts",
    "workflows",
)


def iter_py(relative_dir: str) -> Iterator[Path]:
    directory = ROOT / relative_dir
    if not directory.is_dir():
        return
    yield from sorted(directory.rglob("*.py"))


def iter_all_framework_py() -> Iterator[Path]:
    for directory in FRAMEWORK_DIRS + ("tests",):
        yield from iter_py(directory)
    root_conftest = ROOT / "conftest.py"
    if root_conftest.is_file():
        yield root_conftest


def tree_of(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def import_roots(tree: ast.AST) -> set[str]:
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def import_modules(tree: ast.AST) -> set[str]:
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def call_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                names.add(func.attr)
            elif isinstance(func, ast.Name):
                names.add(func.id)
    return names


def contains_assert(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.Assert) for node in ast.walk(tree))


def forbidden_except_lines(tree: ast.AST) -> list[int]:
    """`except:` desnudo o `except Exception:` que traga el error."""
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if node.type is None:
            lines.append(node.lineno)
        elif (
            isinstance(node.type, ast.Name)
            and node.type.id in {"Exception", "BaseException"}
            and all(isinstance(stmt, ast.Pass) for stmt in node.body)
        ):
            lines.append(node.lineno)
    return lines


def url_literals(tree: ast.AST) -> list[str]:
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and "://" in node.value
        and node.value not in ("http://", "https://")
    ]
