"""PDP de VIU: fachada sobre la base common de producto."""

from typing import ClassVar

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from domain.errors.precondition_error import PreconditionError
from pages.common.pages.product_page import CommonProductPage
from pages.viu.product.product_locators import ProductLocators


class ProductPage(CommonProductPage):
    PRODUCT_LOCATORS: ClassVar[type] = ProductLocators

    def dismiss_post_add_overlays(self) -> None:
        """Resuelve el feedback post-add de VIU: toast + modal de promo.

        El toast `div.notification` es la confirmación del add asíncrono
        y llega en dos variantes: `.success` (agregado) y `.error`
        ("La cantidad solicitada no está disponible"). En productos con
        promo aparece además un `modal-container` con backdrop que
        intercepta clics si queda abierto.
        """
        try:
            self.page.locator(ProductLocators.NOTIFICATION_TOAST).first.wait_for(
                state="visible", timeout=10000
            )
        except PlaywrightTimeoutError:
            return
        if self.page.locator(ProductLocators.NOTIFICATION_ERROR).count():
            raise PreconditionError(
                "add rechazado: la cantidad solicitada no está disponible"
            )
        accept = self.page.locator(ProductLocators.NOTIFICATION_ACCEPT)
        if accept.count():
            accept.first.click()
        modal_close = self.page.locator(ProductLocators.CART_MODAL_CLOSE)
        if modal_close.count():
            modal_close.first.click()
        backdrop = self.page.locator(ProductLocators.MODAL_BACKDROP)
        if backdrop.count():
            try:
                # El backdrop se desvanece solo al cerrar el modal.
                backdrop.first.wait_for(state="hidden", timeout=4000)
            except PlaywrightTimeoutError:
                # force: el backdrop animado nunca queda "stable"; solo se
                # clica cuando persiste tras el cierre del modal.
                backdrop.first.click(force=True, position={"x": 5, "y": 5})

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
            try:
                backdrop.first.wait_for(state="hidden", timeout=4000)
            except PlaywrightTimeoutError:
                backdrop.first.click(force=True, position={"x": 5, "y": 5})
        self.page.locator(ProductLocators.MINICART_BUTTON).first.click()
