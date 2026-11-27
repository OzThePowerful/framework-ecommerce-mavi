"""Checkout de Muebles América (OneStepCheckout)."""

import re
import time
from decimal import Decimal, InvalidOperation
from fnmatch import fnmatch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import ElementStateError, NavigationError
from domain.models.address import Address
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

    # --- Datos del comprador campo por campo (CP_EC_MA_CHECKOUT_002) ------
    def capture_field(self, name: str, value: str) -> None:
        """Captura `value` en el campo `name` y sale de él (Tab) para que
        corra la validación KO del campo."""
        field = self.page.locator(CheckoutLocators.FIELD_BY_NAME.format(name=name))
        field.first.wait_for(state="visible")
        field.first.fill(value)
        field.first.press("Tab")

    def field_value(self, name: str) -> str | None:
        """Valor actual del campo `name`; None si no está visible."""
        field = self.page.locator(CheckoutLocators.FIELD_BY_NAME.format(name=name))
        return field.first.input_value() if field.count() else None

    def field_error(self, name: str) -> str | None:
        """Mensaje de validación del campo `name`; None si no tiene error."""
        return self.page.evaluate(CheckoutLocators.FIELD_ERROR_EXPR, name)

    def invalid_fields(self) -> list[str]:
        """Names de los campos visibles marcados como inválidos."""
        return list(self.page.evaluate(CheckoutLocators.INVALID_FIELDS_EXPR) or [])

    def fill_address(self, address: Address) -> None:
        """Dirección del comprador (calle, número, CP → autocompletado,
        referencias) con el AddressComponent común."""
        self.customer_form.address.fill(address)

    # --- Domicilio y entrega (CP_EC_MA_CHECKOUT_003) ---------------------
    def capture_postcode(self, zip_code: str) -> None:
        """Captura el CP y espera el autocompletado de colonia/ciudad."""
        self.capture_field("postcode", zip_code)
        self.customer_form.address.wait_postcode_autocomplete()

    def colonia_options(self) -> list[str]:
        """Colonias que ofrece el CP (sin el placeholder 'Colonia')."""
        select = self.page.locator(CheckoutLocators.COLONIA_SELECT)
        if not select.count():
            return []
        options = select.first.locator("option")
        labels = [options.nth(i).inner_text().strip() for i in range(options.count())]
        return [label for label in labels if label and label.casefold() != "colonia"]

    def select_colonia(self, name: str) -> str | None:
        """Selecciona la colonia que coincide con `name` (sin distinguir
        mayúsculas). Devuelve la opción elegida, o None si no existe."""
        match = next(
            (o for o in self.colonia_options() if o.casefold() == name.casefold()),
            None,
        )
        if match:
            self.page.locator(CheckoutLocators.COLONIA_SELECT).first.select_option(
                label=match
            )
        return match

    def selected_colonia(self) -> str | None:
        select = self.page.locator(CheckoutLocators.COLONIA_SELECT)
        if not select.count():
            return None
        checked = select.first.locator("option:checked")
        return checked.first.inner_text().strip() if checked.count() else None

    def delivery_options(self) -> list[str]:
        """Métodos de entrega presentados (visibles) por el checkout."""
        return [
            method
            for method, selector in CheckoutLocators.DELIVERY_OPTIONS.items()
            if self.page.locator(selector).first.is_visible()
        ]

    def shipping_cost_label(self) -> str | None:
        """Etiqueta del costo de envío en el resumen: 'Gratis', '$X' o None
        si aún no se calcula."""
        summary = self.page.locator(CheckoutLocators.SHIPPING_SUMMARY)
        if not summary.count():
            return None
        match = re.search(
            r"env\S*\s*:?\s*(Gratis|\$[\d,]+\.\d+)",
            summary.first.inner_text() or "",
            re.IGNORECASE,
        )
        return match.group(1) if match else None

    def continue_to_payment(self, timeout_ms: int = 20000) -> None:
        """'Continuar' del OSC: espera que 'Forma de pago' se habilite, la
        abre y espera a que quede como etapa activa (no crea la orden)."""
        self.gate.wait_payment_stage_enabled(timeout=timeout_ms)
        self.page.locator(CheckoutLocators.PAYMENT_STEP).first.click()
        deadline = time.monotonic() + timeout_ms / 1000
        while self.current_stage() != "forma_de_pago" and time.monotonic() < deadline:
            self.page.wait_for_timeout(250)

    # --- Evidencia (CP_EC_MA_E2E_001) --------------------------------------
    def evidence_mask(self) -> list:
        """Locators a tapar en los screenshots del checkout: inputs y selects
        visibles (identidad real del comprador, domicilio y tarjeta)."""
        return [self.page.locator(CheckoutLocators.EVIDENCE_MASK)]

    # --- Resumen ----------------------------------------------------------
    def summary_items(self) -> list[dict]:
        """Productos del resumen final ("Detalle de la compra"):
        `{sku, name, price, qty, delivery}` leídos del texto de cada
        `li.omni-product-item`; un campo ausente queda en None (el step
        decide). Solo lectura (CP_EC_MA_ORDER_001)."""
        items = self.page.locator(CheckoutLocators.SUMMARY_ITEM)
        return [
            self._parse_summary_item(items.nth(i).inner_text())
            for i in range(items.count())
        ]

    @staticmethod
    def _parse_summary_item(text: str) -> dict:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        sku_index = next(
            (i for i, line in enumerate(lines) if line.upper().startswith("SKU#")),
            None,
        )
        sku = name = None
        if sku_index is not None:
            sku = lines[sku_index].split(":", 1)[-1].strip() or None
            if sku_index + 1 < len(lines):
                name = lines[sku_index + 1]
        price = re.search(r"A:\s*(\$[\d,]+\.\d{2})", text)
        qty = re.search(r"Cantidad:\s*(\d+)", text)
        delivery = re.search(r"Entrega entre el [^\n]+", text)
        return {
            "sku": sku,
            "name": name,
            "price": (
                Money(Decimal(re.sub(r"[^\d.]", "", price.group(1))))
                if price else None
            ),
            "qty": int(qty.group(1)) if qty else None,
            "delivery": delivery.group(0).strip() if delivery else None,
        }

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
