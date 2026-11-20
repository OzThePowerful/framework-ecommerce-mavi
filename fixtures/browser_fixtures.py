"""Browser Lifecycle centralizado: Playwright → Browser → Context → Page."""

import pytest
from playwright.sync_api import expect, sync_playwright

from core.browser.browser_context import create_browser_context
from core.browser.browser_factory import launch_browser


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
def page(context, execution_context):
    expect.set_options(timeout=execution_context.expect_timeout)
    test_page = context.new_page()
    yield test_page
    test_page.close()
