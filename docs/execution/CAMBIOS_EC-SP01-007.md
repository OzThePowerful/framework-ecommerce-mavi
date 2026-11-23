# Cambios aplicados — EC-SP01-007

> Quality Gate y contratos de arquitectura.
> Fecha: 2026-11-23 · Séptimo hito del Sprint 01.

## Resumen

Los controles AST y el quality gate ya existían desde EC-SP01-001;
esta tarea completó el contrato: **reorganización en 6 archivos por
política**, dos reglas que faltaban del listado mínimo (**asserts en
workflows**, **dependencias circulares**) y las **pruebas negativas
del propio gate**.

## Cambios aplicados

### `tests/architecture/` (reorganizada)

| Archivo | Controles |
|---|---|
| `test_layer_boundaries.py` | core→capas funcionales, repositories→pages, **ciclos (nuevo)**, conftest mínimo |
| `test_page_object_policy.py` | Page Objects sin asserts/`expect` |
| `test_locator_policy.py` | acciones en `*_locators`, locators en tests, locators en steps BDD |
| `test_workflow_policy.py` | workflows sin locators + **workflows sin asserts (nuevo)** |
| `test_data_policy.py` | data_providers→pages + URLs literales en capas funcionales |
| `test_exception_policy.py` | `except` tragado + `print` prohibido |
| `test_gate_selfcheck.py` (nuevo) | 6 pruebas negativas: cada detector debe marcar código violador sintético y pasar código limpio |
| `rules.py` | +`module_graph()`/`find_cycles()` (DFS con pila gris, ciclos normalizados), +`tree_of_source()` para código sintético, +`violations_importing`/`violations_calls` compartidas |

`test_architecture_rules.py` monolítico: **eliminado** (contenido
distribuido).

### `docs/architecture/dependency_rules.md`

Tabla reorganizada por archivo de política + nuevas reglas +
explicación del selfcheck.

## Estado verificado ya existente

- `scripts/quality_gate.py`: los 4 pasos del contrato con exit code
  correcto (0 OK / 1 FAIL por paso).
- `scripts/validate_architecture.py`: atajo a los controles.
- Ruff en `pyproject.toml` con excludes coherentes.

## Evidencia de violación deliberada (obligatoria)

Archivo temporal `pages/muebles_america/home/tmp_violation_page.py`
con un `assert` en un Page Object:

```text
FAILED tests/architecture/test_page_object_policy.py
E  AssertionError: Page Objects con asserts/expect:
E  ['pages\\muebles_america\\home\\tmp_violation_page.py']
```

Tras eliminar el archivo: `test_page_objects_sin_asserts` → **PASS**.
El gate identifica la violación y se restaura al corregir.

## Validación

| Comando | Resultado |
|---|---|
| `python scripts/quality_gate.py` | compileall ✅ · ruff ✅ · architecture 20 ✅ · collect 70 ✅ |
| `pytest tests/unit` | 49 passed |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage` (headless) | 1 passed en ~34s |
