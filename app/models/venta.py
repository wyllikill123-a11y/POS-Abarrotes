import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "datos" / "abarrotes.db"


def obtener_conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        cambio=0.0,
    ):
        if not carrito:
            raise ValueError("El carrito está vacío.")

        # 1. Validar y acumular cantidades por producto
        demandas_por_codigo = defaultdict(float)
        for item in carrito:
            cant = float(item.get("cantidad", 0))
            prec = float(item.get("precio", 0))

            if cant <= 0:
                raise ValueError(
                    f"Cantidad inválida para '{item.get('nombre', 'Producto')}'."
                )
            if prec <= 0:
                raise ValueError(
                    f"Precio inválido para '{item.get('nombre', 'Producto')}'."
                )

            clave_prod = item.get("id") or item.get("codigo")
            demandas_por_codigo[clave_prod] += cant

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            try:
                subtotal = 0.0
                info_productos = {}

                # 2. Validar existencias globales por producto
                for clave, cant_requerida in demandas_por_codigo.items():
                    cursor.execute(
                        """
                        SELECT id, existencia, activo, nombre
                        FROM productos
                        WHERE id = ? OR codigo = ? OR codigo_barras = ?
                    """,
                        (clave, clave, clave),
                    )

                    producto = cursor.fetchone()

                    if producto is None:
                        raise ValueError(f"El producto '{clave}' no existe.")

                    if producto["activo"] == 0:
                        raise ValueError(
                            f"El producto '{producto['nombre']}' está desactivado."
                        )

                    existencia_actual = float(producto["existencia"])
                    if existencia_actual < cant_requerida:
                        raise ValueError(
                            f"Inventario insuficiente para '{producto['nombre']}'. "
                            f"Disponible: {existencia_actual}, Solicitado total: {cant_requerida}"
                        )

                    info_productos[clave] = producto

                # 3. Calcular subtotales
                for item in carrito:
                    cant = float(item["cantidad"])
                    prec = float(item["precio"])
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
                    raise ValueError(
                        "El total de la venta no puede ser negativo."
                    )

                if metodo_pago.upper() != "EFECTIVO":
                    monto_recibido = total
                    cambio = 0.0
                else:
                    monto_recibido = round(float(monto_recibido), 2)
                    if monto_recibido < total:
                        raise ValueError(
                            "El monto recibido es menor al total de la venta."
                        )
                    cambio = round(monto_recibido - total, 2)

                # 5. Insertar venta principal
                cursor.execute(
                    """
                    INSERT INTO ventas (
                        total, metodo_pago, descuento, monto_recibido, cambio
                    )
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        total,
                        metodo_pago.upper(),
                        descuento,
                        monto_recibido,
                        cambio,
                    ),
                )

                venta_id = cursor.lastrowid

                # 6. Insertar detalle y actualizar stock
                for item in carrito:
                    clave_prod = item.get("id") or item.get("codigo")
                    prod_info = info_productos[clave_prod]
                    producto_db_id = prod_info["id"]

                    cursor.execute(
                        """
                        INSERT INTO detalle_ventas(
                            venta_id, producto_id, cantidad, precio_unitario, subtotal
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            venta_id,
                            producto_db_id,
                            float(item["cantidad"]),
                            float(item["precio"]),
                            item["subtotal"],
                        ),
                    )

                    cursor.execute(
                        """
                        UPDATE productos
                        SET existencia = existencia - ?
                        WHERE id = ? AND activo = 1
                    """,
                        (float(item["cantidad"]), producto_db_id),
                    )

                    if cursor.rowcount == 0:
                        raise ValueError(
                            f"No fue posible actualizar el inventario de '{prod_info['nombre']}'."
                        )

                conexion.commit()
                return venta_id

            except Exception:
                conexion.rollback()
                raise

    # =====================================================
    # CANCELACIONES Y DEVOLUCIONES
    # =====================================================

    @staticmethod
    def cancelar_venta(venta_id):
        """Cancela una venta devolviendo todo el stock involucrado al inventario."""
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            try:
                # Obtener detalles de la venta
                cursor.execute(
                    """
                    SELECT producto_id, cantidad 
                    FROM detalle_ventas 
                    WHERE venta_id = ?
                """,
                    (venta_id,),
                )
                detalles = cursor.fetchall()

                if not detalles:
                    raise ValueError(
                        f"No se encontró la venta #{venta_id} o no contiene detalles."
                    )

                # Revertir el stock en productos
                for item in detalles:
                    cursor.execute(
                        """
                        UPDATE productos
                        SET existencia = existencia + ?
                        WHERE id = ?
                    """,
                        (item["cantidad"], item["producto_id"]),
                    )

                # Eliminar detalles y venta
                cursor.execute(
                    "DELETE FROM detalle_ventas WHERE venta_id = ?",
                    (venta_id,),
                )
                cursor.execute(
                    "DELETE FROM ventas WHERE id = ?", (venta_id,)
                )

                conexion.commit()
                return True
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
            cursor.execute(
                "SELECT * FROM ventas WHERE id = ?", (venta_id,)
            )
            return cursor.fetchone()

    @staticmethod
    def obtener_detalle_ventas(venta_id):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    dv.*, 
                    p.nombre AS producto_nombre, 
                    p.codigo AS producto_codigo
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
                ORDER BY dv.id ASC
            """,
                (venta_id,),
            )
            return cursor.fetchall()

    @staticmethod
    def obtener_ticket(venta_id):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT * FROM ventas WHERE id = ?", (venta_id,)
            )
            venta = cursor.fetchone()

            cursor.execute(
                """
                SELECT 
                    dv.*, 
                    p.nombre AS producto_nombre, 
                    p.codigo AS producto_codigo,
                    p.unidad AS unidad
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
                ORDER BY dv.id ASC
            """,
                (venta_id,),
            )
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
                cursor.execute(
                    """
                    SELECT * FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE(?, 'localtime')
                    ORDER BY fecha DESC
                """,
                    (fecha,),
                )
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
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_cobrado,
                        COALESCE(SUM(descuento), 0) as total_descuentos
                    FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE(?, 'localtime')
                """,
                    (fecha,),
                )
            return cursor.fetchone()

    @staticmethod
    def obtener_por_rango(fecha_inicio, fecha_fin):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT * FROM ventas
                WHERE DATE(fecha, 'localtime') BETWEEN DATE(?, 'localtime') AND DATE(?, 'localtime')
                ORDER BY fecha DESC
            """,
                (fecha_inicio, fecha_fin),
            )
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
            cursor.execute(
                """
                SELECT * FROM ventas
                WHERE CAST(id AS TEXT) LIKE ? OR metodo_pago LIKE ?
                ORDER BY fecha DESC
            """,
                (f"%{texto}%", f"%{texto}%"),
            )
            return cursor.fetchall()

    @staticmethod
    def ultima_venta():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "SELECT * FROM ventas ORDER BY id DESC LIMIT 1"
            )
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