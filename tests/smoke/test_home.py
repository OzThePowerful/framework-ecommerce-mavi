"""E2E Home: la pantalla abre en estado utilizable y se identifica la marca.

Casos: CP_EC_MA_HOME_001 (--site muebles_america) y
CP_EC_VIU_HOME_001 (--site viu). El test es agnóstico de marca: el sitio lo
selecciona el ExecutionContext y las expectativas salen del dataset `home`
vía DataProvider; los asserts viven aquí, no en los pages.
"""

import pytest

pytestmark = pytest.mark.smoke


@pytest.fixture
def home_expectations(data_provider) -> dict:
    return data_provider.get_record("home", "home_001")


def test_home_001_estado_utilizable_y_marca(
    pages, execution_context, home_expectations
):
    home = pages.home()
    home.open_home()
    home.accept_cookies_if_present()
    home.wait_until_ready()

    assert home.header.is_visible(), "El header debería estar visible"
    assert home.header.search_box().count() == 1, (
        "Debería existir un buscador accesible en el header"
    )
    assert home.header.is_cart_accessible(), (
        "El acceso al carrito debería estar visible"
    )
    assert home.header.is_account_accessible(), (
        "El acceso a la cuenta debería estar visible"
    )
    assert not home.has_blockers(), (
        "No debería quedar ningún bloqueo tras descartar los iniciales"
    )
    assert home.brand() == home_expectations["expected_brand"], (
        f"La marca debería ser {home_expectations['expected_brand']}"
    )
    assert home_expectations["expected_title_fragment"] in home.page.title(), (
        "El título debería identificar la marca del ecommerce"
    )
