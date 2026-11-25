# Guía de desarrollo

Cómo crear cada tipo de artefacto siguiendo las convenciones del repo.
Regla general: **imita el artefacto vecino más parecido** y respeta las
reglas de `tests/architecture/` (se verifican en el Quality Gate).

## Cómo crear Locators

Archivo `pages/<sitio>/<modulo>/<modulo>_locators.py` — clase de
constantes, sin lógica ni acciones Playwright:

```python
"""Locators de <modulo> de <Marca> (solo definiciones)."""


class ModuloLocators:
    SUBMIT_BUTTON = "button.add-to-cart:visible"
```

- Prefiere selectores de rol/texto o clases estables de plataforma;
  `:visible` discrimina las copias móvil/desktop duplicadas.
- Si el locator es idéntico en todas las marcas, vive en
  `pages/common/components/<modulo>/<modulo>_locators.py`.

## Cómo crear un Component

`pages/common/components/<nombre>/<nombre>_component.py` si es común, o
`pages/<sitio>/components/<nombre>/` si es propio de la marca. Un
componente encapsula una región reutilizable de la UI (header, minicart,
mega-menú); usa su `*_locators.py` y devuelve estado o modelos de dominio.

**Solo se promueve a `common/` cuando está verificado en ≥2 marcas** —
nunca por anticipado.

## Cómo crear un Page Object

Un `*_page.py` por pantalla/módulo. Si el comportamiento es común:

1. Crea/extend la base en `pages/common/pages/<modulo>_page.py`
   (`CommonXPage(BasePage)`).
2. La fachada de marca queda delgada en `pages/<sitio>/<modulo>/<modulo>_page.py`:

```python
"""<Módulo> de <Marca>: fachada sobre la base common."""

from typing import ClassVar

from pages.common.pages.modulo_page import CommonModuloPage
from pages.<sitio>.modulo.modulo_locators import ModuloLocators


class ModuloPage(CommonModuloPage):
    LOCATORS: ClassVar[type] = ModuloLocators
```

- Registra el sitio en `PageFactory._SITE_PACKAGES` (`fixtures/page_fixtures.py`)
  si es marca nueva; los métodos `pages.<modulo>()` ya resuelven el módulo.
- Sin asserts, sin URLs, sin `except` tragados.

## Cómo crear un Workflow

`workflows/common/<nombre>_workflow.py` si es multi-ecommerce. Coordina
pages, levanta `PreconditionError` cuando el negocio bloquea, y devuelve
modelos de dominio — nunca locators ni asserts. Ejemplo de referencia:
`workflows/common/sale_cash_workflow.py`.

## Cómo crear un Domain Model

`domain/models/<nombre>.py` — `@dataclass` inmutable con tipos; el dinero
viaja como `domain.money.money.Money`. Los modelos son el contrato entre
pages/workflows y tests.

## Cómo crear un Dataset

`data/<sitio>/<tema>.yaml` (o `data/common/` si es compartido). Los tests
lo leen vía fixture `data_provider.get_record(tema, clave)` — nunca por
ruta física. Datos privados (identidad del comprador, credenciales) van en
`.env` con prefijo `MAVI_*` y se exponen vía fixtures (`guest_customer`,
`site_credentials`, `payment_card`).

## Cómo crear un Test Case (feature + step + Case ID)

1. **Feature** en `test_cases/common/<modulo>/<tema>.feature` (o
   `test_cases/<sitio>/` si es exclusivo de una marca):

```gherkin
Feature: <Título>
  Contrato funcional ...

  @NUEVO_001
  Scenario: <descripción>
    Given <preparación>
    When <acción>
    Then <verificación>
```

2. **Registrar el marker** en `pytest.ini` (`NUEVO_001: case id BDD`).
   El hook materializa el nodeid `CP_EC_<CODE>_NUEVO_001` por marca.
   Para un caso trazable sin automatizar aún: tag `@pending`.
3. **Steps** en `tests/bdd/steps/<modulo>_steps.py` — delgados, delegan en
   pages/workflows vía fixtures (`pages`, `data_provider`,
   `execution_context`, `order_ctx`, …) e importa el módulo en
   `tests/bdd/test_features.py` para registrarlo.
4. **Catálogo**: `python scripts/build_plane_catalog.py` regenera
   `test_cases/plane_catalog.yaml`.

## Cómo agregar un nuevo ecommerce

Sin copiar el framework — la marca hereda todo lo común:

1. **`config/sites.yaml`**: agrega `<sitio>` con `code` (prefijo del Case
   ID) y sus `environments` (`base_url` + `checkout_url_pattern`).
2. **`fixtures/page_fixtures.py`**: agrega la marca a `_SITE_PACKAGES`
   → `pages.<sitio>`.
3. **`pages/<sitio>/`**: crea `<modulo>/` por cada fachada que consuma
   `PageFactory` (`home`, `search`, `product`, `cart`, `checkout`,
   `payment`, `order`). Empieza como subclase vacía de la base common;
   agrega `*_locators.py` y overrides **solo** donde el DOM difiera.
4. **`pages/<sitio>/components/`**: componentes propios (p.ej. un menú con
   DOM distinto) inyectados por ClassVar en la fachada.
5. **`data/<sitio>/`**: datasets obligatorios (ver `test_datasets.py`:
   `search`, `products`, `addresses`, `checkout`, `payment`, …).
6. **`.env.example` + `.env`**: bloque `MAVI_GUEST_<CODE>_*` /
   `MAVI_LOGIN_<CODE>_*`.
7. **`.env` CI**: mismas variables como secrets.
8. **Validación**: `pytest --site <sitio> --collect-only` debe materializar
   los `CP_EC_<CODE>_*`; corre `HOME_001` y `SMOKE_001` de la marca nueva.
