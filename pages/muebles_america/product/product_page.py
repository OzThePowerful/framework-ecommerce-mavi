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

    def availability_label(self, timeout_ms: int = 15000) -> str | None:
        """Etiqueta de disponibilidad visible: 'Disponible', 'Agotado' o
        'Solo queda(n) N'. Llega después de cargar la PDP (servicio
        `/api/stock/check`), por eso la espera amplia. Es un sondeo: None
        si la PDP no la muestra en `timeout_ms`."""
        label = self.page.locator(ProductLocators.AVAILABILITY_LABEL)
        try:
            label.first.wait_for(state="visible", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            return None
        return " ".join(label.first.inner_text().split())

    def displayed_quantity(self) -> int | None:
        """Cantidad visible en la PDP; None si no se muestra o no es número."""
        qty = self.page.locator(ProductLocators.QUANTITY)
        if not qty.count():
            return None
        text = qty.first.inner_text().strip()
        return int(text) if text.isdigit() else None

    def add_confirmation_message(self, timeout_ms: int = 10000) -> str | None:
        """Texto del toast post-add ('Tu producto … ha sido agregado a tu
        carrito de compras.'). Sondeo: None si no aparece a tiempo."""
        toast = self.page.locator(ProductLocators.NOTIFICATION).first
        try:
            toast.wait_for(state="visible", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            return None
        return " ".join(toast.inner_text().split())

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
