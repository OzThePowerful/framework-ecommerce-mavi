# CAMBIOS EC-SP01-009 — Componentes comunes y Home MA + VIU

**Tipo**: implementación del primer vertical funcional multi-ecommerce (Home).

## Qué se implementó

Vertical Home completo: abrir home, esperar estado utilizable, identificar
marca, acceder al buscador, acceder al carrito, detectar loaders y detectar
bloqueos — con componentes comunes solo donde la equivalencia está
**verificada** (levantamiento EC-SP01-008 + verificación desktop EC-SP01-009).

### Componentes common (`pages/common/components/`)

| Componente | Estado | Detalle |
|---|---|---|
| `header/` | Enriquecido | `search_box()` (`input[type=search][aria-label='Buscar']:visible`), `open_cart()`/`is_cart_accessible()` (`button[aria-label='Abrir minicart']`), `is_account_accessible()` (`a[href='/login']`), `is_search_submittable()` (`data-testid='subscribeSubmit'`), `wait_until_ready()` |
| `loader/` | Enriquecido | `any_visible()` tolerante + `wait_until_idle()` con selector `:visible` por-item |
| `blockers/` | **Nuevo** | `BlockerComponent`: `dismiss_cookies()` (`[data-testid='closeCookieButton']`, idéntico en ambos) + `has_overlay()` (backdrops) |
| `notifications/` | Sin cambios | Componente genérico existente |
| `footer/` | Sin cambios | Componente existente |

### Pages por marca

- `pages/muebles_america/home/`: agregados `wait_until_ready()`, `brand()`, `has_blockers()`; cookies delegadas al `BlockerComponent` common (elimina locator duplicado); conserva promo overlay y mega-menú (específicos MA).
- `pages/viu/home/`: **nuevo** — compone solo componentes common; sin bloqueos específicos observados.

Sin condicionales por marca: las diferencias viven en page objects separados.

### Datos y caso

- `data/{muebles_america,viu}/home.yaml`: registro `home_001` (`expected_brand`, `expected_title_fragment` verificado en DOM).
- `data/{muebles_america,viu}/products.yaml`: campo `sku` agregado (`WHIR00789`, `WHIR00802`).
- `tests/smoke/test_home.py`: `test_home_001_estado_utilizable_y_marca` — un test agnóstico de marca que implementa `CP_EC_MA_HOME_001` y `CP_EC_VIU_HOME_001` vía `--site`. Asserts solo en el test.

### Corrección a la matriz (EC-SP01-008)

Verificación desktop reveló que `openMicrocart`/`accountButton`/`menuButton`
pertenecen al **drawer móvil oculto**; los controles desktop reales (verificados
en ambos) son `button[aria-label='Abrir minicart']` y `a[href='/login']`.
`docs/architecture/matriz_locators.md` actualizado en consecuencia.

## Validación obligatoria

| Caso | Comando | Resultado |
|---|---|---|
| CP_EC_MA_HOME_001 | `pytest tests/smoke/test_home.py --site muebles_america --target-env stage` | ✅ PASSED (9.4s) |
| CP_EC_VIU_HOME_001 | `pytest tests/smoke/test_home.py --site viu --target-env stage` | ✅ PASSED (5.6s) |

## Validación del framework

| Comando | Resultado |
|---|---|
| `python scripts/quality_gate.py` | ✅ compileall · ruff · 20 architecture · 71 collected |
| `pytest tests/unit` | ✅ 49 passed |
| Regresión E2E `test_guest_checkout_ma.py` (stage) | ✅ PASSED (32.2s) |

## Criterios de aceptación

- ✅ Ambos casos `HOME_001` se ejecutan individualmente (`--site`).
- ✅ La implementación común no contiene condicionales por marca.
- ✅ Pages sin asserts ni datos de prueba ni resolución de URLs.
- ✅ Fuera de alcance respetado: no se implementó Search/PDP/Cart/Checkout.
