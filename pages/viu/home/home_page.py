"""Home de VIU: fachada de pantalla que compone componentes comunes."""

from typing import ClassVar

from pages.common.pages.home_page import CommonHomePage
from pages.viu.components.mega_menu.mega_menu_component import (
    MegaMenuComponent,
)


class HomePage(CommonHomePage):
    MEGA_MENU: ClassVar[type] = MegaMenuComponent
