"""Steps BDD del contrato común de Checkout/Customer.

Reutiliza los steps de home/search/PDP/cart ya registrados; aquí viven
la entrada como invitado, el llenado del formulario del comprador desde
el DataProvider y las validaciones de etapa. Sin locators ni Playwright.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text
from domain.models.address import Address


@when("continúa como invitado", target_fixture="checkout_ctx")
def continue_as_guest(pages) -> dict:
    checkout = pages.checkout()
    checkout.wait_for_guest_gate()
    checkout.continue_as_guest()
    checkout.wait_until_ready()
    return {"checkout": checkout}


@then("el acceso como invitado está disponible")
def guest_gate_available(pages) -> None:
    checkout = pages.checkout()
    checkout.wait_for_guest_gate()
    assert checkout.is_guest_gate_visible(), (
        "El gate 'Continuar como invitado' no se mostró tras continuar"
    )


@when("registra los datos del comprador del dataset")
def fill_customer_form(checkout_ctx, data_provider, guest_customer) -> None:
    params = data_provider.get_record("checkout", "guest")
    address_data = data_provider.get_record("addresses", params["address"])
    customer = guest_customer
    address = Address(
        street=address_data["street"],
        exterior_number=address_data.get("exterior_number"),
        interior_number=address_data.get("interior_number"),
        neighborhood=address_data.get("neighborhood"),
        zip_code=address_data["zip_code"],
        city=address_data["city"],
        state=address_data["state"],
        references=address_data.get("references"),
    )
    checkout_ctx["expected_customer"] = customer
    checkout_ctx["expected_address"] = address
    checkout_ctx["checkout"].fill_customer_form(customer, address)


@then("la etapa de entrega está activa y los campos del comprador son obligatorios")
def shipping_stage_and_required_fields(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    stage = checkout.current_stage()
    assert stage == "entrega", f"Etapa activa esperada 'entrega'; actual {stage!r}"
    required = checkout.required_fields()
    expected = {
        "username",
        "firstname",
        "lastname",
        "telephone",
        "street[0]",
        "custom_attributes[address_number]",
        "postcode",
    }
    missing = expected - set(required)
    assert not missing, f"Campos obligatorios no presentes: {missing}"
    attach_text(
        "Checkout stage",
        json.dumps(
            {"stage": stage, "required_fields": required},
            ensure_ascii=False,
        ),
    )


@when("selecciona el método de entrega del dataset")
def select_delivery_method(checkout_ctx, data_provider) -> None:
    params = data_provider.get_record("checkout", "guest")
    method = params["shipping_method"]
    checkout_ctx["expected_method"] = method
    checkout_ctx["checkout"].select_delivery_method(method)


@then("los datos quedan aceptados y la etapa de pago queda habilitada")
def customer_data_accepted(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    expected = checkout_ctx["expected_customer"]
    saved = checkout.read_customer()
    assert saved.email == expected.email, (
        f"Email leído {saved.email!r} != dataset {expected.email!r}"
    )
    assert saved.name == expected.name, (
        f"Nombre leído {saved.name!r} != dataset {expected.name!r}"
    )
    assert saved.last_name == expected.last_name, (
        f"Apellido leído {saved.last_name!r} != dataset {expected.last_name!r}"
    )
    errors = checkout.validation_errors()
    assert not errors, f"Errores de validación visibles: {errors}"
    checkout.wait_payment_stage_enabled()
    assert checkout.is_payment_stage_enabled(), (
        "La etapa 'Forma de pago' no quedó habilitada tras registrar el comprador"
    )
    saved_address = checkout.read_address()
    expected_address = checkout_ctx["expected_address"]
    assert saved_address.zip_code == expected_address.zip_code
    attach_text(
        "Customer registrado",
        json.dumps(
            {
                "email": saved.email,
                "nombre": f"{saved.name} {saved.last_name}",
                "telefono": saved.phone,
                "cp": saved_address.zip_code,
                "colonia": saved_address.neighborhood,
                "ciudad": saved_address.city,
                "estado": saved_address.state,
                "payment_stage_enabled": checkout.is_payment_stage_enabled(),
            },
            ensure_ascii=False,
        ),
    )


@then("el método de entrega queda activo y el costo de envío está disponible")
def delivery_method_and_cost(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    expected = checkout_ctx["expected_method"]
    mode = checkout.current_delivery_mode()
    assert mode == expected, (
        f"Modo de entrega activo {mode!r} != dataset {expected!r}"
    )
    shipping = checkout.shipping()
    assert shipping.method == expected, (
        f"Método de Shipping {shipping.method!r} != esperado {expected!r}"
    )
    assert shipping.cost.amount >= 0, (
        f"El costo de envío debería ser un importe >= 0: {shipping.cost.amount}"
    )
    checkout.wait_payment_stage_enabled()
    attach_text(
        "Shipping",
        json.dumps(
            {
                "method": shipping.method,
                "cost": str(shipping.cost.amount),
                "estimate": checkout.delivery_estimate(),
                "payment_stage_enabled": checkout.is_payment_stage_enabled(),
            },
            ensure_ascii=False,
        ),
    )
