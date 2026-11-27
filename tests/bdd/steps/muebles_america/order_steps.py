"""Steps BDD de Order exclusivos de Muebles América
(test_cases/muebles_america/order/ — CP_EC_MA_ORDER_001 y _002).

ORDER_001: pasos 1–6 del contrato; ORDER_002: pasos 1–9 (integridad
comercial de la orden final del dataLayer contra Product/Cart/Checkout).
Cada acción lleva su verificación. Las precondiciones reutilizan los
steps de PDP/Cart/Checkout/Payment de MA y los comunes de captura del
comprador y de entrega. Textos distintos a los de la rama VIU
(MA-AISLAMIENTO-001). Sin locators ni Playwright.
PRECAUCIÓN: 'ejecuta la confirmación de la compra' crea una orden REAL.
"""

import json
import re
from decimal import Decimal

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text
from domain.money.money import Money

_ZERO = Money(Decimal("0"))


def _casefold(text: str | None) -> str:
    return " ".join((text or "").split()).casefold()


def _amount(value: Money | None) -> str | None:
    return value and str(value.amount)


# Paso 1 — revisar el resumen final.
@when("revisa el resumen final de la compra")
def review_final_summary(checkout_ctx) -> None:
    checkout = checkout_ctx["checkout"]
    payment = checkout_ctx["payment"]
    checkout_ctx["final_summary"] = {
        "items": checkout.summary_items(),
        "method": payment.selected_method(),
        "button": payment.place_order_label(),
    }


@then("la información de la compra está visible en el resumen")
def purchase_info_visible(checkout_ctx, pdp_ctx) -> None:
    summary = checkout_ctx["final_summary"]
    items = summary["items"]
    product = pdp_ctx["product"]
    cash_method = checkout_ctx["cash_method"]
    attach_text(
        "Resumen final",
        json.dumps(
            {
                "productos": [
                    {**item, "price": item["price"] and str(item["price"].amount)}
                    for item in items
                ],
                "metodo": summary["method"],
                "boton": summary["button"],
            },
            ensure_ascii=False,
        ),
    )
    assert len(items) == 1, f"El resumen debería listar 1 producto; lista {len(items)}"
    item = items[0]
    assert item["sku"] == product.sku, (
        f"SKU del resumen {item['sku']!r} != PDP {product.sku!r}"
    )
    assert _casefold(item["name"]) == _casefold(product.name), (
        f"Nombre del resumen {item['name']!r} != PDP {product.name!r}"
    )
    assert item["qty"] == 1, f"Cantidad del resumen {item['qty']!r}; esperada 1"
    assert item["price"] == product.effective_price, (
        f"Precio del resumen {item['price'] and item['price'].amount} != precio "
        f"de la PDP {product.effective_price.amount}"
    )
    assert item["delivery"], "El resumen no muestra la fecha estimada de entrega"
    assert summary["method"] == cash_method["value"], (
        f"Método seleccionado {summary['method']!r} != contado {cash_method['value']!r}"
    )
    assert _casefold(cash_method["label"]) in _casefold(summary["button"]), (
        f"El botón {summary['button']!r} no muestra el método de contado "
        f"{cash_method['label']!r}"
    )


# Paso 2 — validar el total antes de confirmar.
@when("valida el total antes de confirmar la compra")
def validate_total_before_confirm(checkout_ctx) -> None:
    checkout_ctx["payment"].wait_place_order_enabled()
    checkout_ctx["summary"] = checkout_ctx["checkout"].summary_totals()


