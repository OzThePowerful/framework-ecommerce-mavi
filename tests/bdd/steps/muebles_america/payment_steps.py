"""Steps BDD de Payment exclusivos de Muebles América
(test_cases/muebles_america/payment/ — CP_EC_MA_PAY_001).

Pasos 1–6 del contrato, cada acción con su verificación. Las
precondiciones reutilizan los steps de PDP/Cart/Checkout de MA y los
comunes de captura del comprador y de entrega. Contado = dataset
`payment`/`card` (método, nombre visible y proveedor). Textos distintos a
los de la rama VIU (MA-AISLAMIENTO-001). Sin locators ni Playwright.
Frontera: 'Finalizar compra' habilitado — nunca se pulsa.
"""

import json

import pytest
from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


def _casefold(text: str | None) -> str:
    return " ".join((text or "").split()).casefold()


def _mask_card(number: str | None) -> str | None:
    return number and "*" * max(len(number) - 4, 0) + number[-4:]


@pytest.fixture
def cash_method(data_provider) -> dict:
    """Forma de pago de contado: `checkout`/`guest.payment_method` +
    nombre visible y proveedor de `payment`/`card`."""
    record = data_provider.get_record("payment", "card")
    method = data_provider.get_record("checkout", "guest")["payment_method"]
    assert record["method"] == method, (
        f"payment.card.method {record['method']!r} != "
        f"checkout.guest.payment_method {method!r}"
    )
    return {"value": method, "label": record["label"], "provider": record["provider"]}


# Paso 1 — llegar a la etapa de pago.
@when("llega a la etapa de pago del checkout")
def reach_payment_stage(checkout_ctx, pages) -> None:
    checkout_ctx["checkout"].continue_to_payment()
    checkout_ctx["payment"] = pages.payment()


