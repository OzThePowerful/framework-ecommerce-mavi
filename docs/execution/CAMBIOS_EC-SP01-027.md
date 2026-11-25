# EC-SP01-027 — Documentar estándar y operación del Framework

Documentación para que un desarrollador ajeno al Sprint 01 instale,
entienda y extienda el framework usando solo el repositorio.

## Piezas

| Documento | Cubre del contrato |
|---|---|
| `docs/standards/arquitectura.md` | Arquitectura: mapa de `core`, `pages` (components/pages), `domain`, `workflows`, `data_providers`, `repositories`, `fixtures`, `tests`, `test_cases` + reglas por capa |
| `docs/standards/guia_desarrollo.md` | Desarrollo: cómo crear Page Object, Locators, Component, Workflow, Domain Model, Dataset, Test Case, Feature, Step + **extensión** (agregar ecommerce nuevo en 8 pasos sin copiar el framework) |
| `docs/standards/guia_operacion.md` | Ejecución: por site, environment, Case ID, Smoke, E2E, Allure, evidencias y Quality Gate |
| `README.md` | Instalación: URL real del repo, venv, dependencias, Playwright, CLI de Allure + tabla de enlaces a la documentación |

## Revisión cruzada (criterios de aceptación)

Simulando un dev nuevo, cada criterio quedó verificado contra la doc:

| Criterio | Verificación |
|---|---|
| 1. Clonar | README § Instalación con URL real |
| 2. Instalar | Pasos venv + lock + playwright + allure |
| 3. Quality Gate | `guia_operacion.md` — comandos corridos: compileall/ruff/115 tests/collect ✅ |
| 4. `CP_EC_MA_HOME_001` | `--case-id CP_EC_MA_HOME_001 --collect-only` → 1/21 ✅ |
| 5. `CP_EC_VIU_HOME_001` | `-k CP_EC_VIU_HOME_001` → 1/21 ✅ |
| 6. Localizar Page Object | `arquitectura.md` mapa `pages/<sitio>/<modulo>/` |
| 7. Dónde crear un módulo | `guia_desarrollo.md` recetas + checklist ecommerce |

## Notas

- `docs/standards/` ya existía como directorio reservado; ahora aloja los
  documentos operativos.
- Se retiró el `PENDIENTE` de la URL del repo (quedó la real).