@then("el total a pagar está disponible")
def total_to_pay_available(checkout_ctx) -> None:
    summary = checkout_ctx["summary"]
    item = checkout_ctx["final_summary"]["items"][0]
    enabled = checkout_ctx["payment"].is_place_order_enabled()
    attach_text(
        "Total antes de confirmar",
        json.dumps(
            {
                **{key: str(value.amount) for key, value in summary.items()},
                "boton_habilitado": enabled,
            },
            ensure_ascii=False,
        ),
    )
    assert summary["total"].amount > 0, "El total de la compra debería ser mayor a cero"
    assert summary["subtotal"] == item["price"] * item["qty"], (
        f"Subtotal {summary['subtotal'].amount} != precio {item['price'].amount} "
        f"× cantidad {item['qty']}"
    )
    assert summary["total"] == summary["subtotal"] + summary["shipping"], (
        f"Total {summary['total'].amount} != subtotal {summary['subtotal'].amount} "
        f"+ envío {summary['shipping'].amount}"
    )
    assert enabled, "El botón de confirmación no está habilitado"


# Paso 3 — ejecutar la confirmación (ACCIÓN IRREVERSIBLE: crea la orden).
@when("ejecuta la confirmación de la compra")
def execute_purchase_confirmation(checkout_ctx) -> None:
    checkout_ctx["order_request"] = checkout_ctx["payment"].confirm_order_tracked()


@then("la solicitud de compra queda procesada")
def purchase_request_processed(checkout_ctx) -> None:
    request = checkout_ctx["order_request"]
    attach_text("Solicitud de compra", json.dumps(request, ensure_ascii=False))
    assert 200 <= request["status"] < 300, (
        f"La creación de la orden respondió {request['status']} en {request['path']}"
    )
    if request["body"] is not None:
        assert request["body"].strip('"').isdigit(), (
            f"La creación de la orden no devolvió un id de orden: {request['body']!r}"
        )


# Paso 4 — esperar la respuesta.
@when("espera la respuesta de la confirmación")
def wait_confirmation_response(checkout_ctx, pages) -> None:
    order_page = pages.order()
    order_page.wait_success()
    checkout_ctx["order_page"] = order_page
    checkout_ctx["confirmation_responses"] = checkout_ctx["payment"].confirmation_responses()


@then("la confirmación no produce errores inesperados")
def confirmation_without_errors(checkout_ctx) -> None:
    order_page = checkout_ctx["order_page"]
    responses = checkout_ctx["confirmation_responses"]
    decline = order_page.decline_message()
    on_checkout = checkout_ctx["checkout"].is_on_checkout()
    attach_text(
        "Respuesta de la confirmación",
        json.dumps(
            {"peticiones": responses, "rechazo": decline, "en_checkout": on_checkout},
            ensure_ascii=False,
        ),
    )
    failed = [r for r in responses if r["status"] >= 400]
    assert not failed, f"Peticiones de la confirmación con error: {failed}"
    assert decline is None, f"La confirmación mostró un error: {decline!r}"
    assert not on_checkout, "La compra siguió en el checkout tras confirmarse"


# Paso 5 — revisar la página final.
@when("revisa la página final de la compra")
def review_final_page(checkout_ctx) -> None:
    order_page = checkout_ctx["order_page"]
    checkout_ctx["final_page"] = {
        "url": order_page.page.url,
        "encabezado": order_page.success_heading(),
        "mensaje": order_page.confirmation_message(),
    }


@then("se presenta la confirmación de la compra")
def purchase_confirmation_shown(checkout_ctx) -> None:
    order_page = checkout_ctx["order_page"]
    final_page = checkout_ctx["final_page"]
    attach_text("Página final", json.dumps(final_page, ensure_ascii=False))
    assert order_page.is_success(), (
        f"La página final no es de éxito inequívoco: {final_page['url']!r}"
    )
    assert "hemos recibido tu pedido" in _casefold(final_page["encabezado"]), (
        f"La página final no confirma la compra: {final_page['encabezado']!r}"
    )
    message = _casefold(final_page["mensaje"])
    assert "n° de pedido" in message, (
        f"La página final no presenta el número de pedido: {final_page['mensaje']!r}"
    )


