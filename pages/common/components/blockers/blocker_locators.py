"""Locators de bloqueos transversales (cookie banner, overlays).

closeCookieButton verificado en EC-SP01-008: idéntico en MA y VIU.
"""


class BlockerLocators:
    COOKIE_CLOSE_BUTTON = "[data-testid='closeCookieButton']"
    OVERLAY = "div.modal-backdrop:visible, [class*='overlay']:visible"
