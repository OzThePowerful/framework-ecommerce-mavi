"""Locators de búsqueda y resultados — verificados idénticos en MA y VIU.

El texto "N resultados de búsqueda" es el observable de estado del SPA:
aparece tanto con resultados como con cero.

Al ejecutar la búsqueda el SPA navega a `RESULTS_ROUTE?q=<término>`
(verificado en stage MA y VIU — CP_EC_MA_SEARCH_001).
"""


class SearchLocators:
    GRID = "div.product-tile"
    RESULT_COUNT = "p:has-text('resultados de búsqueda')"
    RESULTS_ROUTE = "/catalogsearch/result"
    QUERY_PARAM = "q"
