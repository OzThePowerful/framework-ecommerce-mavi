"""Punto de registro de plugins del Framework Ecommerce MAVI.

Permanece mínimo por diseño: la lógica vive en fixtures/*.
"""

from dotenv import load_dotenv

# Credenciales del equipo desde .env local (gitignored); las variables
# de entorno del ambiente/CI siempre tienen precedencia.
load_dotenv(override=False)

pytest_plugins = [
    "fixtures.browser_fixtures",
    "fixtures.data_fixtures",
    "fixtures.evidence_fixtures",
    "fixtures.execution_fixtures",
    "fixtures.page_fixtures",
]
