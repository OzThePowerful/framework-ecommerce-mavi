"""Genera test_cases/plane_catalog.yaml — catálogo normalizado de Test
Cases para Plane (EC-SP01-018).

El framework nunca llama a Plane directamente: este archivo es el
artefacto importable que el Bridge/Plane consume. Cada caso se define
una sola vez y se materializa por marca:

    muebles_america → CP_EC_MA_<MODULO>_<NNN>
    viu             → CP_EC_VIU_<MODULO>_<NNN>

Uso:  python scripts/build_plane_catalog.py
"""

from pathlib import Path

import yaml

OUTPUT = Path(__file__).resolve().parents[1] / "test_cases" / "plane_catalog.yaml"

ECOMMERCES = (
    ("muebles_america", "MA", "Muebles América"),
    ("viu", "VIU", "VIU"),
)

VALID_STATES = ("Not Automated", "In Development", "Automated", "Blocked")

# Definición única por módulo: `suffix` completa el Case ID.
CASES = [
    {
        "suffix": "HOME_001",
        "modulo": "Home",
        "titulo": "La home carga en estado utilizable e identifica la marca",
        "objetivo": (
            "Comprobar que la página principal carga correctamente y "
            "proporciona los controles mínimos para iniciar un flujo de compra."
        ),
        "prioridad": "Alta",
        "tipo": "Smoke",
        "precondiciones": (
            "Ambiente stage disponible; URL del sitio configurada; "
            "navegador soportado; conexión con el sitio."
        ),
        "datos": (
            "Dataset `home`/`home_001` (título de marca y elementos de "
            "navegación esperados)."
        ),
        "pasos": (
            "1. Navegar a la URL configurada. 2. Esperar la carga inicial. "
            "3. Validar la identidad visual. 4. Localizar el buscador. "
            "5. Localizar el acceso al carrito. 6. Revisar la navegación principal."
        ),
        "resultado_esperado": (
            "Sitio responde 2xx/3xx; home utilizable sin bloqueos; logo y "
            "título de la marca; buscador visible y habilitado; carrito "
            "disponible; navegación principal con 'Departamentos'."
        ),
        "postcondicion": "Sin cambios de estado en el sitio.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/home/home.feature",
        "tags": ["smoke", "regression", "home"],
    },
    {
        "suffix": "SEARCH_001",
        "modulo": "Search",
        "titulo": "Búsqueda con resultados devuelve cards elegibles y contador consistente",
        "objetivo": (
            "Verificar que el buscador devuelve resultados y que el "
            "scroll infinito carga todas las cards del contador."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Ambiente stage; catálogo con productos indexados.",
        "datos": "Dataset `search`/`with_results` (término, mínimo).",
        "pasos": (
            "1. Abrir home. 2. Buscar el término. 3. Leer contador. "
            "4. Cargar todas las cards por scroll."
        ),
        "resultado_esperado": (
            "Contador >= mínimo; cards cargadas == contador; "
            "existe card elegible."
        ),
        "postcondicion": "Sin cambios de estado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/search/search.feature",
        "tags": ["search", "regression", "scroll-infinito"],
    },
    {
        "suffix": "SEARCH_002",
        "modulo": "Search",
        "titulo": "Búsqueda sin resultados muestra el estado vacío",
        "objetivo": "Verificar el estado vacío correcto ante un término inexistente.",
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Ambiente stage.",
        "datos": "Dataset `search`/`without_results`.",
        "pasos": "1. Abrir home. 2. Buscar término inexistente.",
        "resultado_esperado": "Contador/estado de 0 resultados visible.",
        "postcondicion": "Sin cambios de estado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/search/search.feature",
        "tags": ["search", "estado-vacio"],
    },
    {
        "suffix": "PDP_001",
        "modulo": "PDP",
        "titulo": "La PDP expone el modelo Product con datos comerciales válidos",
        "objetivo": (
            "Verificar que la PDP produce un Product (nombre, SKU, "
            "precio, disponibilidad) consistente con la URL."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Ambiente stage; búsqueda con resultados.",
        "datos": "Producto elegible desde búsqueda.",
        "pasos": "1. Buscar. 2. Abrir card elegible. 3. Leer modelo Product.",
        "resultado_esperado": (
            "SKU coherente con URL, nombre no vacío, precio > 0, "
            "CTA habilitado."
        ),
        "postcondicion": "Sin cambios de estado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/product/pdp.feature",
        "tags": ["pdp", "product", "regression"],
    },
    {
        "suffix": "PDP_002",
        "modulo": "PDP",
        "titulo": "Un configurable expone padre y variantes como Product",
        "objetivo": (
            "Verificar el modelo de artículos configurables "
            "(padre MA/VIU distinto, hijos compartidos)."
        ),
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Ambiente stage; configurable con stock.",
        "datos": (
            "Dataset `products`/`configurable_colchon` "
            "(SKU padre por marca, variantes AMER00733-736)."
        ),
        "pasos": "1. Buscar el colchón. 2. Abrir la card. 3. Leer padre y variantes.",
        "resultado_esperado": (
            "SKU padre del dataset; 4 variantes con SKU/stock propios."
        ),
        "postcondicion": "Sin cambios de estado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/product/pdp.feature",
        "tags": ["pdp", "configurable"],
    },
    {
        "suffix": "CART_001",
        "modulo": "Cart",
        "titulo": "La integridad comercial Product→Cart se conserva",
        "objetivo": (
            "Verificar que el item del carrito coincide con el Product "
            "(SKU, nombre, qty, precio) y los importes del resumen."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Ambiente stage; producto con stock.",
        "datos": "Producto elegible.",
        "pasos": "1. Agregar a carrito. 2. Abrir /checkout/cart. 3. Comparar item y resumen.",
        "resultado_esperado": (
            "CartItem == Product esperado; subtotal/descuento/total "
            "consistentes."
        ),
        "postcondicion": "Producto queda en el carrito de la sesión.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/cart/cart.feature",
        "tags": ["cart", "integridad", "regression"],
    },
    {
        "suffix": "CART_002",
        "modulo": "Cart",
        "titulo": "Continuar al checkout desde el carrito muestra el gate de invitado",
        "objetivo": "Verificar la transición carrito → gate 'Continuar como invitado'.",
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Producto en carrito.",
        "datos": "Producto elegible.",
        "pasos": "1. Agregar. 2. Abrir carrito. 3. Continuar a checkout.",
        "resultado_esperado": "Botón 'Continuar como invitado' visible.",
        "postcondicion": "En la puerta del checkout.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/cart/cart.feature",
        "tags": ["cart", "checkout", "gate"],
    },
    {
        "suffix": "CHECKOUT_001",
        "modulo": "Checkout",
        "titulo": "Acceder al checkout como invitado expone los campos requeridos",
        "objetivo": "Verificar el gate de invitado y la etapa Entrega con campos obligatorios.",
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Producto en carrito; gate de invitado.",
        "datos": "—",
        "pasos": (
            "1. Continuar como invitado. 2. Esperar checkout listo. "
            "3. Revisar etapa y campos."
        ),
        "resultado_esperado": "Etapa 'entrega' activa; campos obligatorios presentes.",
        "postcondicion": "Checkout en etapa Entrega.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/checkout/checkout.feature",
        "tags": ["checkout", "guest"],
    },
    {
        "suffix": "CHECKOUT_002",
        "modulo": "Checkout",
        "titulo": "Registrar los datos del comprador habilita la etapa de pago",
        "objetivo": (
            "Verificar que el formulario acepta comprador+dirección y "
            "habilita Forma de pago."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": (
            "Checkout invitado en etapa Entrega; identidad MAVI_GUEST_* "
            "en .env."
        ),
        "datos": "Identidad `.env` + dataset `addresses`/`guadalajara` + `checkout`/`guest`.",
        "pasos": "1. Llenar formulario. 2. Autocompletar por CP. 3. Leer datos guardados.",
        "resultado_esperado": (
            "Datos aceptados sin errores; paymentExpansionButton "
            "habilitado."
        ),
        "postcondicion": "Dirección registrada en la sesión.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/checkout/checkout.feature",
        "tags": ["checkout", "customer", "address"],
    },
    {
        "suffix": "CHECKOUT_003",
        "modulo": "Checkout",
        "titulo": "Seleccionar el método de entrega expone el costo de envío",
        "objetivo": "Verificar toggle domicilio/sucursal y costo de envío calculado.",
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Comprador y dirección registrados.",
        "datos": "Dataset `checkout`/`guest`.shipping_method.",
        "pasos": "1. Seleccionar método de entrega. 2. Esperar cálculo de envío.",
        "resultado_esperado": (
            "Modo activo correcto; Shipping con costo Money disponible; "
            "pago habilitado."
        ),
        "postcondicion": "Método de entrega seleccionado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/checkout/checkout.feature",
        "tags": ["checkout", "shipping"],
    },
    {
        "suffix": "CUSTOMER_001",
        "modulo": "Customer",
        "titulo": "La captura del comprador persiste nombre, correo y teléfono",
        "objetivo": "Verificar que read_customer() recupera el Customer ingresado.",
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Checkout invitado; identidad MAVI_GUEST_*.",
        "datos": "Identidad `.env`.",
        "pasos": "1. Registrar comprador. 2. Leer el modelo Customer guardado.",
        "resultado_esperado": "Email/nombre/apellidos leídos == identidad ingresada.",
        "postcondicion": "Comprador registrado en la sesión.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/customer/customer.feature",
        "tags": ["customer"],
    },
    {
        "suffix": "ADDRESS_001",
        "modulo": "Address",
        "titulo": "La dirección autocompleta colonia, ciudad y estado desde el CP",
        "objetivo": (
            "Verificar el lookup por código postal y la lectura del "
            "modelo Address."
        ),
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Checkout invitado.",
        "datos": "Dataset `addresses`/`guadalajara` (CP 44100).",
        "pasos": "1. Capturar calle/número/CP. 2. Blur del CP. 3. Verificar autocompletado.",
        "resultado_esperado": (
            "Colonia AMERICANA, ciudad GUADALAJARA, estado Jalisco "
            "resueltos."
        ),
        "postcondicion": "Dirección registrada.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/address/address.feature",
        "tags": ["address", "cp-autocomplete"],
    },
    {
        "suffix": "SHIPPING_001",
        "modulo": "Shipping",
        "titulo": "La entrega a domicilio expone costo y estimación",
        "objetivo": (
            "Verificar el costo de envío a domicilio como Money y la "
            "estimación de entrega."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Dirección registrada.",
        "datos": "Dataset `checkout`/`guest`.",
        "pasos": "1. Seleccionar 'a_domicilio'. 2. Esperar 'Envío' en resumen.",
        "resultado_esperado": "Costo resuelto (Gratis o importe); estimación visible.",
        "postcondicion": "Envío calculado.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/shipping/shipping.feature",
        "tags": ["shipping", "costo-envio"],
    },
    {
        "suffix": "SHIPPING_002",
        "modulo": "Shipping",
        "titulo": "El retiro en sucursal abre el store picker y selecciona tienda",
        "objetivo": (
            "Verificar el picker de sucursal (modal, estados, tiendas, "
            "'Entregar aquí') y el contacto de pickup."
        ),
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Dirección registrada; tiendas disponibles en el estado.",
        "datos": "Estado Jalisco; tienda del listado.",
        "pasos": (
            "1. Seleccionar sucursal. 2. Abrir 'Seleccionar tienda'. "
            "3. Elegir estado y tienda. 4. Contacto pickup."
        ),
        "resultado_esperado": "Tienda seleccionada; modo StorePickupSelected activo.",
        "postcondicion": "Entrega en tienda configurada.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/shipping/shipping.feature",
        "tags": ["shipping", "pickup", "store-selector"],
    },
    {
        "suffix": "PAY_001",
        "modulo": "Payment",
        "titulo": "Seleccionar contado y preparar la orden sin confirmarla",
        "objetivo": (
            "Verificar la selección de openpay_cards con tarjeta "
            "sandbox hasta 'Finalizar compra' habilitado."
        ),
        "prioridad": "Alta",
        "tipo": "Funcional",
        "precondiciones": "Checkout completo (comprador, dirección, entrega).",
        "datos": "Dataset `payment`/`card` (sandbox OpenPay).",
        "pasos": (
            "1. Abrir etapa de pago. 2. Seleccionar tarjeta. "
            "3. Completar campos. 4. Verificar botón habilitado."
        ),
        "resultado_esperado": (
            "Método seleccionado sin errores; _btnCheckout habilitado "
            "(nunca clickeado)."
        ),
        "postcondicion": "Orden lista para confirmar; NO se crea orden.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/payment/payment.feature",
        "tags": ["payment", "contado", "openpay"],
    },
    {
        "suffix": "PAY_002",
        "modulo": "Payment",
        "titulo": "El pago en efectivo no es seleccionable por encima de $30,000",
        "objetivo": (
            "Verificar la regla de negocio: openpay_stores deshabilitado "
            "con total > $30,000 MXN."
        ),
        "prioridad": "Media",
        "tipo": "Funcional (negocio)",
        "precondiciones": "Carrito con total > $30,000 MXN.",
        "datos": "Producto/carrito de alto monto (pendiente de dataset).",
        "pasos": "1. Armar carrito > $30k. 2. Checkout. 3. Verificar radio openpay_stores.",
        "resultado_esperado": "Radio 'Efectivo' presente pero disabled → no seleccionable.",
        "postcondicion": "Sin cambios.",
        "automatizable": True,
        "estado_automatizacion": "Not Automated",
        "implementacion": (
            "Escenario @pending en test_cases/common/payment/"
            "payment.feature; falta dataset de alto monto"
        ),
        "tags": ["payment", "regla-negocio", "openpay-stores"],
    },
    {
        "suffix": "PAY_003",
        "modulo": "Payment",
        "titulo": "El contado a MSI se prepara con la tarjeta 4242",
        "objetivo": (
            "Verificar el flujo de meses sin intereses (contado diferido "
            "bancario) con 4242…4242."
        ),
        "prioridad": "Media",
        "tipo": "Funcional",
        "precondiciones": "Checkout completo.",
        "datos": "Dataset `payment`/`card_msi` (sandbox).",
        "pasos": "1. Seleccionar tarjeta. 2. Capturar 4242…4242. 3. Verificar opción MSI si aplica.",
        "resultado_esperado": "Método seleccionado; _btnCheckout habilitado.",
        "postcondicion": "Orden lista; NO se confirma.",
        "automatizable": True,
        "estado_automatizacion": "Not Automated",
        "implementacion": ("Escenario @pending en test_cases/common/payment/payment.feature; falta wiring MSI"),
        "tags": ["payment", "msi", "contado"],
    },
    {
        "suffix": "ORDER_001",
        "modulo": "Order",
        "titulo": "Confirmar la compra genera una orden con folio verificable",
        "objetivo": (
            "Ejecutar 'Finalizar compra' y capturar folio + mensaje de "
            "éxito inequívoco."
        ),
        "prioridad": "Alta",
        "tipo": "E2E",
        "precondiciones": "Stage autorizado para órdenes de prueba; identidad real MAVI_GUEST_*.",
        "datos": "Tarjeta sandbox + identidad real.",
        "pasos": (
            "1. Flujo completo hasta pago. 2. confirm_order(). "
            "3. Verificar página de éxito y folio."
        ),
        "resultado_esperado": (
            "URL onepage/success; .checkout-success con "
            "'Tu N° de pedido es: #NNNNNNNNNN'."
        ),
        "postcondicion": "Orden REAL creada en stage (folio en Allure).",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/order/order.feature",
        "tags": ["order", "e2e", "irreversible"],
    },
    {
        "suffix": "ORDER_002",
        "modulo": "Order",
        "titulo": "La orden es consistente con los datos comerciales del flujo",
        "objetivo": "Comparar la orden contra Product, Cart, Shipping, total y método de pago.",
        "prioridad": "Alta",
        "tipo": "E2E",
        "precondiciones": "Stage autorizado para órdenes de prueba.",
        "datos": "Tarjeta sandbox + identidad real.",
        "pasos": (
            "1. Flujo completo + resumen previo. 2. Confirmar. "
            "3. Comparar folio/importes/método."
        ),
        "resultado_esperado": (
            "Subtotal/Envío/Total del resumen == Cart+Shipping; "
            "método == openpay_cards."
        ),
        "postcondicion": "Orden REAL creada en stage.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": "test_cases/common/order/order.feature",
        "tags": ["order", "consistencia", "irreversible"],
    },
    {
        "suffix": "SMOKE_001",
        "modulo": "Smoke",
        "titulo": "Smoke: guest checkout muestra un precio de pedido mayor a cero",
        "objetivo": (
            "Verificación rápida del flujo navegación → checkout "
            "invitado con precio > 0."
        ),
        "prioridad": "Alta",
        "tipo": "Smoke",
        "precondiciones": "Ambiente stage.",
        "datos": "Dataset `guest_checkout`.",
        "pasos": "1. Home → departamento → PDP → carrito → invitado. 2. Leer precio mostrado.",
        "resultado_esperado": "Precio del pedido > 0 como Money.",
        "postcondicion": "Sin cambios.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": (
            "test_cases/common/smoke/sale_cash.feature "
            "(GuestCheckoutWorkflow)"
        ),
        "tags": ["smoke", "regression"],
    },
    {
        "suffix": "E2E_001",
        "modulo": "E2E",
        "titulo": "Flujo completo de venta de contado Home→Order",
        "objetivo": (
            "Ejecutar el recorrido E2E consolidado: búsqueda, PDP, "
            "carrito, checkout, pago y orden."
        ),
        "prioridad": "Alta",
        "tipo": "E2E",
        "precondiciones": "Stage autorizado para órdenes; identidad y tarjeta de prueba.",
        "datos": "Datasets search/products/checkout/payment + .env.",
        "pasos": (
            "Home → Search → PDP → Cart → Guest → Customer → Address → "
            "Shipping → Payment → Order."
        ),
        "resultado_esperado": "Orden creada con folio y datos consistentes de extremo a extremo.",
        "postcondicion": "Orden REAL creada en stage.",
        "automatizable": True,
        "estado_automatizacion": "Automated",
        "implementacion": (
            "test_cases/common/e2e/e2e.feature "
            "(SaleCashWorkflow, confirm_order=True)"
        ),
        "tags": ["e2e", "contado", "irreversible"],
    },
]


def build_catalog() -> dict:
    cases = []
    for site_key, site_id, site_name in ECOMMERCES:
        for case in CASES:
            state = (
                case.get(f"estado_automatizacion_{site_key}")
                or case["estado_automatizacion"]
            )
            impl = (
                case.get(f"implementacion_{site_key}")
                or case["implementacion"]
            )
            cases.append(
                {
                    "id": f"CP_EC_{site_id}_{case['suffix']}",
                    "titulo": case["titulo"],
                    "objetivo": case["objetivo"],
                    "prioridad": case["prioridad"],
                    "tipo": case["tipo"],
                    "ecommerce": site_name,
                    "ecommerce_key": site_key,
                    "modulo": case["modulo"],
                    "precondiciones": case["precondiciones"],
                    "datos": case["datos"],
                    "pasos": case["pasos"],
                    "resultado_esperado": case["resultado_esperado"],
                    "postcondicion": case["postcondicion"],
                    "automatizable": case["automatizable"],
                    "estado_automatizacion": state,
                    "implementacion": impl,
                    "tags": case["tags"],
                }
            )
    return {
        "catalogo": "Test Cases Ecommerce — flujo venta de contado Sprint 01",
        "fuente_de_verdad": "Plane (este artefacto es la entrada normalizada)",
        "convencion_id": "CP_EC_<MA|VIU>_<MODULO>_<NNN>",
        "estados_validos": list(VALID_STATES),
        "total_casos": len(cases),
        "casos": cases,
    }


def main() -> None:
    catalog = build_catalog()
    OUTPUT.write_text(
        yaml.safe_dump(
            catalog,
            allow_unicode=True,
            sort_keys=False,
            width=140,
        ),
        encoding="utf-8",
    )
    print(f"Catálogo generado: {OUTPUT} ({catalog['total_casos']} casos)")


if __name__ == "__main__":
    main()
