# CAMBIOS CP_EC_MA_PDP_001 — Validar información de un producto disponible en PDP

> **Ajuste posterior ([MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)):**
> este caso aplica **solo a Muebles América**. El escenario vive en
> `test_cases/muebles_america/product/` y sus steps en
> `tests/bdd/steps/muebles_america/pdp_steps.py`. Usa el step propio
> `selecciona una card elegible y abre su PDP`, y el step compartido
> `abre la PDP de una card elegible` volvió a su versión anterior.
> `AVAILABILITY_LABEL` / `availability_label()` pasaron a la PDP de MA.
> `CP_EC_VIU_PDP_001` quedó en su versión anterior (lo trabaja la rama
> `origin/viu`). Por decisión del usuario, `data/viu/search.yaml`
> **conserva** `MABE00888`.

## Alcance

Alinear el escenario BDD `@PDP_001` con los 7 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_PDP_001.md`. Como SEARCH_001 y
SEARCH_002, el escenario va **intercalado** (acción → verificación).

Durante la validación apareció una regla de negocio que el framework no
verificaba: la **etiqueta de disponibilidad** de la PDP. También se
cambió el producto de prueba de VIU (ver Hallazgo).

| # | Paso del contrato | Antes | Ahora |
|---|---|---|---|
| 1 | Se muestran productos | Buscaba sin comprobar resultados | Contador ≥ mínimo + ≥ 1 card visible (reutilizados de SEARCH_001) |
| 2 | Se abre **su** PDP | Solo esperaba una URL `*.html` | La URL contiene el slug de la card **y** el nombre de la PDP es igual al de la card |
| 3 | Nombre no vacío | Junto con el SKU en un solo step | Step propio |
| 4 | Identificador válido o ausencia documentada | Exigía sku y product_id; sin `sku` se caía con `KeyError` | Basta un identificador válido (sku en la URL; product_id numérico). El ausente se documenta en Allure como `"ausente"` |
| 5 | Importe mayor a cero | Junto con la disponibilidad | Step propio (precio unitario y efectivo > 0; promocional < unitario) |
| 6 | El producto puede ser comprado | Solo el estado del SPA (status, visibility, stock) | **Etiqueta `Disponible` o `Solo queda N` (N ≥ 1)**; `Agotado` falla. Se conserva la regla de estado |
| 7 | Agregar al carrito disponible y habilitado | Igual | Sin cambio de lógica; texto alineado |
| Tags | `@pdp` | Solo `@PDP_001` | `@PDP_001 @pdp` |

El `.feature` es común, así que `CP_EC_VIU_PDP_001` también queda
alineado. `@PDP_002` (configurable) no se tocó.

## Hallazgo: el estado del SPA no basta para saber si un producto se vende

En stage VIU, el primer resultado de "estufa" era `WHIR00686`:

| Fuente | Qué dice |
|---|---|
| `__INITIAL_STATE__.product.current` | `status 1`, `visibility 4`, `is_in_stock true`, `qty 6`, `stock_status 1` → "vendible" |
| Etiqueta de la PDP | **Agotado** (`span.fw-700.cl-accent`) |
| Botón agregar al carrito | No existe |

Además, `KOBL00213` muestra "Solo queda 1" con `qty 5` en el estado: el N
de la etiqueta no es `stock.qty`. **La etiqueta es la fuente de verdad
para el cliente**, por eso el paso 6 la exige. Por confirmación del
negocio, `WHIR00686` está agotado.

Regla de la etiqueta (confirmada por negocio): `Disponible` / `Agotado` /
`Solo queda N`. "Solo queda N" aparece cuando quedan pocas piezas; el
umbral es una configuración del backend, así que **el framework no
valida el umbral**, solo que N ≥ 1.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/product/pdp.feature` | `@PDP_001 @pdp` intercalado 1:1 con el contrato (11 steps) |
| `tests/bdd/steps/pdp_steps.py` | El step compartido `abre la PDP de una card elegible` (12 escenarios) conserva su texto y comportamiento; además guarda `card_name`/`card_href` antes de navegar. Hay 6 steps nuevos (pasos 2–7) con adjuntos Allure "Product PDP", "Identificadores" y "Disponibilidad PDP". Se retiran los 3 steps viejos, que solo usaba PDP_001 |
| `pages/common/components/pdp/pdp_locators.py` | `AVAILABILITY_LABEL`: localiza por texto (`Disponible\|Agotado\|Solo queda N`), no por clase de color |
| `pages/common/components/pdp/pdp_component.py` | `availability_label()` (sondeo: `None` si no hay etiqueta). `read_product()` lee `sku` con `.get(...) or ""` para que la ausencia llegue al step en vez de un `KeyError` |
| `pages/common/pages/product_page.py` | Exposición de `availability_label()` |
| `data/viu/search.yaml` | `with_results.term`: `"estufa"` → `"MABE00888"` (1 resultado, Disponible, 43 piezas) |
| `pytest.ini` | Marker `pdp` registrado |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Definición `PDP_001` actualizada al contrato y catálogo regenerado. Solo cambian las entradas MA/VIU PDP_001 |

