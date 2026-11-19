"""Primer test migrado desde Example_Valentin/test_UIValidations.py.

E2E UI Muebles América: Home → Línea blanca → PDP → carrito → checkout
como invitado. La URL sale de config/sites.yaml vía ExecutionContext;
los locators viven en pages/muebles_america/*_locators.py.
"""

import re

import pytest

pytestmark = pytest.mark.smoke

PRODUCT_NAME = "Campana Decorativa De Pared Midea MJWM7736S3GS"


def test_core_locators_grid_ma(pages):
    home = pages.home()
    home.open_home()
    home.accept_cookies_if_present()
    home.close_promo_if_present()
    home.open_category_from_menu(
        department="Departamentos",
        category="Línea blanca",
        href="/departamentos/linea-blanca.html",
    )

    listing = pages.search()
    listing.open_product(PRODUCT_NAME)

    product = pages.product()
    product.add_to_cart()
    product.open_cart_from_notification()

    cart = pages.cart()
    cart.buy_now()

    checkout = pages.checkout()
    checkout.continue_as_guest()
    checkout.wait_until_ready()
    price = checkout.get_displayed_price()

    assert price and re.search(r"\d", price), (
        "El checkout debería mostrar un precio con importe"
    )
