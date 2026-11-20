# Framework Ecommerce MAVI

Framework de automatización UI multi-ecommerce (Playwright + Pytest + BDD +
Allure) construido sobre la arquitectura POM objetivo del departamento.

## Descripción

Un solo framework valida los ecommerce **Muebles América (MA)**, **VIU** y
**MAVI**. El sitio y el ambiente se eligen al ejecutar y llegan a todas las
capas mediante `ExecutionContext`; los tests nunca definen URLs.

El flujo funcional está implementado inicialmente para MA: Home → categoría →
PDP → carrito → checkout como invitado.

### Arquitectura

```text
Core               → infraestructura técnica (config, browser, contexto,
                     evidencias, reporting, logging, errores técnicos)
   ↓
UI Automation      → pages/ (Page Objects + locators + componentes)
   ↓
Business Workflows → workflows/ (coordinación; sin locators ni asserts)
   ↓
Test Execution     → tests/, fixtures/, steps BDD (validaciones)
```

Ejemplo del flujo de MA:

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Test | `tests/smoke/test_guest_checkout_ma.py` | Valida que el checkout muestre un precio mayor a cero. |
| Workflow | `workflows/muebles_america/guest_checkout_workflow.py` | `GuestCheckoutWorkflow` coordina las pantallas y devuelve el precio como `Money`. |
| Pages | `pages/muebles_america/<pantalla>/` | Un `*_page.py` y un `*_locators.py` por pantalla. |
| Componentes | `pages/muebles_america/components/` | Menú de departamentos (`mega_menu`) y ventana de promociones (`promotions_window`). |
| Datos | `data/muebles_america/guest_checkout.yaml` | Departamento, categoría y producto del flujo. |

Los componentes propios de una marca viven en `pages/<sitio>/components/`.
Solo pasan a `pages/common/components/` cuando se demuestra que son
equivalentes en otra marca.

### Reglas de dependencia

Se verifican en `tests/architecture/`; el detalle está en
`docs/architecture/dependency_rules.md`.

- `core` nunca importa `pages`, `workflows` ni `tests`.
- Los locators viven en `*_locators.py`, separados del comportamiento.
- Los Page Objects no contienen asserts ni `expect`.
- Los workflows no contienen locators.
- Los tests no usan locators directamente.
- Prohibido `except Exception:` tragado; los errores se clasifican.
- Sin `print()` como diagnóstico: logging estructurado con
  `run_id`/`case_id`/`site`/`environment`.
- Sin URLs literales en capas funcionales: se resuelven desde
  `config/sites.yaml` vía `ExecutionContext`.
- `conftest.py` raíz mínimo: solo registra plugins de `fixtures/`.

## Requisitos

- Python **3.13** (compatible con `>=3.11`).
- Git.
- Chromium de Playwright (se instala en el paso 3 de la instalación).
- Acceso de red a la tienda configurada para ejecutar las pruebas E2E.

## Instalación

1. Clona el repositorio y entra a la carpeta.

<!-- PENDIENTE: indicar la URL del repositorio remoto -->

```bash
git clone <url-del-repositorio>
cd framework-ecommerce-mavi
```

2. Instala las dependencias con versiones fijas.

```bash
python -m pip install -r requirements.lock
```

3. Instala el navegador de Playwright.

```bash
python -m playwright install chromium
```

`requirements.in` declara las dependencias directas y `requirements.lock`
fija las versiones resueltas.

## Uso

### Ejecución

```bash
# Suite completa (sitio y ambiente por defecto: muebles_america/stage)
pytest

# Selección multi-ecommerce
pytest --site muebles_america --target-env stage
pytest --site viu --target-env stage

# Perfil con navegador visible
pytest --exec-profile headed

# Solo pruebas sin navegador
pytest tests/unit tests/architecture

# E2E de MA: Home → categoría → PDP → carrito → checkout como invitado
pytest tests/smoke/test_guest_checkout_ma.py
```

Variables de entorno que sobrescriben las opciones: `MAVI_ECOM_SITE`,
`MAVI_ECOM_ENV` y `MAVI_ECOM_CASE_ID`.

### Configuración

| Archivo | Rol |
|---|---|
| `config/sites.yaml` | Única fuente de `base_url` y `checkout_url_pattern` por sitio y ambiente. |
| `config/environments.yaml` | Catálogo de ambientes válidos (`stage`, `prod`). |
| `config/execution_profiles.yaml` | Perfiles de ejecución (navegador, headless, timeouts). |

El ambiente se valida en **dos niveles**: debe estar declarado en
`environments.yaml` *y* existir para el sitio en `sites.yaml`.
Una combinación inválida aborta la ejecución con `UnknownSiteError` /
`UnknownEnvironmentError` en el arranque (`pytest_configure`); nunca
hay redirección silenciosa ni defaults peligrosos.

### Browser lifecycle

Los plugins de `fixtures/` administran el ciclo completo sin lógica de
ecommerce:

```text
playwright_instance (sesión)
  → browser (sesión, headless/browser del ExecutionContext)
    → context (por test, timeouts del ExecutionContext)
      → page (por test, expect_timeout aplicado)
        → pages (PageFactory del sitio activo)
```

Todas son yield-fixtures: el `close()` post-yield libera recursos tanto
en PASS como en FAIL. El navegador se selecciona por
`execution_profiles.yaml` (`chromium`, preparado para `firefox`/`webkit`)
y `headless`/`headed` por `--exec-profile`.

<!-- PENDIENTE: asignar el Case ID de Plane a test_guest_checkout_ma.py. Mientras tanto, el case_id solo llega con --case-id o MAVI_ECOM_CASE_ID. -->

### Quality gate

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

### Datos de prueba

- **Entrada**: `data/<sitio>/*.yaml` vía `DataProvider`. Hoy se usa
  `YamlDataProvider`; `ExcelDataProvider` es intercambiable. Si un dataset no
  existe para el sitio, se busca en `data/common/`.
- **Generados**: `repositories/` escribe en `artifacts/generated/<run_id>/`
  con escritura atómica.

Para cambiar el producto o la categoría del flujo de MA, edita
`data/muebles_america/guest_checkout.yaml`; no hace falta tocar el test.

### Reportes

Allure escribe resultados en `artifacts/allure-results` (configurado en
`pytest.ini`). Las evidencias de cada corrida quedan en
`artifacts/runs/<run_id>/`.

### BDD

Los `.feature` (contrato funcional) viven en `test_cases/<sitio>/` y los
steps delgados en `tests/bdd/steps/`. El runner es
`tests/bdd/test_features.py`.

## Licencia

<!-- PENDIENTE: indicar la licencia; el repositorio no tiene archivo LICENSE -->
