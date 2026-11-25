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

    def wait_method_selectable(self, method: str, timeout: int = 15000) -> None:
        """Espera la habilitación asíncrona del radio por KO."""
        try:
            self.page.wait_for_function(
                """(value) => {
                    const r = document.querySelector(
                        `input[name='payment[method]'][value='${value}']`
                    );
                    return r && !r.hasAttribute('disabled');
                }""",
                arg=method,
                timeout=timeout,
            )
        except PlaywrightTimeoutError as exc:
            raise PaymentError(
                f"El método de pago '{method}' no es seleccionable "
                f"(disponibles: {self.payment_methods()})"
            ) from exc

    def select_method(self, method: str) -> None:
        """Selecciona el método de pago; exige que sea seleccionable."""
        self.wait_method_selectable(method)
        radio = self.page.locator(
            PaymentLocators.METHOD_BY_VALUE.format(value=method)
        ).first
        # El input real queda oculto tras el label estilizado de KO: el
        # estado enabled ya está garantizado por wait_method_selectable y
        # force evita el actionability-check de visibilidad.
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
        """Completa los campos nativos de tarjeta de OpenPay.

        KO re-renderiza el fieldset al seleccionar el método: cada fill se
        verifica y reintenta hasta que el valor persiste.
        """
        number_locator = self.page.locator(PaymentLocators.CARD_NUMBER)
        number_locator.wait_for(state="visible")
        self._wait_card_fieldset_stable()
        self._fill_until_persists(number_locator, number)
        self._select_until_persists(
            PaymentLocators.CARD_EXP_MONTH, exp_month
        )
        self._select_until_persists(
            PaymentLocators.CARD_EXP_YEAR, exp_year
        )
        self._fill_until_persists(
            self.page.locator(PaymentLocators.CARD_CVV), cvv
        )

    def _wait_card_fieldset_stable(self, timeout: int = 10000) -> None:
        """KO re-renderiza el fieldset al seleccionar el método; espera a
        que el DOM del fieldset deje de mutar antes de llenar."""
        try:
            self.page.wait_for_function(
                """() => {
                    const f = document.getElementById('openpay_cards_cc_number');
                    if (!f) return false;
                    if (!window.__ccStable) {
                        window.__ccStable = {count: 0, last: f.outerHTML};
                    }
                    const s = window.__ccStable;
                    if (f.outerHTML === s.last) { s.count += 1; }
                    else { s.count = 0; s.last = f.outerHTML; }
                    return s.count >= 8;
                }""",
                polling=250,
                timeout=timeout,
            )
        except PlaywrightTimeoutError:
            # Estabilidad no confirmada: se continúa y el fill verifica.
            pass

    def _fill_until_persists(self, locator, value: str, retries: int = 6) -> None:
        for _ in range(retries):
            locator.fill(value)
            # KO valida en blur: sin Tab el botón queda disabled.
            locator.first.press("Tab")
            self.page.wait_for_timeout(500)
            if not locator.count():
                continue
            # OpenPay enmascara con espacios: comparar solo dígitos.
            actual = "".join(
                ch for ch in locator.first.input_value() if ch.isdigit()
            )
            if actual == "".join(ch for ch in value if ch.isdigit()):
                return
        raise ElementStateError(
            "El campo de tarjeta no retuvo el valor (re-render de KO)"
        )

    def _select_until_persists(
        self, selector: str, label: str, retries: int = 6
    ) -> None:
        locator = self.page.locator(selector)
        for _ in range(retries):
            locator.select_option(label=label)
            locator.first.press("Tab")
            self.page.wait_for_timeout(400)
            if locator.count() and locator.first.input_value():
                return
        raise ElementStateError(
            f"El select {selector} no retuvo la opción {label!r}"
        )

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

    def confirm_order(self) -> None:
        """ACCION IRREVERSIBLE: ejecuta 'Finalizar compra' y crea la orden.

        Solo invocable desde casos ORDER/E2E en ambientes donde la creación
        de órdenes de prueba está autorizada. Tras el click la validación
        de éxito/declinación corresponde a OrderComponent.wait_success().
        """
        self.wait_place_order_enabled()
        self.page.locator(PaymentLocators.PLACE_ORDER).first.click()

    # --- Errores ----------------------------------------------------------
    def validation_errors(self) -> list[str]:
        errors = self.page.locator(PaymentLocators.FIELD_ERRORS)
        return [
            errors.nth(i).inner_text().strip()
            for i in range(errors.count())
            if errors.nth(i).inner_text().strip()
        ]
