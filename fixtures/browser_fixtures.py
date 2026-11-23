"""Browser Lifecycle centralizado: Playwright → Browser → Context → Page.

El teardown de `page` captura la evidencia de fallo (screenshot, URL,
excepción, manifest) antes de liberar recursos.
"""

import pytest
from playwright.sync_api import expect, sync_playwright

from core.browser.browser_context import create_browser_context
from core.browser.browser_factory import launch_browser
from core.evidence.evidence_manager import EvidenceManager
from core.reporting.allure_manager import attach_failure_artifacts


def _failed_report(node):
    """Primer reporte fallido del test (setup tiene precedencia)."""
    for phase in ("setup", "call", "teardown"):
        report = getattr(node, f"rep_{phase}", None)
        if report is not None and report.failed:
            return report
    return None


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance, execution_context):
    instance = launch_browser(playwright_instance, execution_context)
    yield instance
    instance.close()


@pytest.fixture
def context(browser, execution_context):
    browser_context = create_browser_context(browser, execution_context)
    yield browser_context
    browser_context.close()


@pytest.fixture
def page(context, execution_context, run_context, request):
    expect.set_options(timeout=execution_context.expect_timeout)
    test_page = context.new_page()
    yield test_page
    report = _failed_report(request.node)
    if report is not None:
        case_id = execution_context.case_id or request.node.name
        manager = EvidenceManager(run_context.run_id, case_id)
        artifacts = manager.capture_failure(
            test_page, report, execution_context, request.node.name
        )
        attach_failure_artifacts(artifacts)
    test_page.close()
