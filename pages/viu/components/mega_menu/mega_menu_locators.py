"""Locators del menú Departamentos (hover) de VIU.

Estructura verificada en stage: el botón 'Departamentos' abre por hover
un .categories-modal con .categories-list-desktop (botones por
departamento); el hover sobre un departamento revela los links <a> de
sus categorías (tercer nivel no requiere clic intermedio).
"""


class MegaMenuLocators:
    DEPARTMENTS_TRIGGER = "header button:has-text('Departamentos')"
    # El DOM contiene dos .categories-modal (desktop/móvil); solo el
    # visible expone la lista operable. Como en MA, al activarse el
    # departamento el sitio oculta el <button> y muestra un <a> con el
    # mismo texto: se acepta cualquiera de los dos.
    DEPARTMENT_ITEM = (
        ".categories-modal:visible .categories-list-desktop "
        ":is(button, a):has-text('{department}') >> visible=true"
    )
    CATEGORY_LINK = (
        ".categories-modal:visible a[href='{href}'] >> visible=true"
    )
