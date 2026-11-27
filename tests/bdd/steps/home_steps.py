"""Steps BDD del contrato común de Home (test_cases/common/home/).

Steps delgados: delegan en HomePage/HeaderComponent; sin locators ni
secuencias Playwright. El sitio lo decide el ExecutionContext (--site).
"""

import json

from pytest_bdd import then

from core.reporting.allure_manager import attach_text


@then("el sitio responde con un estado correcto")
def site_responds_ok(home_ctx) -> None:
    status = home_ctx["status"]
    attach_text("Respuesta HTTP", json.dumps({"status": status}))
    assert status is not None, "La navegación no obtuvo respuesta HTTP"
    assert 200 <= status < 400, f"El sitio respondió con status HTTP {status}"


@then("la home identifica la marca del sitio activo")
def home_identifies_brand(pages, execution_context) -> None:
    home = pages.home()
    assert home.header.is_visible(), "El header de la home no es visible"
    assert home.brand() == execution_context.site, (
        f"Marca leída {home.brand()!r} != sitio activo "
        f"{execution_context.site!r}"
    )
    attach_text(
        "Home",
        json.dumps({"brand": home.brand()}, ensure_ascii=False),
    )


@then("el buscador está accesible")
def search_box_accessible(pages) -> None:
    header = pages.home().header
    assert header.is_search_submittable(), (
        "El buscador del header no está en estado accesible"
    )


@then("el acceso al carrito está disponible")
def cart_access_available(pages) -> None:
    header = pages.home().header
    assert header.is_cart_accessible(), (
        "El acceso al carrito del header no está disponible"
    )


@then("la navegación principal está disponible")
def main_navigation_available(pages) -> None:
    header = pages.home().header
    assert header.is_navigation_accessible(), (
        "La navegación principal del header no está disponible"
    )