# Paso 6 — obtener el número de orden.
@when("obtiene el número de orden de la compra")
def get_order_number(checkout_ctx) -> None:
    checkout_ctx["order"] = checkout_ctx["order_page"].read_order(
        payment_method=checkout_ctx["expected_payment_method"]
    )


@then("el número de orden es un identificador válido")
def order_number_valid(checkout_ctx, pdp_ctx) -> None:
    order = checkout_ctx["order"]
    message = checkout_ctx["final_page"]["mensaje"] or ""
    attach_text(
        "Order",
        json.dumps(
            {
                "folio": order.folio,
                "sku": pdp_ctx["product"].sku,
                "total": str(checkout_ctx["summary"]["total"].amount),
                "payment_method": order.payment_method,
            },
            ensure_ascii=False,
        ),
    )
    assert order.folio and order.folio.isdigit(), f"Folio inválido: {order.folio!r}"
    assert re.search(rf"#\s*{order.folio}\b", message), (
        f"El folio {order.folio!r} no aparece en la confirmación: {message!r}"
    )


# --- CP_EC_MA_ORDER_002 -----------------------------------------------------
def _order_item(checkout_ctx) -> dict:
    return checkout_ctx["final_order"]["items"][0]


def _flow_item(cart_ctx, checkout_ctx):
    """Ítem del carrito y del resumen final (precondición: 1 producto)."""
    return cart_ctx["cart"].items[0], checkout_ctx["final_summary"]["items"][0]


def _amounts(values: dict) -> dict:
    return {key: _amount(value) for key, value in values.items()}


def _event_view(event: dict) -> tuple:
    return (
        event["total"],
        event["shipping"],
        [(item["sku"], item["qty"], item["price"]) for item in event["items"]],
    )


def _serializable(event: dict) -> dict:
    data = {k: (_amount(v) if isinstance(v, Money) else v) for k, v in event.items()}
    data["items"] = [
        {k: (_amount(v) if isinstance(v, Money) else v) for k, v in item.items()}
        for item in event["items"]
    ]
    data.pop("events", None)
    return data


# Paso 1 — obtener la información final de la orden.
@when("obtiene la información final de la orden")
def get_final_order(checkout_ctx) -> None:
    folio = checkout_ctx["order"].folio
    checkout_ctx["final_order"] = checkout_ctx["order_page"].final_order(folio)


@then("la información final de la orden está disponible")
def final_order_available(checkout_ctx) -> None:
    final = checkout_ctx["final_order"]
    folio = checkout_ctx["order"].folio
    assert final is not None, (
        f"La página final no publica la orden {folio!r} (eventos purchase del dataLayer)"
    )
    events = final["events"]
    attach_text(
        "Orden final",
        json.dumps([_serializable(event) for event in events], ensure_ascii=False),
    )
    assert final["items"], f"La orden {folio!r} no informa productos"
    for field in ("subtotal", "shipping", "total"):
        assert final[field] is not None, f"La orden {folio!r} no informa {field!r}"
    first = _event_view(events[0])
    incoherent = [_event_view(e) for e in events[1:] if _event_view(e) != first]
    assert not incoherent, (
        f"Los eventos de la orden {folio!r} no coinciden entre sí: {first} vs {incoherent}"
    )


# Paso 2 — comparar producto.
@when("compara el producto de la orden con la compra")
def compare_order_product(checkout_ctx) -> None:
    checkout_ctx["order_item"] = _order_item(checkout_ctx)


