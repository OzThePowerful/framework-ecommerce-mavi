# Cambios aplicados — EC-SP01-006

> Logging, evidencia y reportes Allure.
> Fecha: 2026-11-23 · Sexto hito del Sprint 01.

## Resumen

La infraestructura de logging y Allure ya existía; esta tarea
implementó la pieza que faltaba por completo: **captura automática de
evidencia ante fallo** (screenshot, URL, excepción, manifest),
jerarquía de artefactos por ejecución/caso, e identificación de la
ejecución dentro de Allure.

## Estado verificado ya existente

- `logger.py` estructurado con `run_id`/`case_id`/`site`/`environment`;
  `print` prohibido por regla arquitectónica.
- `RunContext` con Run ID único; rutas ancladas al proyecto
  (`artifact_paths.py`).
- `allure-pytest` instalado y `--alluredir` en `pytest.ini`;
  helpers `attach_text`/`attach_file`.

## Cambios aplicados

### `core/evidence/artifact_paths.py`

- Nuevo `case_artifacts_dir(run_id, case_id)` →
  `artifacts/runs/<run_id>/<case_id>/` creando `screenshots/`,
  `logs/`, `traces/`, `videos/` (soporte futuro de trace/video).
- Sanitización del nombre de caso para filesystem Windows/Linux.

### `core/evidence/evidence_manager.py` (reescrito)

- Constructor por ejecución y caso: `EvidenceManager(run_id, case_id)`.
- `capture_failure(page, report, context, test_name)`:
  screenshot full-page (`screenshots/failure.png`),
  `logs/current_url.txt`, `logs/exception.txt` (longrepr original) y
  `manifest.json` (run_id, case_id, test, outcome, site, environment,
  browser, base_url, page_url, excepción, timestamp, rutas).
  Tolerante a browser caído (`PlaywrightError` específico).
- `save_screenshot`/`save_log`/`write_manifest` para uso general.

### `fixtures/evidence_fixtures.py`

- `pytest_runtest_makereport` (`wrapper=True`, pytest 9): conserva
  `rep_setup`/`rep_call`/`rep_teardown` en el item.
- Fixture `evidence_manager` ahora por caso
  (`--case-id` o nombre del test como fallback).
- `allure_context` (autouse, sin costo de navegador): labels Allure
  `run_id`, `case_id`, `site`, `environment`, `browser` por test.

### `fixtures/browser_fixtures.py`

- Teardown de `page`: si el test falló, `EvidenceManager.capture_failure`
  antes de `page.close()`; artefactos adjuntados a Allure vía
  `attach_failure_artifacts` (movido a `allure_manager` para no importar
  módulos-plugin entre fixtures — elimina `PytestAssertRewriteWarning`).

### `fixtures/execution_fixtures.py`

- `environment.properties` en `allure-results` al inicio de sesión:
  RUN_ID, SITE, ENVIRONMENT, BROWSER, BASE_URL.

### Logging

- Campo `browser` agregado a `_CONTEXT_FIELDS` y al formato de
  `config/logging.yaml` (el contrato lo lista en la identificación).

### `README.md`

Sección "Reportes y evidencias": árbol de artefactos, captura
automática y campos de logging/Allure.

## Verificación del test adelantado

`test_guest_checkout_ma.py` no requirió cambios: la evidencia es
transversal vía fixtures; ante un fallo suyo se generaría
`artifacts/runs/<run>/<case>/` completo automáticamente.

## Validación

| Comando | Resultado |
|---|---|
| `pytest tests/unit tests/architecture` | 61 passed |
| `ruff check .` | All checks passed |
| `python -m compileall .` | exit 0 |
| **Fallo controlado real** (test temporal `test_fallo_controlado_tmp` con `page` → `raise AssertionError`) | Generó `screenshots/failure.png`, `logs/current_url.txt` (`about:blank`), `logs/exception.txt` (longrepr completo), `manifest.json` (todos los campos) y `traces/`+`videos/`; `environment.properties` de Allure con los 5 campos. Archivo temporal eliminado tras la verificación. |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage` (headless) | 1 passed en ~31s |
