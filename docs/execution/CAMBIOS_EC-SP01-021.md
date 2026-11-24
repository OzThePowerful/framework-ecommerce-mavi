# CAMBIOS EC-SP01-021 — Smoke Suite Muebles América

## Alcance

Smoke rápido no transaccional que confirma el camino comercial crítico
de MA (Home → Search → PDP → Add to Cart → Cart → Start Checkout)
antes de ejecutar flujos más profundos. Caso: `CP_EC_MA_SMOKE_001`.

La travesía ya existía (`GuestCheckoutWorkflow`, BDD desde EC-SP01-019);
este contrato la formaliza como suite smoke ejecutable y trazable.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/smoke/sale_cash.feature` | Tag `@smoke` en el escenario `SMOKE_001` → selección por `-m smoke` |
| `tests/bdd/steps/sale_cash_steps.py` | `perf_counter` alrededor del workflow → adjunto Allure "Smoke timing" (`elapsed_s` + `price`) |
| `tests/smoke/test_guest_checkout_ma.py` | Import actualizado al path canónico `workflows.common` |

## Comandos

```bash
pytest -m smoke --site muebles_america        # suite smoke MA (3 items)
pytest --case-id CP_EC_MA_SMOKE_001           # el caso solo, sitio derivado
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Suite/marker Smoke | `@smoke` BDD + `pytest.mark.smoke` legacy; suite = 3 items |
| Solo MA | `--case-id CP_EC_MA_SMOKE_001` deriva `muebles_america` |
| Sin orden | El flujo se detiene en el gate de invitado + precio; nunca confirma |
| Independencia | Cada ejecución levanta browser/contexto nuevos (sin estado compartido) |
| Tiempos | Adjunto Allure "Smoke timing" + duration nativo del reporte |
| Allure | `attach_text` + `environment.properties` (RUN_ID/SITE/CASE_ID) |

## Validación — 3 ejecuciones consecutivas

| Run | Resultado | Duración |
|---|---|---|
| 1 | ✅ | 42.0s |
| 2 | ✅ | 35.7s |
| 3 | ✅ | 36.4s |

Adjuntos Allure verificados: `{"elapsed_s": 31.61, "price": "11189.00"}`.
