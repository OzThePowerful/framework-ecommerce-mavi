"""Validación del catálogo de Test Cases para Plane (EC-SP01-018).

Criterios del contrato verificados como tests:
- Todos los IDs son únicos.
- Cada ID sigue la convención CP_EC_<MA|VIU>_<MODULO>_<NNN>.
- No existen casos genéricos: el ecommerce siempre se determina.
- MA y VIU tienen sus propios Case IDs.
- Cada caso contiene los campos mínimos requeridos.
- Estados de automatización válidos; Automated → implementación ligada.
"""

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

CATALOG = (
    Path(__file__).resolve().parents[2]
    / "test_cases"
    / "plane_catalog.yaml"
)

ID_RE = re.compile(r"^CP_EC_(MA|VIU)_[A-Z0-9]+_\d{3}$")
VALID_STATES = {"Not Automated", "In Development", "Automated", "Blocked"}
REQUIRED_FIELDS = {
    "id",
    "titulo",
    "objetivo",
    "prioridad",
    "tipo",
    "ecommerce",
    "modulo",
    "precondiciones",
    "datos",
    "pasos",
    "resultado_esperado",
    "postcondicion",
    "automatizable",
    "estado_automatizacion",
    "tags",
}
VALID_SITES = {"muebles_america", "viu"}
EXPECTED_MODULES = {
    "Home",
    "Search",
    "PDP",
    "Cart",
    "Checkout",
    "Customer",
    "Address",
    "Shipping",
    "Payment",
    "Order",
    "Smoke",
    "E2E",
}


@pytest.fixture(scope="module")
def catalog() -> dict:
    assert CATALOG.exists(), (
        "Falta test_cases/plane_catalog.yaml; "
        "ejecutar scripts/build_plane_catalog.py"
    )
    return yaml.safe_load(CATALOG.read_text(encoding="utf-8"))


def test_ids_unicos(catalog):
    ids = [c["id"] for c in catalog["casos"]]
    assert len(ids) == len(set(ids)), (
        f"IDs duplicados: {[i for i in ids if ids.count(i) > 1]}"
    )


def test_convencion_id(catalog):
    for case in catalog["casos"]:
        assert ID_RE.match(case["id"]), (
            f"ID fuera de convención: {case['id']}"
        )


def test_sin_casos_genericos(catalog):
    for case in catalog["casos"]:
        assert case["ecommerce_key"] in VALID_SITES, (
            f"Caso sin ecommerce determinable: {case['id']}"
        )
        site_id = {"muebles_america": "MA", "viu": "VIU"}[
            case["ecommerce_key"]
        ]
        assert case["id"].startswith(f"CP_EC_{site_id}_"), (
            f"ID {case['id']} no corresponde a {site_id}"
        )


def test_ambas_marcas_tienen_ids_propios(catalog):
    por_marca = {
        site: {c["id"] for c in catalog["casos"] if c["ecommerce_key"] == site}
        for site in VALID_SITES
    }
    assert por_marca["muebles_america"] != por_marca["viu"]
    assert all(id_.startswith("CP_EC_MA_") for id_ in por_marca["muebles_america"])
    assert all(id_.startswith("CP_EC_VIU_") for id_ in por_marca["viu"])


def test_campos_minimos_presentes(catalog):
    for case in catalog["casos"]:
        missing = REQUIRED_FIELDS - set(case)
        assert not missing, f"{case['id']}: faltan campos {missing}"
        for field in REQUIRED_FIELDS - {"datos"}:
            value = case[field]
            filled = bool(value) or value is False
            assert filled, f"{case['id']}: campo vacío {field}"


def test_estados_validos(catalog):
    for case in catalog["casos"]:
        assert case["estado_automatizacion"] in VALID_STATES, (
            f"{case['id']}: estado inválido {case['estado_automatizacion']!r}"
        )


def test_automated_liga_implementacion(catalog):
    for case in catalog["casos"]:
        if case["estado_automatizacion"] == "Automated":
            impl = case.get("implementacion") or ""
            assert (
                "feature" in impl
                or "test_" in impl
                or "Cubierto" in impl
            ), f"{case['id']}: Automated sin implementación trazable"


def test_cobertura_modulos_por_marca(catalog):
    for site in VALID_SITES:
        modulos = {
            c["modulo"]
            for c in catalog["casos"]
            if c["ecommerce_key"] == site
        }
        assert modulos == EXPECTED_MODULES, (
            f"{site}: módulos faltantes {EXPECTED_MODULES - modulos}"
        )
