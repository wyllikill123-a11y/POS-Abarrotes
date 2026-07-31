import sqlite3

DB_PATH = "app/database/abarrotes.db"


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
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

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            try:
                subtotal = 0.0

                # ==========================================
                # VALIDACIONES DE PRODUCTOS Y STOCK
                # ==========================================
                for item in carrito:
                    cantidad = float(item["cantidad"])
                    precio = float(item["precio"])
                    subtotal_item = float(item["subtotal"])

                    if cantidad <= 0:
                        raise ValueError(
                            f"Cantidad inválida para '{item['nombre']}'."
                        )

                    if precio <= 0:
                        raise ValueError(
                            f"Precio inválido para '{item['nombre']}'."
                        )

                    cursor.execute("""
                        SELECT existencia, activo
                        FROM productos
                        WHERE codigo = ? OR codigo_barras = ?
                    """, (item["codigo"], item["codigo"]))

                    producto = cursor.fetchone()

                    if producto is None:
                        raise ValueError(
                            f"El producto '{item['codigo']}' no existe."
                        )

                    existencia = float(producto["existencia"])
                    activo = producto["activo"]

                    if activo == 0:
                        raise ValueError(
                            f"El producto '{item['nombre']}' está desactivado."
                        )

                    if existencia < cantidad:
                        raise ValueError(
                            f"Inventario insuficiente para '{item['nombre']}'. "
                            f"Disponible: {existencia}, Solicitado: {cantidad}"
                        )

                    subtotal += subtotal_item

                # ==========================================
                # VALIDACIONES DE MONTOS
                # ==========================================
                descuento = float(descuento)
                if descuento < 0:
                    raise ValueError("El descuento no puede ser negativo.")

                total = subtotal - descuento

                if total < 0:
                    raise ValueError("El total de la venta no puede ser negativo.")

                if metodo_pago != "EFECTIVO":
                    monto_recibido = total
                    cambio = 0.0
                else:
                    monto_recibido = float(monto_recibido)
                    cambio = float(cambio)

                    if monto_recibido < total:
                        raise ValueError("El monto recibido es menor al total de la venta.")

                # ==========================================
                # INSERTAR REGISTRO DE VENTA
                # ==========================================
                cursor.execute("""
                    INSERT INTO ventas(
                        subtotal,
                        descuento,
                        total,
                        metodo_pago,
                        monto_recibido,
                        cambio
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    subtotal,
                    descuento,
                    total,
                    metodo_pago,
                    monto_recibido,
                    cambio
                ))

                venta_id = cursor.lastrowid

                # ==========================================
                # INSERTAR DETALLES Y DESCONTAR INVENTARIO
                # ==========================================
                for item in carrito:
                    cursor.execute("""
                        INSERT INTO detalle_venta(
                            venta_id,
                            producto_codigo,
                            producto_nombre,
                            cantidad,
                            unidad,
                            precio_unitario,
                            subtotal
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        venta_id,
                        item["codigo"],
                        item["nombre"],
                        item["cantidad"],
                        item.get("unidad", "Pieza"),
                        item["precio"],
                        item["subtotal"]
                    ))

                    # Descontar del inventario
                    cursor.execute("""
                        UPDATE productos
                        SET existencia = existencia - ?,
                            fecha_actualizacion = CURRENT_TIMESTAMP
                        WHERE (codigo = ? OR codigo_barras = ?) AND activo = 1
                    """, (
                        item["cantidad"],
                        item["codigo"],
                        item["codigo"]
                    ))

                    if cursor.rowcount == 0:
                        raise ValueError(
                            f"No fue posible actualizar el inventario de '{item['nombre']}'."
                        )

                conexion.commit()
                return venta_id

            except Exception:
                conexion.rollback()
                raise

    # =====================================================
    # CONSULTAS Y CONSULTAS DE HISTORIAL
    # =====================================================

    @staticmethod
    def obtener_por_id(venta_id):
        """Obtiene la cabecera de una venta por su ID."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
            return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_detalle_venta(venta_id):
        """Obtiene todos los artículos asociados a una venta."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT *
                FROM detalle_venta
                WHERE venta_id = ?
                ORDER BY id ASC
            """, (venta_id,))
            return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_ticket(venta_id):
        """
        Retorna la cabecera y el detalle de una venta.
        Ideal para reimprimir tickets.
        """
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,))
            venta = cursor.fetchone()

            cursor.execute("""
                SELECT *
                FROM detalle_venta
                WHERE venta_id = ?
                ORDER BY id ASC
            """, (venta_id,))
            detalle = cursor.fetchall()

            return venta, detalle
        finally:
            conexion.close()

    @staticmethod
    def obtener_ventas_del_dia(fecha=None):
        """Retorna la lista de ventas del día actual (o de la fecha YYYY-MM-DD)."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            if fecha is None:
                cursor.execute("""
                    SELECT *
                    FROM ventas
                    WHERE DATE(fecha) = DATE('now', 'localtime')
                    ORDER BY fecha DESC
                """)
            else:
                cursor.execute("""
                    SELECT *
                    FROM ventas
                    WHERE DATE(fecha) = DATE(?)
                    ORDER BY fecha DESC
                """, (fecha,))
            return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_resumen_ventas_dia(fecha=None):
        """Retorna totales agrupados del día: total cobrado, número de ventas y descuentos."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            if fecha is None:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_cobrado,
                        COALESCE(SUM(descuento), 0) as total_descuentos
                    FROM ventas
                    WHERE DATE(fecha) = DATE('now', 'localtime')
                """)
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_cobrado,
                        COALESCE(SUM(descuento), 0) as total_descuentos
                    FROM ventas
                    WHERE DATE(fecha) = DATE(?)
                """, (fecha,))
            return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def obtener_por_rango(fecha_inicio, fecha_fin):
        """Obtiene el historial de ventas entre dos fechas (YYYY-MM-DD)."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT *
                FROM ventas
                WHERE DATE(fecha) BETWEEN DATE(?) AND DATE(?)
                ORDER BY fecha DESC
            """, (fecha_inicio, fecha_fin))
            return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def obtener_todas():
        """Retorna el historial completo de ventas."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT *
                FROM ventas
                ORDER BY fecha DESC
            """)
            return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def buscar(texto):
        """Busca ventas por ID o por Método de Pago."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT *
                FROM ventas
                WHERE
                    CAST(id AS TEXT) LIKE ?
                    OR metodo_pago LIKE ?
                ORDER BY fecha DESC
            """, (f"%{texto}%", f"%{texto}%"))
            return cursor.fetchall()
        finally:
            conexion.close()

    @staticmethod
    def ultima_venta():
        """Retorna el registro de la última venta efectuada."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT *
                FROM ventas
                ORDER BY id DESC
                LIMIT 1
            """)
            return cursor.fetchone()
        finally:
            conexion.close()

    @staticmethod
    def total_hoy():
        """Obtiene la suma total vendida en el día actual."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT IFNULL(SUM(total), 0)
                FROM ventas
                WHERE DATE(fecha) = DATE('now', 'localtime')
            """)
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    @staticmethod
    def contar_ventas():
        """Retorna el número total de registros de ventas realizadas."""
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM ventas")
            return cursor.fetchone()[0]
        finally:
            conexion.close()