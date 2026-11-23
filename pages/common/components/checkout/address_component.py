"""Componente Address: bloque de dirección del formulario OSC.

Extrae la responsabilidad de dirección (calle, número, CP →
autocompletado de colonia/ciudad/estado, referencias) del formulario
del comprador.
"""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import FrameworkError
from domain.models.address import Address
from pages.common.components.checkout.checkout_locators import (
    CheckoutLocators,
)
from pages.common.components.checkout.field_utils import (
    fill_visible,
    first_non_empty,
    selected_label,
    value,
    value_or_none,
)


class AddressComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def fill(self, address: Address) -> None:
        """Llena la dirección; el CP va al final (dispara el lookup)."""
        fill_visible(self.page, CheckoutLocators.STREET, address.street)
        if address.exterior_number:
            fill_visible(
                self.page,
                CheckoutLocators.EXTERIOR_NUMBER,
                address.exterior_number,
            )
        postcode = self.page.locator(CheckoutLocators.POSTCODE).first
        postcode.wait_for(state="visible")
        postcode.fill(address.zip_code)
        postcode.press("Tab")  # el lookup del CP corre en blur/change
        self.wait_postcode_autocomplete()
        if address.references:
            fill_visible(
                self.page, CheckoutLocators.REFERENCE, address.references
            )

    def wait_postcode_autocomplete(self, timeout: int = 10000) -> None:
        """El CP carga colonia (select con opciones) y ciudad/estado."""
        try:
            self.page.wait_for_function(
                """() => {
                    const sel = document.querySelector(
                        "select[name='colonia_select_shipping']");
                    if (sel && sel.options.length > 1) return true;
                    const cities = document.querySelectorAll(
                        "input[name='city']");
                    for (const c of cities) {
                        if (c.value && c.value.length > 0) return true;
                    }
                    return false;
                }""",
                timeout=timeout,
            )
        except PlaywrightTimeoutError as exc:
            raise FrameworkError(
                "El CP no disparó el autocompletado de colonia/ciudad"
            ) from exc

    def read(self) -> Address:
        return Address(
            street=value(self.page, CheckoutLocators.STREET),
            exterior_number=value_or_none(
                self.page, CheckoutLocators.EXTERIOR_NUMBER
            ),
            zip_code=value(self.page, CheckoutLocators.POSTCODE),
            neighborhood=first_non_empty(self.page, CheckoutLocators.COLONIA),
            city=value_or_none(self.page, CheckoutLocators.CITY),
            state=selected_label(self.page, CheckoutLocators.STATE),
            references=value_or_none(self.page, CheckoutLocators.REFERENCE),
        )
