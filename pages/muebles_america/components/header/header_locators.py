"""Locators del Header de Muebles América (solo definiciones).

Extienden los comunes con lo que usa CP_EC_MA_HOME_001, verificado en
stage MA (desktop 1366×768): el logo es el link a inicio con
`title='Página de Inicio'` (<img src="/assets/muebles-america-logo.png">)
y la navegación principal es `nav.desktop-navbar` con botones
(Departamentos, Promociones, Créditos, OUTLET).

Viven en la marca porque HOME_001 aplica solo a MA (MA-AISLAMIENTO-001):
VIU evoluciona su Home en su propia rama.
"""

from pages.common.components.header.header_locators import (
    HeaderLocators as CommonHeaderLocators,
)


class HeaderLocators(CommonHeaderLocators):
    HOME_LOGO = "header:visible a[href='/'][title='Página de Inicio']"
    MAIN_NAV_ITEMS = "header:visible nav.desktop-navbar button:visible"
