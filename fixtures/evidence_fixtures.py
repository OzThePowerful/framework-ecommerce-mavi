"""Fixtures de evidencia: hook de fallo, manager por caso y labels Allure."""

import pytest

from core.evidence.evidence_manager import EvidenceManager
from core.reporting.allure_manager import label


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Conserva el resultado de cada fase para inspección en teardown."""
    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report


@pytest.fixture
def evidence_manager(run_context, execution_context, request) -> EvidenceManager:
    """EvidenceManager ligado al Run ID y al Case ID del test."""
    case_id = execution_context.case_id or request.node.name
    return EvidenceManager(run_context.run_id, case_id)


@pytest.fixture(autouse=True)
def allure_context(run_context, execution_context, request):
    """Allure identifica run/case/ecommerce/ambiente/navegador por test."""
    label("run_id", run_context.run_id)
    label("case_id", execution_context.case_id or request.node.name)
    label("site", execution_context.site)
    label("environment", execution_context.environment)
    label("browser", execution_context.browser)
