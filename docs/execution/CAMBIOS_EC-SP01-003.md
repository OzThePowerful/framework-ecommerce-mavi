# Cambios aplicados — EC-SP01-003

> Implementar Browser Lifecycle y arquitectura de Fixtures.
> Fecha: 2026-12-08 · Tercer hito del Sprint 01.

## Resumen

El lifecycle Playwright/Pytest ya existía desde EC-SP01-001 con la
forma requerida por el contrato; esta tarea cerró los gaps detectados
en la auditoría:

1. **`expect_timeout` quedó efectivo**: existía en `ExecutionContext`
   pero nunca se aplicaba. Ahora la fixture `page` lo configura vía
   `expect.set_options`.
2. **Pruebas de lifecycle inexistentes**: el contrato exige
   `pytest tests/unit -k fixture` con pruebas propias. Se creó
   `tests/unit/test_browser_fixtures.py` con 6 pruebas offline
   (Chromium local headless, sin red externa).

## Estado verificado ya existente

- Los 5 plugins coinciden con el contrato: `browser_fixtures`,
  `execution_fixtures`, `data_fixtures`, `page_fixtures`,
  `evidence_fixtures`; `conftest.py` solo registra `pytest_plugins`.
- Cadena `Playwright → Browser → BrowserContext → Page → Test →
  Cleanup`: `playwright_instance`/`browser` en sesión, `context`/`page`
  por función, todas yield-fixtures con `close()` post-yield → el
  cleanup corre en PASS y en FAIL.
- `create_browser_context` aplica `navigation_timeout` y
  `action_timeout` desde el `ExecutionContext`.
- Headless/headed por `--exec-profile`; selección de navegador
  preparada: `launch_browser` resuelve `context.browser` con
  `getattr(playwright, ...)`, `ConfigError` si no es soportado.
- Sin lógica de ecommerce en browser fixtures; MA/VIU/MAVI comparten
  el mismo lifecycle.
- `PageFactory` inyecta `Page` a los Page Objects; los timeouts por
  defecto no se duplican en pages (los `timeout=` puntuales son esperas
  cortas de elementos opcionales/animados, no reconfiguración).

## Cambios aplicados

### `fixtures/browser_fixtures.py`

La fixture `page` ahora recibe `execution_context` y aplica el tercer
timeout del contexto:

```python
expect.set_options(timeout=execution_context.expect_timeout)
```

### `tests/unit/test_browser_fixtures.py` (nuevo, 6 pruebas)

| Prueba | Verifica |
|---|---|
| `test_fixture_browser_conectado` | Chromium headless local conectado |
| `test_fixture_context_aislado` | Contexto aislado dentro del browser |
| `test_fixture_page_funcional` | Page operativa sin red (`about:blank`) |
| `test_fixture_pages_factory_construye_page_objects` | Page Objects reciben Page vía factory |
| `test_fixture_navegador_no_soportado_falla_explicito` | Navegador inválido → `ConfigError` sin lanzar proceso |
| `test_fixture_lifecycle_cierra_recursos_ante_fallo` | Cleanup corre ante fallo; `browser.is_connected()` == False |

## Verificación del test adelantado

`tests/smoke/test_guest_checkout_ma.py` consume únicamente las
fixtures `pages`, `execution_context` y `data_provider`; no toca
Playwright ni configura timeouts. Cumple el contrato sin cambios.

## Validación

| Comando | Resultado |
|---|---|
| `pytest tests/unit -k fixture` | 6 passed (inicialización controlada de Chromium) |
| `pytest tests/unit tests/architecture` | 37 passed |
| `ruff check .` | All checks passed |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage --exec-profile headed` | 1 passed en ~44s |
