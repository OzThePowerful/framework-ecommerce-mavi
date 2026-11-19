# Cambios aplicados — EC-SP01-001

> Inicializar y normalizar la estructura del Framework Ecommerce MAVI.
> Fecha: 2026-11-19 · Primer commit del repositorio.

## Resumen

Se creó la primera versión ejecutable del Framework Ecommerce MAVI
directamente sobre la arquitectura objetivo (Core → UI Automation →
Business Workflows → Test Execution), con fronteras explícitas entre
infraestructura, UI, dominio, workflows, datos y ejecución, y sin
reproducir la deuda técnica identificada en MAVIPOS.

Adicionalmente se migró el primer test de
`Example_Valentin/test_UIValidations.py` a la arquitectura nueva
(decisión del usuario: migración con Page Objects mínimos).

## Estructura creada

| Capa | Contenido |
|---|---|
| `config/` | `sites.yaml`, `environments.yaml`, `execution_profiles.yaml`, `logging.yaml` |
| `core/` | `browser/` (factory + context), `execution/` (ExecutionContext, RunContext, taxonomía de errores), `config/` (loader + SiteConfig), `evidence/`, `reporting/` (Allure), `logging/` |
| `pages/` | `base_page.py` mínimo, `common/components/` (header, footer, loader, notifications) y `muebles_america/` (home, search, product, cart, checkout, payment, order) con `*_page.py` + `*_locators.py` separados; `viu/` y `mavi/` como paquetes pendientes |
| `workflows/` | Capa de coordinación con `sale_cash_workflow.py` como esqueleto (flujo de venta fuera de alcance) |
| `domain/` | `models/` (Product, Cart, Customer, Address, Order), `money/Money`, `errors/` (BusinessError, PreconditionError) |
| `data/` | `common/`, `muebles_america/`, `viu/`, `mavi/` (datasets en tarea EC-SP01-004) |
| `data_providers/` | `BaseDataProvider` (ABC), `YamlDataProvider` (fallback `common`), `ExcelDataProvider` (contrato implementado con openpyxl) |
| `repositories/` | Escritura atómica + Run ID + rutas ancladas al proyecto (execution, generated_customers, generated_orders) |
| `api/` | `clients/`, `models/`, `contracts/`, `monitoring/` (preparación API-First) |
| `knowledge/` | `catalog/api/`, `contracts/business/` |
| `test_cases/` | `.feature` de contrato funcional (`sale_cash.feature`, @pending) |
| `tests/` | `bdd/` (runner inicial + steps/), `architecture/` (12 controles), `unit/` (9 pruebas), `smoke/` (primer test migrado), `integration/`, `regression/` |
| `fixtures/` | Plugins por responsabilidad: browser, execution, data, page, evidence |
| `scripts/` | `quality_gate.py`, `validate_architecture.py`, `audit_framework.py`, `validate_api_catalog.py` |
| Raíz | `conftest.py` mínimo, `pytest.ini`, `pyproject.toml` (Ruff), `requirements.in`, `requirements.lock`, `README.md`, `.gitignore` |
| `docs/` | `architecture/dependency_rules.md` |

## Primer test migrado

`tests/smoke/test_core_locators_grid_ma.py` — flujo E2E de Muebles
América (Home → Línea blanca → PDP → carrito → checkout invitado →
precio):

- Sin locators en el test (viven en `pages/muebles_america/*_locators.py`).
- Sin URLs en el test (resueltas por `ExecutionContext` desde `sites.yaml`).
- Pages como fachada que componen componentes comunes
  (`HeaderComponent`, `NotificationComponent`).
- `except PlaywrightTimeoutError` específico en el popup promocional
  (sin `except Exception: pass`).
- El assert del precio permanece en el test (los pages no validan).
- `continue_as_guest()` espera navegación con el patrón
  `checkout_url_pattern` de configuración.

## Decisiones de implementación

- **Multi-ecommerce por configuración**: `--site`, `--target-env`,
  `--exec-profile`, `--case-id`; overrides `MAVI_ECOM_SITE`,
  `MAVI_ECOM_ENV`, `MAVI_ECOM_CASE_ID`. Validación temprana en
  `pytest_configure`: combinación inválida → error explícito, nunca
  redirección silenciosa.
- **URLs pendientes**: VIU y MAVI usan placeholders `.invalid` con
  TODO; MA stage/prod apuntan al sitio real conocido (pendiente URL de
  stage real).
- **Browser lifecycle propio** en `fixtures/browser_fixtures.py`
  (Playwright → Browser → Context → Page), independiente del ecommerce.
- **Run ID** único por sesión (`RunContext`) con artefactos bajo
  `artifacts/runs/<run_id>/`.
- **BDD runner preparado** (`tests/bdd/test_features.py`); el `.feature`
  existe como contrato documentado hasta implementar sus steps.
- **Captura de evidencias en fallo** diferida a EC-SP01-003
  (`EvidenceManager` ya disponible por fixture).

## Evidencia de validación (2026-11-19)

| Comando | Resultado |
|---|---|
| `python -m compileall .` | ✅ exit 0 |
| `python -m ruff check .` | ✅ All checks passed |
| `pytest tests/architecture` | ✅ 12 passed |
| `pytest --collect-only` | ✅ 22 collected |
| `pytest tests/unit` | ✅ 9 passed |
| Chromium vía `browser_factory` | ✅ inicializa (headless) |
| `pytest --site viu --target-env stage --collect-only` | ✅ 22 collected |
| `pytest --site nope --collect-only` | ✅ `UnknownSiteError` explícito |

## Entorno

Python 3.13.12 · pytest 9.1.1 · playwright 1.61.0 · pytest-bdd 9.0.1 ·
allure-pytest 2.16.2 · ruff 0.17.6 · PyYAML 6.0.3 · openpyxl 3.1.5 ·
pytest-playwright 0.9.0 · pytest-base-url 2.1.0.

## Fuera de alcance (según EC-SP01-001)

Flujo completo de venta, automatización de Home/Search/PDP/Cart/Checkout
más allá del primer test, VIU/MAVI funcionales, APIs reales, captura de
tráfico, sincronización Plane, modificación del Bridge.