@then("el producto de la orden coincide con la compra")
def order_product_matches(checkout_ctx, cart_ctx, pdp_ctx) -> None:
    final = checkout_ctx["final_order"]
    order_item = checkout_ctx["order_item"]
    product = pdp_ctx["product"]
    cart_item, summary_item = _flow_item(cart_ctx, checkout_ctx)
    skus = {
        "orden": order_item["sku"],
        "pdp": product.sku,
        "carrito": cart_item.product.sku,
        "checkout": summary_item["sku"],
    }
    attach_text(
        "Producto",
        json.dumps(
            {"sku": skus, "nombre_orden": order_item["name"], "nombre_pdp": product.name},
            ensure_ascii=False,
        ),
    )
    assert len(final["items"]) == 1, (
        f"La orden debería tener 1 producto; tiene {len(final['items'])}"
    )
    assert len(set(skus.values())) == 1, f"El SKU no coincide entre etapas: {skus}"
    assert _casefold(order_item["name"]) == _casefold(product.name), (
        f"Producto de la orden {order_item['name']!r} != PDP {product.name!r}"
    )


# Paso 3 — comparar cantidad.
@when("compara la cantidad de la orden con la compra")
def compare_order_quantity(checkout_ctx) -> None:
    checkout_ctx["order_qty"] = _order_item(checkout_ctx)["qty"]


@then("la cantidad de la orden coincide con la compra")
def order_quantity_matches(checkout_ctx, cart_ctx) -> None:
    cart_item, summary_item = _flow_item(cart_ctx, checkout_ctx)
    quantities = {
        "orden": checkout_ctx["order_qty"],
        "pdp": cart_ctx["expected_qty"],
        "carrito": cart_item.quantity,
        "checkout": summary_item["qty"],
    }
    attach_text("Cantidad", json.dumps(quantities, ensure_ascii=False))
    assert len(set(quantities.values())) == 1, (
        f"La cantidad no coincide entre etapas: {quantities}"
    )


# Paso 4 — comparar subtotal.
@when("compara el subtotal de la orden con la compra")
def compare_order_subtotal(checkout_ctx) -> None:
    checkout_ctx["order_subtotal"] = checkout_ctx["final_order"]["subtotal"]


@then("el subtotal de la orden coincide con la compra")
def order_subtotal_matches(checkout_ctx, cart_ctx, pdp_ctx) -> None:
    cart = cart_ctx["cart"]
    subtotals = {
        "orden": checkout_ctx["order_subtotal"],
        "carrito": cart.subtotal,
        "checkout": checkout_ctx["summary"]["subtotal"],
    }
    unit_prices = {
        "orden": _order_item(checkout_ctx)["price"],
        "pdp": pdp_ctx["product"].effective_price,
        "carrito": cart.items[0].effective_unit_price,
    }
    attach_text(
        "Subtotal",
        json.dumps(
            {"subtotal": _amounts(subtotals), "precio_unitario": _amounts(unit_prices)},
            ensure_ascii=False,
        ),
    )
    assert len(set(unit_prices.values())) == 1, (
        f"El precio unitario no coincide entre etapas: {_amounts(unit_prices)}"
    )
    assert len(set(subtotals.values())) == 1, (
        f"El subtotal no coincide entre etapas: {_amounts(subtotals)}"
    )


# Paso 5 — comparar descuento (cuando aplique).
@when("compara el descuento de la orden con la compra")
def compare_order_discount(checkout_ctx) -> None:
    item = _order_item(checkout_ctx)
    checkout_ctx["order_discount"] = {
        "coupon": checkout_ctx["final_order"]["coupon"],
        "product": item["list_price"] - item["price"] if item["list_price"] else None,
    }


@then("el descuento de la orden coincide con la compra cuando aplica")
def order_discount_matches(checkout_ctx, cart_ctx, pdp_ctx) -> None:
    discount = checkout_ctx["order_discount"]
    product = pdp_ctx["product"]
    cart_discount = cart_ctx["cart"].discount
    pdp_discount = product.unit_price - product.effective_price
    attach_text(
        "Descuento",
        json.dumps(
            {
                "cupon_orden": discount["coupon"],
                "descuento_carrito": _amount(cart_discount),
                "descuento_producto_orden": _amount(discount["product"]),
                "descuento_producto_pdp": _amount(pdp_discount),
            },
            ensure_ascii=False,
        ),
    )
    assert bool(discount["coupon"]) == (cart_discount > _ZERO), (
        f"Cupón de la orden {discount['coupon']!r} vs descuento del carrito "
        f"{cart_discount.amount}: no coinciden"
    )
    if discount["product"] is not None:
        assert discount["product"] == pdp_discount, (
            f"Descuento de producto de la orden {discount['product'].amount} != "
            f"PDP {pdp_discount.amount}"
        )


