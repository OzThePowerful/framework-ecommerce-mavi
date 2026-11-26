"""Steps BDD del contrato común de Cart (test_cases/common/cart.feature).

Reutiliza los steps de home/search de search_steps.py y el When de PDP de
pdp_steps.py; aquí solo viven los steps propios del carrito.
Sin locators ni secuencias Playwright: los asserts comparan el Product de
dominio leído en PDP contra el Cart leído de la página.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


@when("agrega el producto al carrito", target_fixture="cart_ctx")
def add_product_to_cart(pdp_ctx) -> dict:
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
    product_page.dismiss_post_add_overlays()
    return {"expected": expected, "expected_qty": expected_qty}


@when("abre el carrito de compras")
def open_cart(pages, cart_ctx) -> None:
    cart_page = pages.cart()
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


@then("se muestra la opción de continuar como invitado")
def guest_gate_visible(pages) -> None:
    checkout = pages.checkout()
    checkout.wait_for_guest_gate()
    assert checkout.is_guest_gate_visible(), (
        "El gate 'Continuar como invitado' no se mostró tras continuar"
    )
