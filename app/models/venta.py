import sqlite3

DB_PATH = "app/database/abarrotes.db"


class Venta:

    @staticmethod
    def registrar_venta(
        carrito,
        metodo_pago="EFECTIVO",
        descuento=0,
        monto_recibido=0,
        cambio=0
    ):
        if not carrito:
            raise ValueError("El carrito está vacío.")

        with sqlite3.connect(DB_PATH) as conexion:
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()

            try:
                subtotal = 0.0

                # ==========================================
                # VALIDACIONES
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
                        WHERE codigo = ?
                    """, (item["codigo"],))

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
                            f"No hay suficiente inventario para '{item['nombre']}'."
                        )

                    subtotal += subtotal_item

                if descuento < 0:
                    raise ValueError(
                        "El descuento no puede ser negativo."
                    )

                total = subtotal - descuento

                if total < 0:
                    raise ValueError(
                        "El total de la venta no puede ser negativo."
                    )

                if metodo_pago != "EFECTIVO":
                    monto_recibido = total
                    cambio = 0

                if metodo_pago == "EFECTIVO":

                    monto_recibido = float(monto_recibido)
                    cambio = float(cambio)

                    if monto_recibido < total:
                        raise ValueError(
                            "El monto recibido es menor al total."
                        )

                # ==========================================
                # INSERTAR VENTA
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
                # DETALLE + DESCONTAR INVENTARIO
                # ==========================================
                for item in carrito:

                    cursor.execute("""
                        INSERT INTO detalle_venta(
                            venta_id,
                            producto_codigo,
                            cantidad,
                            precio_unitario,
                            subtotal
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        venta_id,
                        item["codigo"],
                        item["cantidad"],
                        item["precio"],
                        item["subtotal"]
                    ))

                    cursor.execute("""
                        UPDATE productos
                        SET existencia = existencia - ?
                        WHERE codigo = ?
                        AND activo = 1
                    """, (
                        item["cantidad"],
                        item["codigo"]
                    ))

                    if cursor.rowcount == 0:
                        raise ValueError(
                            f"No fue posible descontar inventario del producto '{item['codigo']}'."
                        )

                conexion.commit()

                return venta_id

            except Exception:
                conexion.rollback()
                raise