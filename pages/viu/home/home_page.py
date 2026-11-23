"""Home de VIU: fachada de pantalla que compone componentes comunes."""

from playwright.sync_api import Page

from core.execution.execution_context import ExecutionContext
from pages.base_page import BasePage
from pages.common.components.blockers.blocker_component import BlockerComponent
from pages.common.components.header.header_component import HeaderComponent
from pages.common.components.loader.loader_component import LoaderComponent
from pages.common.components.notifications.notification_component import (
    NotificationComponent,
)


class HomePage(BasePage):
    def __init__(self, page: Page, context: ExecutionContext) -> None:
        super().__init__(page, context)
        self.header = HeaderComponent(page)
        self.blockers = BlockerComponent(page)
        self.loader = LoaderComponent(page)
        self.notifications = NotificationComponent(page)

    def open_home(self) -> None:
        """Abre la home resolviendo la URL desde el ExecutionContext."""
        self.open("/")

    def wait_until_ready(self) -> None:
        """Estado utilizable: header operativo y loaders resueltos."""
        self.header.wait_until_ready()
        self.loader.wait_until_idle()

    def brand(self) -> str:
        """Identificador de marca del sitio activo en el contexto."""
        return self.context.site

    def accept_cookies_if_present(self) -> None:
        self.blockers.dismiss_cookies()

    def has_blockers(self) -> bool:
        """Detecta overlays/backdrops que interceptan la interacción."""
        return self.blockers.has_overlay()
