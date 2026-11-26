# CAMBIOS CP_EC_MA_SEARCH_002 — Validar búsqueda sin resultados

## Alcance

Alinear el escenario BDD `@SEARCH_002` con los 5 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_SEARCH_002.md`. Igual que en SEARCH_001,
el escenario va **intercalado** (acción → verificación).

El caso existía con 3 steps y del contrato cubría solo el paso 5:

| # | Paso del contrato | Antes | Ahora |
|---|---|---|---|
| 1 | Home disponible | Abría la home sin comprobar nada | `la home queda en estado utilizable` (reutilizado de HOME_001) |
| 2 | Valor aceptado | Escribía y enviaba en un solo paso | Captura separada + `input_value == término` (reutilizado de SEARCH_001) |
| 3 | La solicitud finaliza correctamente | Espera implícita del contador | Ruta `/catalogsearch/result` con `q == término` + pantalla de resultados disponible (reutilizados de SEARCH_001) |
| 4 | No aparecen productos válidos | **No se revisaba el listado**: un contador en 0 con productos en pantalla pasaba igual | Ninguna card visible en el listado (step nuevo) |
| 5 | Mensaje o comportamiento de cero resultados | Contador == 0 | Sin cambio |

El `.feature` es común, así que `CP_EC_VIU_SEARCH_002`, cuyo contrato
tiene los mismos 5 pasos, queda igual de alineado.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/search/search.feature` | `@SEARCH_002 @search @negative` intercalado 1:1 con el contrato (9 steps) |
| `tests/bdd/steps/search_steps.py` | Nuevos: `captura en el buscador el término sin resultados del dataset` y `no aparece ningún producto en el listado`. Se retira `busca el término sin resultados del dataset`, que solo usaba este escenario |
| `pytest.ini` | Marker `negative` registrado |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Definición `SEARCH_002` actualizada al contrato (tipo "Funcional negativo", pasos, resultado, postcondición, tag `negative`) y catálogo regenerado. Solo cambian las entradas MA/VIU SEARCH_002 |

**No se tocan** páginas, componentes, locators ni datasets: la página de
búsqueda ya exponía todo lo necesario desde SEARCH_001
(`type_term`, `typed_term`, `submit_search`, `results_query`,
`is_results_view_ready`, `visible_card_count`).

Observables verificados en stage con el término `zzzz-producto-inexistente-qa`
(desktop 1366×768):

| Observable | MA | VIU |
|---|---|---|
| `input_value` tras capturar | término completo | término completo |
| URL tras ejecutar | `/catalogsearch/result?q=zzzz-producto-inexistente-qa` | igual |
| Estado vacío | contador `0 resultados de búsqueda` (no hay otro mensaje) | igual |
| Cards / recomendaciones | 0 / ninguna | 0 / ninguna |

## Datos

El término controlado sale de `data/<sitio>/search.yaml` →
`without_results` (`term: zzzz-producto-inexistente-qa`,
`expected_results: 0`). La clave `invalid_search` del contrato es
conceptual; no se renombró, con el mismo criterio que en SEARCH_001.

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_SEARCH_002
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_SEARCH_002
pytest -m negative --site muebles_america      # escenarios negativos
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Término controlado sin resultados | Dataset `search`/`without_results` vía `data_provider` |
| Tags `@muebles_america @search @negative` | `@search @negative` en el escenario; la marca la materializa el Case ID |
| Sin información inconsistente | El paso 4 (0 cards visibles) y el paso 5 (contador 0) se verifican por separado: si el contador dice 0 pero el listado muestra productos, el caso falla |
| Postcondición (VIU): no se selecciona ningún producto | El escenario no abre ninguna card |
| Asserts fuera de Page Objects | Solo en `search_steps.py` / `home_steps.py` |

## Validación

Quality Gate (`guia_operacion.md`):

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 115 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_SEARCH_002` | ✅ | 12.0s |
| `CP_EC_MA_SEARCH_002` run 1 | ✅ | 7.6s |
| `CP_EC_MA_SEARCH_002` run 2 | ✅ | 7.9s |
| `CP_EC_MA_SEARCH_002` run 3 | ✅ | 7.4s |
| `CP_EC_VIU_SEARCH_002` | ✅ | 7.3s |
| `CP_EC_MA_SEARCH_001` (comparte steps) | ✅ | 8.0s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed | 98.8s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 5 passed | 148.0s |

Prueba negativa del paso 4: con `without_results.term: "parrilla"`
(término con resultados) en el dataset de MA, el caso **falla** en el
step nuevo (`Una búsqueda sin coincidencias no debería mostrar
productos; el listado muestra 44`). Después se restauró el dataset y
`git diff` lo confirmó.

## Notas

- `CP_EC_MA_PDP_001` sigue pendiente: su propuesta no se autorizó.
