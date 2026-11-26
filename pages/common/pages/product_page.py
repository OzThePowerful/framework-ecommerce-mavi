"""PDP: fachada base compartida por las marcas.

La lectura del producto y el add-to-cart son comunes; el flujo post-add
(toast, promos, apertura del carrito) difiere por marca y lo implementa la
subclase en `dismiss_post_add_overlays` / `open_cart_from_notification`.
"""

from typing import ClassVar

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from domain.models.product import Product
from pages.base_page import BasePage
from pages.common.components.notifications.notification_component import (
    NotificationComponent,
)
from pages.common.components.pdp.pdp_component import PdpComponent


class CommonProductPage(BasePage):
    PRODUCT_LOCATORS: ClassVar[type | None] = None

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
        self.page.locator(
            self.PRODUCT_LOCATORS.ADD_TO_CART_BUTTON
        ).first.click()

    def dismiss_post_add_overlays(self) -> None:
        """Despeja el overlay post-add; cada marca define el suyo."""
        raise NotImplementedError

    def open_cart_from_notification(self) -> None:
        """Abre el carrito desde la notificación post-add de la marca."""
        raise NotImplementedError
