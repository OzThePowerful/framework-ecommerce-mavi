"""Componente PDP: lee el estado del producto y construye el modelo Product.

Contrato de disponibilidad (regla de venta verificada):
  stock.is_in_stock && stock.qty > 0 && status == 1 && visibility == 4

`price`/`final_price` = precio vigente; `regular_price`/`original_price` =
precio de lista → si final < regular hay `promotional_price`.
"""

from decimal import Decimal

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.execution.execution_errors import FrameworkError
from domain.models.product import Product
from domain.money.money import Money
from pages.common.components.pdp.pdp_locators import PdpLocators


class PdpComponent:
    REQUIRED_STATUS = 1  # artículo activo
    REQUIRED_VISIBILITY = 4  # visible en catálogo y búsqueda

    def __init__(self, page: Page) -> None:
        self.page = page

    def _current(self) -> dict:
        data = self.page.evaluate(PdpLocators.CURRENT_PRODUCT_EXPR)
        if not isinstance(data, dict):
            raise FrameworkError(
                "La PDP no expone __INITIAL_STATE__.product.current."
            )
        return data

    def wait_until_ready(self) -> None:
        """PDP lista para sondear: estado del SPA cargado y veredicto de
        stock renderizado.

        Sin este wait, `is_available`/`is_add_to_cart_enabled` sondean una
        PDP a medio renderizar (badge aún no pintado) y devuelven falsos
        negativos. El badge agota su espera sin tronar: si la PDP no pinta
        etiqueta, `is_available` decide el veredicto.
        """
        self.page.wait_for_function(
            "() => window.__INITIAL_STATE__ && window.__INITIAL_STATE__.product"
            " && !!window.__INITIAL_STATE__.product.current"
        )
        try:
            self.page.locator(PdpLocators.STOCK_BADGE).first.wait_for(
                state="visible", timeout=5000
            )
        except PlaywrightTimeoutError:
            pass

    def read_product(self) -> Product:
        """Convierte el estado observado en el modelo de dominio Product."""
        cur = self._current()
        regular = Decimal(
            str(cur.get("regular_price") or cur.get("original_price") or cur["price"])
        )
        final = Decimal(str(cur.get("final_price") or cur["price"]))
        stock = cur.get("stock") or {}
        return Product(
            # "" = sku no expuesto: el llamador decide/documenta la ausencia
            # (CP_EC_MA_PDP_001 paso 4) en vez de tronar con KeyError.
            sku=str(cur.get("sku") or ""),
            name=str(cur["name"]),
            product_id=str(stock.get("product_id") or cur.get("id") or ""),
            unit_price=Money(regular),
            promotional_price=Money(final) if final < regular else None,
            availability=self.is_available(),
        )

    def stock_quantity(self) -> int:
        """Piezas disponibles en inventario (`stock.qty`)."""
        return int((self._current().get("stock") or {}).get("qty") or 0)

    def quantity(self) -> int:
        """Cantidad seleccionada en la PDP (sin stepper visible: default 1)."""
        return int(self._current().get("qty") or 1)

    def is_available(self) -> bool:
        """Regla de venta: activo, visible y con stock real.

        El stock se decide por la etiqueta observable: `cl-green-label`
        presente (cualquier variante positiva: 'Disponible', 'Solo queda
        1', 'Solo quedan N') y sin etiqueta 'Agotado' — el JSON del SPA
        llega desfasado (declara in-stock en productos agotados).
        """
        cur = self._current()
        stock = cur.get("stock") or {}
        has_stock_badge = (
            self.page.locator(PdpLocators.AVAILABILITY_BADGE).count() > 0
            and self.page.locator(PdpLocators.OUT_OF_STOCK_BADGE).count() == 0
        )
        return bool(
            stock.get("is_in_stock")
            and int(stock.get("qty") or 0) > 0
            and cur.get("status") == self.REQUIRED_STATUS
            and cur.get("visibility") == self.REQUIRED_VISIBILITY
            and has_stock_badge
        )

    def is_add_to_cart_enabled(self) -> bool:
        """Estado del CTA de agregar al carrito.

        Es un sondeo (`is_*`): cuando el producto está agotado el CTA no
        existe — devuelve False en vez de tronar con timeout, para que el
        llamador distinga 'no comprable' de 'no habilitado'.
        """
        cta = self.page.locator(PdpLocators.ADD_TO_CART)
        try:
            cta.first.wait_for(state="visible", timeout=5000)
        except PlaywrightTimeoutError:
            return False
        return cta.first.is_enabled()

    def type_id(self) -> str:
        """`simple` o `configurable` según el producto cargado."""
        return str(self._current().get("type_id") or "")

    def is_configurable(self) -> bool:
        return self.type_id() == "configurable"

    def parent_sku(self) -> str | None:
        """Sku del producto padre (solo configurables).

        El prefijo difiere por marca (p.ej. 1COLCxxxx en MA vs 2COLCxxxx en
        VIU); los sku hijos sí son compartidos.
        """
        sku = self._current().get("parentSku")
        return str(sku) if sku else None

    def variants(self) -> list[Product]:
        """Hijos de un configurable como Product (mismo contrato).

        Disponibilidad por hijo: is_in_stock && qty>0 && status==1.
        La regla visibility==4 aplica al padre: los hijos siempre tienen
        visibility=1 (no se exhiben individualmente).
        """
        cur = self._current()
        products: list[Product] = []
        for child in cur.get("configurable_children") or []:
            regular = Decimal(
                str(child.get("regular_price") or child.get("price") or 0)
            )
            final = Decimal(str(child.get("final_price") or regular))
            stock = child.get("stock") or {}
            available = bool(
                stock.get("is_in_stock")
                and int(stock.get("qty") or 0) > 0
                and child.get("status") == self.REQUIRED_STATUS
            )
            products.append(
                Product(
                    sku=str(child.get("sku") or ""),
                    name=str(child.get("name") or ""),
                    product_id=None,
                    unit_price=Money(regular),
                    promotional_price=Money(final) if final < regular else None,
                    availability=available,
                )
            )
        return products
