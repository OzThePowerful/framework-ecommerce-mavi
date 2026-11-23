"""Steps BDD del contrato común de Payment (contado).

Reutiliza la cadena de steps de home/search/PDP/cart/checkout; aquí
viven la apertura de la etapa de pago, la selección del método de
contado con la tarjeta de prueba de las env vars y la validación de
la última frontera permitida: 'Finalizar compra' habilitado.
Sin locators ni Playwright; nunca se confirma la orden.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


@when("abre la etapa de forma de pago")
def open_payment_stage(checkout_ctx, pages) -> None:
    checkout = checkout_ctx["checkout"]
    checkout.wait_payment_stage_enabled()
    payment = pages.payment()
    payment.open_payment_stage()
    checkout_ctx["payment"] = payment


@when(
    "selecciona el método de contado del dataset y completa la tarjeta de prueba"
)
def select_contado_and_fill_card(
    checkout_ctx, data_provider, payment_card
) -> None:
    params = data_provider.get_record("checkout", "guest")
    method = params["payment_method"]
    payment = checkout_ctx["payment"]

    errors = payment.validation_errors()
    assert not errors, f"Errores previos de validación: {errors}"

    payment.select_method(method)
    payment.fill_card(
        number=payment_card["number"],
        exp_month=payment_card["exp_month"],
        exp_year=payment_card["exp_year"],
        cvv=payment_card["cvv"],
    )
    checkout_ctx["expected_payment_method"] = method


@then("el método de contado queda seleccionado y la orden lista para confirmar")
def order_ready_to_confirm(checkout_ctx) -> None:
    payment = checkout_ctx["payment"]
    expected = checkout_ctx["expected_payment_method"]

    selected = payment.selected_method()
    assert selected == expected, (
        f"Método seleccionado {selected!r} != esperado {expected!r}"
    )

    errors = payment.validation_errors()
    assert not errors, f"Errores de validación de pago: {errors}"

    # Frontera del contrato: el botón queda habilitado — NUNCA se clica.
    payment.wait_place_order_enabled()
    assert payment.is_place_order_enabled()

    attach_text(
        "Payment",
        json.dumps(
            {
                "method": selected,
                "external_provider": payment.expects_external_provider(
                    selected
                ),
                "place_order_enabled": payment.is_place_order_enabled(),
                "methods_available": payment.payment_methods(),
            },
            ensure_ascii=False,
        ),
    )
