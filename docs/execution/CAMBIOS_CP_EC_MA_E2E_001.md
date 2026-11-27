# CAMBIOS CP_EC_MA_E2E_001 — Validar flujo completo de venta de contado

## Alcance

Alinear `CP_EC_MA_E2E_001` con el contrato
`Context_Contratos/MA/CP_EC_MA_E2E_001.md`, **solo para Muebles América**
(mecanismo de [MA-AISLAMIENTO-001](CAMBIOS_MA-AISLAMIENTO-001.md)):
- el flujo Home → Search → PDP → Cart → Checkout → Customer → Address → Shipping → Payment → Order, con verificación y **evidencia por etapa**;
- después, las **9 validaciones obligatorias** intercaladas 1:1 con la tabla del contrato;
- al final, un resumen de la evidencia.

El escenario de MA **no usa `SaleCashWorkflow`**: encadena los steps de MA
de cada módulo, que ya están verificados por sus propios contratos.

> ⚠️ **El caso crea una orden REAL en stage MA** cada vez que se ejecuta
> (ejecución autorizada en stage). Ver [Comandos](#comandos) para excluirlo.

Decisiones al autorizar:
- **Producto:** la primera card elegible de la búsqueda del dataset (hoy `MABE00902`), igual que el resto de MA. Se evaluó `WHIR00789` (`products.yaml`): aparece en la búsqueda "parrilla", pero su card no muestra precio en el listado (la regla de card elegible lo salta); en la PDP es comprable a $11,189.00 con "Solo quedan 12";
- **Evidencia:** screenshot en las 10 etapas; en el checkout se **enmascaran** los inputs y selects (identidad real del comprador, domicilio y tarjeta).

| Elemento | Antes (escenario común, `SaleCashWorkflow`) | Ahora (escenario MA) |
|---|---|---|
| Flujo por etapas | 2 steps opacos ("prepara" y "ejecuta el flujo completo"); ninguna etapa se verificaba en Gherkin | 10 etapas, cada una con acción, verificación (steps de HOME, SEARCH, PDP, CART, CHECKOUT_001/003, PAY_001 y ORDER_001/002 de MA) y evidencia |
| Producto | SKU carrito = PDP | SKU orden = PDP = carrito = checkout; nombre orden = PDP (y card → PDP en la etapa PDP) |
| Cantidad | Solo ≥ 1 | Orden = PDP = carrito = checkout |
| Precio | Carrito = PDP | PDP = carrito = ítem del checkout = orden |
| Subtotal (matemáticamente correcto) | Resumen = carrito | En cada etapa, subtotal = precio × cantidad (carrito observado, resumen del checkout y orden), y los tres coinciden |
| Descuento | Solo en la fórmula del total | Cupón de la orden ⇔ descuento del carrito; descuento de producto de la orden = PDP |
| Shipping | Resumen = Shipping | Costo de la etapa de entrega = resumen = orden |
| Total | Resumen = fórmula | Orden = checkout = subtotal − descuento + envío |
| Forma de pago | `result.payment_method == request.payment_method`: **comparaba el valor consigo mismo** | `tipo_pago` de la orden = `payment.card.sale_type` ("contado") y método = `openpay_cards` |
| Folio | Numérico | Numérico, presente en la confirmación y = `transaction_id` de la orden final |
| Evidencia suficiente | Un adjunto "SaleResult snapshot"; screenshots solo si fallaba | 10 screenshots (`artifacts/runs/<run>/CP_EC_MA_E2E_001/screenshots/NN_<etapa>.png`, adjuntos en Allure) + `logs/e2e_resumen.txt` y adjunto "Evidencia E2E" con etapas, producto, importes, tipo de pago y folio |
| Tags | `@E2E_001` | `@muebles_america` (Feature) + `@E2E_001 @e2e @cash_sale @critical` |

**`CP_EC_VIU_E2E_001` no cambia:** sigue corriendo el escenario común con
`SaleCashWorkflow`, que `origin/viu` cambió en su rama (`b5ab5d2`).

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/muebles_america/e2e/e2e.feature` (nuevo) | `@muebles_america` + `@E2E_001 @e2e @cash_sale @critical`: 10 etapas con evidencia + 9 validaciones + cierre (111 steps) |
| `tests/bdd/steps/muebles_america/e2e_steps.py` (nuevo) | `queda la evidencia de la etapa "<Etapa>"` (screenshot enmascarado si la página es el checkout), validaciones de precio, subtotal y shipping en todo el flujo, y el cierre "la venta de contado queda evidenciada de extremo a extremo" (exige las 10 etapas en orden con su captura en disco y el folio). Fixture `e2e_evidence` |
| `tests/bdd/test_features.py` | Importa los steps de E2E de MA |
| `core/evidence/evidence_manager.py` | `save_screenshot(page, name, mask=None)`: el `mask` opcional usa el `mask` nativo de Playwright. **Sin `mask` el comportamiento es idéntico** (hook de fallo y VIU no cambian) |
| `pages/muebles_america/checkout/checkout_locators.py` + `checkout_page.py` | `EVIDENCE_MASK = "input:visible, select:visible"` y `evidence_mask()` |
| `pytest.ini` | Markers `e2e` y `critical`; la descripción de `cash_sale` advierte que incluye E2E_001 |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Bloque `muebles_america` en E2E_001 con el contrato. Solo cambia `CP_EC_MA_E2E_001`; el resto es renumeración de alias YAML |

Se reutilizan de ORDER_002 de MA las validaciones de producto, cantidad,
descuento, total, forma de pago y folio, sin modificarlas.

**No se tocan:**
- `test_cases/common/e2e/e2e.feature`, `tests/bdd/steps/e2e_steps.py` ni `SaleCashWorkflow`;
- los steps de HOME, SEARCH, PDP, CART, CHECKOUT, PAY y ORDER de MA (solo se reusan);
- ningún dataset ni nada de VIU.

Los 9 textos nuevos no existen en esta rama ni en `origin/viu`.

## Comandos

```bash
# Crea una orden REAL en stage (requiere MAVI_GUEST_MA_* en .env)
pytest tests/bdd/test_features.py --case-id CP_EC_MA_E2E_001
pytest -m "e2e or critical" --site muebles_america

# -m cash_sale ahora tiene PAY_001 (sin orden), ORDER_001 y E2E_001 (con orden)
pytest -m "cash_sale and not order and not e2e" --site muebles_america   # solo sin orden

# Regresión de MA sin órdenes
pytest tests/bdd/test_features.py --site muebles_america -k "not ORDER and not E2E"
```

Evidencia de una corrida: `artifacts/runs/<run_id>/CP_EC_MA_E2E_001/`
(`screenshots/01_home.png` … `10_order.png`, `logs/e2e_resumen.txt`) y los
adjuntos "Etapa <X>" y "Evidencia E2E" en Allure.

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Precondiciones: módulos operativos, producto elegible, dataset de cliente y dirección, contado definido, ambiente habilitado | Cada etapa verifica su módulo; card elegible de `search`; `.env` + `addresses`; `payment`/`card`; stage |
| Flujo Home → … → Order | 10 etapas en el orden del contrato; el cierre exige exactamente esas etapas, en ese orden |
| 9 validaciones obligatorias | Una pareja *When/Then* por elemento de la tabla |
| Resultado final: orden válida + evidencia suficiente | Folio validado contra la orden final + 10 capturas + resumen de evidencia |
| Tags `@muebles_america @e2e @cash_sale @critical` | Feature + escenario; markers registrados |
| Asserts fuera de Page Objects | Solo en steps; `evidence_mask()` y `save_screenshot` no tienen asserts |

## Validación

Quality Gate:

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 120 passed (incluye los 4 de evidencia) |
| `--collect-only` MA / VIU | ✅ 21 / 21 (35 recolectados, 14 descartados por marca) |
| `-m "e2e or critical or cash_sale"` (MA) | ✅ 3 (`PAY_001`, `ORDER_001`, `E2E_001`) |

En vivo (stage, con `.env` local):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base `CP_EC_MA_E2E_001` (escenario común) | ❌ **sin orden**: `SaleCashWorkflow` lee el precio de la primera card y "parrilla" tiene cards sin precio (`Locator.inner_text: Timeout` en `[class*='default-price'] .price`). Es una falla previa del escenario común; VIU la corrigió en su rama | 20.9s |
| `CP_EC_MA_E2E_001`, run 1 / 2 / 3 | ✅ órdenes 2000059239 / 2000059242 / 2000059245 | 82.8s / 76.2s / 88.9s |
| `CP_EC_MA_CHECKOUT_003` / `CP_EC_MA_PAY_001` (comparten página de checkout y steps) | ✅ | 30.1s / 38.6s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed (sin cambio de tamaño) | 87.9s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 4 passed | 135.0s |

Órdenes de prueba creadas en stage MA (todas `MABE00902`, $6,119.00,
`openpay_cards`, envío gratis): `2000059239`, `2000059242`, `2000059245`.

Evidencia revisada (run 1): las capturas de Checkout, Customer, Address,
Shipping y Payment tapan todos los inputs y selects; se siguen viendo el
producto, el resumen y el estado de cada etapa. Home, Search, PDP, Cart y
Order van sin máscara (no muestran datos del comprador).

Pruebas negativas (sin navegador, **sin crear órdenes**): se llama a cada
step nuevo con datos consistentes (pasa) e inconsistentes (falla):
- precio: `El precio no es consistente en el flujo: {… 'orden': '5999.00'}`;
- subtotal: `Subtotal ≠ precio × cantidad en: {'checkout': {'observado': '6200.00', 'precio_x_cantidad': '6119.00'}}`;
- envío: `El envío no es consistente en el flujo: {… 'orden': '199.00'}`;
- evidencia: `Etapas evidenciadas [… 'Payment'] != flujo del contrato [… 'Payment', 'Order']`.

Simulación de merge (`git merge-tree` del working tree contra `origin/viu`
`b5ab5d2`):
- 0 conflictos de código; solo `plane_catalog.yaml`, que es generado;
- 0 steps duplicados.

## Notas

- Shipping, descuento y total solo se han visto con envío gratis y sin
  promoción (`MABE00902`). Las reglas no cambian con otros valores, pero
  no se han observado en vivo.
- `-m cash_sale`, `-m e2e` y `-m critical` incluyen casos que crean
  órdenes; usar los filtros de [Comandos](#comandos) para regresiones.
- El escenario común de E2E falla hoy en MA por las cards sin precio; ya no
  aplica a MA porque el escenario de MA lo reemplaza. VIU lo corrigió en
  su workflow (`origin/viu`).
- El documento de operación (`guia_operacion.md`) sigue sin excluir ORDER
  en su comando "sin órdenes" (pendiente de ORDER_001).
