"""Componente Payment: selección y preparación del método de pago.

Frontera del contrato: llega hasta `#_btnCheckout` **habilitado** — el
click que crea la orden nunca se ejecuta desde el framework.
"""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import (
    ElementStateError,
    PaymentError,
)
from pages.common.components.payment.payment_locators import (
    EXTERNAL_PROVIDER_METHODS,
    PaymentLocators,
)


class PaymentComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Etapa ----------------------------------------------------------
    def open_payment_stage(self) -> None:
        """Expande 'Forma de pago' (debe estar habilitada tras la dirección)."""
        button = self.page.locator(PaymentLocators.PAYMENT_STEP)
        if "opened" not in (button.first.get_attribute("class") or ""):
            button.first.click()
        self.page.locator(PaymentLocators.METHOD_RADIOS).first.wait_for(
            state="visible"
        )

    # --- Métodos --------------------------------------------------------
    def payment_methods(self) -> list[str]:
        """Values de los métodos de pago presentes en el DOM."""
        radios = self.page.locator(PaymentLocators.METHOD_RADIOS)
        return [
            radios.nth(i).get_attribute("value")
            for i in range(radios.count())
            if radios.nth(i).get_attribute("value")
        ]

    def is_method_selectable(self, method: str) -> bool:
        """El radio del método existe y no está deshabilitado.

        Encapsula reglas de negocio del OSC como el límite de monto de
        `openpay_stores` (> $30,000 MXN el método no es seleccionable).
        """
        radio = self.page.locator(
            PaymentLocators.METHOD_BY_VALUE.format(value=method)
        )
        return (
            radio.count() > 0
            and radio.first.get_attribute("disabled") is None
        )

    def select_method(self, method: str) -> None:
        """Selecciona el método de pago; exige que sea seleccionable."""
        if not self.is_method_selectable(method):
            raise PaymentError(
                f"El método de pago '{method}' no es seleccionable "
                f"(disponibles: {self.payment_methods()})"
            )
        radio = self.page.locator(
            PaymentLocators.METHOD_BY_VALUE.format(value=method)
        ).first
        radio.check(force=True)

    def selected_method(self) -> str | None:
        checked = self.page.locator(PaymentLocators.METHOD_CHECKED)
        if not checked.count():
            return None
        return checked.first.get_attribute("value")

    def expects_external_provider(self, method: str) -> bool:
        """True si el método sale del dominio (popup/redirect del proveedor)."""
        return method in EXTERNAL_PROVIDER_METHODS

    # --- Datos de tarjeta (contado OpenPay) ------------------------------
    def fill_card(
        self,
        number: str,
        exp_month: str,
        exp_year: str,
        cvv: str,
    ) -> None:
        """Completa los campos nativos de tarjeta de OpenPay."""
        self.page.locator(PaymentLocators.CARD_NUMBER).fill(number)
        self.page.locator(PaymentLocators.CARD_EXP_MONTH).select_option(
            label=exp_month
        )
        self.page.locator(PaymentLocators.CARD_EXP_YEAR).select_option(
            label=exp_year
        )
        self.page.locator(PaymentLocators.CARD_CVV).fill(cvv)

    def set_billing_same_as_shipping(self, checked: bool) -> None:
        checkbox = self.page.locator(PaymentLocators.BILLING_SAME_AS_SHIPPING)
        if checkbox.count():
            checkbox.first.set_checked(checked)

    def is_billing_same_as_shipping(self) -> bool:
        checkbox = self.page.locator(PaymentLocators.BILLING_SAME_AS_SHIPPING)
        return checkbox.count() > 0 and checkbox.first.is_checked()

    # --- Frontera -------------------------------------------------------
    def is_place_order_enabled(self) -> bool:
        button = self.page.locator(PaymentLocators.PLACE_ORDER)
        return button.count() > 0 and button.first.get_attribute("disabled") is None

    def wait_place_order_enabled(self, timeout: int = 20000) -> None:
        """Última frontera permitida: botón habilitado. Nunca se clickea."""
        try:
            self.page.wait_for_function(
                """() => {
                    const b = document.getElementById('_btnCheckout');
                    return b && !b.hasAttribute('disabled');
                }""",
                timeout=timeout,
            )
        except PlaywrightTimeoutError as exc:
            raise ElementStateError(
                "El botón 'Finalizar compra' no quedó habilitado"
            ) from exc

    # --- Errores ----------------------------------------------------------
    def validation_errors(self) -> list[str]:
        errors = self.page.locator(PaymentLocators.FIELD_ERRORS)
        return [
            errors.nth(i).inner_text().strip()
            for i in range(errors.count())
            if errors.nth(i).inner_text().strip()
        ]
