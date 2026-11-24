# CAMBIOS EC-SP01-020 — Ejecución selectiva por Case ID

## Alcance

`pytest --case-id CP_EC_<MA|VIU>_<MODULO>_<NNN>` ejecuta un único
Test Case con resolución completa: Case ID → ecommerce → feature →
scenario → ejecución.

## Piezas

| Pieza | Detalle |
|---|---|
| `core/execution/case_selector.py` | `parse_case_id` (formato + marca en `sites.yaml` + existencia en `plane_catalog.yaml`), `resolve_run_site` (deriva sitio; conflicto explícito → `ConfigError`), `catalog_case_ids`, `CaseSelection` |
| `fixtures/execution_fixtures.py` | `pytest_configure` resuelve el sitio efectivo una vez (`config._mavi_run_site`); errores → `UsageError` limpio. El hook de colección filtra al item del Case ID y reporta los deseleccionados vía `pytest_deselected`; 0 matches → `UsageError` |
| Allure | `CASE_ID=` en `environment.properties` (Run ID ya se propagaba vía `ExecutionContext.case_id`) |

## Comportamiento

```bash
pytest --case-id CP_EC_MA_CART_001    # sitio derivado: muebles_america
pytest --case-id CP_EC_VIU_HOME_001   # sitio derivado: viu
```

| Regla | Resultado |
|---|---|
| MA no ejecuta VIU (y viceversa) | El sitio derivado materializa solo IDs de esa marca — imposible por construcción |
| `--site`/`MAVI_ECOM_SITE` contradictorio | `ERROR: Conflicto …` (exit 4) |
| Case ID inexistente | `ERROR: Case ID inexistente en el catálogo …` + sugerencias (`difflib`) |
| Formato inválido | `ERROR: Case ID inválido …` con formato esperado |
| `--site` por defecto (no explícito) | No bloquea: `--case-id CP_EC_VIU_*` deriva `viu` aunque el default sea MA |

## Validación obligatoria del contrato

| Comando | Resultado |
|---|---|
| `--case-id CP_EC_MA_HOME_001` | ✅ 1 passed / 20 deselected |
| `--case-id CP_EC_VIU_HOME_001` | ✅ 1 passed / 20 deselected (SITE=viu en Allure) |
| `--case-id CP_EC_MA_CART_001` | ✅ 1 passed / 20 deselected |
| `--case-id CP_EC_VIU_CART_001` | ✅ 1 passed / 20 deselected |
| `--case-id CP_EC_MA_PDP_999` | ✅ ERROR explícito + sugerencias (exit 4) |
| `--case-id CP_EC_VIU_HOME_001 --site muebles_america` | ✅ ERROR Conflicto (exit 4) |

## Pruebas unitarias

`tests/unit/test_case_selector.py` — 17 casos: parse, formatos
inválidos, marca desconocida, inexistente, precedencia env/--site,
derivación con default no explícito, conflictos.
