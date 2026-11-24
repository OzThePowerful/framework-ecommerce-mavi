"""Steps BDD del contrato común de Order (confirmación de orden).

Reutiliza toda la cadena de steps previos; aquí viven la ejecución de
'Finalizar compra' (acción irreversible autorizada en stage), la
detección de éxito inequívoco, la captura del folio y la consistencia
comercial Order vs Product/Cart/Shipping/total/pago.
Sin locators ni Playwright.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


@when("confirma la compra", target_fixture="order_ctx")
def confirm_purchase(checkout_ctx, pages) -> dict:
    payment = checkout_ctx["payment"]
    payment.confirm_order()
    order_page = pages.order()
    order_page.wait_success()
    order = order_page.read_order(
        payment_method=checkout_ctx.get("expected_payment_method")
    )
    return {"order": order, "order_page": order_page}


@then("se genera una orden con folio y mensaje de confirmación")
def order_has_folio(order_ctx) -> None:
    order_page = order_ctx["order_page"]
    order = order_ctx["order"]

    assert order_page.is_success(), (
        "La página posterior a confirmar no es de éxito inequívoco"
    )
    assert order.folio and order.folio.isdigit(), (
        f"Folio inválido: {order.folio!r}"
    )
    message = (order.confirmation_message or "").lower()
    assert "pedido" in message or "compra" in message, (
        f"Sin mensaje de confirmación: {message!r}"
    )

    attach_text(
        "Order",
        json.dumps(
            {
                "folio": order.folio,
                "payment_method": order.payment_method,
                "confirmation": order.confirmation_message,
            },
            ensure_ascii=False,
        ),
    )


@when("captura el resumen comercial previo a confirmar")
def capture_summary(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    checkout_ctx["summary"] = checkout.summary_totals()
    checkout_ctx["shipping_obj"] = checkout.shipping()


@then("la orden es consistente con producto, carrito, envío, total y pago")
def order_is_consistent(order_ctx, checkout_ctx, cart_ctx) -> None:
    order = order_ctx["order"]
    cart = cart_ctx["cart"]
    expected_product = cart_ctx["expected"]
    shipping = checkout_ctx["shipping_obj"]
    summary = checkout_ctx["summary"]

    assert order.folio and order.folio.isdigit(), (
        f"Folio inválido: {order.folio!r}"
    )
    assert not cart.is_empty, "El carrito del flujo estaba vacío"

    item = cart.items[0]
    assert item.product.sku == expected_product.sku, (
        f"SKU carrito {item.product.sku!r} != PDP {expected_product.sku!r}"
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
    assert order.payment_method == checkout_ctx["expected_payment_method"], (
        f"Método orden {order.payment_method!r} != "
        f"{checkout_ctx['expected_payment_method']!r}"
    )

    attach_text(
        "Order consistency",
        json.dumps(
            {
                "folio": order.folio,
                "sku": item.product.sku,
                "subtotal": str(summary["subtotal"].amount),
                "shipping": str(summary["shipping"].amount),
                "total": str(summary["total"].amount),
                "payment_method": order.payment_method,
            },
            ensure_ascii=False,
        ),
    )
