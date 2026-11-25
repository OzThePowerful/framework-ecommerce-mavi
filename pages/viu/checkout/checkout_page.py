"""Checkout de VIU (OneStepCheckout): fachada sobre la base common."""

from domain.money.money import Money
from pages.common.pages.checkout_page import CommonCheckoutPage


class CheckoutPage(CommonCheckoutPage):
    def continue_as_guest(self) -> None:
        self.gate.continue_as_guest()

    # --- Resumen ----------------------------------------------------------
    def get_displayed_price(self) -> Money:
        """Total mostrado en el resumen del checkout como Money."""
        return self.delivery.summary_total()
