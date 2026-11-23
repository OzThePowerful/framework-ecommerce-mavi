"""Locators de búsqueda y resultados — verificados idénticos en MA y VIU.

El texto "N resultados de búsqueda" es el observable de estado del SPA:
aparece tanto con resultados como con cero.
"""


class SearchLocators:
    GRID = "div.product-tile"
    RESULT_COUNT = "p:has-text('resultados de búsqueda')"