# Paso 6 — comparar shipping.
@when("compara el envío de la orden con la compra")
def compare_order_shipping(checkout_ctx) -> None:
    checkout_ctx["order_shipping"] = checkout_ctx["final_order"]["shipping"]


@then("el envío de la orden coincide con el checkout")
def order_shipping_matches(checkout_ctx) -> None:
    shipping = {
        "orden": checkout_ctx["order_shipping"],
        "checkout": checkout_ctx["summary"]["shipping"],
    }
    attach_text("Envío", json.dumps(_amounts(shipping), ensure_ascii=False))
    assert shipping["orden"] == shipping["checkout"], (
        f"El envío no coincide: {_amounts(shipping)}"
    )


# Paso 7 — comparar total.
@when("compara el total de la orden con la compra")
def compare_order_total(checkout_ctx) -> None:
    checkout_ctx["order_total"] = checkout_ctx["final_order"]["total"]


@then("el total de la orden coincide con el checkout")
def order_total_matches(checkout_ctx, cart_ctx) -> None:
    final = checkout_ctx["final_order"]
    totals = {
        "orden": checkout_ctx["order_total"],
        "checkout": checkout_ctx["summary"]["total"],
        "subtotal_menos_descuento_mas_envio": (
            final["subtotal"] - cart_ctx["cart"].discount + final["shipping"]
        ),
    }
    attach_text("Total", json.dumps(_amounts(totals), ensure_ascii=False))
    assert len(set(totals.values())) == 1, f"El total no coincide: {_amounts(totals)}"


# Paso 8 — revisar forma de pago.
@when("revisa la forma de pago de la orden")
def review_order_payment(checkout_ctx, data_provider) -> None:
    checkout_ctx["expected_sale_type"] = data_provider.get_record("payment", "card")[
        "sale_type"
    ]


@then("la forma de pago de la orden corresponde a contado")
def order_payment_is_cash(checkout_ctx) -> None:
    sale_type = checkout_ctx["final_order"]["sale_type"]
    expected = checkout_ctx["expected_sale_type"]
    method = checkout_ctx["order"].payment_method
    cash_value = checkout_ctx["cash_method"]["value"]
    attach_text(
        "Forma de pago",
        json.dumps(
            {"tipo_pago_orden": sale_type, "esperado": expected, "metodo": method},
            ensure_ascii=False,
        ),
    )
    assert _casefold(sale_type) == _casefold(expected), (
        f"La orden informa tipo de pago {sale_type!r}; esperado {expected!r}"
    )
    assert method == cash_value, f"Método de la orden {method!r} != contado {cash_value!r}"


# Paso 9 — revisar folio.
@when("revisa el folio de la orden")
def review_order_folio(checkout_ctx) -> None:
    checkout_ctx["order_folio"] = checkout_ctx["order_page"].order_number()


@then("el folio de la orden es un identificador válido")
def order_folio_valid(checkout_ctx) -> None:
    folio = checkout_ctx["order_folio"]
    final = checkout_ctx["final_order"]
    attach_text(
        "Folio",
        json.dumps(
            {
                "pagina": folio,
                "orden": final["folio"],
                "sku": _order_item(checkout_ctx)["sku"],
                "total": _amount(final["total"]),
            },
            ensure_ascii=False,
        ),
    )
    assert folio and folio.isdigit(), f"Folio inválido: {folio!r}"
    assert folio == final["folio"], (
        f"Folio de la página {folio!r} != folio de la orden {final['folio']!r}"
    )
