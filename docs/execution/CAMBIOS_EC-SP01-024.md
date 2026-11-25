# CAMBIOS EC-SP01-024 — E2E de venta de contado VIU

## Alcance

Mismo contrato comercial del E2E MA (EC-SP01-023) aplicado a VIU:
vertical completo Home → Search → PDP → Cart → Checkout → Customer →
Address → Shipping → Payment → Order del caso `CP_EC_VIU_E2E_001`
sobre `SaleCashWorkflow` con `confirm_order=True`.

La implementación VIU difiere internamente (mega-menu propio, toast
"Aceptar" + minicart desde header) pero satisface las mismas
garantías de negocio: integridad comercial, snapshot y folio.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/e2e/e2e.feature` | Then: `la integridad comercial del flujo es consistente de extremo a extremo` |
| `tests/bdd/steps/e2e_steps.py` | `order_ctx` expone `result` (SaleResult) + `request`; adjunto Allure "SaleResult snapshot"; Then de integridad |

## Validaciones obligatorias

SKU · cantidad · precio · subtotal · descuento · shipping · total ·
payment method · folio — mismas aserciones del contrato MA sobre el
`SaleResult`.

## Ejecución

```bash
pytest --case-id CP_EC_VIU_E2E_001   # crea orden real en stage VIU
```

## Validación en vivo — repetibilidad

| Run | Resultado | Folio |
|---|---|---|
| 1 | ✅ | **12000050189** |
| 2 | ✅ | **12000050192** |

Snapshot verificado: Estufa Whirlpool WER7600S, SKU WHIR00686, qty 1,
unit_price/subtotal/total $18,999.00, envío $0.00, `openpay_cards`.
