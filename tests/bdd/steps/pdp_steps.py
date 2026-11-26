"""Steps BDD del contrato común de PDP (test_cases/common/pdp.feature).

Reutiliza los steps Given/When de búsqueda definidos en search_steps.py;
aquí solo viven los steps propios de PDP. Sin locators ni Playwright.
@PDP_001 sigue 1:1 los pasos de CP_EC_<CODE>_PDP_001.
"""

import json
import re

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text

_ABSENT = "ausente"
# Etiquetas de la PDP que permiten comprar; 'Agotado' no lo permite.
_PURCHASABLE_LABEL = re.compile(r"^(disponible|solo queda (\d+))$", re.IGNORECASE)


@when("abre la PDP de una card elegible", target_fixture="pdp_ctx")
def open_eligible_pdp(pages, search_ctx) -> dict:
    card = search_ctx["results"].eligible_card()
    assert card is not None, "La búsqueda no produjo una card elegible"
    # Se leen antes de navegar: tras open() el tile deja de existir.
    card_name = card.name()
    card_href = card.identifier()
    card.open()
    return {
        "product_page": pages.product(),
        "card": card,
        "card_name": card_name,
        "card_href": card_href,
    }


def _normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


# Paso 2 — la PDP abierta corresponde a la card seleccionada.
@then("se abre la PDP del producto seleccionado")
def pdp_matches_selected_card(pdp_ctx) -> None:
    product_page = pdp_ctx["product_page"]
    slug = pdp_ctx["card_href"].split("?")[0]
    assert slug and slug in product_page.page.url, (
        f"La PDP debería corresponder a {slug!r}; URL actual: "
        f"{product_page.page.url}"
    )
    product = product_page.read_product()
    pdp_ctx["product"] = product
    attach_text(
        "Product PDP",
        json.dumps(
            {
                "product_name": product.name,
                "sku": product.sku or None,
                "product_id": product.product_id or None,
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
    assert _normalize(product.name) == _normalize(pdp_ctx["card_name"]), (
        f"La PDP muestra {product.name!r}; se seleccionó "
        f"{pdp_ctx['card_name']!r}"
    )


# Paso 3 — nombre.
@then("el producto tiene nombre no vacío")
def product_has_name(pdp_ctx) -> None:
    assert pdp_ctx["product"].name.strip(), "El producto debería tener nombre"


# Paso 4 — identificador válido o ausencia documentada.
@then("el producto expone un identificador válido o se documenta su ausencia")
def product_identifier(pdp_ctx) -> None:
    product = pdp_ctx["product"]
    url = pdp_ctx["product_page"].page.url.lower()
    identifiers = {
        "sku": product.sku or _ABSENT,
        "product_id": product.product_id or _ABSENT,
    }
    attach_text(
        "Identificadores", json.dumps(identifiers, ensure_ascii=False)
    )
    present = {k: v for k, v in identifiers.items() if v != _ABSENT}
    assert present, "La PDP no expone sku ni product_id"
    if "sku" in present:
        assert present["sku"].lower() in url, (
            f"El sku {present['sku']!r} debería aparecer en el slug de la PDP"
        )
    if "product_id" in present:
        assert present["product_id"].isdigit(), (
            f"El product_id {present['product_id']!r} debería ser numérico"
        )


# Paso 5 — precio.
@then("el precio es un importe válido mayor a cero")
def product_price_valid(pdp_ctx) -> None:
    product = pdp_ctx["product"]
    assert product.unit_price.amount > 0, "El precio unitario debería ser > 0"
    assert product.effective_price.amount > 0, (
        "El precio efectivo debería ser > 0"
    )
    assert product.effective_price.amount <= product.unit_price.amount, (
        "El precio efectivo no debería exceder el precio unitario"
    )
    if product.promotional_price is not None:
        assert product.promotional_price.amount < product.unit_price.amount, (
            "El precio promocional debería ser menor al unitario"
        )


# Paso 6 — disponibilidad: etiqueta visible al cliente + regla de estado.
@then("la disponibilidad permite comprar el producto")
def product_purchasable(pdp_ctx) -> None:
    product_page = pdp_ctx["product_page"]
    label = product_page.availability_label()
    attach_text(
        "Disponibilidad PDP", json.dumps({"label": label}, ensure_ascii=False)
    )
    assert label is not None, "La PDP no muestra la etiqueta de disponibilidad"
    match = _PURCHASABLE_LABEL.match(label)
    assert match, (
        f"La PDP marca el producto como {label!r}; no se puede comprar"
    )
    if match.group(2) is not None:
        assert int(match.group(2)) >= 1, (
            f"La etiqueta {label!r} debería indicar al menos 1 pieza"
        )
    assert product_page.stock_quantity() > 0, "El stock debería ser mayor a cero"
    assert product_page.quantity() >= 1, "La cantidad mínima debería ser 1"
    assert pdp_ctx["product"].availability is True, (
        "El producto debería estar disponible según la regla de venta"
    )


# Paso 7 — agregar al carrito.
@then("la acción de agregar al carrito está disponible y habilitada")
def add_to_cart_enabled(pdp_ctx) -> None:
    assert pdp_ctx["product_page"].is_add_to_cart_enabled(), (
        "La acción de agregar al carrito debería estar visible y habilitada"
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
