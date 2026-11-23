"""Componente Loader: esperas observables de indicadores de carga."""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.common.components.loader.loader_locators import LoaderLocators


class LoaderComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def wait_until_hidden(self, selector: str = LoaderLocators.GENERIC) -> None:
        self.page.wait_for_selector(selector, state="detached")

    def any_visible(self, appear_timeout: int = 1000) -> bool:
        """Detecta si aparece algún loader; tolerante a que nunca aparezca."""
        try:
            self.page.locator(LoaderLocators.GENERIC_VISIBLE).first.wait_for(
                state="visible", timeout=appear_timeout
            )
        except PlaywrightTimeoutError:
            return False
        return True

    def wait_until_idle(self, appear_timeout: int = 1000) -> None:
        """Si un loader aparece, espera a que desaparezca."""
        if self.any_visible(appear_timeout):
            self.page.locator(LoaderLocators.GENERIC_VISIBLE).first.wait_for(
                state="hidden"
            )
