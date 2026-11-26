"""Steps BDD de Checkout exclusivos de Muebles América
(test_cases/muebles_america/checkout/ — CP_EC_MA_CHECKOUT_001).

Pasos 4 y 5 del contrato. Los pasos 1–3 y las precondiciones reutilizan
los steps de PDP/Cart de MA y los comunes `continúa al checkout desde el
carrito` / `continúa como invitado`. Textos distintos a los de la rama
VIU (MA-AISLAMIENTO-001). Sin locators ni Playwright.
"""

import json

import pytest
from pytest_bdd import then

from core.reporting.allure_manager import attach_text


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
