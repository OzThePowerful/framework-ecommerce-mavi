"""Steps BDD del E2E de venta de contado (test_cases/common/e2e/).

Delega todo el recorrido al SaleCashWorkflow; los steps solo resuelven
los datos (dataset + .env) y exponen la orden leída. Reutiliza el Then
de order_steps al publicar el mismo `order_ctx`. Sin locators.

PRECAUCIÓN: ejecuta 'Finalizar compra' → crea una orden REAL en stage.
"""

import json
from pathlib import Path

from pytest_bdd import given, then, when

from core.reporting.allure_manager import attach_file, attach_text
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
    request = SaleRequest(
        search_term=checkout["search_term"],
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
def run_sale_cash(e2e_ctx, page, pages, evidence_manager, execution_context) -> dict:
    e2e_evidence: list[dict] = []

    def capture_stage(stage: str) -> None:
        checkout = pages.checkout()
        mask = checkout.evidence_mask() if checkout.is_on_checkout() else None
        name = f"{len(e2e_evidence) + 1:02d}_{stage}"
        path = evidence_manager.save_screenshot(page, name, mask=mask)
        attach_file(path, name=f"Etapa {stage}")
        e2e_evidence.append(
            {
                "stage": stage,
                "url": page.url,
                "screenshot": str(path),
                "masked": bool(mask),
            }
        )

    result = SaleCashWorkflow(
        pages, execution_context, on_stage=capture_stage
    ).run(e2e_ctx["request"])
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
        "e2e_evidence": e2e_evidence,
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


# Etapas que emite SaleCashWorkflow vía `on_stage`, en orden.
_WORKFLOW_STAGES = (
    "product", "cart", "guest", "customer_address",
    "shipping", "payment", "summary", "order",
)


@then("la evidencia de la venta de contado está completa")
def sale_evidence_complete(order_ctx, evidence_manager) -> None:
    evidence = order_ctx["e2e_evidence"]
    stages = [entry["stage"] for entry in evidence]
    missing = [
        entry["stage"]
        for entry in evidence
        if not Path(entry["screenshot"]).is_file()
        or not Path(entry["screenshot"]).stat().st_size
    ]
    assert not missing, f"Etapas sin captura en disco: {missing}"
    assert tuple(stages) == _WORKFLOW_STAGES, (
        f"Etapas evidenciadas {stages} != flujo {list(_WORKFLOW_STAGES)}"
    )
    masked = [entry["stage"] for entry in evidence if entry["masked"]]
    assert masked, (
        "Ninguna captura quedó enmascarada (checkout sin evidencia protegida)"
    )
    result = order_ctx["result"]
    summary = {
        "etapas": stages,
        "evidencia": evidence,
        "capturas_enmascaradas": masked,
        "producto": {"sku": result.product.sku, "nombre": result.product.name},
        "folio": result.order.folio if result.order else None,
    }
    content = json.dumps(summary, ensure_ascii=False, indent=2)
    evidence_manager.save_log("e2e_resumen", content)
    attach_text("Evidencia E2E", content)
    assert summary["folio"], "La evidencia no registra el folio de la orden"
