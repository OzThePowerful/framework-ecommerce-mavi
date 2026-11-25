# EC-SP01-026 — Hardening técnico y estabilización

Auditoría de deuda técnica sobre la lista del contrato, corrección de
hallazgos y justificación de excepciones inevitables.

## Auditoría

| Señal | Resultado |
|---|---|
| `wait_for_timeout` | 7 usos — todos son **polling acotado con verificación** (lazy-load de PLP, re-render KO en blur, estabilización del store picker y del mega-menú). No hay sleeps perezosos; se documenta la intención donde faltaba. |
| `force=True` | 1 uso en `select_method` — el input real queda oculto tras el label KO; justificado con comentario (`wait_method_selectable` ya garantiza `enabled`). |
| `.first()` / `.nth()` | ~92 — patrón deliberado: los sitios duplican DOM (desktop/móvil); `:visible` + `.first` discrimina la copia activa. |
| XPath | Ninguno en el framework (solo `Example_Valentin/`, gitignored). |
| `except Exception` | 1 real en `SaleCashWorkflow._stage` — boundary que anota, loggea y **re-lanza** (legítimo); 1 en test corregido a `pytest.raises(DataError)`. |
| `print()` | Ninguno en framework (arch test lo vigila). |
| Asserts en Pages/Workflows | Ninguno (arch test lo vigila). |
| URLs/datos hardcodeados, rutas absolutas | Ninguno (todo vía `sites.yaml`/datasets). |
| TODO/código comentado | Ninguno. |
| Scripts temporales | Ninguno (raíz limpia; `Example_Valentin/` es referencia local gitignored). |
| Duplicación | Resuelta en EC-SP01-025 (`pages/common/pages/`). |

## Correcciones aplicadas

| Hallazgo | Fix |
|---|---|
| `is_add_to_cart_enabled` tronaba con `TimeoutError` cuando el CTA no existe (producto agotado) | Sondeo `is_*` ahora devuelve `False` tras gracia de 5s — el caller distingue "no comprable" (`PreconditionError`) de "no habilitado" |
| `except Exception` en `test_datasets` | Acotado a `pytest.raises(DataError)` |
| `force=True` y polls `wait_for_timeout` sin contexto | Comentarios justificativos (KO oculta el input; repintado asíncrono sin evento determinista) |
| Producto E2E VIU agotado (WER7600S → "Agotado") | `search_term` movido al dataset `checkout.guest` por marca: VIU `MIDE00067` (Estufa Midea $6,699), MA `estufa`; `e2e_steps` ya no depende del dataset `search` |

## Validación obligatoria

| Paso | Resultado |
|---|---|
| `compileall` / `ruff` / architecture / unit / collect-only | ✅ (115 tests, 139 collected) |
| Smoke MA + Smoke VIU | ✅ 43.8s / 54.4s |
| E2E disponibles | ✅ MA folio **2000058624** · VIU folio **12000050276** |

No existen workarounds silenciosos utilizados únicamente para conseguir PASS.
