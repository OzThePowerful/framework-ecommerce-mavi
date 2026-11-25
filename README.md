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
equivalentes en otra marca. Componentes comunes verificados: `header`
(buscador, minicart, cuenta), `loader`, `blockers` (cookies/overlays),
`notifications`, `search` (grid + scroll infinito), `product_card`, `pdp`
(modelo `Product` desde el estado del SPA, incluidos configurables),
`cart` (minicart → `/checkout/cart`, ítems y resumen como `Cart`/`CartItem`),
`checkout` (gate invitado + acordeón OSC), `customer_form` (datos del
comprador como `Customer`), `address` (dirección → `Address`, CP con
autocompletado), `shipping` (entrega domicilio/sucursal + store picker y
costo como `Shipping`), `payment` (métodos de pago, contado OpenPay;
`confirm_order()` ejecuta la compra solo desde casos ORDER/E2E
autorizados), `order` (éxito inequívoco + folio de la orden) y `footer`.

Las tarjetas de prueba son datos ficticios de sandbox OpenPay
(`4111…1111` contado, `4242…4242` MSI — también contado): viven
versionadas en `data/<sitio>/payment.yaml` (fixture `payment_card`).
Los datos privados del equipo van en `.env` — gitignored — cargados por
`conftest.py` vía `load_dotenv()` (en CI llegan como secrets): login
`MAVI_LOGIN_<SITIO>_*` (fixture `site_credentials`), API `MAVI_API_*`
e identidad del comprador `MAVI_GUEST_<SITIO>_*` (fixture
`guest_customer` — correo real, el checkout lo valida externamente).

### Reglas de dependencia

Se verifican en `tests/architecture/`; el detalle está en
`docs/architecture/dependency_rules.md`.
La estrategia de selectores por pantalla/marca (verificada contra el DOM real)
está en `docs/architecture/matriz_locators.md`; el levantamiento funcional del
checkout (campos, métodos de pago, contado, fronteras e irreversibles) en
`docs/architecture/levantamiento_checkout.md`.

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

### Dominio

`domain/` contiene los modelos de negocio independientes de la UI
(`Product`, `Cart`/`CartItem`, `Customer`, `Address`, `Shipping`,
`Order`) y `Money` — importes con `Decimal`, cuantizados a 2
decimales, con operaciones y comparaciones que rechazan mezclar
monedas. Las capas funcionales intercambian estos objetos, no
diccionarios genéricos.

### Datos de prueba

- **Entrada**: `data/<sitio>/*.yaml` vía `DataProvider`. Hoy se usa
  `YamlDataProvider`; `ExcelDataProvider` es intercambiable sin tocar
  consumidores. Si un dataset no existe para el sitio, se busca en
  `data/common/` (fallback).
- **Generados**: `repositories/` escribe en `artifacts/generated/<run_id>/`
  con escritura atómica.

Datasets base por ecommerce (`data/muebles_america/` y `data/viu/`):

| Dataset | Contenido |
|---|---|
| `search.yaml` | Términos con/sin resultados |
| `products.yaml` | Productos verificados en stage |
| `customers.yaml` | Clientes de prueba (ficticios) |
| `addresses.yaml` | Direcciones de prueba (ficticias) |
| `checkout.yaml` | Parámetros del checkout; referencia claves de `customers`/`addresses` |
| `payment.yaml` | Métodos de pago (`status: pending` hasta levantamiento) |

Nomenclatura: cada archivo es un mapa `clave_logica → campos` (ej.
`guest:`, `guadalajara:`). El consumo es `provider.get_dataset(nombre)`
o `provider.get_record(dataset, clave)`; los tests nunca conocen rutas.
No se almacenan datos personales reales ni secretos.

Para cambiar el producto o la categoría del flujo de MA, edita
`data/muebles_america/guest_checkout.yaml`; no hace falta tocar el test.

### Reportes y evidencias

Allure escribe resultados en `artifacts/allure-results` (configurado en
`pytest.ini`). Cada test queda etiquetado con `run_id`, `case_id`,
`site`, `environment` y `browser`, y `environment.properties` resume la
ejecución.

La evidencia por ejecución y por caso queda en:

```text
artifacts/runs/<run_id>/<case_id>/
├── screenshots/   # failure.png full-page ante un fallo
├── logs/          # current_url.txt, exception.txt
├── traces/        # preparado para Playwright trace (futuro)
├── videos/        # preparado para video (futuro)
└── manifest.json  # run_id, case_id, outcome, sitio, ambiente,
                   # navegador, URL de la página y excepción original
```

La captura es automática: si un test que usó `page` falla, el teardown
de la fixture genera la evidencia y la adjunta a Allure antes de
liberar el navegador. Los logs estructurados incluyen `run_id`,
`case_id`, `site`, `environment` y `browser` por línea.

### BDD

Los `.feature` (contrato funcional) viven en `test_cases/common/<modulo>/`
y se materializan por marca con `--site <muebles_america|viu>`; los
steps delgados están en `tests/bdd/steps/` y el runner es
`tests/bdd/test_features.py`.

Cada escenario lleva su Case ID como tag (`@<MODULO>_<NNN>`); un hook
de colección renombra el item a `CP_EC_<MA|VIU>_<MODULO>_<NNN>`, así
`-k CP_EC_VIU_CART_001` ejecuta un caso puntual. Escenarios marcados
`@pending` se coleccionan como `skipped` — nunca como PASS.

```bash
pytest tests/bdd/test_features.py --site viu                    # suite BDD VIU
pytest tests/bdd/test_features.py -k CP_EC_MA_ORDER_001 --site muebles_america
```

### Ejecución selectiva por Case ID

`--case-id` ejecuta un único Test Case y **deriva el sitio de su marca**
(no hace falta `--site`; uno explícito que contradiga la marca falla):

```bash
pytest --case-id CP_EC_MA_CART_001    # ejecuta solo ese caso en MA
pytest --case-id CP_EC_VIU_HOME_001   # ejecuta solo ese caso en VIU
```

El ID se valida contra `test_cases/plane_catalog.yaml`: formato
inválido, ID inexistente o conflicto de marca son errores explícitos
(exit 4) con sugerencias — nunca una corrida vacía.

### Smoke suite

Verificación rápida no transaccional del camino comercial (Home →
departamento → PDP → Cart → Checkout invitado). Nunca crea órdenes.

```bash
pytest -m smoke --site muebles_america   # suite smoke MA
pytest -m smoke --site viu               # suite smoke VIU
pytest --case-id CP_EC_MA_SMOKE_001      # el caso, sitio derivado
```
```

Nota operativa: `E2E_001` y `ORDER_001/002` crean órdenes reales en
stage — excluirlos de regresiones habituales con `-k "not E2E and not ORDER"`.

### Catálogo de Test Cases (Plane)

El catálogo normalizado `test_cases/plane_catalog.yaml` (42 casos,
12 módulos) se regenera con `python scripts/build_plane_catalog.py`.
Plane es la fuente de verdad; el framework produce el artefacto.
Convención: `CP_EC_<MA|VIU>_<MODULO>_<NNN>`. Ver `docs/test_catalog/`.

Distribución actual: 38 Automated · 4 Not Automated
(`PAY_002`/`PAY_003` ×2 marcas — reglas de negocio sin dataset).

## Licencia

<!-- PENDIENTE: indicar la licencia; el repositorio no tiene archivo LICENSE -->
