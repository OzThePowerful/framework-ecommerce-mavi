# Arquitectura del Framework Ecommerce MAVI

Mapa completo del repositorio: qué vive en cada directorio y qué reglas lo
gobiernan. Para las reglas verificables ver
[architecture/dependency_rules.md](../architecture/dependency_rules.md).

## Estructura por capas

```text
core/            → infraestructura técnica; nunca importa pages/workflows/tests
pages/           → Page Objects, componentes y locators (UI Automation)
domain/          → modelos y errores de negocio (sin Playwright)
workflows/       → coordinación entre pages; sin locators ni asserts
fixtures/        → fixtures de pytest (contexto, browser, pages, datos)
tests/           → unit, architecture, bdd/steps, smoke, integration, regression
test_cases/      → contrato funcional Gherkin (.feature) por módulo
data_providers/  → lectura de datasets YAML (data/<site>/, data/common/)
repositories/    → acceso a sistemas externos (no importan pages)
api/             → clientes/contratos/monitoring (uso futuro API-First)
config/          → sites.yaml, environments.yaml, execution_profiles.yaml
data/            → datasets por sitio (data/<site>/) + data/common/
scripts/         → tooling (p.ej. build_plane_catalog.py)
docs/            → architecture/, execution/ (CAMBIOS por contrato), standards/
artifacts/       → salida de corridas (allure-results, evidencias) — gitignored
```

## pages/ — la capa UI

```text
pages/base_page.py              → BasePage: open(), page, context
pages/common/components/        → componentes verificados idénticos en marcas
pages/common/pages/             → fachadas base (CommonXPage) — EC-SP01-025
pages/<sitio>/<modulo>/         → <modulo>_page.py (fachada) + <modulo>_locators.py
pages/<sitio>/components/       → componentes propios de la marca
```

Reglas:

- La variación de marca vive en **subclases**, nunca en `if site`.
- Los locators viven en `*_locators.py` (clases de constantes, sin acciones).
- Los Page Objects no contienen `assert` ni `expect` — devuelven estado.
- DOM duplicado (desktop/móvil): se discrimina con `:visible` + `.first`.
- Los sitios y URLs se resuelven desde `config/sites.yaml` vía
  `ExecutionContext` — prohibido hardcodear URLs.

## workflows/

Coordinan el recorrido funcional devolviendo modelos de dominio
(`workflows/common/` es multi-ecommerce; los alias en
`workflows/<sitio>/` existen por compatibilidad de imports).

## tests/ y test_cases/

```text
tests/bdd/test_features.py      → runner: materializa test_cases/common/ por --site
tests/bdd/steps/<modulo>_steps.py → steps delgados (delegan en pages/workflows)
test_cases/common/<modulo>/     → .feature compartido por todas las marcas
test_cases/<sitio>/             → .feature exclusivos de una marca (si aplica)
```

Cada escenario lleva tag `@<MODULO>_<NNN>`; el hook de colección lo
renombra a `CP_EC_<CODE>_<MODULO>_<NNN>` (MA/VIU según `sites.yaml`).
`@pending` marca casos trazables sin automatizar (skip, nunca PASS falso).

## Errores

Clasificados en `core/execution/execution_errors.py`: `FrameworkError`
(técnico), `NavigationError`, `ElementStateError`, `DataError`,
`PaymentError` y `domain/errors/` (p.ej. `PreconditionError` del negocio).
Prohibido `except Exception:` tragado — los arch tests lo vigilan.
