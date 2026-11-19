"""Fábrica de Page Objects por sitio: Page recibida vía fixture/factory."""

import importlib

import pytest
from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from core.execution.execution_errors import FrameworkError

_SITE_PACKAGES = {
    "muebles_america": "pages.muebles_america",
    "viu": "pages.viu",
    "mavi": "pages.mavi",
}


class PageFactory:
    """Construye Page Objects del sitio activo en el ExecutionContext."""

    def __init__(self, page: Page, context: ExecutionContext) -> None:
        self._page = page
        self._context = context

    def _build(self, subpackage: str, class_name: str):
        base = _SITE_PACKAGES.get(self._context.site)
        if base is None:
            raise FrameworkError(
                f"Sitio '{self._context.site}' sin paquete de pages registrado."
            )
        module_name = f"{base}.{subpackage}.{subpackage}_page"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            raise FrameworkError(
                f"Page '{subpackage}' no implementada para "
                f"'{self._context.site}' ({module_name})."
            ) from exc
        page_class = getattr(module, class_name)
        return page_class(self._page, self._context)

    def home(self):
        return self._build("home", "HomePage")

    def search(self):
        return self._build("search", "SearchPage")

    def product(self):
        return self._build("product", "ProductPage")

    def cart(self):
        return self._build("cart", "CartPage")

    def checkout(self):
        return self._build("checkout", "CheckoutPage")

    def payment(self):
        return self._build("payment", "PaymentPage")

    def order(self):
        return self._build("order", "OrderPage")


@pytest.fixture
def pages(page, execution_context) -> PageFactory:
    """Fábrica de pages del sitio activo; el test no elige URLs ni marca."""
    return PageFactory(page, execution_context)
