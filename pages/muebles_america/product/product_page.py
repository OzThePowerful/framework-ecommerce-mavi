"""PDP de Muebles América."""

from typing import ClassVar

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_context import ExecutionContext
from pages.common.pages.product_page import CommonProductPage
from pages.muebles_america.components.promotions_window.promotions_window_component import (
    PromotionsWindowComponent,
)
from pages.muebles_america.product.product_locators import ProductLocators


class ProductPage(CommonProductPage):
    PRODUCT_LOCATORS: ClassVar[type] = ProductLocators

    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.promotions_window = PromotionsWindowComponent(page)

    def dismiss_post_add_overlays(self) -> None:
        """Despeja promo y toast post-add para liberar el header.

        El toast es la confirmación del add asíncrono: se espera primero
        para no continuar antes de que el producto quede en el carrito.
        """
        try:
            self.page.locator(ProductLocators.NOTIFICATION).first.wait_for(
                state="visible", timeout=10000
            )
        except PlaywrightTimeoutError:
            pass
        self.promotions_window.close_if_present()
        if self.notifications.is_visible(ProductLocators.NOTIFICATION):
            close = self.page.locator(ProductLocators.NOTIFICATION_CLOSE)
            if close.count():
                close.first.click()

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
