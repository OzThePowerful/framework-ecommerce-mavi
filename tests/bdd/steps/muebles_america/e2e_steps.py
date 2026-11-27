"""Steps BDD del E2E de venta de contado exclusivos de Muebles América
(test_cases/muebles_america/e2e/ — CP_EC_MA_E2E_001).

El flujo Home → … → Order reutiliza los steps de MA de cada módulo; aquí
viven la evidencia por etapa, las validaciones obligatorias que no cubre
ORDER_002 (precio, subtotal y shipping en todo el flujo) y el cierre con
el resumen de evidencia. Textos distintos a los de la rama VIU
(MA-AISLAMIENTO-001). Sin locators: los screenshots los toma el
EvidenceManager (en el checkout, con los campos capturados enmascarados).
PRECAUCIÓN: el escenario confirma la compra y crea una orden REAL.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from pytest_bdd import parsers, then, when

from core.reporting.allure_manager import attach_file, attach_text
from domain.money.money import Money

# Etapas del flujo del contrato, en orden.
E2E_STAGES = (
    "Home", "Search", "PDP", "Cart", "Checkout",
    "Customer", "Address", "Shipping", "Payment", "Order",
)


def _amounts(values: dict) -> dict:
    return {key: value and str(value.amount) for key, value in values.items()}


@pytest.fixture
def e2e_evidence() -> list[dict]:
    """Evidencia acumulada por etapa: `{stage, url, screenshot, masked}`."""
    return []


# --- Evidencia por etapa ----------------------------------------------------
@then(parsers.parse('queda la evidencia de la etapa "{stage}"'))
def stage_evidence(stage, page, pages, evidence_manager, e2e_evidence) -> None:
    assert stage in E2E_STAGES, f"Etapa desconocida {stage!r}; esperadas {E2E_STAGES}"
    checkout = pages.checkout()
    mask = checkout.evidence_mask() if checkout.is_on_checkout() else None
    name = f"{len(e2e_evidence) + 1:02d}_{stage.lower()}"
    path = evidence_manager.save_screenshot(page, name, mask=mask)
    attach_file(path, name=f"Etapa {stage}")
    e2e_evidence.append(
        {"stage": stage, "url": page.url, "screenshot": str(path), "masked": bool(mask)}
    )


# --- Validación obligatoria: precio ------------------------------------------
@when("compara el precio del producto en todo el flujo")
def compare_price_across_flow(checkout_ctx, cart_ctx, pdp_ctx) -> None:
    checkout_ctx["e2e_prices"] = {
        "pdp": pdp_ctx["product"].effective_price,
        "carrito": cart_ctx["cart"].items[0].effective_unit_price,
        "checkout": checkout_ctx["final_summary"]["items"][0]["price"],
        "orden": checkout_ctx["final_order"]["items"][0]["price"],
    }


@then("el precio del producto es consistente en todo el flujo")
def price_consistent_across_flow(checkout_ctx) -> None:
    prices = checkout_ctx["e2e_prices"]
    attach_text("Precio E2E", json.dumps(_amounts(prices), ensure_ascii=False))
    missing = [stage for stage, price in prices.items() if price is None]
    assert not missing, f"Etapas sin precio observable: {missing}"
    assert len(set(prices.values())) == 1, (
        f"El precio no es consistente en el flujo: {_amounts(prices)}"
    )


# --- Validación obligatoria: subtotal ----------------------------------------
@when("verifica el subtotal de cada etapa")
def verify_subtotal_per_stage(checkout_ctx, cart_ctx) -> None:
    cart_item = cart_ctx["cart"].items[0]
    summary_item = checkout_ctx["final_summary"]["items"][0]
    order_items = checkout_ctx["final_order"]["items"]
    order_expected = Money(Decimal("0"))
    for item in order_items:
        order_expected = order_expected + item["price"] * item["qty"]
    checkout_ctx["e2e_subtotals"] = {
        "carrito": {
            "observado": cart_ctx["observed_subtotal"],
            "precio_x_cantidad": cart_item.effective_unit_price * cart_item.quantity,
        },
        "checkout": {
            "observado": checkout_ctx["summary"]["subtotal"],
            "precio_x_cantidad": summary_item["price"] * summary_item["qty"],
        },
        "orden": {
            "observado": checkout_ctx["final_order"]["subtotal"],
            "precio_x_cantidad": order_expected,
        },
    }


@then("el subtotal es matemáticamente correcto en cada etapa")
def subtotal_correct_per_stage(checkout_ctx) -> None:
    subtotals = checkout_ctx["e2e_subtotals"]
    attach_text(
        "Subtotal E2E",
        json.dumps({stage: _amounts(v) for stage, v in subtotals.items()}, ensure_ascii=False),
    )
    wrong = {
        stage: _amounts(v)
        for stage, v in subtotals.items()
        if v["observado"] != v["precio_x_cantidad"]
    }
    assert not wrong, f"Subtotal ≠ precio × cantidad en: {wrong}"
    observed = {stage: v["observado"] for stage, v in subtotals.items()}
    assert len(set(observed.values())) == 1, (
        f"El subtotal no coincide entre etapas: {_amounts(observed)}"
    )


# --- Validación obligatoria: shipping ----------------------------------------
@when("compara el envío en todo el flujo")
def compare_shipping_across_flow(checkout_ctx) -> None:
    checkout_ctx["e2e_shipping"] = {
        "etapa_entrega": checkout_ctx["shipping_cost"],
        "resumen": checkout_ctx["summary"]["shipping"],
        "orden": checkout_ctx["final_order"]["shipping"],
    }


@then("el envío es consistente en todo el flujo")
def shipping_consistent_across_flow(checkout_ctx) -> None:
    shipping = checkout_ctx["e2e_shipping"]
    attach_text("Envío E2E", json.dumps(_amounts(shipping), ensure_ascii=False))
    assert len(set(shipping.values())) == 1, (
        f"El envío no es consistente en el flujo: {_amounts(shipping)}"
    )


# --- Cierre: evidencia de extremo a extremo -----------------------------------
@when("reúne la evidencia de la venta de contado")
def collect_sale_evidence(checkout_ctx, pdp_ctx, e2e_evidence) -> None:
    final = checkout_ctx["final_order"]
    checkout_ctx["e2e_summary"] = {
        "etapas": [entry["stage"] for entry in e2e_evidence],
        "evidencia": e2e_evidence,
        "producto": {"sku": pdp_ctx["product"].sku, "nombre": pdp_ctx["product"].name},
        "importes": _amounts(
            {"subtotal": final["subtotal"], "envio": final["shipping"], "total": final["total"]}
        ),
        "tipo_pago": final["sale_type"],
        "metodo": checkout_ctx["order"].payment_method,
        "folio": checkout_ctx["order"].folio,
    }


@then("la venta de contado queda evidenciada de extremo a extremo")
def sale_evidenced_end_to_end(checkout_ctx, evidence_manager) -> None:
    summary = checkout_ctx["e2e_summary"]
    content = json.dumps(summary, ensure_ascii=False, indent=2)
    evidence_manager.save_log("e2e_resumen", content)
    attach_text("Evidencia E2E", content)
    assert tuple(summary["etapas"]) == E2E_STAGES, (
        f"Etapas evidenciadas {summary['etapas']} != flujo del contrato {list(E2E_STAGES)}"
    )
    missing = [
        entry["stage"]
        for entry in summary["evidencia"]
        if not Path(entry["screenshot"]).is_file() or not Path(entry["screenshot"]).stat().st_size
    ]
    assert not missing, f"Etapas sin captura en disco: {missing}"
    assert summary["folio"], "La evidencia no registra el folio de la orden"
