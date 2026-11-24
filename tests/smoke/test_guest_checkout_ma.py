"""E2E UI Muebles América: Home → categoría → PDP → carrito → checkout como
invitado.

El flujo lo coordina GuestCheckoutWorkflow; los datos salen del dataset
`guest_checkout` vía DataProvider; la URL, de config/sites.yaml vía
ExecutionContext. El test solo valida el resultado.
"""

import pytest

from workflows.common.guest_checkout_workflow import (
    GuestCheckoutRequest,
    GuestCheckoutWorkflow,
)

pytestmark = pytest.mark.smoke


@pytest.fixture
def guest_checkout_request(data_provider) -> GuestCheckoutRequest:
    record = data_provider.get_record("guest_checkout", "linea_blanca")
    return GuestCheckoutRequest.from_record(record)


def test_guest_checkout_muestra_precio(pages, execution_context, guest_checkout_request):
    price = GuestCheckoutWorkflow(pages, execution_context).run(guest_checkout_request)

    assert price.amount > 0, (
        f"El checkout debería mostrar un precio mayor a cero; se obtuvo {price}"
    )
