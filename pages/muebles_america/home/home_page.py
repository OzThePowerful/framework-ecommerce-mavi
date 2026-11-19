"""Home de Muebles América: fachada de pantalla que compone componentes."""

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.header.header_component import HeaderComponent
from pages.common.components.notifications.notification_component import (
    NotificationComponent,
)
from pages.muebles_america.home.home_locators import HomeLocators


class HomePage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.header = HeaderComponent(page)
        self.notifications = NotificationComponent(page)

    def open_home(self) -> None:
        """Abre la home resolviendo la URL desde el ExecutionContext."""
        self.open("/")

    def accept_cookies_if_present(self) -> None:
        button = self.page.locator(HomeLocators.COOKIE_CLOSE_BUTTON)
        if button.count() > 0:
            button.first.click()

    def close_promo_if_present(self) -> None:
        try:
            self.page.locator(HomeLocators.PROMO_CLOSE_BUTTON).click(timeout=3000)
        except PlaywrightTimeoutError:
            pass  # El popup promocional no siempre aparece; se continúa.

    def open_category_from_menu(
        self, department: str, category: str, href: str
    ) -> None:
        self.page.locator(
            HomeLocators.DEPARTMENT_BUTTON.format(department=department)
        ).hover()
        self.page.locator(
            HomeLocators.CATEGORY_BUTTON.format(category=category)
        ).hover()
        self.page.locator(HomeLocators.CATEGORY_LINK.format(href=href)).click()
