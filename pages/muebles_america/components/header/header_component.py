"""Header de Muebles América: extiende el común con lo que usan HOME_001
y SEARCH_001 de MA. Devuelve estado, sin asserts.

Se inyecta en la Home de MA vía `HomePage.HEADER` (MA-AISLAMIENTO-001).
"""

from pages.common.components.header.header_component import (
    HeaderComponent as CommonHeaderComponent,
)
from pages.muebles_america.components.header.header_locators import (
    HeaderLocators,
)


class HeaderComponent(CommonHeaderComponent):
    def is_search_usable(self) -> bool:
        """Buscador visible y habilitado para capturar un término."""
        box = self.search_box().first
        return box.is_visible() and box.is_enabled()

    def is_cart_available(self) -> bool:
        """Acceso al carrito visible y habilitado."""
        cart = self.page.locator(HeaderLocators.CART_BUTTON).first
        return cart.is_visible() and cart.is_enabled()

    def is_logo_visible(self) -> bool:
        """Logo de la marca (link a inicio) visible en el header."""
        return self.page.locator(HeaderLocators.HOME_LOGO).first.is_visible()

    def main_nav_items(self) -> list[str]:
        """Textos de los elementos habilitados de la navegación principal."""
        items = self.page.locator(HeaderLocators.MAIN_NAV_ITEMS)
        return [
            items.nth(i).inner_text().strip()
            for i in range(items.count())
            if items.nth(i).is_enabled()
        ]
