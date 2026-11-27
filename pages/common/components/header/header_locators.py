"""Locators del Header (solo definiciones; prohibido acciones/lógica).

Verificados en el DOM real de ambos sitios (EC-SP01-008/009): el header
existe duplicado (desktop/mobile) → las interacciones usan `:visible`.
En desktop el carrito se abre por `aria-label='Abrir minicart'` y la cuenta
por `a[href='/login']`; los data-testid openMicrocart/accountButton/
menuButton pertenecen al drawer móvil oculto.
"""


class HeaderLocators:
    ROOT = "header"
    VISIBLE_ROOT = "header:visible"
    NAV = "header nav:visible"
    LOGO = "header [class*='logo']"
    SEARCH_INPUT = "input[type='search'][aria-label='Buscar']:visible"
    SEARCH_SUBMIT = "button[data-testid='subscribeSubmit']:visible"
    CART_BUTTON = "header:visible button[aria-label='Abrir minicart']"
    ACCOUNT_LINK = "header:visible a[href='/login']"
    MENU_BUTTON = "[data-testid='menuButton']"  # drawer móvil (oculto en desktop)
