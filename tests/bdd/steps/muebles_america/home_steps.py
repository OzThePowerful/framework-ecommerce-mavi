"""Steps BDD de Home exclusivos de Muebles América
(test_cases/muebles_america/home/ — CP_EC_MA_HOME_001).

Steps delgados: delegan en HomePage/HeaderComponent de MA; sin locators
ni secuencias Playwright. Las expectativas de marca salen del dataset
`home`/`home_001`. `la home queda en estado utilizable` y `el buscador
está visible y habilitado` también los usa SEARCH_001/002 de MA.
Textos distintos a los de la rama VIU para no chocar (MA-AISLAMIENTO-001).
"""

import json

import pytest
from pytest_bdd import given, then, when

from core.reporting.allure_manager import attach_text


@pytest.fixture
def home_expectations(data_provider) -> dict:
    return data_provider.get_record("home", "home_001")


# Paso 1 — navegar a la URL configurada.
@given(
    "el usuario navega a la URL configurada del sitio activo",
    target_fixture="home_status",
)
def navigate_to_configured_url(pages) -> int | None:
    return pages.home().open_home()


# Paso 2 — esperar la carga inicial.
@when("espera a que finalice la carga inicial de la home")
def wait_initial_load(pages) -> None:
    home = pages.home()
    home.accept_cookies_if_present()
    home.wait_until_ready()


@then("el sitio responde correctamente")
def site_responds(home_status) -> None:
    assert home_status is not None, "La navegación no obtuvo respuesta HTTP"
    assert 200 <= home_status < 400, (
        f"El sitio respondió con status HTTP {home_status}"
    )


@then("la home queda en estado utilizable")
def home_usable(pages) -> None:
    home = pages.home()
    assert home.header.is_visible(), "El header de la home no es visible"
    assert not home.has_blockers(), (
        "Un overlay bloquea la interacción tras la carga inicial"
    )


# Paso 3 — identidad visual.
@then("la home se identifica con la marca del sitio activo")
def home_identifies_brand(pages, home_expectations) -> None:
    home = pages.home()
    title = home.title()
    assert home.header.is_logo_visible(), "El logo de la marca no es visible"
    assert home_expectations["expected_title_fragment"] in title, (
        f"El título {title!r} no identifica la marca "
        f"{home_expectations['expected_title_fragment']!r}"
    )


# Paso 4 — buscador.
@then("el buscador está visible y habilitado")
def search_box_usable(pages) -> None:
    assert pages.home().header.is_search_usable(), (
        "El buscador del header no está visible y habilitado"
    )


# Paso 5 — carrito.
@then("el acceso al carrito está visible y habilitado")
def cart_available(pages) -> None:
    assert pages.home().header.is_cart_available(), (
        "El acceso al carrito no está visible y habilitado"
    )


# Paso 6 — navegación principal.
@then("la navegación principal ofrece los elementos para comenzar una compra")
def main_nav_ready(pages, home_status, home_expectations) -> None:
    home = pages.home()
    items = home.header.main_nav_items()
    missing = [
        item for item in home_expectations["expected_nav_items"]
        if item not in items
    ]
    assert not missing, (
        f"Faltan elementos de navegación {missing}; disponibles: {items}"
    )
    attach_text(
        "Home",
        json.dumps(
            {
                "status": home_status,
                "title": home.title(),
                "nav_items": items,
            },
            ensure_ascii=False,
        ),
    )
