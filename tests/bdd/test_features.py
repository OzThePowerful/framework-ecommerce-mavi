"""Runner BDD del Framework Ecommerce MAVI.

Los .feature viven en test_cases/<ámbito>/<modulo>/ (contrato funcional)
y los steps delgados en tests/bdd/steps/. El contrato común se
materializa por marca vía --site: cada escenario lleva su tag de caso
(@<MODULO>_<NNN>) y el hook de colección lo renombra a
CP_EC_<CODE>_<MODULO>_<NNN> (ver conftest.py).

test_cases/<sitio>/ contiene escenarios exclusivos de una marca (tag de
marca a nivel de Feature): en esa marca reemplazan al común con el mismo
tag de caso y en las demás se descartan (MA-AISLAMIENTO-001,
fixtures/execution_fixtures.py::keep_for_site).
"""

from pathlib import Path

from pytest_bdd import scenarios

from tests.bdd.steps.address_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.cart_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.checkout_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.e2e_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.home_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.muebles_america.cart_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.checkout_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.e2e_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.home_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.order_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.payment_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.pdp_steps import *  # noqa: F401,F403
from tests.bdd.steps.muebles_america.search_steps import *  # noqa: F401,F403
from tests.bdd.steps.order_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.payment_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.pdp_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.sale_cash_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.search_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.shipping_steps import *  # noqa: F401,F403  (registra steps)

_TEST_CASES = Path(__file__).resolve().parents[2] / "test_cases"
_COMMON = _TEST_CASES / "common"

scenarios(str(_COMMON))
# Escenarios exclusivos por marca (p.ej. test_cases/muebles_america/).
for _site_dir in sorted(p for p in _TEST_CASES.iterdir() if p.is_dir()):
    if _site_dir != _COMMON and any(_site_dir.rglob("*.feature")):
        scenarios(str(_site_dir))
