# CAMBIOS CP_EC_MA_SEARCH_001 — Buscar producto utilizando un término válido

> **Ajuste posterior ([MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)):**
> este caso aplica **solo a Muebles América**. El escenario vive en
> `test_cases/muebles_america/search/` y sus steps nuevos en
> `tests/bdd/steps/muebles_america/search_steps.py`.
> `test_cases/common/search/search.feature` y `search_steps.py` volvieron
> a su versión anterior, así que `CP_EC_VIU_SEARCH_001` **no** quedó con
> estos pasos (lo trabaja la rama `origin/viu`). Las primitivas de
> `search_component` / `search_page` siguen en común como aditivas.

## Alcance

Alinear el escenario BDD `@SEARCH_001` con los 7 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_SEARCH_001.md`. El escenario se escribe
**intercalado** (acción → verificación), igual que el contrato.

El caso ya existía y pasaba, pero no cubría los primeros pasos:

| # | Paso del contrato | Antes | Ahora |
|---|---|---|---|
| 1 | Home disponible | Solo abría la home | `la home queda en estado utilizable` (reutilizado de HOME_001) |
| 2 | Buscador disponible | No se validaba | `el buscador está visible y habilitado` (reutilizado de HOME_001) |
| 3 | El campo acepta el valor | `search()` escribía y enviaba en un solo paso | Captura separada + `input_value == término` |
| 4 | La solicitud es procesada | No se validaba | Ruta `/catalogsearch/result` con `q == término` |
| 5 | Pantalla de resultados disponible | Espera implícita | Contador "N resultados de búsqueda" visible |
| 6 | Al menos un producto | Contador ≥ mínimo | Contador ≥ mínimo **y** ≥ 1 card visible |
| 7 | Al menos un producto navegable | Card elegible que abre su PDP | Sin cambio |

Validación adicional que se conserva (EC-SP01-010, no la pide el
contrato): las cards cargadas por scroll coinciden con el contador.

El `.feature` es común, así que `CP_EC_VIU_SEARCH_001` también queda con
estos pasos.

## Cambios

| Pieza | Detalle |
|---|---|
| `pages/common/components/search/search_component.py` | `search()` se divide en `type_term()` + `submit_search()`, sin cambio de comportamiento para los 14 escenarios que lo usan. Métodos nuevos: `typed_term()`, `is_results_view_ready()`, `results_query()` y `visible_card_count()` |
| `pages/common/components/search/search_locators.py` | `RESULTS_ROUTE = "/catalogsearch/result"` y `QUERY_PARAM = "q"`, verificados en stage MA y VIU |
| `pages/common/pages/search_page.py` | Exposición de las primitivas nuevas en la fachada |
| `test_cases/common/search/search.feature` | `@SEARCH_001 @search` intercalado 1:1 con el contrato |
| `tests/bdd/steps/search_steps.py` | Steps nuevos: captura, aceptación del valor, ejecución, solicitud procesada, pantalla disponible y producto visible. El step compartido `busca el término con resultados del dataset` no cambia |
| `pytest.ini` | Marker `search` registrado |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Definición `SEARCH_001` actualizada al contrato y catálogo regenerado. Solo cambian las entradas MA/VIU SEARCH_001 |

Observables verificados en stage (desktop 1366×768):

| Observable | MA (`parrilla`) | VIU (`estufa`) |
|---|---|---|
| `input_value` tras capturar | `'parrilla'` | `'estufa'` |
| URL tras ejecutar | `/catalogsearch/result?q=parrilla` | `/catalogsearch/result?q=estufa` |
| Contador | 44 resultados de búsqueda | 52 resultados de búsqueda |
| Cards iniciales | 44 | 50 (el resto se carga con scroll) |

## Datos

El término sale de `data/muebles_america/search.yaml` → `with_results`
(`term: parrilla`, `min_results: 1`) vía DataProvider. En el caso
automático no hay valores hardcodeados. El `valid_search: refrigerador`
del contrato es un ejemplo conceptual. La clave `with_results` **no se
renombró** porque la comparten 14 escenarios de MA y VIU.

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_SEARCH_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_SEARCH_001
pytest -m search --site muebles_america        # escenarios de Search marcados
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Término desde datos de prueba | Dataset `search`/`with_results` vía `data_provider` |
| Tags `@muebles_america @search` | `@search` en el escenario; la marca la materializa el Case ID |
| Asserts fuera de Page Objects | Solo en `search_steps.py` / `home_steps.py` |
| Steps sin Playwright | Delegan en `SearchPage`; arch test `test_bdd_steps_sin_secuencias_playwright` |
| Sin URLs literales | Solo la ruta relativa `RESULTS_ROUTE` (arch test `test_sin_urls_en_capas_funcionales`) |

## Validación

Quality Gate (`guia_operacion.md`):

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 115 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 |

En vivo (stage). Se ejecutó dos veces porque hubo una integración de
cambios de Magento en medio. La tabla registra la corrida **posterior** a
la integración:

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_SEARCH_001` | ✅ | 8.9s |
| `CP_EC_MA_SEARCH_001` run 1 | ✅ | 12.9s |
| `CP_EC_MA_SEARCH_001` run 2 | ✅ | 8.1s |
| `CP_EC_MA_SEARCH_001` run 3 | ✅ | 7.9s |
| `CP_EC_VIU_SEARCH_001` | ✅ | 9.5s |
| `CP_EC_MA_SEARCH_002` (comparte el componente) | ✅ | 5.7s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed | 94.0s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 5 passed | 133.2s |

Prueba negativa del paso 6: con un término sin resultados y
`min_results: 0` en el dataset de MA, el caso **falla** en el step nuevo
(`El listado no muestra ninguna card de producto`). Después se restauró
el dataset.

## Notas

- `CP_EC_MA_PDP_001` queda pendiente: su propuesta no se autorizó.
