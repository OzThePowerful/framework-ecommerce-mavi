# Cambios aplicados — EC-SP01-002

> Implementar configuración multi-ecommerce y ExecutionContext.
> Fecha: 2026-12-08 · Segundo hito del Sprint 01.

## Resumen

La configuración multi-ecommerce ya existía desde EC-SP01-001; esta
tarea cerró los gaps detectados en la auditoría contra el contrato:

1. **`environments.yaml` pasó de configuración muerta a catálogo
   efectivo**: `load_environments()` existía pero nunca se llamaba.
   Ahora `resolve_site()` valida el ambiente en dos niveles.
2. **La construcción del `ExecutionContext` dejó de vivir solo en la
   fixture**: se extrajo a `ExecutionContext.build()` (classmethod),
   punto único de construcción reutilizable por pytest y por futuros
   consumidores (MAVI AI Bridge, CLI).
3. **Cobertura unitaria ampliada**: perfiles, environments.yaml y la
   construcción del contexto ahora tienen pruebas de configuración
   válida e inválida.

## Cambios aplicados

### `core/config/site_config.py`

`resolve_site()` ahora valida el ambiente en **dos niveles**:

| Nivel | Origen | Fallo |
|---|---|---|
| 1. Ambiente declarado | `config/environments.yaml` (catálogo de ambientes válidos) | `UnknownEnvironmentError` — "no declarado en environments.yaml" |
| 2. Ambiente disponible | `config/sites.yaml` → `sites.<sitio>.environments` | `UnknownEnvironmentError` — "no existe para el sitio" |

Se añadió el parámetro opcional `environments` (inyectable para
pruebas), igual que `sites`.

### `core/execution/execution_context.py`

Nuevo `ExecutionContext.build(site, environment, profile_name,
case_id, run_id)` que encapsula la resolución completa:
`load_execution_profile()` + `resolve_site()` → instancia inmutable.
Misma lógica que antes vivía en la fixture; sin duplicación.

### `fixtures/execution_fixtures.py`

La fixture `execution_context` ahora solo resuelve los overrides
`MAVI_ECOM_*` / opciones CLI y delega en `ExecutionContext.build()`.
Se eliminaron los imports ya no usados (`load_execution_profile`).

### `tests/unit/` — cobertura nueva

| Archivo | Pruebas |
|---|---|
| `test_config_loader.py` (nuevo) | perfil default resuelve, perfil desconocido → `UnknownProfileError`, environments.yaml declara stage/prod, sites.yaml declara los 3 ecommerce |
| `test_execution_context.py` (nuevo) | `build()` completo (project, site_code, URLs, browser, case_id, run_id, timeouts), sitio inválido, ambiente inválido, perfil inválido |
| `test_site_config.py` (extendido) | ambiente presente en sites.yaml pero ausente del catálogo → error explícito; ambiente declarado pero no disponible para el sitio → error explícito |

### `README.md`

Se documentó la validación de ambientes en dos niveles y el rol de
cada archivo de `config/`.

## Verificación del test adelantado

`tests/smoke/test_guest_checkout_ma.py` cumple las reglas del
contrato, sin cambios necesarios:

- Sin URLs ni resolución de sitio/ambiente (delega en `ExecutionContext`
  recibido por fixture).
- Sin locators (el test orquesta `GuestCheckoutWorkflow` + datos del
  `DataProvider`).
- La validación funcional (`price.amount > 0`) permanece en el test.
- El workflow recibe el contexto; no implementa selección de ecommerce.

## Validación

| Comando | Resultado |
|---|---|
| `python -m compileall .` | exit 0 |
| `ruff check .` | All checks passed |
| `pytest tests/unit tests/architecture` | 31 passed |
| `pytest --site muebles_america --target-env stage --collect-only` | 32 collected |
| `pytest --site viu --target-env stage --collect-only` | 32 collected |
| `pytest --site mavi --target-env stage --collect-only` | 32 collected |
| `pytest --site nope --target-env stage --collect-only` | `UnknownSiteError` explícito en arranque |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage --exec-profile headed` | 1 passed en ~38s (E2E real contra stage) |
