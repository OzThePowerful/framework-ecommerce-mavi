# CAMBIOS CP_EC_MA_CART_002 — Validar producto, cantidad, precio y subtotal del carrito

## Alcance

Alinear `CP_EC_MA_CART_002` con los 8 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_CART_002.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado** (acción → verificación).

El `@CART_002` común **no correspondía al contrato**: verificaba la
transición carrito → gate "Continuar como invitado", no la consistencia
comercial PDP → Cart.

| # | Paso del contrato | Antes (escenario común) | Ahora (escenario MA) |
|---|---|---|---|
| — | Precondición: PDP capturada | Sin verificar | `se abre la PDP del producto seleccionado` + `se registran el nombre, el identificador y el precio del producto` (de CART_001) |
| — | Precondición: producto agregado | Step compartido con timeout tragado | `agrega el producto disponible al carrito` + `el ecommerce procesa la adición del producto` (de CART_001) |
| 1 | Carrito disponible | Solo espera | Ruta `/checkout/cart` + contenedor visible (de CART_001) |
| 2 | Nombre coincide con PDP | No cubierto | Exactamente 1 ítem; nombre normalizado (espacios, mayúsculas) igual al de la PDP |
| 3 | SKU coincide, si está disponible | No cubierto | Si la fila muestra `SKU#:`, debe ser igual al de la PDP; si no, adjunto "Identificador en carrito" con `"ausente"` |
| 4 | Cantidad = seleccionada | No cubierto | Cantidad de la fila == cantidad seleccionada en la PDP |
| 5 | Precio unitario = precio aplicable | No cubierto | Precio de la fila == precio efectivo de la PDP (promocional si es menor al de lista) |
| 6 | Subtotal disponible | No cubierto | "Subtotal:" del resumen presente y > 0 (`summary_subtotal()` devuelve `None` si falta; `page_subtotal()` devolvía 0) |
| 7 | Calcular subtotal esperado con precisión decimal | No cubierto | `Money(precio aplicable × Decimal(qty))`: Decimal redondeado a centavos (`ROUND_HALF_UP`), nunca float |
| 8 | Observado vs esperado | No cubierto | Igualdad exacta al centavo. Se compara el subtotal **antes** de descuentos; el descuento del resumen se adjunta |
| Tags | `@muebles_america @cart @commercial_validation` | Solo `@CART_002` | `@muebles_america` (Feature) + `@CART_002 @cart @commercial_validation` |

Cobertura adicional que se conserva (decisión del usuario): al final,
`continúa al checkout desde el carrito` y `se muestra la opción de
continuar el checkout como invitado`. Es la verificación del CART_002
anterior.

