"""Componente Footer."""

from playwright.sync_api import Page

from pages.common.components.footer.footer_locators import FooterLocators


class FooterComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def is_visible(self) -> bool:
        return self.page.locator(FooterLocators.ROOT).first.is_visible()
