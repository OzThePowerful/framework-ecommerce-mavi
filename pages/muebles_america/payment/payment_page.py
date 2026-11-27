"""Pago de Muebles América: fachada sobre la base common.

El flujo de pago es el de la base común; aquí se agregan las lecturas de
CP_EC_MA_PAY_001 (opciones estabilizadas, método activo, etiqueta del
botón y valores de tarjeta conservados), que nunca pulsan 'Finalizar
compra', y la confirmación con registro de peticiones de
CP_EC_MA_ORDER_001 (`confirm_order_tracked`, acción irreversible).
"""

import time
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Response

from pages.common.components.payment.payment_locators import (
    PaymentLocators as CommonPaymentLocators,
)
from pages.common.pages.payment_page import CommonPaymentPage
from pages.muebles_america.payment.payment_locators import PaymentLocators


class PaymentPage(CommonPaymentPage):
    def payment_options(
        self, settle_ms: int = 1500, timeout_ms: int = 15000
    ) -> list[dict]:
        """Métodos de pago `{value, label, enabled}` una vez estabilizada la
        etapa: radios y estado del botón de confirmación deben repetirse
        sin cambios durante `settle_ms` — y el estado estable debe ser el
        de mayor habilitación observado. KO oscila al abrir la etapa
        ('todos → solo Efectivo → todos'): una fase transitoria puede
        durar más que `settle_ms`, así que el cierre no basta con '≥1
        habilitado'. Al agotar `timeout_ms` devuelve la lectura con más
        métodos habilitados vista (el step decide)."""

        def snapshot() -> tuple[list[dict], bool]:
            return (
                self.page.evaluate(PaymentLocators.OPTIONS_EXPR),
                self.is_place_order_enabled(),
            )

        def enabled_count(state: tuple[list[dict], bool]) -> int:
            return sum(1 for option in state[0] if option["enabled"])

        deadline = time.monotonic() + timeout_ms / 1000
        state = best = snapshot()
        stable_since = time.monotonic()
        while time.monotonic() < deadline:
            self.page.wait_for_timeout(250)
            current = snapshot()
            if enabled_count(current) > enabled_count(best):
                best = current
            if current != state:
                state, stable_since = current, time.monotonic()
                continue
            if current == best and (
                time.monotonic() - stable_since
            ) * 1000 >= settle_ms:
                break
        return list(best[0])

    def active_method(self) -> str | None:
        """`value` del método cuyo contenedor está marcado `_active`."""
        radio = self.page.locator(PaymentLocators.ACTIVE_METHOD_RADIO)
        return radio.first.get_attribute("value") if radio.count() else None

    def place_order_label(self) -> str | None:
        """Texto del botón de confirmación ('Finalizar compra' o
        'Pagar con <método>'). Solo lectura: nunca se pulsa."""
        button = self.page.locator(CommonPaymentLocators.PLACE_ORDER)
        if not button.count():
            return None
        return " ".join(button.first.inner_text().split())

    def card_values(self) -> dict[str, str | None]:
        """Valores conservados en los campos de tarjeta: número y CVV solo
        dígitos (OpenPay enmascara con espacios); mes y año, la opción
        elegida."""

        def digits(selector: str) -> str | None:
            field = self.page.locator(selector)
            if not field.count():
                return None
            return "".join(ch for ch in field.first.input_value() if ch.isdigit())

        def selected(selector: str) -> str | None:
            option = self.page.locator(selector).locator("option:checked")
            return option.first.inner_text().strip() if option.count() else None

        return {
            "number": digits(CommonPaymentLocators.CARD_NUMBER),
            "exp_month": selected(CommonPaymentLocators.CARD_EXP_MONTH),
            "exp_year": selected(CommonPaymentLocators.CARD_EXP_YEAR),
            "cvv": digits(CommonPaymentLocators.CARD_CVV),
        }

    # --- Confirmación (CP_EC_MA_ORDER_001) --------------------------------
    def confirm_order_tracked(self, timeout_ms: int = 90000) -> dict:
        """ACCIÓN IRREVERSIBLE: ejecuta 'Finalizar compra' (`confirm_order`
        común) registrando las respuestas POST de la confirmación, y espera
        la de creación de la orden (`payment-information`).

        Devuelve `{path, status, body}` de esa respuesta; `body` es None si
        el navegador ya no conserva el cuerpo. Las demás respuestas se leen
        con `confirmation_responses()`. Solo para casos ORDER autorizados.
        """
        self._confirmation_log: list[dict] = []

        def is_tracked(response: Response) -> bool:
            return response.request.method == "POST" and any(
                part in response.url for part in PaymentLocators.CONFIRMATION_REQUESTS
            )

        def record(response: Response) -> None:
            if is_tracked(response):
                self._confirmation_log.append(
                    {"path": urlsplit(response.url).path, "status": response.status}
                )

        self._confirmation_listener = record
        self.page.on("response", record)
        with self.page.expect_response(
            lambda r: is_tracked(r) and PaymentLocators.PLACE_ORDER_REQUEST in r.url,
            timeout=timeout_ms,
        ) as info:
            self.confirm_order()
        response = info.value
        try:
            body = response.text().strip()
        except PlaywrightError:
            body = None
        return {
            "path": urlsplit(response.url).path,
            "status": response.status,
            "body": body,
        }

    def confirmation_responses(self) -> list[dict]:
        """Respuestas POST `{path, status}` registradas desde
        `confirm_order_tracked`; deja de registrar al leerlas."""
        listener = getattr(self, "_confirmation_listener", None)
        if listener is not None:
            self.page.remove_listener("response", listener)
            self._confirmation_listener = None
        return list(getattr(self, "_confirmation_log", []))
