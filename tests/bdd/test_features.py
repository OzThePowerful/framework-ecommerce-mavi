"""Runner BDD del Framework Ecommerce MAVI.

Los .feature viven en test_cases/<ámbito>/ (contrato funcional) y los steps
delgados en tests/bdd/steps/. El contrato común de búsqueda se materializa
por marca vía --site (CP_EC_MA_SEARCH_001/002, CP_EC_VIU_SEARCH_001/002).
"""

from pathlib import Path

from pytest_bdd import scenarios

from tests.bdd.steps.search_steps import *  # noqa: F401,F403  (registra steps)

_COMMON = Path(__file__).resolve().parents[2] / "test_cases" / "common"

scenarios(str(_COMMON / "search.feature"))
