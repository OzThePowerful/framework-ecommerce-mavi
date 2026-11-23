"""Componente Checkout (gate): transición carrito → identificación.

Base mínima compartida por ambas marcas; el formulario completo del
OneStepCheckout se implementa en el vertical de checkout.
"""

from playwright.sync_api import Page

from pages.common.components.checkout.checkout_locators import (
    CheckoutGateLocators,
)


class CheckoutComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_for_guest_gate(self) -> None:
        self.page.locator(CheckoutGateLocators.GUEST_CONTINUE).first.wait_for(
            state="visible"
        )

    def is_guest_gate_visible(self) -> bool:
        return self.page.locator(CheckoutGateLocators.GUEST_CONTINUE).count() > 0
