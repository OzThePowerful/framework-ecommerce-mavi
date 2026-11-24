"""Steps BDD del E2E de venta de contado (test_cases/common/e2e/).

Delega todo el recorrido al SaleCashWorkflow; los steps solo resuelven
los datos (dataset + .env) y exponen la orden leída. Reutiliza el Then
de order_steps al publicar el mismo `order_ctx`. Sin locators.

PRECAUCIÓN: ejecuta 'Finalizar compra' → crea una orden REAL en stage.
"""

import json

from pytest_bdd import given, then, when

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
    item = result.cart.items[0] if result.cart.items else None
    attach_text(
        "SaleResult snapshot",
        json.dumps(
            {
                "product": result.product.name,
                "sku": result.product.sku,
                "quantity": item.quantity if item else None,
                "unit_price": str(
                    item.effective_unit_price.amount if item else ""
                ),
                "subtotal": str(result.summary["subtotal"].amount),
                "discount": str(result.cart.discount.amount),
                "shipping_method": result.shipping.method,
                "shipping": str(result.shipping.cost.amount),
                "total": str(result.summary["total"].amount),
                "payment_method": result.payment_method,
                "folio": result.order.folio if result.order else None,
            },
            ensure_ascii=False,
        ),
    )
    return {
        "order": result.order,
        "order_page": pages.order(),
        "result": result,
        "request": e2e_ctx["request"],
    }


@then("la integridad comercial del flujo es consistente de extremo a extremo")
def commercial_integrity(order_ctx) -> None:
    """Validaciones obligatorias del contrato E2E sobre el SaleResult."""
    result = order_ctx["result"]
    request = order_ctx["request"]
    cart = result.cart
    summary = result.summary
    shipping = result.shipping

    assert not cart.is_empty, "El carrito del flujo estaba vacío"
    item = cart.items[0]
    assert item.product.sku == result.product.sku, (
        f"SKU carrito {item.product.sku!r} != PDP {result.product.sku!r}"
    )
    assert item.quantity >= 1, f"Cantidad inválida: {item.quantity}"
    assert item.effective_unit_price == result.product.effective_price, (
        f"Precio carrito {item.effective_unit_price.amount} != "
        f"PDP {result.product.effective_price.amount}"
    )
    assert summary["subtotal"] == cart.subtotal, (
        f"Subtotal resumen {summary['subtotal']} != carrito {cart.subtotal}"
    )
    assert summary["shipping"] == shipping.cost, (
        f"Envío resumen {summary['shipping']} != Shipping {shipping.cost}"
    )
    expected_total = cart.subtotal - cart.discount + shipping.cost
    assert summary["total"] == expected_total, (
        f"Total resumen {summary['total']} != esperado {expected_total}"
    )
    assert result.payment_method == request.payment_method, (
        f"Método {result.payment_method!r} != {request.payment_method!r}"
    )
