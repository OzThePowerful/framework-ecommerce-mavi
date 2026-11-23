"""Componente PDP: lee el estado del producto y construye el modelo Product.

Contrato de disponibilidad (regla de venta verificada):
  stock.is_in_stock && stock.qty > 0 && status == 1 && visibility == 4

`price`/`final_price` = precio vigente; `regular_price`/`original_price` =
precio de lista → si final < regular hay `promotional_price`.
"""

from decimal import Decimal

from playwright.sync_api import Page

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

    def read_product(self) -> Product:
        """Convierte el estado observado en el modelo de dominio Product."""
        cur = self._current()
        regular = Decimal(
            str(cur.get("regular_price") or cur.get("original_price") or cur["price"])
        )
        final = Decimal(str(cur.get("final_price") or cur["price"]))
        stock = cur.get("stock") or {}
        return Product(
            sku=str(cur["sku"]),
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
        """Regla de venta: activo, visible y con stock positivo."""
        cur = self._current()
        stock = cur.get("stock") or {}
        return bool(
            stock.get("is_in_stock")
            and int(stock.get("qty") or 0) > 0
            and cur.get("status") == self.REQUIRED_STATUS
            and cur.get("visibility") == self.REQUIRED_VISIBILITY
        )

    def is_add_to_cart_enabled(self) -> bool:
        """Estado del CTA de agregar al carrito."""
        return self.page.locator(PdpLocators.ADD_TO_CART).first.is_enabled()

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
