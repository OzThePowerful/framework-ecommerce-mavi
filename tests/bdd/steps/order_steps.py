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
from domain.money.money import Money


def _serializable(value):
    if isinstance(value, Money):
        return str(value.amount)
    if isinstance(value, dict):
        return {k: _serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serializable(v) for v in value]
    return value


def _event_view(event: dict) -> dict:
    """Proyección comercial de un evento purchase normalizado — para
    verificar que los eventos duplicados declaran lo mismo.

    `list_price` se excluye: es auxiliar y un evento puede omitirlo mientras
    el duplicado lo declara (verificado en VIU, orden 12000050543) — no es
    una incoherencia comercial.
    """
    return {
        "items": [
            {k: v for k, v in item.items() if k != "list_price"}
            for item in _serializable(event["items"])
        ],
        "subtotal": _serializable(event["subtotal"]),
        "shipping": _serializable(event["shipping"]),
        "total": _serializable(event["total"]),
    }


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


@then("el total del resumen está disponible")
def summary_total_available(checkout_ctx) -> None:
    summary = checkout_ctx["summary"]
    assert summary["total"].amount > 0, (
        f"Total del resumen no disponible: {summary['total'].amount}"
    )
    attach_text(
        "Resumen pre-confirmación",
        json.dumps(
            {
                "subtotal": str(summary["subtotal"].amount),
                "shipping": str(summary["shipping"].amount),
                "total": str(summary["total"].amount),
            },
            ensure_ascii=False,
        ),
    )


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
    assert item.quantity == cart_ctx["expected_qty"], (
        f"Cantidad carrito {item.quantity} != esperada {cart_ctx['expected_qty']}"
    )
    assert item.effective_unit_price.amount == expected_product.effective_price.amount, (
        f"Precio unitario carrito {item.effective_unit_price.amount} != "
        f"PDP {expected_product.effective_price.amount}"
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
                "quantity": item.quantity,
                "unit_price": str(item.effective_unit_price.amount),
                "subtotal": str(summary["subtotal"].amount),
                "shipping": str(summary["shipping"].amount),
                "total": str(summary["total"].amount),
                "payment_method": order.payment_method,
            },
            ensure_ascii=False,
        ),
    )


@then("la orden del dataLayer coincide con el flujo")
def datalayer_order_matches_flow(order_ctx, checkout_ctx, cart_ctx) -> None:
    """Orden final desde los eventos `purchase` del dataLayer — fuente
    autoritativa que publica el ecommerce al confirmar."""
    order = order_ctx["order"]
    final = order_ctx["order_page"].final_order(order.folio)
    assert final is not None, (
        f"La página final no publica la orden {order.folio!r} "
        "(eventos purchase del dataLayer)"
    )
    attach_text(
        "Orden final (dataLayer)",
        json.dumps(_serializable(final), ensure_ascii=False),
    )

    views = [_event_view(e) for e in final["events"]]
    incoherent = [v for v in views[1:] if v != views[0]]
    assert not incoherent, (
        f"Los eventos de la orden {order.folio!r} no coinciden entre sí: "
        f"{views[0]} vs {incoherent}"
    )

    expected_product = cart_ctx["expected"]
    summary = checkout_ctx["summary"]
    assert final["items"], f"La orden {order.folio!r} no informa productos"
    item = final["items"][0]
    assert item["sku"] == expected_product.sku, (
        f"SKU orden {item['sku']!r} != PDP {expected_product.sku!r}"
    )
    assert item["qty"] == cart_ctx["expected_qty"], (
        f"Cantidad orden {item['qty']} != esperada {cart_ctx['expected_qty']}"
    )
    assert item["price"] == expected_product.effective_price, (
        f"Precio orden {item['price']} != "
        f"PDP {expected_product.effective_price}"
    )
    assert final["subtotal"] == summary["subtotal"], (
        f"Subtotal orden {final['subtotal']} != resumen {summary['subtotal']}"
    )
    assert final["shipping"] == summary["shipping"], (
        f"Envío orden {final['shipping']} != resumen {summary['shipping']}"
    )
    assert final["total"] == summary["total"], (
        f"Total orden {final['total']} != resumen {summary['total']}"
    )
    assert (final.get("sale_type") or "").strip(), (
        f"La orden {order.folio!r} no declara forma de pago (tipo_pago)"
    )
