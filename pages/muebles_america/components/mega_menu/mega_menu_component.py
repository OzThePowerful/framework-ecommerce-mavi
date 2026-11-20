"""Menú de departamentos de Muebles América (se abre por hover y anima)."""

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import ElementStateError
from pages.muebles_america.components.mega_menu.mega_menu_locators import (
    MegaMenuLocators,
)

_POLL_INTERVAL_MS = 100


class MegaMenuComponent:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open_category(
        self, department: str, category: str, href: str, attempts: int = 3
    ) -> None:
        """Navega departamento → categoría → link de la categoría.

        El menú anima al abrirse: si se interactúa a mitad de la animación el
        mouse queda fuera y el menú se cierra. Se espera a que cada nivel quede
        quieto y, si aun así se cierra, se reintenta desde el inicio.
        """
        department_btn = self.page.locator(
            MegaMenuLocators.DEPARTMENT_BUTTON.format(department=department)
        )
        category_trigger = self.page.locator(
            MegaMenuLocators.CATEGORY_TRIGGER.format(category=category)
        )
        link = self.page.locator(MegaMenuLocators.CATEGORY_LINK.format(href=href))

        for attempt in range(1, attempts + 1):
            try:
                self.page.mouse.move(0, 0)
                department_btn.hover()
                self._wait_until_stable(category_trigger)
                category_trigger.hover()
                self._wait_until_stable(link)
                # click() mueve el mouse en un solo salto hasta el link, así no
                # pasa por encima de otras categorías del menú.
                link.click(timeout=5000)
                return
            except (PlaywrightTimeoutError, ElementStateError) as exc:
                if attempt == attempts:
                    raise ElementStateError(
                        f"No se pudo abrir '{department} > {category}' desde el "
                        f"menú tras {attempts} intentos"
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
