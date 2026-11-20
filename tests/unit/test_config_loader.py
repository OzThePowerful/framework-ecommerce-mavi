"""Pruebas unitarias del ConfigLoader (perfiles y environments)."""

import pytest

from core.config.config_loader import (
    load_environments,
    load_execution_profile,
    load_sites,
)
from core.execution.execution_errors import UnknownProfileError

pytestmark = pytest.mark.unit


def test_perfil_default_se_resuelve():
    profile = load_execution_profile("default")
    assert profile["browser"] == "chromium"
    assert profile["navigation_timeout_ms"] > 0


def test_perfil_desconocido_falla_explicito():
    with pytest.raises(UnknownProfileError):
        load_execution_profile("perfil_inexistente")


def test_environments_declara_stage_y_prod():
    declared = load_environments()["environments"]
    assert {"stage", "prod"} <= set(declared)


def test_sites_declara_tres_ecommerce():
    catalog = load_sites()["sites"]
    assert {"muebles_america", "viu", "mavi"} <= set(catalog)
