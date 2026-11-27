"""Steps BDD de Search exclusivos de Muebles América
(test_cases/muebles_america/search/ — CP_EC_MA_SEARCH_001 / _002).

Reutiliza los steps comunes de tests/bdd/steps/search_steps.py (home,
búsqueda, contador, scroll, card elegible, cero resultados); aquí solo
viven los que agregaron SEARCH_001/002 de MA. Sin locators ni
Playwright: delegan en SearchPage (MA-AISLAMIENTO-001).
"""

from pytest_bdd import then, when


@when(
    "captura en el buscador el término con resultados del dataset",
    target_fixture="search_ctx",
)
def type_term_with_results(pages, data_provider) -> dict:
    record = data_provider.get_record("search", "with_results")
    results = pages.search()
    results.type_term(record["term"])
    return {"record": record, "results": results}


@then("el buscador acepta el término capturado")
def search_box_accepts_term(search_ctx) -> None:
    expected = search_ctx["record"]["term"]
    typed = search_ctx["results"].typed_term()
    assert typed == expected, (
        f"El buscador contiene {typed!r}; se capturó {expected!r}"
    )


@when("ejecuta la búsqueda")
def submit_search(search_ctx) -> None:
    search_ctx["results"].submit_search()


@then("la búsqueda se procesa para el término capturado")
def search_processed(search_ctx) -> None:
    expected = search_ctx["record"]["term"]
    query = search_ctx["results"].results_query()
    assert query is not None, (
        "La búsqueda no navegó a la ruta de resultados; URL actual: "
        f"{search_ctx['results'].page.url}"
    )
    assert query == expected, (
        f"Los resultados corresponden a {query!r}; se buscó {expected!r}"
    )


@then("la pantalla de resultados queda disponible")
def results_view_ready(search_ctx) -> None:
    assert search_ctx["results"].is_results_view_ready(), (
        "La pantalla de resultados no muestra el contador de búsqueda"
    )


@then("se muestra al menos un producto en el listado")
def at_least_one_product_visible(search_ctx) -> None:
    visible = search_ctx["results"].visible_card_count()
    assert visible >= 1, "El listado no muestra ninguna card de producto"


@when(
    "captura en el buscador el término sin resultados del dataset",
    target_fixture="search_ctx",
)
def type_term_without_results(pages, data_provider) -> dict:
    record = data_provider.get_record("search", "without_results")
    results = pages.search()
    results.type_term(record["term"])
    return {"record": record, "results": results}


@then("no aparece ningún producto en el listado")
def no_product_visible(search_ctx) -> None:
    visible = search_ctx["results"].visible_card_count()
    assert visible == 0, (
        f"Una búsqueda sin coincidencias no debería mostrar productos; "
        f"el listado muestra {visible}"
    )
