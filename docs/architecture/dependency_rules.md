# Reglas de dependencia — Framework Ecommerce MAVI

## Capas

```text
Core                → infraestructura técnica (config, browser, contexto,
                      evidencias, Allure, logging, errores técnicos)
   ↓
UI Automation       → pages/, componentes UI, locators
   ↓
Business Workflows  → workflows/ (coordinación entre pages; sin locators)
   ↓
Test Execution      → tests/, fixtures/, steps BDD (validaciones)
```

Integraciones y datos desacoplados: `data_providers/`, `repositories/`,
`api/`, `knowledge/`, `domain/`.

## Reglas verificables (tests/architecture/)

Controles agrupados por política (EC-SP01-007); implementación AST en
`tests/architecture/rules.py`.

### `test_layer_boundaries.py`

| Regla | Control |
|---|---|
| `core` no importa `pages`/`workflows`/`tests` | `test_core_no_importa_capas_funcionales` |
| `repositories` no importa `pages` | `test_repositories_no_importan_pages` |
| sin dependencias circulares entre módulos | `test_sin_dependencias_circulares` |
| `conftest.py` mínimo | `test_conftest_minimo` |

### `test_page_object_policy.py`

| Regla | Control |
|---|---|
| Page Objects sin asserts ni `expect` | `test_page_objects_sin_asserts` |

### `test_locator_policy.py`

| Regla | Control |
|---|---|
| locators sin acciones ni lógica | `test_locators_no_contienen_acciones` |
| tests sin locators directos | `test_tests_sin_locators_directos` |
| steps BDD sin secuencias Playwright | `test_bdd_steps_sin_secuencias_playwright` |

### `test_workflow_policy.py`

| Regla | Control |
|---|---|
| workflows sin locators | `test_workflows_sin_locators` |
| workflows sin asserts ni `expect` | `test_workflows_sin_asserts` |

### `test_data_policy.py`

| Regla | Control |
|---|---|
| `data_providers` no importa `pages` | `test_data_providers_no_importan_pages` |
| sin URLs literales en capas funcionales | `test_sin_urls_en_capas_funcionales` |

### `test_exception_policy.py`

| Regla | Control |
|---|---|
| prohibido `except Exception:`/`except:` tragado | `test_sin_except_exception_tragado` |
| prohibido `print()` (usar logging) | `test_sin_print_en_framework` |

### `test_gate_selfcheck.py`

Pruebas negativas del propio gate: cada detector se alimenta con
código sintético violador (debe marcar) y limpio (debe pasar), para
garantizar que una regla realmente protege.

## Otras reglas

- Las URLs se resuelven únicamente en `core/config/` desde `config/sites.yaml`.
- La selección de sitio/ambiente pertenece al `ExecutionContext`.
- `DataProvider` (entrada) ≠ `Repository` (artefactos generados).
- Toda escritura generada: ruta anclada al proyecto + Run ID + escritura
  atómica.
- Plane/Bridge: el framework produce un resultado normalizado; nunca llama
  a Plane directamente.
