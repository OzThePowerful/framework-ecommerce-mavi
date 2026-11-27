"""Steps BDD del contrato común de Cart (test_cases/common/cart.feature).

Reutiliza los steps de home/search de search_steps.py y el When de PDP de
pdp_steps.py; aquí solo viven los steps propios del carrito.
Sin locators ni secuencias Playwright: los asserts comparan el Product de
dominio leído en PDP contra el Cart leído de la página.
"""

import json
import re

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


@when("agrega el producto al carrito", target_fixture="cart_ctx")
def add_product_to_cart(pages, pdp_ctx) -> dict:
    product_page = pdp_ctx["product_page"]
    expected = product_page.read_product()
    expected_qty = product_page.quantity()
    attach_text(
        "Product PDP",
        json.dumps(
            {
                "sku": expected.sku,
                "name": expected.name,
                "unit_price": str(expected.effective_price.amount),
                "quantity": expected_qty,
            },
            ensure_ascii=False,
        ),
    )
    product_page.add_to_cart()
    cart_page = pages.cart()
    confirmation = product_page.add_confirmation_message()
    minicart_count = cart_page.wait_for_minicart_count(expected_qty)
    product_page.dismiss_post_add_overlays()
    return {
        "expected": expected,
        "expected_qty": expected_qty,
        "cart_page": cart_page,
        "confirmation": confirmation,
        "minicart_count": minicart_count,
    }


@then("el ecommerce procesa la adición al carrito")
def add_processed_to_cart(cart_ctx) -> None:
    expected = cart_ctx["expected"]
    item = cart_ctx["cart_page"].state_item(expected.sku)
    attach_text("Adición procesada", json.dumps(item, ensure_ascii=False))
    assert item is not None, (
        f"El estado del carrito no registró el sku {expected.sku!r}"
    )
    assert item.get("server_item_id"), (
        f"El ítem {expected.sku!r} no quedó aceptado por el ecommerce "
        "(sin server_item_id)"
    )
    assert item.get("qty") == cart_ctx["expected_qty"], (
        f"El ítem {expected.sku!r} se procesó con cantidad "
        f"{item.get('qty')}; se esperaba {cart_ctx['expected_qty']}"
    )


@then("el ecommerce confirma la adición al carrito")
def add_confirmed_to_cart(cart_ctx) -> None:
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
    assert "agregado" in _normalize(message), (
        f"La confirmación no indica que el producto se agregó: {message!r}"
    )
    assert _normalize(name) in _normalize(message), (
        f"La confirmación no menciona el producto {name!r}: {message!r}"
    )
    assert cart_ctx["minicart_count"] == cart_ctx["expected_qty"], (
        f"El minicart muestra {cart_ctx['minicart_count']} producto(s); "
        f"se esperaba {cart_ctx['expected_qty']}"
    )


@when("abre el carrito de compras")
def open_cart(pages, cart_ctx) -> None:
    cart_page = cart_ctx.get("cart_page") or pages.cart()
    cart_page.open_cart()
    cart_ctx["cart_page"] = cart_page
    cart_ctx["cart"] = cart_page.read_cart()


@when("continúa al checkout desde el carrito")
def continue_to_checkout(cart_ctx) -> None:
    cart_ctx["cart_page"].continue_to_checkout()


@then("el producto agregado es visible en el carrito con cantidad 1")
def added_product_visible_in_cart(cart_ctx) -> None:
    model = cart_ctx["cart"]
    expected = cart_ctx["expected"]
    assert len(model.items) == 1, (
        f"El carrito debería tener 1 ítem; tiene {len(model.items)}"
    )
    item = model.items[0]
    assert item.product.sku == expected.sku, (
        f"SKU carrito {item.product.sku!r} != PDP {expected.sku!r}"
    )
    assert item.product.name == expected.name, (
        f"Nombre carrito {item.product.name!r} != PDP {expected.name!r}"
    )
    assert item.quantity == cart_ctx["expected_qty"], (
        f"Cantidad {item.quantity} != esperada {cart_ctx['expected_qty']}"
    )
    attach_text(
        "Cart item",
        json.dumps(
            {
                "sku": item.product.sku,
                "name": item.product.name,
                "quantity": item.quantity,
            },
            ensure_ascii=False,
        ),
    )


@then("el carrito contiene el producto con datos coherentes con la PDP")
def cart_item_matches_pdp_product(cart_ctx) -> None:
    model = cart_ctx["cart_page"].read_cart()
    cart_ctx["cart"] = model
    expected = cart_ctx["expected"]
    assert len(model.items) == 1, (
        f"El carrito debería tener 1 ítem; tiene {len(model.items)}"
    )
    item = model.items[0]
    assert item.product.sku == expected.sku, (
        f"SKU carrito {item.product.sku!r} != PDP {expected.sku!r}"
    )
    assert item.product.name == expected.name, (
        f"Nombre carrito {item.product.name!r} != PDP {expected.name!r}"
    )
    assert item.quantity == cart_ctx["expected_qty"], (
        f"Cantidad {item.quantity} != esperada {cart_ctx['expected_qty']}"
    )
    assert item.effective_unit_price.amount == expected.effective_price.amount, (
        f"Precio carrito {item.effective_unit_price.amount} != "
        f"PDP {expected.effective_price.amount}"
    )
    attach_text(
        "Cart",
        json.dumps(
            {
                "sku": item.product.sku,
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": str(item.effective_unit_price.amount),
                "item_subtotal": str(item.subtotal.amount),
            },
            ensure_ascii=False,
        ),
    )


@then("el subtotal del ítem coincide con la cantidad por el precio unitario")
def item_subtotal_matches_qty_times_price(cart_ctx) -> None:
    expected_product = cart_ctx["expected"]
    expected = expected_product.effective_price.amount * cart_ctx["expected_qty"]
    observed = cart_ctx["cart_page"].page_subtotal().amount
    assert observed == expected, (
        f"Subtotal observado {observed} != "
        f"qty {cart_ctx['expected_qty']} x precio PDP "
        f"{expected_product.effective_price.amount} = {expected}"
    )
    attach_text(
        "Subtotal esperado",
        json.dumps(
            {
                "quantity": cart_ctx["expected_qty"],
                "unit_price_pdp": str(expected_product.effective_price.amount),
                "expected_subtotal": str(expected),
                "observed_subtotal": str(observed),
            },
            ensure_ascii=False,
        ),
    )


@then("los importes del carrito son consistentes con el subtotal y el total")
def cart_amounts_are_consistent(cart_ctx) -> None:
    cart_page = cart_ctx["cart_page"]
    model = cart_ctx["cart"]
    subtotal = cart_page.page_subtotal()
    discount = cart_page.page_discount()
    total = cart_page.page_total()
    assert subtotal == model.subtotal, (
        f"Subtotal página {subtotal.amount} != modelo {model.subtotal.amount}"
    )
    assert discount.amount == model.discount.amount, (
        f"Descuento página {discount.amount} != modelo {model.discount.amount}"
    )
    assert total == model.total, (
        f"Total página {total.amount} != modelo {model.total.amount}"
    )
    attach_text(
        "Importes del carrito",
        json.dumps(
            {
                "subtotal": str(subtotal.amount),
                "discount": str(discount.amount),
                "total": str(total.amount),
            },
            ensure_ascii=False,
        ),
    )


