"""Runner BDD del Framework Ecommerce MAVI.

Los .feature viven en test_cases/<ámbito>/ (contrato funcional) y los steps
delgados en tests/bdd/steps/. El contrato común de búsqueda se materializa
por marca vía --site (CP_EC_MA_SEARCH_001/002, CP_EC_VIU_SEARCH_001/002).
"""

from pathlib import Path

from pytest_bdd import scenarios

from tests.bdd.steps.cart_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.checkout_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.order_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.payment_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.pdp_steps import *  # noqa: F401,F403  (registra steps)
from tests.bdd.steps.search_steps import *  # noqa: F401,F403  (registra steps)

_COMMON = Path(__file__).resolve().parents[2] / "test_cases" / "common"

scenarios(str(_COMMON / "search.feature"))
scenarios(str(_COMMON / "pdp.feature"))
scenarios(str(_COMMON / "cart.feature"))
scenarios(str(_COMMON / "checkout.feature"))
scenarios(str(_COMMON / "payment.feature"))
scenarios(str(_COMMON / "order.feature"))
