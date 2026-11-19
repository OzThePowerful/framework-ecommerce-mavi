"""Punto de registro de plugins del Framework Ecommerce MAVI.

Permanece mínimo por diseño: la lógica vive en fixtures/*.
"""

pytest_plugins = [
    "fixtures.browser_fixtures",
    "fixtures.data_fixtures",
    "fixtures.evidence_fixtures",
    "fixtures.execution_fixtures",
    "fixtures.page_fixtures",
]
