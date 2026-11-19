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

| Regla | Control |
|---|---|
| `core` no importa `pages`/`workflows`/`tests` | `test_core_no_importa_capas_funcionales` |
| `data_providers` no importa `pages` | `test_data_providers_no_importan_pages` |
| `repositories` no importa `pages` | `test_repositories_no_importan_pages` |
| locators sin acciones ni lógica | `test_locators_no_contienen_acciones` |
| Page Objects sin asserts ni `expect` | `test_page_objects_sin_asserts` |
| workflows sin locators | `test_workflows_sin_locators` |
| steps BDD sin secuencias Playwright | `test_bdd_steps_sin_secuencias_playwright` |
| tests sin locators directos | `test_tests_sin_locators_directos` |
| prohibido `except Exception:`/`except:` tragado | `test_sin_except_exception_tragado` |
| prohibido `print()` (usar logging) | `test_sin_print_en_framework` |
| sin URLs literales en capas funcionales | `test_sin_urls_en_capas_funcionales` |
| `conftest.py` mínimo | `test_conftest_minimo` |

## Otras reglas

- Las URLs se resuelven únicamente en `core/config/` desde `config/sites.yaml`.
- La selección de sitio/ambiente pertenece al `ExecutionContext`.
- `DataProvider` (entrada) ≠ `Repository` (artefactos generados).
- Toda escritura generada: ruta anclada al proyecto + Run ID + escritura
  atómica.
- Plane/Bridge: el framework produce un resultado normalizado; nunca llama
  a Plane directamente.
