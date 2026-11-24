"""Fixtures de contexto: CLI pytest → ConfigLoader → ExecutionContext."""

import os
import re

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


_CASE_TAG = re.compile(r"^[A-Z0-9]+_\d{3}$")
_PENDING_REASON = "Caso definido y trazable; automatización pendiente"


def case_id_from_tags(tag_names, site_code: str) -> str | None:
    """Resuelve el Case ID: tag @<MODULO>_<NNN> + código de marca.

    Un escenario BDD debe llevar exactamente un tag de caso; con más de
    uno o sin él no hay materialización (conserva su nombre).
    """
    tags = [name for name in tag_names if _CASE_TAG.match(name)]
    if len(tags) != 1:
        return None
    return f"CP_EC_{site_code}_{tags[0]}"


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Materializa Case IDs y trata @pending como skip explícito.

    Corre antes del deselect por -k: `pytest -k CP_EC_MA_…` filtra por
    el identificador oficial del caso.
    """
    site = os.environ.get(_SITE_ENV_VAR) or config.getoption("--site")
    env = os.environ.get(_ENV_ENV_VAR) or config.getoption("--target-env")
    site_code = resolve_site(site, env).code

    for item in items:
        tags = {mark.name for mark in item.iter_markers()}
        case_id = case_id_from_tags(tags, site_code)
        if case_id:
            item.name = case_id
            item.keywords[case_id] = True
            item._nodeid = f"{item.nodeid.rsplit('::', 1)[0]}::{case_id}"
        if "pending" in tags:
            item.add_marker(pytest.mark.skip(reason=_PENDING_REASON))
