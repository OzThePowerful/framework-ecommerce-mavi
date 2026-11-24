"""Steps BDD del smoke de venta de contado (test_cases/common/smoke/).

Delega el recorrido completo al GuestCheckoutWorkflow; el step solo
resuelve el dataset y valida el precio devuelto. Sin locators.
"""

from decimal import Decimal

from pytest_bdd import then, when

from workflows.common.guest_checkout_workflow import (
    GuestCheckoutRequest,
    GuestCheckoutWorkflow,
)


@when(
    "realiza el recorrido de venta de contado hasta el checkout como invitado",
    target_fixture="smoke_ctx",
)
def run_guest_checkout_journey(pages, execution_context, data_provider) -> dict:
    record = data_provider.get_record("guest_checkout", "linea_blanca")
    request = GuestCheckoutRequest.from_record(record)
    price = GuestCheckoutWorkflow(pages, execution_context).run(request)
    return {"price": price}


@then("el checkout muestra el precio del pedido")
def checkout_price_is_positive(smoke_ctx) -> None:
    price = smoke_ctx["price"]
    assert price.amount > Decimal("0"), (
        f"El checkout debería mostrar un precio > 0; mostró {price.amount}"
    )
