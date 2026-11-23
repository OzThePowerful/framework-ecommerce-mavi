"""Utilidades de campos KO compartidas por los componentes del checkout."""

from playwright.sync_api import Page


def fill_visible(page: Page, selector: str, value: str) -> None:
    field = page.locator(selector).first
    field.wait_for(state="visible")
    field.fill(value)


def value(page: Page, selector: str) -> str:
    return page.locator(selector).first.input_value()


def value_or_none(page: Page, selector: str) -> str | None:
    text = page.locator(selector).first.input_value()
    return text or None


def first_non_empty(page: Page, selector: str) -> str | None:
    """Primer valor no vacío entre instancias KO duplicadas/ocultas."""
    fields = page.locator(selector)
    for i in range(fields.count()):
        text = fields.nth(i).input_value()
        if text:
            return text
    return None


def selected_label(page: Page, selector: str) -> str | None:
    select = page.locator(selector).first
    selected = select.locator("option:checked")
    if not selected.count():
        return None
    label = selected.first.inner_text().strip()
    return label or None
