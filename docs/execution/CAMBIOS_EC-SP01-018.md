# CAMBIOS EC-SP01-018 — Catálogo de Test Cases en formato Plane

## Alcance

Generar el catálogo inicial de Test Cases del flujo de venta de contado
en un formato normalizado e importable a Plane. Plane es la fuente de
verdad; el framework produce el artefacto, no llama a Plane.

## Piezas nuevas

| Pieza | Detalle |
|---|---|
| `scripts/build_plane_catalog.py` | Define cada caso una vez y lo materializa por marca (MA + VIU). Salida YAML normalizada. |
| `test_cases/plane_catalog.yaml` | 42 casos (21 × 2 marcas), generado — no editar a mano. |
| `tests/unit/test_plane_catalog.py` | Verifica criterios de aceptación: IDs únicos, convención `CP_EC_<MA\|VIU>_<MODULO>_<NNN>`, campos mínimos, estados válidos, casos Automated con implementación referenciada. |
| `docs/test_catalog/README.md` | Convención, módulos, inventario y cómo regenerar. |

## Inventario

42 casos en 12 módulos: 33 Automated, 4 In Development
(SHIPPING_002 ×2, E2E_001 ×2), 5 Not Automated
(PAY_002, PAY_003 ×2, SMOKE_001 VIU).

Criterios cubiertos por `test_plane_catalog.py`: IDs únicos y con la
convención; campos completos (título, objetivo, prioridad, tipo,
precondiciones, datos, pasos, resultado esperado, postcondición);
estado de automatización dentro del catálogo válido; casos en estado
`Automated` con implementación trazable a feature/test.

## Cómo regenerar / mantener

```
python scripts/build_plane_catalog.py   # reescribe plane_catalog.yaml
python -m pytest tests/unit/test_plane_catalog.py
```

Al agregar un escenario nuevo al framework: sumar su entrada al arreglo
`CASES` del generador, regenerar y correr el test.

## Validación

| Prueba | Resultado |
|---|---|
| `tests/unit/test_plane_catalog.py` | ✅ 8 passed |
| Unitarios + architecture | ✅ 70 passed |
| `pytest --collect-only` | ✅ 92 collected |
| Ruff | ✅ limpio |
