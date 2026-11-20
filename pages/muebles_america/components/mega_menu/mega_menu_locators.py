"""Locators del menú de departamentos (hover) de Muebles América."""


class MegaMenuLocators:
    DEPARTMENT_BUTTON = "role=button[name='{department}']"
    # Al hacer hover, el sitio oculta el <button> de la categoría y muestra en
    # su lugar un <a> con el mismo texto; por eso se acepta cualquiera de los
    # dos, quedándose con el que esté visible. Se acota al <header> porque el
    # home tiene tiles de categoría con el mismo texto.
    CATEGORY_TRIGGER = "header :is(button, a):has-text('{category}') >> visible=true"
    CATEGORY_LINK = "a[href='{href}']"
