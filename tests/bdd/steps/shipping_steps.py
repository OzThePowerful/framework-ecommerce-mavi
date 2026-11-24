"""Steps BDD del contrato común de Shipping (test_cases/common/shipping/).

El retiro en sucursal: toggle, store picker (estado → tienda →
'Entregar aquí') y contacto de recolección. Se elige la primera tienda
visible del estado del dataset. Sin locators ni Playwright.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


@when("selecciona la entrega en sucursal")
def select_store_pickup(checkout_ctx) -> None:
    checkout_ctx["checkout"].select_delivery_method("sucursal")


@when("elige una tienda del estado del dataset")
def pick_store_from_dataset_state(checkout_ctx, data_provider) -> None:
    checkout = checkout_ctx["checkout"]
    state = data_provider.get_record("checkout", "guest")["store_state"]
    checkout.open_store_picker()
    checkout.select_picker_state(state)
    stores = checkout.stores()
    assert stores, f"Sin sucursales visibles para el estado {state!r}"
    checkout_ctx["selected_store"] = stores[0]
    checkout.select_store(stores[0])


@when("captura el contacto de recolección del comprador")
def fill_pickup_contact(checkout_ctx) -> None:
    customer = checkout_ctx["expected_customer"]
    checkout_ctx["checkout"].fill_pickup_contact(
        firstname=customer.name,
        father_name=customer.last_name,
        mother_name=customer.mothers_name,
        phone=customer.phone,
    )


@then("el modo de entrega queda en sucursal con tienda seleccionada")
def pickup_mode_and_store_active(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    mode = checkout.current_delivery_mode()
    assert mode == "sucursal", (
        f"Modo de entrega activo {mode!r} != 'sucursal'"
    )
    attach_text(
        "Shipping pickup",
        json.dumps(
            {
                "mode": mode,
                "store": checkout_ctx["selected_store"],
            },
            ensure_ascii=False,
        ),
    )
