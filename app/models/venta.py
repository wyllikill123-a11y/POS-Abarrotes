import sqlite3


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

        conexion = sqlite3.connect("app/database/abarrotes.db")
        cursor = conexion.cursor()
        
        try:
            # ==========================
            # VALIDACIONES PREVIAS
            # ==========================
            subtotal = 0

            for item in carrito:
                if item["cantidad"] <= 0:
                    raise ValueError(
                        f"Cantidad inválida para {item['nombre']}."
                    )

                if item["precio"] <= 0:
                    raise ValueError(
                        f"Precio inválido para {item['nombre']}."
                    )

                cursor.execute("""
                    SELECT
                        existencia,
                        activo
                    FROM productos
                    WHERE codigo = ?
                """, (item["codigo"],))

                producto = cursor.fetchone()

                if producto is None:
                    raise ValueError(
                        f"No existe el producto {item['codigo']}."
                    )

                existencia, activo = producto

                if activo == 0:
                    raise ValueError(
                        f"El producto '{item['nombre']}' está desactivado."
                    )

                if existencia < item["cantidad"]:
                    raise ValueError(
                        f"No hay suficiente inventario para '{item['nombre']}'."
                    )

                subtotal += item["subtotal"]

            total = subtotal - descuento

            # Si el pago no es efectivo o no se especificó pago, el monto recibido es el total
            if monto_recibido == 0 or metodo_pago != "EFECTIVO":
                monto_recibido = total
                cambio = 0

            # ==========================
            # GUARDAR VENTA (Tabla Maestro)
            # ==========================
            cursor.execute("""
            INSERT INTO ventas(
                subtotal,
                descuento,
                total,
                metodo_pago,
                monto_recibido,
                cambio
            )
            VALUES(?,?,?,?,?,?)
            """, (
                subtotal,
                descuento,
                total,
                metodo_pago,
                monto_recibido,
                cambio
            ))
            venta_id = cursor.lastrowid

            # ==========================
            # DETALLE DE VENTA
            # ==========================
            for item in carrito:
                cursor.execute("""
                    INSERT INTO detalle_venta(
                        venta_id,
                        producto_codigo,
                        cantidad,
                        precio_unitario,
                        subtotal
                    )
                    VALUES(?,?,?,?,?)
                """, (
                    venta_id,
                    item["codigo"],
                    item["cantidad"],
                    item["precio"],
                    item["subtotal"]
                ))

                # ==========================
                # DESCONTAR INVENTARIO
                # ==========================
                cursor.execute("""
                    UPDATE productos
                    SET
                        existencia = existencia - ?
                    WHERE
                        codigo = ?
                        AND activo = 1
                """, (
                    item["cantidad"],
                    item["codigo"]
                ))

            conexion.commit()
            return venta_id

        except Exception as e:
            conexion.rollback()
            raise e

        finally:
            conexion.close()