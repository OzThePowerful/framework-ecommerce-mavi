"""Fixtures de contexto: CLI pytest → ConfigLoader → ExecutionContext."""

import os

import pytest

from core.config.site_config import resolve_site
from core.evidence.artifact_paths import allure_results_dir
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
    case_id = os.environ.get(_CASE_ENV_VAR) or request.config.getoption("--case-id")
    context = ExecutionContext.build(
        site=site,
        environment=environment,
        profile_name=request.config.getoption("--exec-profile"),
        case_id=case_id,
        run_id=run_context.run_id,
    )
    _write_allure_environment(context)
    return context


def _write_allure_environment(context: ExecutionContext) -> None:
    """environment.properties: Allure identifica la ejecución completa."""
    lines = "\n".join(
        (
            f"RUN_ID={context.run_id}",
            f"SITE={context.site}",
            f"ENVIRONMENT={context.environment}",
            f"BROWSER={context.browser}",
            f"BASE_URL={context.base_url}",
        )
    )
    (allure_results_dir() / "environment.properties").write_text(
        lines + "\n", encoding="utf-8"
    )
