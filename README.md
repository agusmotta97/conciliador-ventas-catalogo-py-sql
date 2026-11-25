# conciliador-ventas-catalogo-py-sql
Sistema en Python y SQLite para importar ventas desde archivos CSV, conciliar stock automáticamente y calcular ganancias netas mediante SQL JOIN.

# Conciliador de Ventas y Catálogo (Python + SQLite + CSV)

Sistema de gestión relacional por consola desarrollado en **Python** y **SQLite** diseñado para automatizar la importación de ventas desde planillas externas (`.csv`), actualizar el inventario y calcular reportes financieros de facturación y ganancia neta mediante consultas `INNER JOIN`.

## Problema comercial que resuelve
Los comercios que venden a través de múltiples canales (como Mercado Libre, tiendas online o cajas registradoras externas) suelen exportar sus ventas diarias en archivos CSV/Excel. Cruzar esa información manualmente contra el catálogo interno genera demoras operativas, errores de stock y falta de visibilidad sobre la rentabilidad real de cada artículo. Este programa automatiza la validación de códigos (SKU), el descuento de mercadería y el cálculo de márgenes limpios.

## Funcionalidades principales
* **Entorno autocontenido:** Inicializa automáticamente la base de datos relacional (`tienda_relacional.db`), carga un catálogo de prueba y genera un archivo de ejemplo (`ventas_externas.csv`) si no existen en el directorio.
* **Importación y conciliación masiva (`csv.DictReader`):** Lee planillas externas fila por fila, verifica la existencia del `SKU` en el catálogo y valida que haya disponibilidad física antes de descontar stock.
* **Registro histórico de operaciones:** Almacena cada venta conciliada en una tabla transaccional vinculada mediante clave foránea (`FOREIGN KEY`).
* **Reporte financiero con `INNER JOIN`:** Cruza la tabla de ventas con los costos y precios del catálogo para calcular unidades vendidas, facturación total y ganancia neta acumulada ordenada por rentabilidad.
* **Control de errores:** Manejo de excepciones mediante bloques `try / except` para gestionar archivos faltantes (`FileNotFoundError`), datos corruptos (`ValueError`) y errores de base de datos (`sqlite3.Error`).

## Estructura de la Base de Datos (Modelo Relacional)
El sistema trabaja con dos tablas relacionadas a través del código de producto (`sku`):

### Tabla 1: `catalogo` (Maestra de productos)

| Campo | Tipo de dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `sku` | `TEXT` | `PRIMARY KEY` | Código único identificador del artículo |
| `nombre` | `TEXT` | `NOT NULL` | Descripción del producto |
| `costo` | `REAL` | `NOT NULL` | Costo unitario de reposición |
| `precio_venta` | `REAL` | `NOT NULL` | Precio de venta al público |
| `stock` | `INTEGER` | `NOT NULL` | Unidades físicas disponibles |

### Tabla 2: `ventas_procesadas` (Historial conciliado)

| Campo | Tipo de dato | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id_venta` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Identificador único de la transacción |
| `sku` | `TEXT` | `NOT NULL`, `FOREIGN KEY` | Referencia al `sku` de la tabla `catalogo` |
| `cantidad` | `INTEGER` | `NOT NULL` | Unidades vendidas en la operación |
| `fecha` | `TEXT` | `NOT NULL` | Fecha de la venta importada |

## Tecnologías y buenas prácticas aplicadas
* **Lenguaje:** Python 3 (módulos estándar `sqlite3`, `csv` y `os`).
* **Base de datos:** SQLite3 con consultas de agregación (`SUM`, `GROUP BY`, `ORDER BY`) y cruce relacional (`INNER JOIN`).
* **Seguridad:** Consultas SQL parametrizadas (`?`) para prevenir inyección SQL.
* **Arquitectura:** Programación estructurada modular con control de flujo mediante variables bandera.

## Cómo ejecutar el proyecto
1. Asegurate de tener instalado **Python 3** en tu computadora.
2. Descargá o cloná este repositorio.
3. Abrí una terminal en la carpeta del proyecto y ejecutá:
   ```bash
   python ventas-catalogo.py
   ```
