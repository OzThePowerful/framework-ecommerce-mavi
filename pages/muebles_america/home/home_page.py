"""Home de Muebles América: fachada de pantalla que compone componentes."""

from typing import ClassVar

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from pages.common.pages.home_page import CommonHomePage
from pages.muebles_america.components.header.header_component import (
    HeaderComponent,
)
from pages.muebles_america.components.mega_menu.mega_menu_component import (
    MegaMenuComponent,
)
from pages.muebles_america.home.home_locators import HomeLocators


class HomePage(CommonHomePage):
    MEGA_MENU: ClassVar[type] = MegaMenuComponent
    HEADER: ClassVar[type] = HeaderComponent

    def close_promo_if_present(self) -> None:
        try:
            self.page.locator(HomeLocators.PROMO_CLOSE_BUTTON).click(timeout=3000)
        except PlaywrightTimeoutError:
            return  # El popup promocional no siempre aparece; se continúa.
