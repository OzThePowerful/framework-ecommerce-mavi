# CAMBIOS EC-SP01-022 — Smoke Suite VIU

## Alcance

Smoke rápido no transaccional que confirma el camino comercial crítico
de VIU (Home → departamento → PDP → Add to Cart → Cart → Start
Checkout) antes de ejecutar pruebas posteriores. Caso:
`CP_EC_VIU_SMOKE_001`.

Mismos criterios del Smoke MA (EC-SP01-021) aplicados a VIU: la
travesía comparte el `GuestCheckoutWorkflow` y el feature BDD
`test_cases/common/smoke/sale_cash.feature`, que materializa
`CP_EC_VIU_SMOKE_001` con `--site viu` o `--case-id`.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/smoke/sale_cash.feature` | Tag `@smoke` en el escenario `SMOKE_001` → selección por `-m smoke` |
| `tests/bdd/steps/sale_cash_steps.py` | `perf_counter` alrededor del workflow → adjunto Allure "Smoke timing" (`elapsed_s` + `price`) |
| `tests/smoke/test_guest_checkout_viu.py` | Smoke pytest VIU (paridad con el de MA; import canónico `workflows.common`) |
| `README.md` | Comandos de la suite smoke VIU |

## Comandos

```bash
pytest -m smoke --site viu               # suite smoke VIU (4 items)
pytest --case-id CP_EC_VIU_SMOKE_001     # el caso solo, sitio derivado
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Suite/marker Smoke | `@smoke` BDD + `pytest.mark.smoke` en el pytest VIU |
| Solo VIU | `--case-id CP_EC_VIU_SMOKE_001` deriva `viu` |
| Sin orden | El flujo se detiene en el gate de invitado + precio; nunca confirma |
| Independencia | Cada ejecución levanta browser/contexto nuevos |
| Tiempos | Adjunto Allure "Smoke timing" + duration nativo |
| Allure | `attach_text` + `environment.properties` (RUN_ID/SITE/CASE_ID) |

## Validación — 3 ejecuciones consecutivas

| Run | Resultado | Duración |
|---|---|---|
| 1 | ✅ | 52.4s |
| 2 | ✅ | 53.5s |
| 3 | ✅ | 52.3s |

Adicional: `tests/smoke/test_guest_checkout_viu.py --site viu` ✅ 56.6s.
