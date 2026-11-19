"""Componente Header: los pages lo componen; sin herencia profunda."""

from playwright.sync_api import Page

from pages.common.components.header.header_locators import HeaderLocators


class HeaderComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(HeaderLocators.ROOT).first.is_visible()
