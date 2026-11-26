"""Steps BDD de Checkout exclusivos de Muebles América
(test_cases/muebles_america/checkout/ — CP_EC_MA_CHECKOUT_001 / _002).

CHECKOUT_001: pasos 4 y 5 del contrato. CHECKOUT_002: pasos 1–7, campo
por campo. Las precondiciones reutilizan los steps de PDP/Cart de MA y
los comunes `continúa al checkout desde el carrito` / `continúa como
invitado`. Textos distintos a los de la rama VIU (MA-AISLAMIENTO-001).
Sin locators ni Playwright. Correo y teléfono del comprador (privados,
.env) se adjuntan enmascarados.
"""

import json

import pytest
from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text
from domain.models.address import Address

_ABSENT = "ausente"
# `name` de los campos del comprador en el OSC.
_FIELD = {
    "name": "firstname",
    "last_name": "lastname",
    "mothers_name": "custom_attributes[address_mothers_name]",
    "email": "username",
    "phone": "telephone",
    "street": "street[0]",
    "exterior_number": "custom_attributes[address_number]",
    "zip_code": "postcode",
}


def _mask_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return email and "***"
    user, domain = email.split("@", 1)
    return f"{user[:1]}***@{domain[:1]}***"


def _mask_phone(phone: str | None) -> str | None:
    return phone and "*" * max(len(phone) - 4, 0) + phone[-4:]


def _casefold(text: str | None) -> str:
    return " ".join((text or "").split()).casefold()


@pytest.fixture
def checkout_entry(data_provider) -> dict:
    return data_provider.get_record("checkout", "entry")


