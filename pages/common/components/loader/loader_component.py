"""Componente Loader: esperas observables de indicadores de carga."""

from playwright.sync_api import Page

from pages.common.components.loader.loader_locators import LoaderLocators


class LoaderComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_hidden(self, selector: str = LoaderLocators.GENERIC) -> None:
        self.page.wait_for_selector(selector, state="detached")