**No se cambió** `is_available()` ni `Product.availability`, que siguen
con la regla de estado. Los usan el workflow de venta y las variantes de
PDP_002, que no tienen etiqueta. Incorporar la etiqueta a la
disponibilidad del dominio queda como propuesta futura.

**Impacto lateral del dato VIU:** `with_results` lo comparten los
escenarios VIU que buscan "con resultados" (Search, PDP, Cart, Checkout,
Customer, Address, Shipping, Payment, Order, E2E). Todos pasan a usar
`MABE00888` y dejan de caer en el producto agotado.

Observables verificados en stage (desktop 1366×768):

| Producto | Etiqueta | Clase | CTA |
|---|---|---|---|
| MA `MABE00902` (término `parrilla`) | Disponible | `cl-green-label` | ✅ |
| VIU `MABE00888` (término `MABE00888`) | Disponible | `cl-green-label` | ✅ |
| VIU `KOBL00213` | Solo queda 1 | `cl-green-label` | ✅ |
| VIU `WHIR00686` | Agotado | `cl-accent` | ❌ |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_PDP_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_PDP_001
pytest -m pdp --site muebles_america          # escenarios de PDP marcados
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Producto obtenido desde Search | Card elegible del término `with_results` vía `data_provider` |
| Datos observados a conservar | Adjunto "Product PDP": product_name, sku, product_id, unit_price, promotional_price, availability (+ etiqueta en "Disponibilidad PDP"); `pdp_ctx["product"]` disponible para steps posteriores |
| Ausencia documentada (paso 4) | Adjunto "Identificadores" con `"ausente"` por campo |
| Tags `@muebles_america @pdp` | `@pdp` en el escenario; la marca la materializa el Case ID |
| Asserts fuera de Page Objects | Solo en `pdp_steps.py` / `search_steps.py` |

## Validación

Quality Gate (`guia_operacion.md`):

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 115 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 |

En vivo (stage, después de la integración de Magento):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_PDP_001` | ✅ | 12.1s |
| Línea base previa `CP_EC_VIU_PDP_001` (código anterior) | ❌ CTA ausente en `WHIR00686` (Agotado) | — |
| `CP_EC_MA_PDP_001` run 1 / 2 / 3 | ✅ | 9.1s / 8.8s / 8.3s |
| `CP_EC_VIU_PDP_001` run 1 / 2 / 3 | ✅ | 9.0s / 9.3s / 8.4s |
| `CP_EC_VIU_SEARCH_001` (dato VIU nuevo) | ✅ | 7.3s |
| `CP_EC_VIU_CART_001` (dato VIU + step compartido) | ✅ | 13.7s |
| `CP_EC_MA_CART_001` (step compartido) | ✅ | 14.9s |
| Smoke MA | ✅ 5 passed | 96.3s |
| Smoke VIU | ✅ 5 passed | 137.9s |

Pruebas negativas:

- **Paso 6, en vivo:** con el término VIU `WHIR00686` el caso **falla**
  (`La PDP marca el producto como 'Agotado'; no se puede comprar`).
  Después se restauró el dataset y se verificó que el contenido era
  idéntico.
- **Pasos 2 y 4, con objetos falsos (fuera del repo):** 8 de 8 según lo
  esperado. Fallan nombre distinto, slug distinto, ambos identificadores
  ausentes, product_id no numérico y sku que no está en la URL. Pasan la
  coincidencia con espacios o mayúsculas distintos y que falte solo uno
  de los dos identificadores (queda documentado).

## Notas

- La etiqueta de disponibilidad es una regla de negocio nueva para el
  framework: conviene incluirla en `docs/business_rules/reglas_negocio.md`
  cuando se genere.
- Pendiente para negocio/Magento: el estado del SPA (`is_in_stock`, `qty`)
  de `WHIR00686` contradice su etiqueta "Agotado".
- El contrato VIU pide también el tag `@product`; no se agregó porque el
  de MA no lo pide.