# Paso 4 — primera etapa cargada.
@then("la primera etapa del checkout queda cargada")
def first_checkout_stage_loaded(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    stage = checkout.current_stage()
    on_checkout = checkout.is_on_checkout()
    payment_enabled = checkout.is_payment_stage_enabled()
    attach_text(
        "Checkout inicial",
        json.dumps(
            {
                "url": checkout.page.url,
                "on_checkout": on_checkout,
                "stage": stage,
                "payment_stage_enabled": payment_enabled,
            },
            ensure_ascii=False,
        ),
    )
    assert on_checkout, (
        f"La URL {checkout.page.url!r} no corresponde al checkout de la marca"
    )
    assert stage == "entrega", f"Etapa activa esperada 'entrega'; actual {stage!r}"
    assert not payment_enabled, (
        "La etapa 'Forma de pago' no debería estar habilitada al iniciar el checkout"
    )


# Paso 5 — controles requeridos disponibles.
@then("los campos requeridos del comprador están disponibles para capturarse")
def required_fields_available(checkout_ctx, checkout_entry) -> None:
    checkout = checkout_ctx["checkout"]
    expected = list(checkout_entry["required_fields"])
    required = checkout.required_fields()
    unavailable = checkout.unavailable_fields(expected)
    attach_text(
        "Campos requeridos",
        json.dumps(
            {"esperados": expected, "requeridos_en_pantalla": required,
             "no_disponibles": unavailable},
            ensure_ascii=False,
        ),
    )
    missing = [name for name in expected if name not in required]
    assert not missing, f"Campos no marcados como obligatorios: {missing}"
    assert not unavailable, (
        f"Campos requeridos que no se pueden capturar: {unavailable}"
    )


# --- CP_EC_MA_CHECKOUT_002 --------------------------------------------------
def _capture_and_check(checkout_ctx, key: str, value: str) -> None:
    """Assert común de los pasos 2–5: el campo conserva el valor y no
    muestra error de validación."""
    checkout = checkout_ctx["checkout"]
    name = _FIELD[key]
    observed = checkout.field_value(name)
    error = checkout.field_error(name)
    assert observed == value, (
        f"El campo {name!r} no conservó el valor capturado"
    )
    assert error is None, f"El campo {name!r} muestra un error: {error!r}"


# Paso 1 — datos del comprador desde el DataProvider.
@when("obtiene los datos del comprador del dataset")
def get_customer_data(checkout_ctx, data_provider, guest_customer) -> None:
    params = data_provider.get_record("checkout", "guest")
    data = data_provider.get_record("addresses", params["address"])
    checkout_ctx["customer"] = guest_customer
    checkout_ctx["address"] = Address(
        street=data["street"],
        exterior_number=data.get("exterior_number"),
        interior_number=data.get("interior_number"),
        neighborhood=data.get("neighborhood"),
        zip_code=data["zip_code"],
        city=data["city"],
        state=data["state"],
        references=data.get("references"),
    )


@then("los datos del comprador están disponibles")
def customer_data_available(checkout_ctx) -> None:
    customer = checkout_ctx["customer"]
    address = checkout_ctx["address"]
    attach_text(
        "Datos del comprador",
        json.dumps(
            {
                "nombre": customer.name,
                "apellido": customer.last_name,
                "apellido_materno": customer.mothers_name or _ABSENT,
                "correo": _mask_email(customer.email),
                "telefono": _mask_phone(customer.phone),
                "cp": address.zip_code,
                "ciudad": address.city,
            },
            ensure_ascii=False,
        ),
    )
    for label, value in (
        ("nombre", customer.name),
        ("apellido", customer.last_name),
        ("correo", customer.email),
        ("teléfono", customer.phone),
        ("calle", address.street),
        ("CP", address.zip_code),
    ):
        assert value, f"El dataset del comprador no trae {label}"


# Paso 2 — nombre.
@when("captura el nombre del comprador")
def capture_name(checkout_ctx) -> None:
    checkout_ctx["checkout"].capture_field(
        _FIELD["name"], checkout_ctx["customer"].name
    )


@then("el nombre queda válido")
def name_valid(checkout_ctx) -> None:
    _capture_and_check(checkout_ctx, "name", checkout_ctx["customer"].name)


# Paso 3 — apellidos (paterno; materno si el dataset lo trae).
@when("captura los apellidos del comprador")
def capture_last_names(checkout_ctx) -> None:
    customer = checkout_ctx["customer"]
    checkout = checkout_ctx["checkout"]
    checkout.capture_field(_FIELD["last_name"], customer.last_name)
    if customer.mothers_name:
        checkout.capture_field(_FIELD["mothers_name"], customer.mothers_name)


@then("los apellidos quedan válidos")
def last_names_valid(checkout_ctx) -> None:
    customer = checkout_ctx["customer"]
    _capture_and_check(checkout_ctx, "last_name", customer.last_name)
    attach_text(
        "Apellidos",
        json.dumps(
            {"paterno": "capturado",
             "materno": "capturado" if customer.mothers_name else _ABSENT},
            ensure_ascii=False,
        ),
    )
    if customer.mothers_name:
        _capture_and_check(checkout_ctx, "mothers_name", customer.mothers_name)


# Paso 4 — correo.
@when("captura el correo del comprador")
def capture_email(checkout_ctx) -> None:
    checkout_ctx["checkout"].capture_field(
        _FIELD["email"], checkout_ctx["customer"].email
    )


@then("el correo queda aceptado")
def email_accepted(checkout_ctx) -> None:
    _capture_and_check(checkout_ctx, "email", checkout_ctx["customer"].email)


# Paso 5 — teléfono.
@when("captura el teléfono del comprador")
def capture_phone(checkout_ctx) -> None:
    checkout_ctx["checkout"].capture_field(
        _FIELD["phone"], checkout_ctx["customer"].phone
    )


@then("el teléfono queda aceptado")
def phone_accepted(checkout_ctx) -> None:
    _capture_and_check(checkout_ctx, "phone", checkout_ctx["customer"].phone)


# Paso 6 — demás campos obligatorios (dirección + autocompletado por CP).
@when("completa los demás campos obligatorios del dataset")
def complete_other_required(checkout_ctx) -> None:
    checkout_ctx["checkout"].fill_address(checkout_ctx["address"])


@then("los datos de dirección quedan aceptados")
def address_accepted(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    expected = checkout_ctx["address"]
    saved = checkout.read_address()
    attach_text(
        "Dirección capturada",
        json.dumps(
            {
                "calle": saved.street,
                "numero": saved.exterior_number,
                "cp": saved.zip_code,
                "colonia": saved.neighborhood,
                "ciudad": saved.city,
                "estado": saved.state,
            },
            ensure_ascii=False,
        ),
    )
    assert saved.street == expected.street, "La calle no conservó el valor capturado"
    assert saved.exterior_number == expected.exterior_number, (
        "El número exterior no conservó el valor capturado"
    )
    assert saved.zip_code == expected.zip_code, "El CP no conservó el valor capturado"
    assert saved.neighborhood, "El CP no autocompletó la colonia"
    assert saved.city, "El CP no autocompletó la ciudad"
    assert _casefold(saved.city) == _casefold(expected.city), (
        f"Ciudad autocompletada {saved.city!r} != dataset {expected.city!r}"
    )
    assert _casefold(saved.state) == _casefold(expected.state), (
        f"Estado {saved.state!r} != dataset {expected.state!r}"
    )
    for key in ("street", "exterior_number", "zip_code"):
        error = checkout.field_error(_FIELD[key])
        assert error is None, f"El campo {_FIELD[key]!r} muestra un error: {error!r}"


# Paso 7 — continuar sin validaciones pendientes.
@when("continúa a la forma de pago")
def continue_to_payment(checkout_ctx) -> None:
    checkout_ctx["checkout"].continue_to_payment()


@then("no quedan validaciones pendientes del comprador")
def no_pending_customer_validations(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    expected = checkout_ctx["customer"]
    errors = checkout.validation_errors()
    invalid = checkout.invalid_fields()
    stage = checkout.current_stage()
    saved = checkout.read_customer()
    attach_text(
        "Comprador aceptado",
        json.dumps(
            {
                "etapa": stage,
                "errores": errors,
                "campos_invalidos": invalid,
                "correo": _mask_email(saved.email),
                "telefono": _mask_phone(saved.phone),
            },
            ensure_ascii=False,
        ),
    )
    assert not errors, f"Errores de validación visibles: {errors}"
    assert not invalid, f"Campos marcados como inválidos: {invalid}"
    assert stage == "forma_de_pago", (
        f"El checkout no continuó a 'forma_de_pago'; etapa activa {stage!r}"
    )
    for field in ("name", "last_name", "email", "phone"):
        assert getattr(saved, field) == getattr(expected, field), (
            f"El dato {field!r} del comprador cambió al continuar"
        )
