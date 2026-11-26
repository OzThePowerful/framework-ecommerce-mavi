"""Runner BDD del Framework Ecommerce MAVI.

Los .feature viven en test_cases/<ámbito>/<modulo>/ (contrato funcional)
y los steps delgados en tests/bdd/steps/. El contrato común se
materializa por marca vía --site: cada escenario lleva su tag de caso
(@<MODULO>_<NNN>) y el hook de colección lo renombra a
CP_EC_<CODE>_<MODULO>_<NNN> (ver conftest.py).
"""

from pathlib import Path

from pytest_bdd import scenarios

from tests.bdd.steps.address_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.cart_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.checkout_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.e2e_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.home_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.order_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.payment_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.pdp_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.search_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.shipping_steps import *  # noqa: F401,F403  (registra steps)

_COMMON = Path(__file__).resolve().parents[2] / "test_cases" / "common"

scenarios(str(_COMMON))
