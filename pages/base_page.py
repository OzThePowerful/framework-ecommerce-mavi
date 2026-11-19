"""BasePage mínima: solo primitivas UI realmente genéricas.

No debe crecer con lógica de Vue Storefront, Muebles América, checkout ni
componentes particulares; esa lógica vive en componentes o en cada page.
"""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext


class BasePage:
    """Primitivas genéricas: navegación, esperas observables e interacción."""

    def __init__(self, page: Page, context: ExecutionContext) -> None:
        self.page = page
        self.context = context

    def open(self, path: str = "/") -> None:
        """Navega a una ruta resuelta contra la base_url del contexto."""
        self.page.goto(self._resolve_url(path))

    def _resolve_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.context.base_url.rstrip('/')}/{path.lstrip('/')}"

    def wait_for_visible(self, selector: str) -> None:
        self.page.wait_for_selector(selector, state="visible")

    def is_present(self, selector: str) -> bool:
        return self.page.locator(selector).count() > 0
