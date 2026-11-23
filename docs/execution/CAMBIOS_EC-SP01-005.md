# Cambios aplicados — EC-SP01-005

> Implementar modelos de dominio Ecommerce.
> Fecha: 2026-11-23 · Quinto hito del Sprint 01.

## Resumen

`domain/` ya existía con modelos mínimos; esta tarea los completó
hasta cubrir los "modelos mínimos" del contrato, añadió el modelo
`Shipping` faltante, endureció `Money` (normalización + regla
anti-float) y creó la cobertura unitaria obligatoria, que estaba
ausente.

## Cambios aplicados

### `domain/money/money.py`

- **Normalización monetaria**: todo importe se cuantiza a 2 decimales
  (`ROUND_HALF_UP`) en `__post_init__`.
- **Regla anti-float**: `Money(0.1)` → `BusinessError` explícito.
- **Comparaciones**: `<`, `<=`, `>`, `>=` con verificación de moneda
  (igual que `+`/`−`/`×` ya existentes).

### `domain/models/`

| Modelo | Cambio |
|---|---|
| `Product` | +`product_id`, `promotional_price`, `availability`; property `effective_price` |
| `CartItem` | +`unit_price` (snapshot opcional; default = `effective_price`), validación `quantity >= 1` → `PreconditionError` |
| `Cart` | +`discount`, `shipping`; `subtotal`, `shipping_cost` y `total` como properties (`total` era método) |
| `Customer` | `first_name` → `name` (campos del contrato) |
| `Address` | +`exterior_number`, `interior_number`, `neighborhood`, `references` (alineado a `addresses.yaml`) |
| `Shipping` | **modelo nuevo** (`method`, `cost: Money`) — faltaba del contrato |
| `Order` | +`subtotal`, `discount`, `shipping`, `payment_method` |

Sin dependencias a `pages` ni Playwright (verificado por grep y por
`tests/architecture`).

### Pruebas (14 nuevas)

| Archivo | Cobertura |
|---|---|
| `tests/unit/test_money.py` | aritmética, igualdad/orden, moneda distinta → `BusinessError`, float rechazado, cuantización |
| `tests/unit/test_domain_models.py` | `effective_price`, subtotal de `CartItem`, validación `quantity`, totales de `Cart` (subtotal−discount+shipping), `Order`; y **parametrizadas MA+VIU** que construyen `Customer`/`Address` desde los datasets reales vía `DataProvider` — evidencia del criterio "mismos tipos aunque el DOM difiera" |

### `README.md`

Nueva sección "Dominio" (modelos + regla de `Money`).

## Impacto en consumidores

Verificado antes de editar: `Customer`/`Cart.total()` no tenían
consumidores de código (solo datasets); el smoke test usa
`Money.amount`, que sigue siendo `Decimal`.

## Validación

| Comando | Resultado |
|---|---|
| `pytest tests/unit tests/architecture` | 57 passed |
| `ruff check .` | All checks passed |
| `python -m compileall .` | exit 0 |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage` (headless) | 1 passed en ~35s |
