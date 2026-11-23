"""PDP de VIU: fachada sobre el componente common de producto."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from domain.models.product import Product
from pages.base_page import BasePage
from pages.common.components.pdp.pdp_component import PdpComponent
from pages.viu.product.product_locators import ProductLocators


class ProductPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.pdp = PdpComponent(page)

    def read_product(self) -> Product:
        """Modelo de dominio del producto observado en la PDP."""
        return self.pdp.read_product()

    def is_available(self) -> bool:
        return self.pdp.is_available()

    def stock_quantity(self) -> int:
        return self.pdp.stock_quantity()

    def quantity(self) -> int:
        return self.pdp.quantity()

    def is_add_to_cart_enabled(self) -> bool:
        return self.pdp.is_add_to_cart_enabled()

    def is_configurable(self) -> bool:
        return self.pdp.is_configurable()

    def parent_sku(self) -> str | None:
        return self.pdp.parent_sku()

    def variants(self) -> list[Product]:
        return self.pdp.variants()

    def add_to_cart(self) -> None:
        self.page.locator(ProductLocators.ADD_TO_CART_BUTTON).first.click()
