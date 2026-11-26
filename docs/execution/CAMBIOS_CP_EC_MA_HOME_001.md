# CAMBIOS CP_EC_MA_HOME_001 — Validar carga correcta del Home de Muebles América

## Alcance

Alinear el escenario BDD `@HOME_001` con los 6 pasos del contrato
`Context_Contratos/MA/CP_EC_MA_HOME_001.md` (un step por paso).

El caso ya existía y pasaba, pero cubría el contrato solo en parte:

| # | Paso del contrato | Antes | Ahora |
|---|---|---|---|
| 1 | El sitio responde correctamente | No se miraba la respuesta HTTP | Status 2xx/3xx de la navegación |
| 2 | Estado utilizable | Esperas sin comprobar bloqueos | Header visible + sin overlays bloqueantes |
| 3 | Se identifica como Muebles América | `brand() == context.site`: comparaba el contexto consigo mismo y siempre pasaba | Logo visible + título con la marca del dataset |
| 4 | Buscador visible y habilitado | Contaba el botón `subscribeSubmit` | Input de búsqueda `is_visible` + `is_enabled` |
| 5 | Acceso al carrito disponible | No cubierto en BDD | Botón minicart visible + habilitado |
| 6 | Navegación principal | No cubierto | `nav.desktop-navbar` contiene los elementos del dataset (`Departamentos`) |

El `.feature` es común, así que `CP_EC_VIU_HOME_001` (contrato con los
mismos 6 pasos) queda alineado sin código adicional.

## Cambios

| Pieza | Detalle |
|---|---|
| `test_cases/common/home/home.feature` | Escenario `@HOME_001` reescrito: 8 steps 1:1 con el contrato; tags `@smoke @home` del contrato |
| `tests/bdd/steps/home_steps.py` | Steps nuevos delgados (asserts solo aquí) + fixture `home_expectations`; adjunto Allure "Home" con `status`, `title` y `nav_items`. Se retiran los steps `la home identifica la marca…` y `el buscador está accesible`, que solo usaba este escenario |
| `pages/common/components/header/header_locators.py` | `HOME_LOGO` y `MAIN_NAV_ITEMS`, verificados en stage MA y VIU. Se retiran `NAV` y `LOGO`, que no se usaban y no se habían verificado |
| `pages/common/components/header/header_component.py` | `is_search_usable()`, `is_cart_available()`, `is_logo_visible()`, `main_nav_items()`: devuelven estado, sin asserts |
| `pages/base_page.py` | `open()` devuelve el status HTTP (`int \| None`); primitiva genérica |
| `pages/common/pages/home_page.py` | `open_home()` propaga el status; `title()` del documento |
| `data/muebles_america/home.yaml`, `data/viu/home.yaml` | `expected_nav_items: ["Departamentos"]`. Es la entrada estructural al catálogo; Promociones y OUTLET quedan fuera porque son contenido comercial que cambia |
| `pytest.ini` | Marker `home` registrado |
| `scripts/build_plane_catalog.py` → `test_cases/plane_catalog.yaml` | Definición `HOME_001` actualizada al contrato (objetivo, precondiciones, datos, pasos, resultado) y catálogo regenerado. Solo cambian las entradas MA/VIU HOME |

Locators verificados en el DOM de stage (desktop 1366×768):

| Elemento | MA | VIU |
|---|---|---|
| `a[href='/'][title='Página de Inicio']` | `<img src="/assets/muebles-america-logo.png">` | `<svg>` |
| `nav.desktop-navbar button` | Departamentos, Promociones, Créditos, OUTLET | Departamentos, Promociones, Créditos, Regalos, OUTLET |
| `input[type=search][aria-label=Buscar]:visible` | visible, habilitado | visible, habilitado |

## Comandos

```bash
pytest tests/bdd/test_features.py --case-id CP_EC_MA_HOME_001
pytest tests/bdd/test_features.py --case-id CP_EC_VIU_HOME_001
pytest -m smoke --site muebles_america        # ahora incluye HOME_001 (5 items)
pytest -m "home" --site muebles_america        # solo escenarios de Home
```

## Requisitos del contrato

| Requisito | Cómo se cumple |
|---|---|
| Datos `site: muebles_america`, `environment: stage` | `--case-id CP_EC_MA_HOME_001` deriva el sitio; stage por defecto |
| Tags `@muebles_america @home @smoke` | `@home @smoke` en el escenario; la marca la materializa el Case ID |
| Asserts fuera de Page Objects | Solo en `home_steps.py` (arch test `test_page_objects_sin_asserts`) |
| Variación de marca sin `if site` | Título y navegación esperados salen del dataset por marca |
| Postcondición: ninguna | Escenario de solo lectura; no altera estado del sitio |

## Validación

Quality Gate (`guia_operacion.md`):

| Control | Resultado |
|---|---|
| `python -m compileall -q .` | ✅ |
| `ruff check .` | ✅ All checks passed |
| `pytest tests/unit tests/architecture -q` | ✅ 115 passed |
| `--collect-only` MA / VIU | ✅ 21 / 21 |

En vivo (stage):

| Ejecución | Resultado | Duración |
|---|---|---|
| Línea base previa `CP_EC_MA_HOME_001` | ✅ | 9.4s |
| `CP_EC_MA_HOME_001` run 1 | ✅ | 4.9s |
| `CP_EC_MA_HOME_001` run 2 | ✅ | 4.4s |
| `CP_EC_MA_HOME_001` run 3 | ✅ | 4.9s |
| `CP_EC_VIU_HOME_001` | ✅ | 10.1s |
| Smoke MA (`-m smoke --site muebles_america`) | ✅ 5 passed | 93.6s |
| Smoke VIU (`-m smoke --site viu`) | ✅ 5 passed | 135.6s |

Adjunto Allure MA: `{"status": 200, "title": "Muebles América - Donde pagas poco y llevas mucho - …", "nav_items": ["Departamentos", "Promociones", "Créditos", "OUTLET", "-"]}`.

Prueba negativa del paso 3: con `expected_title_fragment: "VIU"` en el
dataset de MA el caso **falla** (`El título 'Muebles América - …' no
identifica la marca 'VIU'`). El paso ya no pasa siempre. El dataset se
restauró después.

## Notas

- La suite `-m smoke` pasa de 4 a 5 items por marca porque se suma `CP_EC_<MARCA>_HOME_001`.
- `tests/smoke/test_home.py` (legado, EC-SP01-009) no se modifica en este cambio.
