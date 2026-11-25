"""PDP de VIU: fachada sobre la base common de producto."""

from typing import ClassVar

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.common.pages.product_page import CommonProductPage
from pages.viu.product.product_locators import ProductLocators


class ProductPage(CommonProductPage):
    PRODUCT_LOCATORS: ClassVar[type] = ProductLocators

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
