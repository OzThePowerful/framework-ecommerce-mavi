# Cambios aplicados — EC-SP01-004

> Implementar DataProvider y datasets base de MA + VIU.
> Fecha: 2026-12-08 · Cuarto hito del Sprint 01.

## Resumen

La capa de datos (contrato, YAML, Excel, fixture, fallback, errores)
ya existía desde EC-SP01-001; esta tarea completó el activo que
faltaba: **los datasets base de Muebles América y VIU**, el contenido
de `data/common/` y la cobertura unitaria obligatoria.

## Estado verificado ya existente

- `BaseDataProvider` (ABC): `get_dataset(name)` / `get_record(dataset, key)`.
- `YamlDataProvider`: `data/<sitio>/<name>.yaml` con fallback a
  `data/common/<name>.yaml`; `DataError` explícito para dataset
  inexistente, registro ausente y YAML inválido.
- `ExcelDataProvider`: mismo contrato con `.xlsx` (openpyxl) —
  intercambiable sin tocar consumidores.
- Fixture `data_provider` por sitio (`fixtures/data_fixtures.py`).
- Ninguna capa funcional lee YAML directamente (verificado: cero
  `yaml.*`/`safe_load`/`openpyxl` en `pages/`, `workflows/`, `tests/`).
- `tests/smoke/test_guest_checkout_ma.py` consume el provider sin
  conocer rutas: `data_provider.get_record("guest_checkout", ...)`.

## Cambios aplicados

### Datasets nuevos (13 archivos)

| Ruta | Contenido |
|---|---|
| `data/muebles_america/{search,products,customers,addresses,checkout,payment}.yaml` | Términos de búsqueda, producto verificado en stage (Parrilla Whirlpool), cliente/dirección QA ficticios, parámetros de checkout con referencias cruzadas, métodos de pago `status: pending` |
| `data/viu/{search,products,customers,addresses,checkout,payment}.yaml` | Misma estructura; producto verificado en viustage.mavi.mx (Estufa Whirlpool WFR7050S), departamento "Línea Blanca" |
| `data/common/customers.yaml` | `default_guest` compartido; ejercita el fallback (lo usa `mavi` mientras no tenga datasets propios) |

Nomenclatura homogénea: mapa `clave_logica → campos`, claves iguales
entre sitios (`guest`, `guadalajara`, `with_results`, …). Solo datos
ficticios — sin secretos ni datos personales reales.

### Pruebas

| Archivo | Pruebas añadidas |
|---|---|
| `tests/unit/test_yaml_data_provider.py` | `test_sitio_valido_prioriza_su_dataset` (sitio gana a common), `test_sitio_inexistente_error_explicito` (DataError nombra el sitio), `test_registro_inexistente_error_explicito` |
| `tests/unit/test_datasets.py` (nuevo) | `test_datasets_base_presentes` (parametrizada MA+VIU: los 6 datasets existen, parsean y son mapas no vacíos), `test_fallback_common_resuelve_cliente` (mavi usa common/customers) |

Los tests de estructura validan vía DataProvider, no por rutas
físicas — consistente con el criterio de aceptación.

### `README.md`

Sección "Datos de prueba": tabla de datasets, nomenclatura de claves,
fallback a `common` e intercambiabilidad Excel.

## Verificación del test adelantado

`test_guest_checkout_ma.py` ya cumple: consume
`data_provider.get_record("guest_checkout", "linea_blanca_parrilla")`
sin conocer la ruta; el dataset `guest_checkout.yaml` se conserva
como dataset dedicado del flujo E2E.

## Validación

| Comando | Resultado |
|---|---|
| `pytest tests/unit tests/architecture` | 43 passed |
| `ruff check .` | All checks passed |
| `python -m compileall .` | exit 0 |
| `pytest tests/smoke/test_guest_checkout_ma.py --site muebles_america --target-env stage --exec-profile headed` | 1 passed en ~37s |
