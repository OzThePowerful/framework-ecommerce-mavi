"""Componente CustomerForm: datos del comprador + dirección del OSC.

Lee y escribe los campos por `name` (los ids KO son dinámicos y los
mismos `name` se repiten en las secciones de facturación/pickup, por
eso todos los selectores llevan `:visible`). El CP dispara el
autocompletado de colonia/ciudad/estado.
"""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import FrameworkError
from domain.models.address import Address
from domain.models.customer import Customer
from pages.common.components.checkout.checkout_locators import CheckoutLocators


class CustomerFormComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Escritura ------------------------------------------------------
    def fill(self, customer: Customer, address: Address) -> None:
        """Llena datos del comprador y dirección; el CP va al final."""
        self._fill_visible(CheckoutLocators.EMAIL, customer.email)
        self._fill_visible(CheckoutLocators.FIRSTNAME, customer.name)
        self._fill_visible(CheckoutLocators.LASTNAME, customer.last_name)
        if customer.mothers_name:
            self._fill_visible(
                CheckoutLocators.MOTHERS_NAME, customer.mothers_name
            )
        if customer.phone:
            self._fill_visible(CheckoutLocators.PHONE, customer.phone)
        self._fill_visible(CheckoutLocators.STREET, address.street)
        if address.exterior_number:
            self._fill_visible(
                CheckoutLocators.EXTERIOR_NUMBER, address.exterior_number
            )
        postcode = self.page.locator(CheckoutLocators.POSTCODE).first
        postcode.wait_for(state="visible")
        postcode.fill(address.zip_code)
        postcode.press("Tab")  # el lookup del CP corre en blur/change
        self.wait_postcode_autocomplete()
        if address.references:
            self._fill_visible(CheckoutLocators.REFERENCE, address.references)

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

    # --- Lectura --------------------------------------------------------
    def read_customer(self) -> Customer:
        return Customer(
            email=self._value(CheckoutLocators.EMAIL),
            name=self._value(CheckoutLocators.FIRSTNAME),
            last_name=self._value(CheckoutLocators.LASTNAME),
            mothers_name=self._value_or_none(CheckoutLocators.MOTHERS_NAME),
            phone=self._value_or_none(CheckoutLocators.PHONE),
        )

    def read_address(self) -> Address:
        return Address(
            street=self._value(CheckoutLocators.STREET),
            exterior_number=self._value_or_none(CheckoutLocators.EXTERIOR_NUMBER),
            zip_code=self._value(CheckoutLocators.POSTCODE),
            neighborhood=self._first_non_empty(CheckoutLocators.COLONIA),
            city=self._value_or_none(CheckoutLocators.CITY),
            state=self._selected_label(CheckoutLocators.STATE),
            references=self._value_or_none(CheckoutLocators.REFERENCE),
        )

    def validation_errors(self) -> list[str]:
        """Mensajes de validación visibles del formulario."""
        errors = self.page.locator(CheckoutLocators.FIELD_ERRORS)
        return [
            errors.nth(i).inner_text().strip()
            for i in range(errors.count())
            if errors.nth(i).inner_text().strip()
        ]

    # --- Internos -------------------------------------------------------
    def _fill_visible(self, selector: str, value: str) -> None:
        field = self.page.locator(selector).first
        field.wait_for(state="visible")
        field.fill(value)

    def _value(self, selector: str) -> str:
        return self.page.locator(selector).first.input_value()

    def _value_or_none(self, selector: str) -> str | None:
        value = self.page.locator(selector).first.input_value()
        return value or None

    def _first_non_empty(self, selector: str) -> str | None:
        """Primer valor no vacío entre instancias KO duplicadas/ocultas."""
        fields = self.page.locator(selector)
        for i in range(fields.count()):
            value = fields.nth(i).input_value()
            if value:
                return value
        return None

    def _selected_label(self, selector: str) -> str | None:
        select = self.page.locator(selector).first
        selected = select.locator("option:checked")
        if not selected.count():
            return None
        label = selected.first.inner_text().strip()
        return label or None
