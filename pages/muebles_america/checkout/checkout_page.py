"""Checkout de Muebles América (OneStepCheckout)."""

import re
from decimal import Decimal, InvalidOperation
from fnmatch import fnmatch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import ElementStateError, NavigationError
from domain.money.money import Money
from pages.common.pages.checkout_page import CommonCheckoutPage
from pages.muebles_america.checkout.checkout_locators import CheckoutLocators


class CheckoutPage(CommonCheckoutPage):
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

    # --- Primera etapa (CP_EC_MA_CHECKOUT_001) -------------------------
    def is_on_checkout(self) -> bool:
        """La URL actual es la del checkout de la marca (patrón glob de
        sites.yaml vía ExecutionContext)."""
        return fnmatch(self.page.url, self.context.checkout_url_pattern)

    def unavailable_fields(self, names: list[str]) -> list[str]:
        """De `names`, los campos que no se pueden capturar: no visibles,
        deshabilitados o de solo lectura. Lista vacía = todos disponibles."""
        unavailable = []
        for name in names:
            field = self.page.locator(
                CheckoutLocators.FIELD_BY_NAME.format(name=name)
            )
            if not field.count() or not field.first.is_editable():
                unavailable.append(name)
        return unavailable

    # --- Resumen ----------------------------------------------------------
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
