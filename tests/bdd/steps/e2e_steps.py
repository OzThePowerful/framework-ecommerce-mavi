"""Steps BDD del E2E de venta de contado (test_cases/common/e2e/).

Delega todo el recorrido al SaleCashWorkflow; los steps solo resuelven
los datos (dataset + .env) y exponen la orden leída. Reutiliza el Then
de order_steps al publicar el mismo `order_ctx`. Sin locators.

PRECAUCIÓN: ejecuta 'Finalizar compra' → crea una orden REAL en stage.
"""

import json

from pytest_bdd import given, when

from core.reporting.allure_manager import attach_text
from domain.models.address import Address
from workflows.common.sale_cash_workflow import (
    PaymentCard,
    SaleCashWorkflow,
    SaleRequest,
)


@given(
    "el usuario prepara una venta de contado con datos de prueba",
    target_fixture="e2e_ctx",
)
def prepare_sale_request(data_provider, guest_customer, payment_card) -> dict:
    checkout = data_provider.get_record("checkout", "guest")
    address = data_provider.get_record("addresses", checkout["address"])
    search = data_provider.get_record("search", "with_results")
    request = SaleRequest(
        search_term=search["term"],
        customer=guest_customer,
        address=Address(
            street=address["street"],
            exterior_number=address.get("exterior_number"),
            interior_number=address.get("interior_number"),
            neighborhood=address.get("neighborhood"),
            zip_code=address["zip_code"],
            city=address["city"],
            state=address["state"],
            references=address.get("references"),
        ),
        shipping_method=checkout["shipping_method"],
        payment_method=checkout["payment_method"],
        card=PaymentCard.from_record(payment_card),
        confirm_order=True,
    )
    return {"request": request}


@when("ejecuta el flujo completo de venta de contado", target_fixture="order_ctx")
def run_sale_cash(e2e_ctx, pages, execution_context) -> dict:
    result = SaleCashWorkflow(pages, execution_context).run(e2e_ctx["request"])
    attach_text(
        "SaleCashWorkflow",
        json.dumps(
            {
                "sku": result.product.sku,
                "total": str(result.summary["total"].amount),
                "shipping": str(result.shipping.cost.amount),
            },
            ensure_ascii=False,
        ),
    )
    return {"order": result.order, "order_page": pages.order()}