@then("la etapa de pago está disponible")
def payment_stage_available(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    payment = checkout_ctx["payment"]
    stage = checkout.current_stage()
    methods = payment.payment_methods()
    errors = checkout.validation_errors()
    label = payment.place_order_label()
    enabled = payment.is_place_order_enabled()
    attach_text(
        "Etapa de pago",
        json.dumps(
            {"etapa": stage, "metodos_presentes": methods, "errores": errors,
             "boton": label, "boton_habilitado": enabled},
            ensure_ascii=False,
        ),
    )
    assert stage == "forma_de_pago", (
        f"La etapa activa debería ser 'forma_de_pago'; actual {stage!r}"
    )
    assert methods, "La etapa de pago no presenta métodos de pago"
    assert not errors, f"Errores de validación visibles: {errors}"
    # El estado del botón al abrir es transitorio (KO): solo se adjunta; se
    # verifica deshabilitado en el paso 2, con la etapa ya estabilizada.


# Paso 2 — consultar métodos disponibles.
@when("consulta los métodos de pago disponibles")
def query_payment_methods(checkout_ctx) -> None:
    checkout_ctx["payment_options"] = checkout_ctx["payment"].payment_options()


@then("se muestran las opciones de pago habilitadas")
def payment_options_enabled(checkout_ctx) -> None:
    payment = checkout_ctx["payment"]
    options = checkout_ctx["payment_options"]
    selected = payment.selected_method()
    label = payment.place_order_label()
    place_order_enabled = payment.is_place_order_enabled()
    attach_text(
        "Métodos de pago",
        json.dumps(
            {"opciones": options, "seleccionado": selected, "boton": label,
             "boton_habilitado": place_order_enabled},
            ensure_ascii=False,
        ),
    )
    enabled = [option for option in options if option["enabled"]]
    assert enabled, f"Ningún método de pago está habilitado: {options}"
    unnamed = [option["value"] for option in enabled if not option["label"]]
    assert not unnamed, f"Métodos habilitados sin nombre visible: {unnamed}"
    assert selected is None, f"Ya hay un método preseleccionado: {selected!r}"
    assert not place_order_enabled, (
        f"El botón {label!r} no debería estar habilitado sin método de pago"
    )


# Paso 3 — identificar la forma de pago de contado.
@when("identifica la forma de pago de contado del dataset")
def identify_cash_method(checkout_ctx, cash_method) -> None:
    checkout_ctx["cash_method"] = cash_method
    checkout_ctx["cash_option"] = next(
        (o for o in checkout_ctx["payment_options"] if o["value"] == cash_method["value"]),
        None,
    )


@then("el método de contado se encuentra entre las opciones")
def cash_method_found(checkout_ctx) -> None:
    expected = checkout_ctx["cash_method"]
    option = checkout_ctx["cash_option"]
    options = checkout_ctx["payment_options"]
    attach_text(
        "Forma de pago de contado",
        json.dumps({"dataset": expected, "encontrado": option}, ensure_ascii=False),
    )
    assert option is not None, (
        f"El método de contado {expected['value']!r} no está entre las opciones: "
        f"{[o['value'] for o in options]}"
    )
    assert _casefold(option["label"]) == _casefold(expected["label"]), (
        f"El método {expected['value']!r} se muestra como {option['label']!r}; "
        f"dataset {expected['label']!r}"
    )
    assert option["enabled"], f"El método de contado {option['label']!r} está deshabilitado"


# Paso 4 — seleccionar el método.
@when("selecciona la forma de pago de contado")
def select_cash_method(checkout_ctx) -> None:
    checkout_ctx["payment"].select_method(checkout_ctx["cash_method"]["value"])
    # Steps comunes posteriores (ORDER/E2E) leen esta clave.
    checkout_ctx["expected_payment_method"] = checkout_ctx["cash_method"]["value"]


@then("la forma de pago de contado queda marcada como activa")
def cash_method_active(checkout_ctx) -> None:
    payment = checkout_ctx["payment"]
    expected = checkout_ctx["cash_method"]
    selected = payment.selected_method()
    active = payment.active_method()
    label = payment.place_order_label()
    attach_text(
        "Método activo",
        json.dumps(
            {"seleccionado": selected, "contenedor_activo": active, "boton": label},
            ensure_ascii=False,
        ),
    )
    assert selected == expected["value"], (
        f"Método seleccionado {selected!r} != contado {expected['value']!r}"
    )
    assert active == expected["value"], (
        f"El método marcado como activo es {active!r}; esperado {expected['value']!r}"
    )
    assert _casefold(expected["label"]) in _casefold(label), (
        f"El botón {label!r} no refleja el método activo {expected['label']!r}"
    )


# Paso 5 — completar los datos permitidos (tarjeta de prueba).
@when("completa los datos permitidos del método de contado")
def fill_cash_method_data(checkout_ctx, payment_card) -> None:
    checkout_ctx["payment"].fill_card(
        number=payment_card["number"],
        exp_month=payment_card["exp_month"],
        exp_year=payment_card["exp_year"],
        cvv=payment_card["cvv"],
    )


@then("la información del método de contado queda aceptada")
def cash_method_data_accepted(checkout_ctx, payment_card) -> None:
    payment = checkout_ctx["payment"]
    values = payment.card_values()
    errors = payment.validation_errors()
    billing_same = payment.is_billing_same_as_shipping()
    attach_text(
        "Datos de pago",
        json.dumps(
            {
                "tarjeta": _mask_card(values["number"]),
                "vencimiento": f"{values['exp_month']}/{values['exp_year']}",
                "cvv": "***" if values["cvv"] else None,
                "facturacion_igual_a_entrega": billing_same,
                "errores": errors,
            },
            ensure_ascii=False,
        ),
    )
    for field in ("number", "exp_month", "exp_year", "cvv"):
        assert values[field] == payment_card[field], (
            f"El campo de tarjeta {field!r} no conservó el valor capturado"
        )
    assert not errors, f"Errores de validación del pago: {errors}"
    assert billing_same, "La facturación no quedó asociada a la dirección de entrega"


# Paso 6 — revisar el resumen: compra lista para finalizar, sin confirmar.
@when("revisa el resumen antes de la confirmación")
def review_summary(checkout_ctx) -> None:
    checkout_ctx["summary"] = checkout_ctx["checkout"].summary_totals()


@then("la compra queda lista para finalizar sin confirmarse")
def purchase_ready_to_finish(checkout_ctx, pdp_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    payment = checkout_ctx["payment"]
    summary = checkout_ctx["summary"]
    expected_method = checkout_ctx["cash_method"]["value"]
    product_price = pdp_ctx["product"].effective_price
    # Frontera del contrato: el botón queda habilitado — NUNCA se pulsa.
    payment.wait_place_order_enabled()
    enabled = payment.is_place_order_enabled()
    selected = payment.selected_method()
    errors = payment.validation_errors()
    on_checkout = checkout.is_on_checkout()
    attach_text(
        "Resumen antes de confirmar",
        json.dumps(
            {
                **{key: str(value.amount) for key, value in summary.items()},
                "precio_pdp": str(product_price.amount),
                "metodo": selected,
                "boton": payment.place_order_label(),
                "boton_habilitado": enabled,
                "en_checkout": on_checkout,
            },
            ensure_ascii=False,
        ),
    )
    assert summary["subtotal"] == product_price, (
        f"Subtotal del resumen {summary['subtotal'].amount} != precio de la PDP "
        f"{product_price.amount} (cantidad 1)"
    )
    assert summary["total"] == summary["subtotal"] + summary["shipping"], (
        f"Total {summary['total'].amount} != subtotal {summary['subtotal'].amount} "
        f"+ envío {summary['shipping'].amount}"
    )
    assert summary["total"].amount > 0, "El total de la compra debería ser mayor a cero"
    assert selected == expected_method, (
        f"El método de pago cambió antes de confirmar: {selected!r}"
    )
    assert not errors, f"Errores de validación visibles: {errors}"
    assert enabled, "El botón de confirmación no quedó habilitado"
    assert on_checkout, (
        f"La compra salió del checkout antes de confirmarse: {checkout.page.url!r}"
    )
