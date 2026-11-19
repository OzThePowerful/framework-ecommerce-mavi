"""Componente Notification: interacciones genéricas sobre toasts/aviso.

El selector concreto lo aporta cada page desde sus propios locators.
"""

from playwright.sync_api import Page


class NotificationComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def click(self, selector: str) -> None:
        self.page.locator(selector).first.click()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).first.is_visible()
