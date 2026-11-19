"""Runner BDD inicial del Framework Ecommerce MAVI.

Los .feature viven en test_cases/<sitio>/ (contrato funcional) y los steps
delgados en tests/bdd/steps/. Los escenarios se enlazan aquí conforme se
implementen sus steps, por ejemplo:

    from pytest_bdd import scenarios
    scenarios("../../test_cases/muebles_america/sale_cash.feature")
"""
