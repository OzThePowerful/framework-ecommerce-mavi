# CAMBIOS CP_EC_MA_SMOKE_001 — Validar Smoke del flujo de compra previo al pago

## Alcance

Alinear `CP_EC_MA_SMOKE_001` con los 6 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_SMOKE_001.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)). El
escenario va **intercalado**: cada acción del contrato lleva su
verificación. **No agrega steps nuevos:** encadena steps de MA que ya
existen (HOME, SEARCH, PDP, CART y CHECKOUT_001). Respeta la restricción
del contrato: no confirma pago ni genera pedido.

Incluye una **corrección previa en la PDP de MA**, decidida al autorizar:
la etiqueta de disponibilidad cambió en stage y rompía PDP_001,
CHECKOUT_001 y este smoke. Ver [Corrección de la PDP](#corrección-de-la-pdp-etiqueta-de-disponibilidad).

| # | Paso del contrato | Antes (escenario común, `GuestCheckoutWorkflow`) | Ahora (escenario MA) |
|---|---|---|---|
| 1 | Abrir Home → operativo | Abría la home sin verificar | `la home queda en estado utilizable` (header visible, sin overlays) |
| 2 | Buscar producto → resultados disponibles | **No buscaba**: navegaba por mega-menú (departamento) | Búsqueda del dataset procesada para el término, pantalla de resultados disponible y ≥ 1 producto en el listado |
| 3 | Abrir PDP → producto disponible | Abría una PDP sin verificar | PDP del producto de la card elegida; etiqueta de disponibilidad comprable, stock > 0 y cantidad mínima 1 |
| 4 | Agregar producto → agregado correctamente | Click sin confirmación | Adición procesada por el ecommerce (ítem con `server_item_id`, cantidad 1) y confirmada (toast con el producto y minicart = 1) |
| 5 | Abrir carrito → producto presente | **No se verificaba** | Carrito disponible con el producto registrado y cantidad 1 |
| 6 | Iniciar Checkout → checkout disponible | Precio del pedido > 0 | Opción de invitado visible; tras continuar como invitado, la primera etapa del checkout carga (URL del checkout, etapa `entrega`, pago aún deshabilitado) |
| Restricción | No confirmar pago ni generar pedido | Se cumplía | Se cumple: termina en la primera etapa del checkout |
| Tags | `@muebles_america @smoke` | `@smoke @SMOKE_001` | `@muebles_america` (Feature) + `@smoke @SMOKE_001` |

Decisiones al autorizar:
- el paso 6 llega **hasta la primera etapa del checkout**, no solo hasta la opción de invitado;
- **no** se conserva la verificación anterior "precio del pedido > 0".

**`CP_EC_VIU_SMOKE_001` no cambia:** sigue corriendo el escenario común, que
`origin/viu` reescribe en su rama (`25a6743`).

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/smoke/sale_cash.feature` (nuevo) | `@muebles_america` + `@smoke @SMOKE_001` (20 steps, todos existentes) |
| `pages/muebles_america/product/product_locators.py` | `AVAILABILITY_LABEL` acepta `Solo quedan? N` (singular y plural) |
| `pages/muebles_america/product/product_page.py` | `availability_label(timeout_ms=15000)`: la espera pasa de 5 s a 15 s y se documenta que la etiqueta llega tras `/api/stock/check` |
| `tests/bdd/steps/muebles_america/pdp_steps.py` | `_PURCHASABLE_LABEL` acepta `solo quedan? (\d+)`; se sigue exigiendo N ≥ 1 |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en SMOKE_001 con el contrato. Solo cambia `CP_EC_MA_SMOKE_001`; el resto es renumeración de alias YAML |

**No se tocan:**
- `test_cases/common/smoke/sale_cash.feature` y `tests/bdd/steps/sale_cash_steps.py`;
- `GuestCheckoutWorkflow` (lo siguen usando los smoke legados `tests/smoke/test_guest_checkout_*.py`);
- ningún dataset ni nada de VIU.

No se usan los textos nuevos de `origin/viu` (`el producto agregado es
visible en el carrito con cantidad 1`, `el acceso como invitado está
disponible`).

## Corrección de la PDP: etiqueta de disponibilidad

Síntoma: `CP_EC_MA_PDP_001`, `CP_EC_MA_CHECKOUT_001` (que pasaba esa misma
mañana) y el nuevo SMOKE_001 fallaban con `La PDP no muestra la etiqueta de
disponibilidad`.

Diagnóstico en stage MA (sondeos de solo lectura sobre PDP_001, producto `MABE00902`):
- la etiqueta se pinta **después** de cargar la PDP, tras `GET /api/stock/check` (≈ 1.6–2.0 s), que responde `{"qty": 24, "is_in_stock": true, …}`;
- el texto visible es **"Solo quedan 24"** (`span.fw-700.cl-green-label`), en plural. La regex solo aceptaba `Disponible`, `Agotado` o `Solo queda N`, en singular, así que ni esperando 45 s había coincidencia;
- con la regex corregida, la etiqueta se encuentra en las tres corridas del smoke (`{"label": "Solo quedan 24"}`).

La espera se amplía a 15 s porque la etiqueta depende de un servicio
adicional (observación del equipo). El `wait_for` termina en cuanto la
etiqueta aparece, así que no alarga las corridas normales.

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_SMOKE_001
pytest -m smoke --site muebles_america
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Flujo Home → Search → PDP → Add to Cart → Cart → Start Checkout | Pasos 1–6, en ese orden, con búsqueda (ya no por departamento) |
| Restricción: no confirmar pago ni generar pedido | Termina en la primera etapa del checkout; no abre "Forma de pago" |
| Resultado final: el flujo comercial básico funciona hasta Checkout | Paso 6: el checkout carga como invitado |
| Tags `@muebles_america @smoke` | Feature + escenario (markers ya registrados) |
| Asserts fuera de Page Objects | Solo en los steps de MA existentes |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 (34 recolectados, 13 descartados por marca) |
| `-m smoke --site muebles_america` | ✅ 5 (sin cambio de tamaño) |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base `CP_EC_MA_SMOKE_001` (escenario común) | ✅ (`price: 11189.00`, por departamento) | 33.5s |
| `CP_EC_MA_SMOKE_001`, antes de la corrección de la PDP, run 1 / 2 / 3 | ❌ `La PDP no muestra la etiqueta de disponibilidad` | 13.9s / 13.2s / 13.4s |
| `CP_EC_MA_CHECKOUT_001` / `CP_EC_MA_PDP_001`, antes de la corrección | ❌ mismo error (el ambiente cambió) | 12.8s / 14.5s |
| `CP_EC_MA_SMOKE_001`, versión final, run 1 / 2 / 3 | ✅ | 28.3s / 33.7s / 28.2s |
| `CP_EC_MA_PDP_001` / `CP_EC_MA_CART_001` / `CP_EC_MA_CHECKOUT_001` (comparten la PDP y los steps de MA) | ✅ | 10.9s / 18.4s / 28.9s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed | 91.0s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 4 passed | 141.8s |

Pruebas negativas:
- **en vivo (paso 2):** con `with_results.term: "zzqxnoexiste"` en `data/muebles_america/search.yaml`, el caso **falla** (`El listado no muestra ninguna card de producto`, 8.1s). El dataset se restauró en `try/finally` (hash idéntico; `data/` sin cambios en `git status`);
- **regla de disponibilidad (sin navegador):** la regex de `pdp_steps` acepta `Disponible`, `Solo queda 1` y `Solo quedan 24`, y rechaza `Agotado`, `Solo quedan` (sin número) y `Quedan 24`.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`b5ab5d2`):
- 0 conflictos de código; solo `plane_catalog.yaml`, que es generado;
- sin steps nuevos.

## Notas

- El smoke ahora busca el término del dataset (`search`/`with_results`) en
  lugar de navegar por el departamento "línea blanca" (`guest_checkout`),
  así que el producto puede cambiar respecto a la línea base.
- Los CAMBIOS anteriores de PDP_001 describen la etiqueta como "Solo queda
  N"; el texto actual en stage es "Solo quedan N" para N > 1.
- `CP_EC_MA_E2E_001` quedó en pausa (solo diagnóstico, sin cambios) para
  ejecutar este contrato antes.
