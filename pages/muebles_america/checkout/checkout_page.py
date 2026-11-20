"""Checkout de Muebles América (OneStepCheckout)."""

import re
from decimal import Decimal, InvalidOperation

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import ElementStateError, NavigationError
from domain.money.money import Money
from pages.base_page import BasePage
from pages.muebles_america.checkout.checkout_locators import CheckoutLocators


class CheckoutPage(BasePage):
    def continue_as_guest(self) -> None:
        """Continúa como invitado esperando la navegación al checkout.

        El patrón de URL proviene de sites.yaml vía ExecutionContext;
        el page no conoce hosts ni ambientes.
        """
        try:
            with self.page.expect_navigation(
                url=self.context.checkout_url_pattern
            ):
                self.page.locator(CheckoutLocators.GUEST_CONTINUE_BUTTON).click()
        except PlaywrightTimeoutError as exc:
            raise NavigationError(
                "No se navegó a "
                f"'{self.context.checkout_url_pattern}' tras continuar como "
                "invitado"
            ) from exc

    def wait_until_ready(self) -> None:
        self.page.wait_for_selector(CheckoutLocators.CHECKOUT_LOADER, state="detached")

    def get_displayed_price(self) -> Money:
        """Expone el precio mostrado como Money; la validación la hace el test."""
        text = self.page.locator(CheckoutLocators.TOTAL_PRICE).first.inner_text()
        # Formato mostrado: "$12,999.00" (separador de miles ",", decimal ".").
        digits = re.sub(r"[^\d.]", "", text)
        try:
            return Money(Decimal(digits))
        except InvalidOperation as exc:
            raise ElementStateError(
                f"El precio del checkout no tiene un importe legible: {text!r}"
            ) from exc
