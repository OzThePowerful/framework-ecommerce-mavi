"""Fixtures de contexto: CLI pytest → ConfigLoader → ExecutionContext."""

import os

import pytest

from core.config.config_loader import load_execution_profile
from core.config.site_config import resolve_site
from core.execution.execution_context import ExecutionContext
from core.execution.run_context import RunContext
from core.logging.logger import configure_logging, get_logger

_SITE_ENV_VAR = "MAVI_ECOM_SITE"
_ENV_ENV_VAR = "MAVI_ECOM_ENV"
_CASE_ENV_VAR = "MAVI_ECOM_CASE_ID"


def pytest_addoption(parser):
    group = parser.getgroup("ecommerce-framework")
    group.addoption(
        "--site",
        default="muebles_america",
        help="Ecommerce objetivo (ver config/sites.yaml).",
    )
    group.addoption(
        "--target-env",
        default="stage",
        help="Ambiente objetivo (ver config/environments.yaml).",
    )
    group.addoption(
        "--case-id",
        default=None,
        help="Case ID en ejecución; su resolución completa es posterior.",
    )
    group.addoption(
        "--exec-profile",
        default="default",
        help="Perfil de config/execution_profiles.yaml.",
    )


def pytest_configure(config):
    """Valida sitio/ambiente en el arranque: combinación inválida = error
    explícito temprano, nunca redirección silenciosa."""
    site = os.environ.get(_SITE_ENV_VAR) or config.getoption("--site")
    environment = os.environ.get(_ENV_ENV_VAR) or config.getoption("--target-env")
    resolve_site(site, environment)


@pytest.fixture(scope="session")
def run_context() -> RunContext:
    """Un RunContext/Run ID por sesión de ejecución."""
    context = RunContext()
    configure_logging()
    get_logger("fixtures.execution", run_id=context.run_id).info(
        "RunContext iniciado"
    )
    return context


@pytest.fixture(scope="session")
def execution_context(request, run_context) -> ExecutionContext:
    """Contexto inequívoco: las capas funcionales nunca resuelven URLs."""
    site = os.environ.get(_SITE_ENV_VAR) or request.config.getoption("--site")
    environment = os.environ.get(_ENV_ENV_VAR) or request.config.getoption(
        "--target-env"
    )
    profile = load_execution_profile(request.config.getoption("--exec-profile"))
    site_config = resolve_site(site, environment)
    return ExecutionContext(
        project="ecommerce",
        site=site_config.site,
        site_code=site_config.code,
        environment=site_config.environment,
        base_url=site_config.base_url,
        checkout_url_pattern=site_config.checkout_url_pattern,
        browser=profile["browser"],
        headless=bool(profile["headless"]),
        case_id=os.environ.get(_CASE_ENV_VAR) or request.config.getoption("--case-id"),
        run_id=run_context.run_id,
        navigation_timeout=int(profile["navigation_timeout_ms"]),
        action_timeout=int(profile["action_timeout_ms"]),
        expect_timeout=int(profile["expect_timeout_ms"]),
    )
