# CAMBIOS EC-SP01-023 — E2E de venta de contado Muebles América

## Alcance

Validación del vertical completo MA (Home → Search → PDP → Cart →
Checkout → Customer → Address → Shipping → Payment → Order) del caso
`CP_EC_MA_E2E_001` sobre `SaleCashWorkflow` con `confirm_order=True`.

La ejecución ya existía desde EC-SP01-019/020; este contrato agrega la
validación de integridad comercial obligatoria y el snapshot completo
de modelos como evidencia.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/e2e/e2e.feature` | Nuevo Then: `la integridad comercial del flujo es consistente de extremo a extremo` |
| `tests/bdd/steps/e2e_steps.py` | `order_ctx` expone `result` (SaleResult) + `request`; adjunto Allure "SaleResult snapshot" con los 10 campos; Then de integridad |

## Validaciones obligatorias (contrato)

| Campo | Aserción |
|---|---|
| producto / SKU | `cart.items[0].product.sku == result.product.sku` |
| cantidad | `item.quantity >= 1` |
| precio | `item.effective_unit_price == product.effective_price` |
| subtotal | `summary["subtotal"] == cart.subtotal` |
| descuento | `cart.discount` entra en el total esperado |
| shipping | `summary["shipping"] == shipping.cost` |
| total | `summary["total"] == subtotal - descuento + envío` |
| payment method | `result.payment_method == request.payment_method` |
| folio | `order.folio` numérico + mensaje de confirmación |

## Ejecución

```bash
pytest --case-id CP_EC_MA_E2E_001   # crea orden real en stage
```

## Validación en vivo — repetibilidad

| Run | Resultado | Folio |
|---|---|---|
| 1 | ✅ | **2000058510** |
| 2 | ✅ | **2000058513** |

Snapshot verificado: Parrilla Mabe PM75KR0, SKU MABE00902, qty 1,
unit_price/subtotal/total $6,119.00, envío $0.00, `openpay_cards`.
