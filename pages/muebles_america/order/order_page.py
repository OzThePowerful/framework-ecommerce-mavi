"""Confirmación de orden de Muebles América: fachada sobre la base common.

El comportamiento es el de la base común; aquí solo se agrega la lectura
del encabezado de la página de éxito (CP_EC_MA_ORDER_001).
"""

from pages.common.components.order.order_locators import OrderLocators
from pages.common.pages.order_page import CommonOrderPage


class OrderPage(CommonOrderPage):
    def success_heading(self) -> str | None:
        """Encabezado visible de la página final (`.page-title`), o None."""
        title = self.page.locator(f"{OrderLocators.SUCCESS_TITLE}:visible")
        if not title.count():
            return None
        return " ".join(title.first.inner_text().split()) or None
