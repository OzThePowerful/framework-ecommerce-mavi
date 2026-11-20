"""PDP de Muebles América."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.notifications.notification_component import (
    NotificationComponent,
)
from pages.muebles_america.components.promotions_window.promotions_window_component import (
    PromotionsWindowComponent,
)
from pages.muebles_america.product.product_locators import ProductLocators


class ProductPage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.notifications = NotificationComponent(page)
        self.promotions_window = PromotionsWindowComponent(page)

    def add_to_cart(self) -> None:
        self.page.locator(ProductLocators.ADD_TO_CART_BUTTON).first.click()

    def open_cart_from_notification(self) -> None:
        """Confirma el toast de agregado y abre el carrito desde él.

        Antes de interactuar con el toast cierra la ventana de promociones si
        se mostró, porque su backdrop intercepta los clics.
        """
        self.page.locator(ProductLocators.NOTIFICATION).first.wait_for(
            state="visible"
        )
        self.promotions_window.close_if_present()
        self.notifications.click(ProductLocators.NOTIFICATION)
        self.page.locator(ProductLocators.CART_NOTIFICATION_BUTTON).first.click()
