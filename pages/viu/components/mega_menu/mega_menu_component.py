"""Menú de departamentos de VIU (hover: trigger → departamento → link).

A diferencia de MA (2 niveles), VIU tiene un trigger raíz
'Departamentos' y luego departamento → link de categoría. El panel
anima al abrirse; se espera a que cada nivel quede quieto y se
reintenta si el menú se cierra a mitad de la interacción.
"""

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import ElementStateError
from pages.viu.components.mega_menu.mega_menu_locators import (
    MegaMenuLocators,
)

_POLL_INTERVAL_MS = 100


class MegaMenuComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_category(
        self, department: str, category: str, href: str, attempts: int = 3
    ) -> None:
        """Navega Departamentos → departamento → link de la categoría."""
        trigger = self.page.locator(MegaMenuLocators.DEPARTMENTS_TRIGGER)
        department_item = self.page.locator(
            MegaMenuLocators.DEPARTMENT_ITEM.format(department=department)
        )
        link = self.page.locator(MegaMenuLocators.CATEGORY_LINK.format(href=href))

        for attempt in range(1, attempts + 1):
            try:
                self.page.mouse.move(0, 0)
                trigger.hover()
                try:
                    # El menú es Vue: un hover antes de la hidratación se
                    # pierde. El click es el trigger alterno (no cierra el
                    # panel si ya está abierto).
                    department_item.wait_for(state="visible", timeout=3000)
                except PlaywrightTimeoutError:
                    trigger.click()
                self._wait_until_stable(department_item)
                department_item.hover()
                self._wait_until_stable(link)
                # Los items del panel siguen recolocándose tras abrirse:
                # un <li> vecino puede interceptar el punto del click.
                panel = self.page.locator(
                    ".categories-modal:visible >> visible=true"
                ).first
                self._wait_until_stable(panel)
                try:
                    link.click(timeout=3000)
                except PlaywrightTimeoutError:
                    link.dispatch_event("click")
                return
            except (PlaywrightTimeoutError, ElementStateError) as exc:
                if attempt == attempts:
                    raise ElementStateError(
                        f"No se pudo abrir 'Departamentos > {department} > "
                        f"{category}' desde el menú tras {attempts} intentos"
                    ) from exc

    def _wait_until_stable(self, locator: Locator, timeout_ms: int = 5000) -> None:
        """Espera a que el elemento sea visible y su caja deje de moverse."""
        locator.wait_for(state="visible", timeout=timeout_ms)
        previous = None
        for _ in range(timeout_ms // _POLL_INTERVAL_MS):
            box = locator.bounding_box(timeout=timeout_ms)
            if box is not None and box == previous:
                return
            previous = box
            self.page.wait_for_timeout(_POLL_INTERVAL_MS)
        raise ElementStateError(
            f"El elemento no dejó de moverse en {timeout_ms} ms"
        )
