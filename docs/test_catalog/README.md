# Catálogo de Test Cases — EC-SP01-018

**Plane es la fuente de verdad de los casos.** El framework **nunca llama
a Plane directamente**: produce un artefacto normalizado que el
Bridge/Plane consume.

| Pieza | Ruta |
|---|---|
| Generador | `scripts/build_plane_catalog.py` |
| Salida normalizada | `test_cases/plane_catalog.yaml` |
| Verificación | `tests/unit/test_plane_catalog.py` |

## Regenerar

```
python scripts/build_plane_catalog.py
```

## Convención

- **ID**: `CP_EC_<MA|VIU>_<MODULO>_<NNN>` — uno por caso por ecommerce.
- **Módulos**: Home, Search, PDP, Cart, Checkout, Customer, Address,
  Shipping, Payment, Order, Smoke, E2E.
- **Estados**: `Not Automated` → `In Development` → `Automated` (→ `Blocked`).
- **Campos mínimos por caso**: id, titulo, objetivo, prioridad, tipo,
  ecommerce, modulo, precondiciones, datos, pasos, resultado_esperado,
  postcondicion, automatizable, estado_automatizacion, implementacion, tags.
- Los casos en `Automated` referencian su feature/test de Pytest.

## Inventario actual (21 casos × 2 marcas = 42)

| Módulo | Casos | Estado |
|---|---|---|
| Smoke | SMOKE_001 | Automated |
| Home | HOME_001 | Automated |
| Search | SEARCH_001, SEARCH_002 | Automated |
| PDP | PDP_001, PDP_002 | Automated |
| Cart | CART_001, CART_002 | Automated |
| Checkout | CHECKOUT_001–003 | Automated |
| Customer | CUSTOMER_001 | Automated (vía CHECKOUT_002) |
| Address | ADDRESS_001 | Automated (vía CHECKOUT_002) |
| Shipping | SHIPPING_001 | Automated |
| Shipping | SHIPPING_002 (store picker) | In Development |
| Payment | PAY_001 | Automated |
| Payment | PAY_002 (>30k), PAY_003 (MSI) | Not Automated |
| Order | ORDER_001, ORDER_002 | Automated |
| E2E | E2E_001 | In Development |
| Smoke VIU | SMOKE_001 VIU | Not Automated (workflow solo MA) |
