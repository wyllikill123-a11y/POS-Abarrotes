import sqlite3
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "abarrotes.db"


def obtener_conexion():
    conexion = sqlite3.connect(
        DB_PATH, timeout=30, check_same_thread=False
    )
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA journal_mode=WAL")
    return conexion


class Venta:

    # =====================================================
    # REGISTRAR VENTA
    # =====================================================

    @staticmethod
    def registrar_venta(
        carrito,
        metodo_pago="EFECTIVO",
        descuento=0.0,
        monto_recibido=0.0,
        cambio=0.0
    ):
        if not carrito:
            raise ValueError("El carrito está vacío.")

        # 1. Validar y acumular cantidades por producto para evitar desbordes por duplicados
        demandas_por_codigo = defaultdict(float)
        for item in carrito:
            cant = float(item.get("cantidad", 0))
            prec = float(item.get("precio", 0))

            if cant <= 0:
                raise ValueError(f"Cantidad inválida para '{item.get('nombre', 'Producto')}'.")
            if prec <= 0:
                raise ValueError(f"Precio inválido para '{item.get('nombre', 'Producto')}'.")

            demandas_por_codigo[item["codigo"]] += cant

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            try:
                subtotal = 0.0

                # 2. Validar existencias globales por producto
                for codigo, cant_requerida in demandas_por_codigo.items():
                    cursor.execute("""
                        SELECT existencia, activo, nombre
                        FROM productos
                        WHERE codigo = ? OR codigo_barras = ?
                    """, (codigo, codigo))

                    producto = cursor.fetchone()

                    if producto is None:
                        raise ValueError(f"El producto con código '{codigo}' no existe.")

                    if producto["activo"] == 0:
                        raise ValueError(f"El producto '{producto['nombre']}' está desactivado.")

                    existencia_actual = float(producto["existencia"])
                    if existencia_actual < cant_requerida:
                        raise ValueError(
                            f"Inventario insuficiente para '{producto['nombre']}'. "
                            f"Disponible: {existencia_actual}, Solicitado total: {cant_requerida}"
                        )

                # 3. Calcular subtotales
                for item in carrito:
                    cant = float(item["cantidad"])
                    prec = float(item["precio"])
                    # Se recalcula internamente para evitar desfasajes del cliente
                    subtotal_item = round(cant * prec, 2)
                    item["subtotal"] = subtotal_item
                    subtotal += subtotal_item

                subtotal = round(subtotal, 2)

                # 4. Validar montos y pago
                descuento = round(float(descuento), 2)
                if descuento < 0:
                    raise ValueError("El descuento no puede ser negativo.")

                total = round(subtotal - descuento, 2)
                if total < 0:
                    raise ValueError("El total de la venta no puede ser negativo.")

                if metodo_pago.upper() != "EFECTIVO":
                    monto_recibido = total
                    cambio = 0.0
                else:
                    monto_recibido = round(float(monto_recibido), 2)
                    if monto_recibido < total:
                        raise ValueError("El monto recibido es menor al total de la venta.")
                    cambio = round(monto_recibido - total, 2)

                # 5. Insertar venta principal
                cursor.execute("""
                    INSERT INTO ventas(
                        subtotal, descuento, total, metodo_pago, monto_recibido, cambio
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (subtotal, descuento, total, metodo_pago.upper(), monto_recibido, cambio))

                venta_id = cursor.lastrowid

                # 6. Insertar detalle y actualizar stock
                for item in carrito:
                    cursor.execute("""
                        INSERT INTO detalle_venta(
                            venta_id, producto_codigo, producto_nombre,
                            cantidad, unidad, precio_unitario, subtotal
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        venta_id,
                        item["codigo"],
                        item["nombre"],
                        float(item["cantidad"]),
                        item.get("unidad", "Pieza"),
                        float(item["precio"]),
                        item["subtotal"]
                    ))

                    cursor.execute("""
                        UPDATE productos
                        SET existencia = existencia - ?,
                            fecha_actualizacion = CURRENT_TIMESTAMP
                        WHERE (codigo = ? OR codigo_barras = ?) AND activo = 1
                    """, (
                        float(item["cantidad"]),
                        item["codigo"],
                        item["codigo"]
                    ))

                    if cursor.rowcount == 0:
                        raise ValueError(f"No fue posible actualizar el inventario de '{item['nombre']}'.")

                conexion.commit()
                return venta_id

            except Exception:
                conexion.rollback()
                raise

    # =====================================================
    # CONSULTAS Y HISTORIAL
    # =====================================================

    @staticmethod
    def obtener_por_id(venta_id):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
            return cursor.fetchone()

    @staticmethod
    def obtener_detalle_venta(venta_id):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT * FROM detalle_venta
                WHERE venta_id = ?
                ORDER BY id ASC
            """, (venta_id,))
            return cursor.fetchall()

    @staticmethod
    def obtener_ticket(venta_id):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
            venta = cursor.fetchone()

            cursor.execute("""
                SELECT * FROM detalle_venta
                WHERE venta_id = ?
                ORDER BY id ASC
            """, (venta_id,))
            detalles = cursor.fetchall()

            return venta, detalles

    @staticmethod
    def obtener_ventas_del_dia(fecha=None):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            if fecha is None:
                cursor.execute("""
                    SELECT * FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE('now', 'localtime')
                    ORDER BY fecha DESC
                """)
            else:
                cursor.execute("""
                    SELECT * FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE(?, 'localtime')
                    ORDER BY fecha DESC
                """, (fecha,))
            return cursor.fetchall()

    @staticmethod
    def obtener_resumen_ventas_dia(fecha=None):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            if fecha is None:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_cobrado,
                        COALESCE(SUM(descuento), 0) as total_descuentos
                    FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE('now', 'localtime')
                """)
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_cobrado,
                        COALESCE(SUM(descuento), 0) as total_descuentos
                    FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE(?, 'localtime')
                """)
            return cursor.fetchone()

    @staticmethod
    def obtener_por_rango(fecha_inicio, fecha_fin):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT * FROM ventas
                WHERE DATE(fecha, 'localtime') BETWEEN DATE(?, 'localtime') AND DATE(?, 'localtime')
                ORDER BY fecha DESC
            """, (fecha_inicio, fecha_fin))
            return cursor.fetchall()

    @staticmethod
    def obtener_todas():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas ORDER BY fecha DESC")
            return cursor.fetchall()

    @staticmethod
    def buscar(texto):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT * FROM ventas
                WHERE CAST(id AS TEXT) LIKE ? OR metodo_pago LIKE ?
                ORDER BY fecha DESC
            """, (f"%{texto}%", f"%{texto}%"))
            return cursor.fetchall()

    @staticmethod
    def ultima_venta():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas ORDER BY id DESC LIMIT 1")
            return cursor.fetchone()

    @staticmethod
    def total_hoy():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0)
                FROM ventas
                WHERE DATE(fecha, 'localtime') = DATE('now', 'localtime')
            """)
            return cursor.fetchone()[0]

    @staticmethod
    def contar_ventas():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM ventas")
            return cursor.fetchone()[0]