"""Steps BDD del contrato común de PDP (test_cases/common/pdp.feature).

Reutiliza los steps Given/When de búsqueda definidos en search_steps.py;
aquí solo viven los steps propios de PDP. Sin locators ni Playwright.
"""

import json

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text


@when("abre la PDP de una card elegible", target_fixture="pdp_ctx")
def open_eligible_pdp(pages, search_ctx) -> dict:
    """Abre la primera PDP comprable de entre las cards elegibles.

    El tile de la PLP no expone el estado de stock (el CTA aparece en
    todas las cards, deshabilitado): se itera candidatos hasta hallar
    una PDP cuyo CTA de compra exista y esté habilitado.
    """
    results = search_ctx["results"]
    product_page = pages.product()
    candidates = results.eligible_cards(max_cards=4)
    assert candidates, "La búsqueda no produjo cards elegibles"
    card = None
    for candidate in candidates:
        candidate.open()
        product_page.wait_until_ready()
        if product_page.is_add_to_cart_enabled():
            card = candidate
            break
        results.back_to_results()
    assert card is not None, (
        "Ninguna de las primeras cards elegibles abrió una PDP comprable "
        "(productos agotados)"
    )
    return {"product_page": product_page, "card": card}


@then("el modelo Product tiene nombre, sku e identificador")
def product_identity(pdp_ctx) -> None:
    product = pdp_ctx["product_page"].read_product()
    pdp_ctx["product"] = product
    attach_text(
        "Product PDP",
        json.dumps(
            {
                "sku": product.sku,
                "product_id": product.product_id,
                "name": product.name,
                "unit_price": str(product.unit_price.amount),
                "promotional_price": (
                    str(product.promotional_price.amount)
                    if product.promotional_price
                    else None
                ),
                "effective_price": str(product.effective_price.amount),
                "currency": product.unit_price.currency,
                "availability": product.availability,
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    assert product.name, "El producto debería tener nombre"
    assert product.sku, "El producto debería tener sku"
    assert product.product_id, "El producto debería tener product_id"
    assert product.sku.lower() in pdp_ctx["product_page"].page.url, (
        "El sku del Product debería aparecer en el slug de la PDP"
    )


@then("el precio es válido y la disponibilidad cumple las reglas de venta")
def product_price_and_availability(pdp_ctx) -> None:
    product = pdp_ctx["product"]
    product_page = pdp_ctx["product_page"]
    assert product.unit_price.amount > 0, "El precio unitario debería ser > 0"
    assert product.effective_price.amount <= product.unit_price.amount, (
        "El precio efectivo no debería exceder el precio unitario"
    )
    if product.promotional_price is not None:
        assert product.promotional_price.amount < product.unit_price.amount, (
            "El precio promocional debería ser menor al unitario"
        )
    assert product_page.stock_quantity() > 0, "El stock debería ser mayor a cero"
    assert product_page.quantity() >= 1, "La cantidad mínima debería ser 1"
    assert product.availability is True, (
        "El producto debería estar disponible según la regla de venta"
    )


@then("el CTA de agregar al carrito está habilitado")
def add_to_cart_enabled(pdp_ctx) -> None:
    assert pdp_ctx["product_page"].is_add_to_cart_enabled(), (
        "El CTA de agregar al carrito debería estar habilitado"
    )


@when(
    "busca el término del producto configurable del dataset",
    target_fixture="configurable_ctx",
)
def search_configurable(pages, data_provider) -> dict:
    record = data_provider.get_record("products", "configurable_colchon")
    results = pages.search()
    results.search(record["term"])
    return {"record": record, "results": results}


@when("abre la PDP del producto configurable del dataset")
def open_configurable_pdp(pages, configurable_ctx) -> None:
    configurable_ctx["results"].open_product(
        configurable_ctx["record"]["name_fragment"]
    )
    configurable_ctx["product_page"] = pages.product()
    configurable_ctx["product_page"].wait_until_ready()


@then("el producto es configurable y su sku padre coincide con el dataset")
def configurable_parent(configurable_ctx) -> None:
    product_page = configurable_ctx["product_page"]
    assert product_page.is_configurable(), (
        "Se esperaba un producto configurable"
    )
    expected = configurable_ctx["record"]["expected_parent_sku"]
    assert product_page.parent_sku() == expected, (
        f"Sku padre esperado {expected}; observado {product_page.parent_sku()}"
    )


@then("cada variante es un Product válido según las reglas de venta")
def variants_are_valid_products(configurable_ctx) -> None:
    product_page = configurable_ctx["product_page"]
    variants = product_page.variants()
    expected = int(configurable_ctx["record"]["expected_variants"])
    assert len(variants) == expected, (
        f"Se esperaban {expected} variantes; se observaron {len(variants)}"
    )
    attach_text(
        "Variantes configurables",
        "\n".join(
            f"{v.sku} | {v.name} | unit={v.unit_price.amount} "
            f"eff={v.effective_price.amount} | avail={v.availability}"
            for v in variants
        ),
    )
    for variant in variants:
        assert variant.sku, "Cada variante debería tener sku"
        assert variant.name, "Cada variante debería tener nombre"
        assert variant.unit_price.amount > 0, (
            f"La variante {variant.sku} debería tener precio > 0"
        )
        assert variant.availability is True, (
            f"La variante {variant.sku} debería estar disponible "
            "(is_in_stock && qty>0 && status==1)"
        )
