"""Steps BDD de Order exclusivos de Muebles América
(test_cases/muebles_america/order/ — CP_EC_MA_ORDER_001).

Pasos 1–6 del contrato, cada acción con su verificación. Las
precondiciones reutilizan los steps de PDP/Cart/Checkout/Payment de MA y
los comunes de captura del comprador y de entrega. Textos distintos a los
de la rama VIU (MA-AISLAMIENTO-001). Sin locators ni Playwright.
PRECAUCIÓN: 'ejecuta la confirmación de la compra' crea una orden REAL.
"""

import json
import re

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


def _casefold(text: str | None) -> str:
    return " ".join((text or "").split()).casefold()


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
