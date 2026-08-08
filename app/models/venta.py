from contextlib import contextmanager
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from app.models.turno import Turno

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "datos" / "abarrotes.db"


@contextmanager
def obtener_conexion():
    """Generador de contexto que asegura abrir y cerrar correctamente la conexión a SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(
        DB_PATH, timeout=30, check_same_thread=False
    )
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA journal_mode=WAL")
    try:
        yield conexion
    finally:
        conexion.close()


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

        metodo_pago = metodo_pago.upper().strip()

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            try:
                # 0. Validar dentro de la misma transacción que exista un turno/caja abierto
                turno_activo = Turno.obtener_activo()
                if not turno_activo:
                    raise ValueError(
                        "No hay una caja/turno abierto. Por favor, realiza la apertura de caja antes de cobrar."
                    )

                # 1. Validar y acumular cantidades por producto (priorizando 'id')
                demandas_por_id = defaultdict(float)
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
                    demandas_por_id[clave_prod] += cant

                subtotal = 0.0
                info_productos = {}

                # 2. Validar existencias globales por producto
                for clave, cant_requerida in demandas_por_id.items():
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

                if metodo_pago != "EFECTIVO":
                    monto_recibido = total
                    cambio = 0.0
                else:
                    monto_recibido = round(float(monto_recibido), 2)
                    if monto_recibido < total:
                        raise ValueError(
                            "El monto recibido es menor al total de la venta."
                        )
                    cambio = round(monto_recibido - total, 2)

                # 5. Insertar venta principal con estatus 'COMPLETADA'
                cursor.execute(
                    """
                    INSERT INTO ventas (
                        turno_id, total, metodo_pago, descuento, monto_recibido, cambio, estatus
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'COMPLETADA')
                """,
                    (
                        turno_activo["id"],
                        total,
                        metodo_pago,
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
        """Cancela lógicamente una venta y devuelve el stock al inventario."""
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            try:
                # Verificar que la venta exista y esté completada
                cursor.execute(
                    "SELECT estatus FROM ventas WHERE id = ?", (venta_id,)
                )
                venta = cursor.fetchone()

                if not venta:
                    raise ValueError(f"No se encontró la venta #{venta_id}.")
                if venta["estatus"] == "CANCELADA":
                    raise ValueError(f"La venta #{venta_id} ya se encuentra cancelada.")

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

                # Marcar la venta como CANCELADA en lugar de eliminarla
                cursor.execute(
                    "UPDATE ventas SET estatus = 'CANCELADA' WHERE id = ?",
                    (venta_id,),
                )

                conexion.commit()
                return True
            except Exception:
                conexion.rollback()
                raise

    # =====================================================
    # DESGLOSE POR MÉTODO DE PAGO Y REPORTES
    # =====================================================

    @staticmethod
    def obtener_ventas_por_metodo_pago(id_turno=None):
        """Retorna un diccionario con el total vendido agrupado por método de pago."""
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            if id_turno:
                query = """
                    SELECT metodo_pago, SUM(total) 
                    FROM ventas 
                    WHERE turno_id = ? AND (estatus IS NULL OR estatus != 'CANCELADA')
                    GROUP BY metodo_pago
                """
                cursor.execute(query, (id_turno,))
            else:
                query = """
                    SELECT metodo_pago, SUM(total) 
                    FROM ventas 
                    WHERE DATE(fecha, 'localtime') = DATE('now', 'localtime')
                      AND (estatus IS NULL OR estatus != 'CANCELADA')
                    GROUP BY metodo_pago
                """
                cursor.execute(query)

            resultados = cursor.fetchall()

        totales = {
            "EFECTIVO": 0.0,
            "TRANSFERENCIA": 0.0,
            "TARJETA": 0.0,
        }

        for fila in resultados:
            metodo = fila["metodo_pago"]
            monto = fila[1]
            if metodo:
                clave = metodo.upper().strip()
                totales[clave] = float(monto or 0)

        return totales

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
                      AND (estatus IS NULL OR estatus != 'CANCELADA')
                    ORDER BY fecha DESC
                """)
            else:
                cursor.execute(
                    """
                    SELECT * FROM ventas
                    WHERE DATE(fecha, 'localtime') = DATE(?, 'localtime')
                      AND (estatus IS NULL OR estatus != 'CANCELADA')
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
                      AND (estatus IS NULL OR estatus != 'CANCELADA')
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
                      AND (estatus IS NULL OR estatus != 'CANCELADA')
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
                  AND (estatus IS NULL OR estatus != 'CANCELADA')
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
                WHERE (CAST(id AS TEXT) LIKE ? OR metodo_pago LIKE ?)
                  AND (estatus IS NULL OR estatus != 'CANCELADA')
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
                  AND (estatus IS NULL OR estatus != 'CANCELADA')
            """)
            return cursor.fetchone()[0]

    @staticmethod
    def contar_ventas():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM ventas WHERE estatus IS NULL OR estatus != 'CANCELADA'")
            return cursor.fetchone()[0]