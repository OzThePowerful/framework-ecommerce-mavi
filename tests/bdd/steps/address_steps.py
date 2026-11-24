"""Steps BDD del contrato común de Address (test_cases/common/address/).

Verifica que el lookup por código postal autocompletó los campos de la
dirección guardada contra el dataset. Sin locators ni Playwright.
"""

import json

from pytest_bdd import then

from core.reporting.allure_manager import attach_text


@then("la dirección autocompleta colonia, ciudad y estado del dataset")
def address_autocomplete_matches_dataset(checkout_ctx) -> None:
    expected = checkout_ctx["expected_address"]
    saved = checkout_ctx["checkout"].read_address()

    # El sitio normaliza los campos autocompletados a mayúsculas.
    assert saved.neighborhood.casefold() == expected.neighborhood.casefold(), (
        f"Colonia {saved.neighborhood!r} != dataset {expected.neighborhood!r}"
    )
    assert saved.city.casefold() == expected.city.casefold(), (
        f"Ciudad {saved.city!r} != dataset {expected.city!r}"
    )
    assert saved.state.casefold() == expected.state.casefold(), (
        f"Estado {saved.state!r} != dataset {expected.state!r}"
    )
    attach_text(
        "Address",
        json.dumps(
            {
                "zip_code": saved.zip_code,
                "neighborhood": saved.neighborhood,
                "city": saved.city,
                "state": saved.state,
            },
            ensure_ascii=False,
        ),
    )
