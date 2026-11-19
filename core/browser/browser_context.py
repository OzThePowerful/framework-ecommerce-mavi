"""Construcción del BrowserContext con los timeouts del ExecutionContext."""

from playwright.sync_api import Browser, BrowserContext

from core.execution.execution_context import ExecutionContext


def create_browser_context(browser: Browser, context: ExecutionContext) -> BrowserContext:
    """Crea un contexto aislado con timeouts centralizados."""
    browser_context = browser.new_context()
    browser_context.set_default_navigation_timeout(context.navigation_timeout)
    browser_context.set_default_timeout(context.action_timeout)
    return browser_context
