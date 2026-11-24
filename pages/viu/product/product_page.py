"""PDP de VIU: fachada sobre el componente common de producto."""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_context import ExecutionContext
from domain.models.product import Product
from pages.base_page import BasePage
from pages.common.components.notifications.notification_component import (
    NotificationComponent,
)
from pages.common.components.pdp.pdp_component import PdpComponent
from pages.viu.product.product_locators import ProductLocators


class ProductPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.pdp = PdpComponent(page)
        self.notifications = NotificationComponent(page)

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

    def dismiss_post_add_overlays(self) -> None:
        """Despeja el toast post-add; VIU no muestra promo al agregar.

        El toast es la confirmación del add asíncrono: se espera primero
        para no continuar antes de que el producto quede en el carrito.
        """
        try:
            self.page.locator(ProductLocators.NOTIFICATION_TOAST).first.wait_for(
                state="visible", timeout=10000
            )
        except PlaywrightTimeoutError:
            pass
        if self.notifications.is_visible(ProductLocators.NOTIFICATION):
            close = self.page.locator(ProductLocators.NOTIFICATION_CLOSE)
            if close.count():
                close.first.click()

    def open_cart_from_notification(self) -> None:
        """Acepta el toast de agregado, despeja el backdrop residual y abre el minicart.

        El toast de VIU no enlaza al carrito como el de MA: hay que aceptarlo
        y abrir el minicart desde el header. Al aceptar queda un
        `modal-backdrop` residual que intercepta clics hasta descartarlo.
        """
        self.page.locator(ProductLocators.NOTIFICATION_TOAST).first.wait_for(
            state="visible"
        )
        self.page.locator(ProductLocators.NOTIFICATION_ACCEPT).first.click()
        backdrop = self.page.locator(ProductLocators.MODAL_BACKDROP)
        if backdrop.count():
            backdrop.first.click(position={"x": 5, "y": 5})
        self.page.locator(ProductLocators.MINICART_BUTTON).first.click()
