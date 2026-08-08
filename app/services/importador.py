import pandas as pd
import sqlite3
from app.database.database import conectar

# Mapeo flexible de encabezados del Excel -> Nombres de atributos en BD
MAPEO_COLUMNAS = {
    "codigo": "codigo",
    "código": "codigo",
    "codigo barras": "codigo_barras",
    "código barras": "codigo_barras",
    "codigo_barras": "codigo_barras",
    "producto": "nombre",
    "nombre": "nombre",
    "nombre producto": "nombre",
    "marca id": "marca_id",
    "marca_id": "marca_id",
    "marca": "marca_nombre",
    "unidad": "unidad",
    "tipo venta": "tipo_venta",
    "tipo_venta": "tipo_venta",
    "precio compra": "precio_compra",
    "precio_compra": "precio_compra",
    "precio venta": "precio_venta",
    "precio_venta": "precio_venta",
    "stock": "existencia",
    "existencia": "existencia",
    "stock mínimo": "stock_minimo",
    "stock minimo": "stock_minimo",
    "stock_minimo": "stock_minimo",
    "activo": "activo",
}


def procesar_excel_productos(ruta_archivo):
    """Lee el archivo Excel y mapea las columnas detectadas."""
    try:
        df = pd.read_excel(ruta_archivo)
    except Exception as e:
        return False, f"Error al leer el archivo Excel: {str(e)}", []

    # Normalizar encabezados (minúsculas y sin espacios adicionales)
    columnas_mapeadas = {}
    for col in df.columns:
        col_limpia = str(col).strip().lower()
        if col_limpia in MAPEO_COLUMNAS:
            columnas_mapeadas[col] = MAPEO_COLUMNAS[col_limpia]

    df = df.rename(columns=columnas_mapeadas)

    # Validar campos obligatorios mínimos
    columnas_requeridas = {"codigo", "nombre", "precio_venta"}
    columnas_presentes = set(df.columns)

    if not columnas_requeridas.issubset(columnas_presentes):
        faltantes = columnas_requeridas - columnas_presentes
        return (
            False,
            f"Faltan columnas obligatorias en el Excel: {', '.join(faltantes)}",
            [],
        )

    productos_procesados = []

    for index, row in df.iterrows():
        # Extracción y limpieza de datos fila por fila
        codigo = str(row.get("codigo", "")).strip()
        nombre = str(row.get("nombre", "")).strip()

        # Omitir filas vacías
        if not codigo or not nombre or codigo.lower() == "nan":
            continue

        # Interpretar estado 'Activo' (acepta 1, "Si", "Sí", "Activo", True)
        val_activo = str(row.get("activo", 1)).strip().lower()
        activo_int = 1 if val_activo in ["1", "si", "sí", "true", "activo"] else 0

        producto = {
            "codigo": codigo,
            "codigo_barras": str(row.get("codigo_barras", "")).strip()
            if pd.notna(row.get("codigo_barras"))
            else None,
            "nombre": nombre,
            "marca_id": int(row["marca_id"])
            if pd.notna(row.get("marca_id")) and str(row.get("marca_id")).isdigit()
            else None,
            "marca_nombre": str(row.get("marca_nombre", "")).strip()
            if pd.notna(row.get("marca_nombre"))
            else None,
            "unidad": str(row.get("unidad", "PZA")).strip().upper()
            if pd.notna(row.get("unidad"))
            else "PZA",
            "tipo_venta": str(row.get("tipo_venta", "Unidad")).strip().capitalize()
            if pd.notna(row.get("tipo_venta"))
            else "Unidad",
            "precio_compra": float(row.get("precio_compra", 0.0))
            if pd.notna(row.get("precio_compra"))
            else 0.0,
            "precio_venta": float(row.get("precio_venta", 0.0))
            if pd.notna(row.get("precio_venta"))
            else 0.0,
            "existencia": float(row.get("existencia", 0.0))
            if pd.notna(row.get("existencia"))
            else 0.0,
            "stock_minimo": float(row.get("stock_minimo", 0.0))
            if pd.notna(row.get("stock_minimo"))
            else 0.0,
            "activo": activo_int,
        }

        productos_procesados.append(producto)

    return (
        True,
        f"Se procesaron {len(productos_procesados)} productos correctamente.",
        productos_procesados,
    )


def guardar_productos_bd(lista_productos):
    """Guarda o actualiza la lista de productos en la BD SQLite."""
    conn = conectar()
    cursor = conn.cursor()

    guardados = 0

    for p in lista_productos:
        # 1. Si viene el nombre de Marca pero no el ID, buscar o crear la marca automáticamente
        if p["marca_nombre"] and not p["marca_id"]:
            cursor.execute(
                "SELECT id FROM marcas WHERE LOWER(nombre) = LOWER(?)",
                (p["marca_nombre"],),
            )
            res = cursor.fetchone()
            if res:
                p["marca_id"] = res["id"]
            else:
                cursor.execute(
                    "INSERT INTO marcas (nombre) VALUES (?)",
                    (p["marca_nombre"],),
                )
                p["marca_id"] = cursor.lastrowid

        # 2. Insertar producto o actualizar si el código ya existe
        cursor.execute(
            """
            INSERT INTO productos (
                codigo, codigo_barras, nombre, marca_id, unidad, tipo_venta,
                precio_compra, precio_venta, existencia, stock_minimo, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(codigo) DO UPDATE SET
                codigo_barras = excluded.codigo_barras,
                nombre = excluded.nombre,
                marca_id = COALESCE(excluded.marca_id, productos.marca_id),
                unidad = excluded.unidad,
                tipo_venta = excluded.tipo_venta,
                precio_compra = excluded.precio_compra,
                precio_venta = excluded.precio_venta,
                existencia = productos.existencia + excluded.existencia,
                stock_minimo = excluded.stock_minimo,
                activo = excluded.activo
        """,
            (
                p["codigo"],
                p["codigo_barras"],
                p["nombre"],
                p["marca_id"],
                p["unidad"],
                p["tipo_venta"],
                p["precio_compra"],
                p["precio_venta"],
                p["existencia"],
                p["stock_minimo"],
                p["activo"],
            ),
        )
        guardados += 1

    conn.commit()
    conn.close()
    return guardados