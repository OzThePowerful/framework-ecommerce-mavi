# CAMBIOS MA-AISLAMIENTO-001 — HOME_001, SEARCH_001, SEARCH_002 y PDP_001 exclusivos de Muebles América

## Alcance

Los contratos `Context_Contratos/MA/CP_EC_MA_HOME_001`, `SEARCH_001`,
`SEARCH_002` y `PDP_001` se implementaron sobre los `.feature`, steps,
locators y componentes **comunes**. Por eso también cambiaron los casos
`CP_EC_VIU_*` equivalentes. Esto no debía pasar: el equipo VIU trabaja
esos mismos casos en la rama `origin/viu` (commits `CP_EC_VIU_HOME_001`,
`SEARCH_001`, `SEARCH_002`, `PDP_001`, `CART_001`, `CART_002`).

Este ajuste deja los 4 casos **solo en Muebles América**. Lo común vuelve
a la base `0747a7f`, la misma de la que partió `origin/viu`.

| Caso | Antes del ajuste | Ahora |
|---|---|---|
| `CP_EC_MA_HOME_001` | Escenario de 8 pasos en `test_cases/common/home/` | Mismo escenario en `test_cases/muebles_america/home/` |
| `CP_EC_VIU_HOME_001` | Corría el escenario MA y estaba en `-m smoke` | Escenario base de 3 pasos (fuera de smoke) |
| `CP_EC_MA_SEARCH_001` / `_002` | Intercalados en `test_cases/common/search/` | Mismos escenarios en `test_cases/muebles_america/search/` |
| `CP_EC_VIU_SEARCH_001` / `_002` | Corrían los escenarios MA | Escenarios base |
| `CP_EC_MA_PDP_001` | Intercalado en `test_cases/common/product/` | Mismo escenario en `test_cases/muebles_america/product/` |
| `CP_EC_VIU_PDP_001` | Corría el escenario MA | Escenario base |

Ninguna verificación de MA cambió. Solo cambió dónde vive cada pieza. La
excepción es el texto del paso 5 de HOME_001, que se renombró (ver Cambios).

### Por qué: choque con `origin/viu`

`git merge-tree steps-ma origin/viu`:

| | Antes del ajuste | Después |
|---|---|---|
| Archivos de código en conflicto | 6 (`home.feature`, `search.feature`, `header_component.py`, `header_locators.py`, `pdp_locators.py`, `pdp_steps.py`) | **0** |
| Steps con el mismo texto definidos dos veces | 1 (`el acceso al carrito está disponible`: git lo mezclaba sin avisar) | **0** |
| Steps usados en un `.feature` sin definición | 3 (VIU usa `la home identifica la marca…`, `el buscador está accesible` y `busca el término sin resultados del dataset`, que MA había retirado) | **0** |

Solo `test_cases/plane_catalog.yaml` queda en conflicto. Es un archivo
generado: tras el merge se regenera con `scripts/build_plane_catalog.py`.

## Mecanismo: escenarios exclusivos por marca

```text
test_cases/common/<modulo>/*.feature        → contrato común (todas las marcas)
test_cases/<sitio>/<modulo>/*.feature       → exclusivo de la marca (tag @<sitio> en la Feature)
```

Regla (`fixtures/execution_fixtures.py::keep_for_site`, en el hook de colección):

1. Un escenario con tag de marca (`@muebles_america`, `@viu`) solo corre en esa marca.
2. En la marca activa, ese escenario **reemplaza** al común que tiene el mismo tag de caso (`@HOME_001`, …).
3. El resto (comunes sin override, tests no BDD) no cambia.

Los items descartados se reportan como *deselected*. `--collect-only` en
`tests/bdd/test_features.py` muestra `21/25 tests collected (4 deselected)`
en cada marca. No hay `if site`: la marca sale de los tags y de
`config/sites.yaml`.

## Cambios

