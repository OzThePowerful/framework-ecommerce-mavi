"""Steps BDD de Cart exclusivos de Muebles América
(test_cases/muebles_america/cart/ — CP_EC_MA_CART_001).

Siguen 1:1 los pasos 2–7 del contrato. Reutilizan los steps de PDP de MA
(`selecciona una card elegible y abre su PDP`, `se abre la PDP del
producto seleccionado`) y los comunes `abre el carrito de compras`,
`el carrito contiene el producto…` y `los importes del carrito…`. Los
steps compartidos `agrega el producto al carrito` y `abre la PDP de una
card elegible` no se usan ni se modifican. Textos distintos a los de la
rama VIU (MA-AISLAMIENTO-001). Sin locators ni Playwright.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text

_ADDED_TEXT = "agregado a tu carrito"


def _normalize(text: str) -> str:
    return " ".join((text or "").split()).casefold()


# Paso 2 — registrar nombre, identificador y precio.
@then("se registran el nombre, el identificador y el precio del producto")
def product_registered(pdp_ctx) -> None:
    product = pdp_ctx["product"]
    attach_text(
        "Producto registrado",
        json.dumps(
            {
                "name": product.name,
                "sku": product.sku or None,
                "product_id": product.product_id or None,
                "effective_price": str(product.effective_price.amount),
            },
            ensure_ascii=False,
        ),
    )
    assert product.name.strip(), "El producto debería tener nombre"
    assert product.sku, (
        "El producto debería exponer sku para identificarlo en el carrito"
    )
    assert product.effective_price.amount > 0, (
        "El precio efectivo debería ser mayor a cero"
    )


# Paso 3 — cantidad 1.
@then("la cantidad seleccionada en la PDP es 1")
def pdp_quantity_is_one(pdp_ctx) -> None:
    product_page = pdp_ctx["product_page"]
    displayed = product_page.displayed_quantity()
    selected = product_page.quantity()
    assert displayed == 1, f"La PDP muestra la cantidad {displayed!r}; se esperaba 1"
    assert selected == 1, f"La cantidad seleccionada es {selected}; se esperaba 1"


# Paso 4 — agregar al carrito.
@when("agrega el producto disponible al carrito", target_fixture="cart_ctx")
def add_available_product(pages, pdp_ctx) -> dict:
    product_page = pdp_ctx["product_page"]
    expected_qty = product_page.quantity()
    product_page.add_to_cart()
    return {
        "expected": pdp_ctx["product"],
        "expected_qty": expected_qty,
        "product_page": product_page,
        "ma_cart": pages.cart(),
    }


@then("el ecommerce procesa la adición del producto")
def add_processed(cart_ctx) -> None:
    sku = cart_ctx["expected"].sku
    item = cart_ctx["ma_cart"].state_item(sku)
    attach_text("Adición procesada", json.dumps(item, ensure_ascii=False))
    assert item is not None, f"El estado del carrito no registró el sku {sku!r}"
    assert item.get("server_item_id"), (
        f"El ítem {sku!r} no quedó aceptado por el ecommerce (sin server_item_id)"
    )
    assert item.get("qty") == 1, (
        f"El ítem {sku!r} se procesó con cantidad {item.get('qty')}; se esperaba 1"
    )


# Paso 5 — confirmación observable.
@when("espera la confirmación de la adición")
def wait_add_confirmation(cart_ctx) -> None:
    product_page = cart_ctx["product_page"]
    cart_ctx["confirmation"] = product_page.add_confirmation_message()
    cart_ctx["minicart_count"] = cart_ctx["ma_cart"].wait_for_minicart_count(1)
    # Libera el header (promo + toast) para abrir el carrito después.
    product_page.dismiss_post_add_overlays()


@then("el ecommerce confirma la adición del producto")
def add_confirmed(cart_ctx) -> None:
    message = cart_ctx["confirmation"]
    name = cart_ctx["expected"].name
    attach_text(
        "Confirmación",
        json.dumps(
            {"message": message, "minicart_count": cart_ctx["minicart_count"]},
            ensure_ascii=False,
        ),
    )
    assert message is not None, "No apareció la confirmación de producto agregado"
    assert _ADDED_TEXT in _normalize(message), (
        f"La confirmación no indica que el producto se agregó: {message!r}"
    )
    assert _normalize(name) in _normalize(message), (
        f"La confirmación no menciona el producto {name!r}: {message!r}"
    )
    assert cart_ctx["minicart_count"] == 1, (
        f"El minicart muestra {cart_ctx['minicart_count']} producto(s); se esperaba 1"
    )


# Paso 6 — carrito disponible.
@then("el carrito está disponible")
def cart_available(cart_ctx) -> None:
    assert cart_ctx["cart_page"].is_open(), (
        "La página del carrito no quedó disponible (ruta o contenedor ausente)"
    )


# Paso 7 — producto agregado visible con cantidad 1.
@then("el producto registrado está visible en el carrito con cantidad 1")
def registered_product_in_cart(cart_ctx) -> None:
    expected = cart_ctx["expected"]
    items = cart_ctx["cart"].items
    attach_text(
        "Carrito",
        json.dumps(
            [
                {"sku": i.product.sku, "name": i.product.name, "quantity": i.quantity}
                for i in items
            ],
            ensure_ascii=False,
        ),
    )
    matches = [i for i in items if i.product.sku == expected.sku]
    assert matches, (
        f"El producto {expected.sku!r} no aparece en el carrito; "
        f"ítems: {[i.product.sku for i in items]}"
    )
    assert len(items) == 1, f"El carrito debería tener 1 ítem; tiene {len(items)}"
    item = matches[0]
    assert _normalize(item.product.name) == _normalize(expected.name), (
        f"Nombre en carrito {item.product.name!r} != registrado {expected.name!r}"
    )
    assert item.quantity == 1, f"Cantidad en carrito {item.quantity}; se esperaba 1"
