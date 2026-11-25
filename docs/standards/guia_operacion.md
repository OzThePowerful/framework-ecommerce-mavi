# Guía de operación — ejecutar el framework

Runbook consolidado de ejecución. Requisitos previos: instalación del
README completada y `.env` configurado.

## Selección de sitio y ambiente

```bash
pytest --site muebles_america --target-env stage   # defaults
pytest --site viu --target-env stage
pytest --site viu --target-env prod
```

Equivalente por variables: `MAVI_ECOM_SITE`, `MAVI_ECOM_ENV`,
`MAVI_ECOM_CASE_ID`. Sitios y ambientes válidos: `config/sites.yaml`.

Perfiles de browser (`config/execution_profiles.yaml`):

```bash
pytest --exec-profile headed   # navegador visible
pytest --exec-profile ci       # timeouts ampliados para CI
```

## Ejecución por Case ID

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_HOME_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_CART_001
```

- El **sitio se deriva de la marca del ID** (`MA` → muebles_america,
  `VIU` → viu): ejecución cruzada imposible.
- Formato: `CP_EC_<MARCA>_<MODULO>_<NNN>`; IDs válidos en
  `test_cases/plane_catalog.yaml`.
- `--site` explícito contradictorio → error claro.
- Equivalente con `-k`: `pytest --site viu -k CP_EC_VIU_HOME_001`.

## Suites

```bash
# Smoke suite (marker)
pytest -m smoke

# Smoke BDD por marca
pytest tests/bdd/test_features.py --case-id CP_EC_MA_SMOKE_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_SMOKE_001

# E2E con orden real (confirma compra — solo bajo autorización)
pytest tests/bdd/test_features.py --case-id CP_EC_MA_E2E_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_E2E_001

# Suite BDD completa de una marca sin órdenes
pytest tests/bdd/test_features.py --site viu -k "not E2E"
```

`@pending` = skipped trazable (automatización pendiente, nunca PASS falso).

## Allure

Los resultados se escriben a `artifacts/allure-results/` en cada corrida
(`--alluredir` ya va en `pytest.ini`):

```bash
allure serve artifacts/allure-results          # reporte interactivo
allure generate artifacts/allure-results -o artifacts/allure-report --clean
```

Adjuntos clave: `environment.properties` (SITE/ENV/CASE_ID), snapshots de
modelos (`Cart`, `SaleResult`) y tiempos (`Smoke timing`).

## Evidencias

En fallo: `artifacts/runs/<run_id>/<case_id>/` con screenshot
`failure.png`, `logs/current_url.txt` y `exception.txt`.

## Quality Gate

Batería que debe estar verde antes de cada commit:

```bash
python -m compileall -q .
ruff check .
pytest tests/unit tests/architecture -q
pytest tests/bdd/test_features.py --site muebles_america --collect-only -q
pytest tests/bdd/test_features.py --site viu --collect-only -q
```

Y para cambios en capas UI: Smoke MA + Smoke VIU en vivo.