| Pieza | Detalle |
|---|---|
| `fixtures/execution_fixtures.py` | `keep_for_site()` (función pura) + aplicación en `pytest_collection_modifyitems` antes de materializar Case IDs |
| `tests/bdd/test_features.py` | Carga además `test_cases/<sitio>/` e importa los steps de `tests/bdd/steps/muebles_america/` |
| `tests/unit/test_case_id_materialization.py` | 5 pruebas de la regla: reemplazo en su marca, descarte en otra, común sin override, items sin tags, override por Case ID |
| `pytest.ini` | Markers `muebles_america` y `viu` |
| `test_cases/common/home/home.feature`, `search/search.feature`, `product/pdp.feature` | Restaurados a `0747a7f` |
| `tests/bdd/steps/home_steps.py`, `search_steps.py`, `pdp_steps.py` | Restaurados a `0747a7f`. Vuelven `la home identifica la marca…`, `el buscador está accesible`, `busca el término sin resultados del dataset` y los 3 Then de PDP base. El step compartido `abre la PDP de una card elegible` vuelve a su versión base |
| `pages/common/components/header/header_locators.py`, `header_component.py` | Restaurados a `0747a7f` (vuelven `NAV` y `LOGO`) |
| `pages/common/components/pdp/pdp_locators.py`, `pages/common/pages/product_page.py` | Restaurados a `0747a7f` |
| `pages/common/components/pdp/pdp_component.py` | Sale `availability_label()` (pasa a MA). Se conserva `sku` vía `.get` (ver "Aditivos en común") |
| `data/viu/home.yaml` | Restaurado a `0747a7f` (sale `expected_nav_items`) |
| `test_cases/muebles_america/home/home.feature` | `@muebles_america`; `@HOME_001 @smoke @home`, 8 pasos. El paso 5 se renombra `el acceso al carrito está visible y habilitado`, porque `origin/viu` define `el acceso al carrito está disponible` con otra implementación |
| `test_cases/muebles_america/search/search.feature` | `@muebles_america`; `@SEARCH_001 @search` y `@SEARCH_002 @search @negative`, sin cambios de pasos |
| `test_cases/muebles_america/product/pdp.feature` | `@muebles_america`; `@PDP_001 @pdp`. Usa `selecciona una card elegible y abre su PDP` en lugar del step compartido |
| `tests/bdd/steps/muebles_america/home_steps.py` | Steps de HOME_001 MA y fixture `home_expectations`. Incluye `la home queda en estado utilizable` y `el buscador está visible y habilitado`, que también usa SEARCH de MA |
| `tests/bdd/steps/muebles_america/search_steps.py` | Steps que agregaron SEARCH_001/002 de MA (captura, aceptación, ejecución, solicitud procesada, pantalla disponible, producto visible, listado vacío) |
| `tests/bdd/steps/muebles_america/pdp_steps.py` | `selecciona una card elegible y abre su PDP` (guarda nombre y href de la card antes de navegar) + pasos 2–7 de PDP_001 MA |
| `pages/muebles_america/components/header/` | `HeaderComponent` / `HeaderLocators` de MA: subclases de las comunes con `is_search_usable`, `is_cart_available`, `is_logo_visible`, `main_nav_items`, `HOME_LOGO` y `MAIN_NAV_ITEMS` |
| `pages/common/pages/home_page.py` | `HEADER: ClassVar` inyectable (por defecto el común), igual que `MEGA_MENU` |
| `pages/muebles_america/home/home_page.py` | `HEADER = HeaderComponent` de MA |
| `pages/muebles_america/product/product_locators.py`, `product_page.py` | `AVAILABILITY_LABEL` y `availability_label()` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Un bloque `muebles_america: {...}` por caso sobrescribe campos solo para MA (`_for_site`). Las 4 fichas base vuelven a `0747a7f` y los textos MA pasan al bloque. Al regenerar, las 4 fichas VIU quedan idénticas a `0747a7f` y las 4 MA solo cambian `implementacion`, que apunta a `test_cases/muebles_america/…` |

### Aditivos en común (decisión del usuario)

Se quedan en común porque **no cambian ningún resultado de VIU** y git los
mezcla sin conflicto con `origin/viu`:

- `pages/base_page.py`: `open()` devuelve el status HTTP (VIU lo ignora).
- `pages/common/pages/home_page.py`: `open_home()` propaga el status y `title()`.
- `pages/common/components/search/search_component.py` y `search_locators.py`, `pages/common/pages/search_page.py`: `type_term`, `typed_term`, `submit_search`, `is_results_view_ready`, `results_query`, `visible_card_count`, `RESULTS_ROUTE`, `QUERY_PARAM`. `search()` sigue haciendo lo mismo.
- `pdp_component.read_product()`: `sku` vía `.get(...) or ""`. Si falta el sku, VIU falla igual que antes, solo que con un assert en lugar de un `KeyError`.

### Dato VIU que se conserva (decisión del usuario)

