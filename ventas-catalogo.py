import sqlite3
import csv
import os

def inicializar_entorno ():

    try:
        conexion = sqlite3.connect("tienda_relacional.db")
        cursor= conexion.cursor ()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalogo (
                sku TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                costo REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_procesadas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES catalogo(sku)
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM catalogo")
        cantidad= cursor.fetchone()[0]

        if cantidad == 0:
            productos_iniciales = [
                ("AUR-001", "Auriculares Bluetooth TWS", 8500.0, 16900.0, 20),
                ("CAR-002", "Cargador Rapido USB-C 20 W", 4200.0, 9500.0, 35),
                ("FUN-003", "Funda Silicona Antigoles", 1500.0, 4500.0, 50),
                ("FUR-004", "Funda Poliamida Antigolpes", 2500.0, 5500.0, 40),
                ("V6D-005", "Vidrio Templado Clasico 9D", 600.0, 2500.0, 60),
                ("VSPY-006", "Vidrio Templado Anti Espia", 1500.0,3500.0, 30),
                ("CAB-007", "Cable Mallado Tipo C 2m", 1800.0, 4800.0, 15),
                ("USBA-008", "Cable Mallado USB-A 2m", 1500.0, 4500.0, 10)
            ]

            cursor.executemany(
                "INSERT INTO catalogo (sku, nombre, costo, precio_venta, stock) VALUES (?, ?, ?, ?, ?)",
                productos_iniciales
            )


        conexion.commit()
        conexion.close()

        if not os.path.exists("ventas_externas.csv"):
            with open("ventas_externas.csv", mode="w", newline="", encoding="utf-8") as archivo_csv:
                escritor = csv.writer(archivo_csv)
                escritor.writerow(["sku", "cantidad", "fecha"])
                escritor.writerow(["AUR-001", 3, "2026-11-24"])
                escritor.writerow(["V6D-004", 10, "2026-11-25"])
                escritor.writerow(["CAB-007", 2, "2026-11-24"])
                escritor.writerow(["SKU-999", 1, "2026-11-24"]) 
            print("Archivo de ejemplo 'ventas_externas.csv' generado.")

    except sqlite3.Error as error_bd:
        print(f"Error al inicializar la base de datos: {error_bd}") 

def ver_catalogo():
    try:
        conexion = sqlite3.connect ("tienda_relacional.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT sku, nombre, costo, precio_venta, stock FROM catalogo")
        filas = cursor.fetchall()

        print("\n--- CATÁLOGO Y STOCK ACTUAL ---")
        print(f"{'SKU':<8} | {'PRODUCTO':<28} | {'COSTO':<10} | {'VENTA':<10} | {'STOCK'}")
        print("-" * 74)

        for fila in filas:
            sku, nombre, costo, venta, stock = fila
            print(f"{sku:<8} | {nombre:<28} | ${costo:<9,.0f} | ${venta:<9,.0f} | {stock} u.")

        conexion.close()
    except sqlite3.Error as error_bd:
        print(f"Error al consultar el catálogo: {error_bd}")   

def procesar_ventas_csv():
    nombre_archivo = "ventas_externas.csv"

    try:
        conexion = sqlite3.connect("tienda_relacional.db")
        cursor = conexion.cursor ()

        with open (nombre_archivo, mode= "r", encoding="utf-8") as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            procesadas = 0

            print(f"\nLeyendo planilla '{nombre_archivo}'...")
            for fila in lector:
                sku = fila["sku"].strip()
                cantidad = int(fila["cantidad"])
                fecha = fila["fecha"].strip()

                cursor.execute("SELECT nombre, stock FROM catalogo WHERE sku = ?", (sku,))
                producto = cursor.fetchone()

                if producto is None:
                    print(f"  [OMITIDO] El código '{sku}' no existe en el catálogo.")
                else:
                    nombre_prod, stock_actual = producto
                    if cantidad > stock_actual:
                        print(f"  [SIN STOCK] '{nombre_prod}' ({sku}): se pidieron {cantidad} u., hay {stock_actual} u.")
                    else:
                        cursor.execute(
                            "UPDATE catalogo SET stock = stock - ? WHERE sku = ?",
                            (cantidad, sku)
                        )
                        cursor.execute(
                            "INSERT INTO ventas_procesadas (sku, cantidad, fecha) VALUES (?, ?, ?)",
                            (sku, cantidad, fecha)
                        )
                        procesadas += 1
                        print(f"  [OK] Venta conciliada: {cantidad}x {nombre_prod} ({fecha})")

        conexion.commit()
        conexion.close()
        print(f"\nConciliación finalizada. Se impactaron {procesadas} ventas correctamente.")
        
    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo '{nombre_archivo}' en la carpeta.")
    except ValueError:
        print("\nError: El archivo CSV contiene cantidades con formato inválido.")
    except sqlite3.Error as error_bd:
        print(f"\nError de base de datos durante la conciliación: {error_bd}")

        
def reportes_ganancias_join():

    try:
        conexion = sqlite3.connect("tienda_relacional.db")
        cursor= conexion.cursor ()


        cursor.execute("""
            SELECT
                c.sku,
                c.nombre,
                SUM(v.cantidad) AS total_unidades,
                SUM(v.cantidad * c.precio_venta) AS facturacion_total,
                SUM(v.cantidad * (c.precio_venta-c.costo)) AS ganancia_neta

            FROM ventas_procesadas v
            INNER JOIN catalogo c ON v.sku = c.sku
            GROUP BY c.sku, c.nombre
            ORDER BY ganancia_neta DESC
        """)
        resultados = cursor.fetchall()

        print("\n=== REPORTE DE FACTURACIÓN Y GANANCIA NETA (SQL JOIN) ===")
        if len(resultados) == 0:
            print("Todavía no hay ventas conciliadas para generar el reporte.")
        else:
            print(f"{'SKU':<8} | {'PRODUCTO':<26} | {'VENDIDOS':<8} | {'FACTURADO':<12} | {'GANANCIA NETA'}")
            print("-" * 80)

            ganancia_acumulada = 0.0
            for fila in resultados:
                sku, nombre, unidades, facturado, ganancia= fila
                ganancia_acumulada  += ganancia
                print(f"{sku:<8} | {nombre:<26} | {unidades:<8} | ${facturado:<11,.0f} | ${ganancia:,.0f}")

            print("_" * 80)
            print(f"GANANCIA NETA TOTAL DEL PERIODO: ${ganancia_acumulada:,.2f}")


        conexion.close()
    except sqlite3.Error as error_bd:
        print(f"Error al generar el reporte: {error_bd}")

def menu_principal():
    inicializar_entorno()
    continuar = True

    while continuar:
        print("\n=== CONCILIADOR DE VENTAS Y CATALOGO ===")
        print("1.Ver catalogo y stock actual")
        print("2.Importar y conciliar planilla 'ventas_externas.csv'")
        print("3.Ver reporte de facturacion y ganancia neta (JOIN)")
        print("4.Salir")

            
        opcion = input ("Elegi una opcion (1-4):").strip()

        if opcion == "1":
            ver_catalogo()
        elif opcion == "2":
            procesar_ventas_csv()
        elif opcion == "3":
            reportes_ganancias_join()
        elif opcion == "4":
            print("Cerrando el conciliador. ¡Hasta la vista Baby!")
            continuar = False
        else:
            print("Opción incorrecta. Elegí un número del 1 al 4.")

menu_principal()

         
    
            