**`CP_EC_VIU_CART_002` no cambia:** sigue corriendo el escenario común,
que el equipo VIU trabaja en `origin/viu`.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/cart/cart.feature` | Agrega `@CART_002 @cart @commercial_validation` (19 steps) |
| `tests/bdd/steps/muebles_america/cart_steps.py` | 8 steps nuevos: pasos 2–8 + gate de invitado con texto propio. Adjuntos "Identificador en carrito" y "Subtotal esperado" |
| `pages/muebles_america/cart/cart_page.py` | `summary_subtotal()`: `Money` del "Subtotal:" del resumen o `None` |
| `pytest.ini` | Marker `commercial_validation` |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en CART_002 con el contrato (tipo "Validación comercial"). Solo cambia la entrada `CP_EC_MA_CART_002` |

**No se tocan:** `test_cases/common/cart/cart.feature`, `tests/bdd/steps/cart_steps.py`,
`CartComponent`, `CommonCartPage` ni nada de VIU. El gate adicional **no**
usa el step común `se muestra la opción de continuar como invitado`,
porque `origin/viu` lo retira: tras el merge sería un step faltante.

Observables verificados en stage MA (`parrilla` → `MABE00902`, desktop 1366×768):

| Observable | Valor |
|---|---|
| PDP (SPA) | `price` = `final_price` = `regular_price` = 6119 (sin promoción) |
| Fila del carrito | `SKU#: MABE00902` · `Parrilla De Gas Mabe PM75KR0 76 Cm` · `1` · `A: $6,119.00` (`span.price.cl-accent`; la fila no muestra subtotal propio) |
| Resumen | `Subtotal: $6,119.00` · `Total (IVA incl.) $6,119.00` · sin descuento |
| Estado del SPA | `row_total 6119`, `discount_amount 0` |
| Adjunto "Subtotal esperado" | `{"quantity": 1, "unit_price_pdp": "6119.00", "expected_subtotal": "6119.00", "observed_subtotal": "6119.00", "discount": "0.00"}` |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_CART_002
pytest -m commercial_validation --site muebles_america   # validaciones comerciales
pytest -m cart --site muebles_america                    # CART_001 + CART_002
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Producto agregado / PDP capturada | Precondiciones verificadas con los steps de CART_001 |
| Precisión decimal | `Decimal` + `Money` (centavos, `ROUND_HALF_UP`); `Money` rechaza floats |
| Reglas comerciales aplicables | Precio aplicable = promocional si existe; subtotal antes de descuentos, con el descuento documentado |
| Resultado final: sin diferencias no justificadas | Pasos 2–8; la única ausencia aceptada es la del SKU en la fila, y queda documentada |
| Tags `@muebles_america @cart @commercial_validation` | Feature + escenario |
| Asserts fuera de Page Objects | Solo en `tests/bdd/steps/muebles_america/cart_steps.py` |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (27 recolectados, 6 descartados por marca) |
| `-m cart` / `-m commercial_validation` (MA) | ✅ 2 / 1 |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_CART_002` (escenario común) | ✅ | 14.3s |
| `CP_EC_MA_CART_002` run 1 / 2 / 3 | ✅ | 14.7s / 15.2s / 15.6s |
| `CP_EC_MA_CART_001` (comparte steps y página) | ✅ | 15.1s |
| `CP_EC_VIU_CART_002` (sin cambios) | ✅ | 15.1s |
| `CP_EC_MA_CHECKOUT_001` (comparte la transición al checkout) | ✅ | 27.2s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 102.1s |

Pruebas negativas con objetos falsos (fuera del repo), **17 de 17 según lo
esperado**:

- **Fallan con mensaje claro:**
  - nombre distinto;
  - 2 ítems;
  - SKU distinto;
  - cantidad distinta;
  - precio distinto;
  - subtotal ausente o en 0;
  - subtotal con 1 centavo de diferencia;
  - `3 × 1999.99` comparado contra `5999.96`.
- **Pasan:**
  - nombre con espacios o mayúsculas distintos;
  - SKU ausente (queda documentado);
  - `3 × 1999.99 = 5999.97`.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`):

- 0 conflictos de código (solo `plane_catalog.yaml`, que es generado).
- 0 steps duplicados.
- 0 steps faltantes nuevos. Los 3 faltantes son de escenarios `@pending` de `payment.feature` y ya existían. El verificador marcó un cuarto como falso positivo: el step del paso 3 se define con dos literales concatenados, que el regex no une. Las 3 corridas en vivo confirman que pytest-bdd sí lo resuelve.

## Notas

- **Limitación:** con cantidad 1, el precio de la fila y el subtotal
  valen lo mismo en stage. El cálculo `qty × precio` está probado con
  objetos falsos (qty 3), pero no en vivo, porque el contrato no pide
  cambiar la cantidad.
- MA `parrilla` no tiene promoción en stage: la regla "precio aplicable =
  promocional" está cubierta por `Product.effective_price`, pero no se
  ejercitó en vivo con un producto en promoción.
- El subtotal se compara antes de descuentos. Si el negocio define otra
  regla (por ejemplo, subtotal neto de promociones del carrito), se
  ajusta el paso 8.
