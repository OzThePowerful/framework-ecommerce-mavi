# Framework Ecommerce MAVI

Framework de automatización UI multi-ecommerce construido sobre la
arquitectura POM objetivo del departamento: Playwright + Pytest + BDD +
Allure, con fronteras explícitas entre infraestructura, UI, dominio,
workflows, datos y ejecución.

Sitios soportados por configuración: **Muebles América (MA)**, **VIU** y
**MAVI** (flujo funcional implementado inicialmente para MA).

## Requisitos

- Python **3.13** (compatible `>=3.11`)
- Git

## Instalación

```bash
python -m pip install -r requirements.lock
python -m playwright install chromium
```

`requirements.in` declara las dependencias directas;
`requirements.lock` fija las versiones resueltas.

## Arquitectura

```text
Core            → infraestructura técnica (config, browser, contexto,
                  evidencias, reporting, logging, errores técnicos)
   ↓
UI Automation   → pages/ (Page Objects + locators + componentes)
   ↓
Business Workflows → workflows/ (coordinación; sin locators ni asserts)
   ↓
Test Execution  → tests/, fixtures/, steps BDD (validaciones)
```

Reglas clave (verificables en `tests/architecture/`, detalle en
`docs/architecture/dependency_rules.md`):

- `core` nunca importa `pages`, `workflows` ni `tests`.
- Los locators viven en `*_locators.py`, separados del comportamiento.
- Los Page Objects no contienen asserts ni `expect`.
- Los workflows no contienen locators.
- Los tests no usan locators directamente.
- Prohibido `except Exception:` tragado; errores clasificados.
- Sin `print()` como diagnóstico: logging estructurado con
  `run_id`/`case_id`/`site`/`environment`.
- Sin URLs literales en capas funcionales: se resuelven desde
  `config/sites.yaml` vía `ExecutionContext`.
- `conftest.py` raíz mínimo: solo registra plugins de `fixtures/`.

## Ejecución

```bash
# Suite completa (sitio/ambiente por defecto: muebles_america/stage)
pytest

# Selección multi-ecommerce
pytest --site muebles_america --target-env stage
pytest --site viu --target-env stage

# Perfil con navegador visible
pytest --exec-profile headed

# Solo pruebas sin navegador
pytest tests/unit tests/architecture

# Primer test E2E migrado (requiere acceso a la tienda configurada)
pytest tests/smoke/test_core_locators_grid_ma.py
```

Overrides por variables de entorno: `MAVI_ECOM_SITE`, `MAVI_ECOM_ENV`,
`MAVI_ECOM_CASE_ID`.

## Quality gate

```bash
python scripts/quality_gate.py
```

Equivale a:

```bash
python -m compileall .
ruff check .
pytest tests/architecture
pytest --collect-only
```

## Datos de prueba

- **Entrada**: `data/<site>/*.yaml` vía `DataProvider`
  (`YamlDataProvider` hoy; `ExcelDataProvider` intercambiable con
  fallback a `data/common/`).
- **Generados**: `repositories/` bajo `artifacts/generated/<run_id>/`
  con escritura atómica.

## Reportes

Allure escribe resultados en `artifacts/allure-results` (configurado en
`pytest.ini`). Evidencias por corrida en `artifacts/runs/<run_id>/`.

## BDD

Los `.feature` (contrato funcional) viven en `test_cases/<sitio>/` y los
steps delgados en `tests/bdd/steps/`; el runner es
`tests/bdd/test_features.py`.