`data/viu/search.yaml` conserva `with_results.term: "MABE00888"`, que
introdujo PDP_001. Con el término base `estufa`, la primera card en stage
sigue siendo `WHIR00686` **Agotado** y sin CTA (sondeo del 2026-11-26:
`WHIR00686` Agotado, `KOBL00213` Solo queda 1, `MABE00829` Disponible).
Con `estufa`, los casos VIU que abren una PDP fallarían en esta rama.
`origin/viu` no toca ese archivo, así que al mezclar VIU **hereda
`MABE00888`**. El equipo VIU debe saberlo.

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_HOME_001     # escenario MA
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_HOME_001    # escenario común
pytest tests/bdd/test_features.py --site viu --collect-only -q    # 21/25 (4 deselected: los de MA)
pytest -m muebles_america --site muebles_america                  # solo escenarios exclusivos de MA
python scripts/build_plane_catalog.py
```

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed (115 + 5 de `keep_for_site`) |
| `--collect-only` MA / VIU | ✅ 21 / 21 (25 recolectados, 4 descartados por marca) |
| Escenario recolectado por marca | ✅ MA → `test_cases/muebles_america/…` ×4; VIU → `test_cases/common/…` ×4 (escenarios base) |
| `-m smoke --collect-only` MA / VIU | ✅ 5 / 4 |

En vivo (stage). Durante la validación stage respondió más lento que en la línea base:

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa (HEAD) MA HOME / SEARCH_001 / SEARCH_002 / PDP_001 | ✅ ✅ ✅ ✅ | 8.3s / 7.7s / 6.4s / 10.3s |
| Línea base previa (HEAD) VIU HOME / SEARCH_001 / SEARCH_002 / PDP_001 | ✅ ✅ ✅ ✅ | 5.7s / 7.3s / 6.5s / 10.5s |
| `CP_EC_MA_HOME_001` run 1 / 2 / 3 | ✅ | 17.2s / 10.1s / 8.1s |
| `CP_EC_MA_SEARCH_001` run 1 / 2 / 3 | ✅ | 17.1s / 15.5s / 17.8s |
| `CP_EC_MA_SEARCH_002` run 1 / 2 / 3 | ✅ | 10.3s / 10.2s / 9.9s |
| `CP_EC_MA_PDP_001` run 1 / 2 / 3 | ✅ | 17.1s / 16.7s / 16.8s |
| `CP_EC_VIU_HOME_001` (escenario base) | ✅ | 17.9s |
| `CP_EC_VIU_SEARCH_001` (escenario base) | ✅ | 14.1s |
| `CP_EC_VIU_SEARCH_002` (escenario base) | ✅ | 11.3s |
| `CP_EC_VIU_PDP_001` (escenario base, `MABE00888`) | ✅ | 12.7s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed | 117.2s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 4 passed (antes 5: `CP_EC_VIU_HOME_001` vuelve a no ser smoke) | 158.0s |

Prueba negativa del escenario MA: con `expected_title_fragment: "VIU"` en
`data/muebles_america/home.yaml`, `CP_EC_MA_HOME_001` **falla** en
`tests/bdd/steps/muebles_america/home_steps.py` (`El título 'Muebles
América - …' no identifica la marca 'VIU'`). El dataset se restauró en un
bloque `try/finally` y `git diff` quedó vacío.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`,
sin tocar ramas ni índice): 0 conflictos de código, 0 steps duplicados y
0 steps faltantes nuevos. Los únicos 3 faltantes son steps de escenarios
`@pending` de `payment.feature` y ya existían antes.

## Notas

- **Al mezclar `origin/viu`:** sus cambios comunes aplicarán también a MA.
  Por ejemplo, `is_available()` pasa a exigir la etiqueta verde y el step
  compartido `abre la PDP de una card elegible` recorre candidatos. Los
  casos MA que usan esas piezas (CART, Checkout, …) deben revalidarse
  después del merge.
- El comentario de cabecera de `test_cases/common/home/home.feature` (base)
  sigue diciendo `--site muebles_america → CP_EC_MA_HOME_001`. No se tocó
  para no generar conflicto con `origin/viu`. En MA ese escenario queda
  reemplazado por el exclusivo.
- `CP_EC_MA_CART_001` sigue pendiente (propuesta no autorizada). Se rehará
  como escenario exclusivo de MA con este mecanismo y con textos de step
  que no choquen con `origin/viu`, que ya define `el producto agregado es
  visible en el carrito con cantidad 1`.
- Los CAMBIOS de HOME_001, SEARCH_001, SEARCH_002 y PDP_001 llevan una
  nota "Ajuste posterior" que apunta a este documento.
