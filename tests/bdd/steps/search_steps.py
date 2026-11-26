"""Steps BDD del contrato común de búsqueda (test_cases/common/search.feature).

Steps delgados: coordinan Page Objects y DataProvider; sin locators ni
secuencias Playwright. El sitio lo decide el ExecutionContext (--site).
"""

from pytest_bdd import given, then, when


@given("el usuario abre la home del sitio activo")
def open_active_site_home(pages) -> None:
    home = pages.home()
    home.open_home()
    home.accept_cookies_if_present()
    home.wait_until_ready()


@when("busca el término con resultados del dataset", target_fixture="search_ctx")
def search_with_results(pages, data_provider) -> dict:
    record = data_provider.get_record("search", "with_results")
    results = pages.search()
    results.search(record["term"])
    return {"record": record, "results": results}


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


@then("se muestran al menos los resultados mínimos esperados")
def results_meet_minimum(search_ctx) -> None:
    minimum = int(search_ctx["record"]["min_results"])
    count = search_ctx["results"].result_count()
    assert count >= minimum, (
        f"Se esperaban >= {minimum} resultados; el contador reportó {count}"
    )


@then("las cards cargadas por scroll coinciden con el contador de resultados")
def loaded_cards_match_counter(search_ctx) -> None:
    results = search_ctx["results"]
    loaded = results.load_all_cards()
    total = results.result_count()
    assert loaded == total, (
        f"El contador declara {total} resultados pero el scroll cargó {loaded} cards"
    )


@then("existe al menos una card elegible con nombre, precio e identificador")
def eligible_card_exists(search_ctx) -> None:
    card = search_ctx["results"].eligible_card()
    assert card is not None, "No se encontró ninguna card elegible"
    assert card.name(), "La card elegible debería exponer nombre"
    assert card.price() > 0, "La card elegible debería tener precio válido"
    assert card.identifier(), "La card elegible debería exponer identificador"
    search_ctx["card"] = card


@then("la card elegible abre la PDP del producto")
def eligible_card_opens_pdp(search_ctx) -> None:
    card = search_ctx["card"]
    expected_href = card.identifier()
    card.open()
    current_url = search_ctx["results"].page.url
    slug = expected_href.split("?")[0]
    assert slug in current_url, (
        f"La PDP debería corresponder a {slug}; URL actual: {current_url}"
    )


@then("se muestran cero resultados")
def zero_results_shown(search_ctx) -> None:
    count = search_ctx["results"].result_count()
    expected = int(search_ctx["record"].get("expected_results", 0))
    assert count == expected, (
        f"Se esperaban {expected} resultados; el contador reportó {count}"
    )
