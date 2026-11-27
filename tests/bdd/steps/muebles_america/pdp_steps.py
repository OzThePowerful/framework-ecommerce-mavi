"""Steps BDD de PDP exclusivos de Muebles América
(test_cases/muebles_america/product/ — CP_EC_MA_PDP_001).

@PDP_001 de MA sigue 1:1 los pasos del contrato. Reutiliza los steps
comunes de búsqueda; el step compartido `abre la PDP de una card
elegible` no se modifica: aquí se usa uno propio que además registra el
nombre y el href de la card antes de navegar (MA-AISLAMIENTO-001).
Sin locators ni Playwright.
"""

import json
import re

from pytest_bdd import then, when

from core.reporting.allure_manager import attach_text

_ABSENT = "ausente"
# Etiquetas de la PDP que permiten comprar; 'Agotado' no lo permite.
_PURCHASABLE_LABEL = re.compile(r"^(disponible|solo quedan? (\d+))$", re.IGNORECASE)


@when("selecciona una card elegible y abre su PDP", target_fixture="pdp_ctx")
def open_selected_card_pdp(pages, search_ctx) -> dict:
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
