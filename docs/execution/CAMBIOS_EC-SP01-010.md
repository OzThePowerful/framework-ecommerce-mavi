# CAMBIOS EC-SP01-010 — Search y Search Results MA + VIU

**Tipo**: implementación del vertical Search con contrato funcional común + BDD.

## Qué se implementó

Vertical completo: capturar término, ejecutar búsqueda, esperar resultados,
detectar cero resultados, listar Product Cards, nombre, precio, identificador
y abrir PDP — con lógica compartida en `pages/common/` (equivalencia
verificada en el DOM real de ambas marcas).

### Componentes common (nuevos)

| Componente | API | Locators verificados |
|---|---|---|
| `product_card/` | `name()`, `identifier()` (href PDP), `price()` (Decimal), `is_purchasable()`, `is_visible()`, `open()` (click + `wait_for_url('**/*.html')`) | `.product-tile__name`, `a.product-link[href*='.html']`, `[class*='default-price'] .price`, `button.add-to-cart` |
| `search/` | `search(term)`, `wait_for_results()`, `result_count()`, `cards()`, `eligible_card()`, `load_all_cards()` | `div.product-tile`, `p:has-text('resultados de búsqueda')` |

- **Espera observable**: `wait_for_results()` se ancla al contador textual
  `N resultados de búsqueda` (el SPA no refresca el grid sin él — verificado).
- **`result_count()`** parsea el total declarado (puede exceder los tiles
  renderizados por paginación).
- **`load_all_cards()`** implementa la paginación por scroll infinito del
  sitio: baja al último tile visible hasta que el grid deje de crecer o
  alcance el total del contador.
- **`eligible_card()`** selecciona por criterios observables (visible,
  navegable, precio>0, comprable) — no usa `results.first` como estrategia.

### Pages por marca

- `pages/muebles_america/search/`: fachada sobre componentes common;
  conserva `open_product(name)` (regresión del workflow intacta).
- `pages/viu/search/` (**nuevo**): misma fachada; `pages.search()` la
  resuelve por PageFactory.

### BDD (requerido por el contrato)

- `test_cases/common/search.feature`: contrato agnóstico de marca con 2
  escenarios (con resultados / sin resultados); `--site` los materializa
  como `CP_EC_MA_SEARCH_001/002` y `CP_EC_VIU_SEARCH_001/002`.
- `tests/bdd/steps/search_steps.py`: steps delgados (pages + DataProvider,
  sin locators); incluye validación **contador = cards cargadas por scroll**.
- `tests/bdd/test_features.py`: wiring `scenarios()` con `import *` de steps.

## Datos

Sin cambios: `search.yaml` de ambos sitios ya tenía `with_results`
(`term`, `min_results`) y `without_results` (`term`, `expected_results: 0`).

## Validación obligatoria — los 4 case IDs

| Caso | Comando | Resultado |
|---|---|---|
| CP_EC_MA_SEARCH_001 | `pytest tests/bdd --site muebles_america` | ✅ PASSED |
| CP_EC_MA_SEARCH_002 | ídem | ✅ PASSED |
| CP_EC_VIU_SEARCH_001 | `pytest tests/bdd --site viu` | ✅ PASSED |
| CP_EC_VIU_SEARCH_002 | ídem | ✅ PASSED |

## Verificación adicional — scroll infinito

| Búsqueda | Contador | Inicial | Tras scroll | Match |
|---|---|---|---|---|
| MA `parrilla` | 44 | 44 | 44 | ✅ |
| VIU `estufa` | 52 | 50 | 52 | ✅ |
| **MA `celular`** | 163 | 50 | **163** | ✅ |
| **VIU `celular`** | 143 | 50 | **143** | ✅ |

## Validación del framework

| Comando | Resultado |
|---|---|
| `python scripts/quality_gate.py` | ✅ compileall · ruff · 20 architecture · 73 collected |
| Regresión `test_guest_checkout_ma.py` + `test_home.py` (stage) | ✅ 2 passed (33.6s) |

## Criterios de aceptación

- ✅ Los 4 casos se ejecutan individualmente (`--site`), deterministas.
- ✅ `results.first` no se usa como estrategia de selección (elegibilidad por
  criterios; `nth()` solo para iterar la colección).
- ✅ Datos exclusivamente vía DataProvider.
- ✅ Sin agregar al carrito (fuera de alcance respetado; solo se detecta
  `is_purchasable()`).
