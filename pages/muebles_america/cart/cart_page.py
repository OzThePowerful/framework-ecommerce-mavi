"""Carrito de Muebles América."""

from pages.base_page import BasePage
from pages.muebles_america.cart.cart_locators import CartLocators


class CartPage(BasePage):
    def buy_now(self) -> None:
        """Avanza del carrito hacia la identificación/checkout."""
        self.page.locator(CartLocators.BUY_NOW_BUTTON).click()
