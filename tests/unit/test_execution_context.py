"""Pruebas unitarias de ExecutionContext.build."""

import pytest

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import (
    UnknownEnvironmentError,
    UnknownProfileError,
    UnknownSiteError,
)

pytestmark = pytest.mark.unit


def test_build_completo():
    context = ExecutionContext.build(
        site="muebles_america",
        environment="stage",
        profile_name="ci",
        case_id="CP_EC_MA_HOME_001",
        run_id="testrun",
    )
    assert context.project == "ecommerce"
    assert context.site == "muebles_america"
    assert context.site_code == "MA"
    assert context.environment == "stage"
    assert context.base_url.startswith("http")
    assert context.checkout_url_pattern
    assert context.browser == "chromium"
    assert context.case_id == "CP_EC_MA_HOME_001"
    assert context.run_id == "testrun"
    assert context.navigation_timeout > 0


def test_build_sitio_invalido():
    with pytest.raises(UnknownSiteError):
        ExecutionContext.build("nope", "stage", "default", None, "r")


def test_build_ambiente_invalido():
    with pytest.raises(UnknownEnvironmentError):
        ExecutionContext.build("muebles_america", "nope", "default", None, "r")


def test_build_perfil_invalido():
    with pytest.raises(UnknownProfileError):
        ExecutionContext.build("muebles_america", "stage", "nope", None, "r")
