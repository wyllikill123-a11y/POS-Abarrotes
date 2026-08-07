from datetime import datetime
from app.database import conectar


class Turno:

    @staticmethod
    def obtener_activo():
        """Retorna el turno abierto actualmente o None si no hay caja abierta."""
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM turnos WHERE estado = 'ABIERTO' ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def abrir(monto_inicial=0.0):
        """Abre un nuevo turno (ej. Turno Mañana o Tarde)."""
        if Turno.obtener_activo():
            raise ValueError("Ya existe una caja/turno abierto actualmente.")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO turnos (fecha_apertura, monto_inicial, estado)
            VALUES (DATETIME('now', 'localtime'), ?, 'ABIERTO')
            """,
            (monto_inicial,),
        )
        conn.commit()
        turno_id = cursor.lastrowid
        conn.close()
        return turno_id

    @staticmethod
    def realizar_corte():
        """Cierra el turno actual calculando únicamente las ventas de su periodo."""
        turno = Turno.obtener_activo()
        if not turno:
            raise ValueError("No hay un turno activo para cerrar.")

        fecha_inicio = turno["fecha_apertura"]

        conn = conectar()
        cursor = conn.cursor()

        # Resumen de ventas hechas entre la apertura de este turno y el momento actual
        cursor.execute(
            """
            SELECT 
                metodo_pago,
                SUM(total) as total_metodo,
                COUNT(id) as num_ventas
            FROM ventas 
            WHERE (turno_id = ? OR fecha >= ?)
            GROUP BY metodo_pago
            """,
            (turno["id"], fecha_inicio),
        )

        filas = cursor.fetchall()

        efectivo = 0.0
        tarjeta = 0.0
        transferencia = 0.0
        total_ventas = 0.0
        num_ventas = 0

        for row in filas:
            metodo = str(row["metodo_pago"]).upper()
            monto = row["total_metodo"] or 0.0
            cant = row["num_ventas"] or 0

            total_ventas += monto
            num_ventas += cant

            if "EFECTIVO" in metodo:
                efectivo += monto
            elif "TARJETA" in metodo:
                tarjeta += monto
            elif "TRANSFER" in metodo:
                transferencia += monto

        monto_final_caja = turno["monto_inicial"] + efectivo
        fecha_cierre = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            UPDATE turnos 
            SET fecha_cierre = ?,
                monto_final = ?,
                monto_efectivo = ?,
                monto_tarjeta = ?,
                monto_transferencia = ?,
                total_ventas = ?,
                estado = 'CERRADO'
            WHERE id = ?
            """,
            (
                fecha_cierre,
                monto_final_caja,
                efectivo,
                tarjeta,
                transferencia,
                total_ventas,
                turno["id"],
            ),
        )

        conn.commit()
        conn.close()

        # Datos recopilados para imprimir el ticket de corte
        return {
            "id_turno": turno["id"],
            "fecha_apertura": fecha_inicio,
            "fecha_cierre": fecha_cierre,
            "monto_inicial": turno["monto_inicial"],
            "monto_efectivo": efectivo,
            "monto_tarjeta": tarjeta,
            "monto_transferencia": transferencia,
            "total_ventas": total_ventas,
            "monto_total_caja": monto_final_caja,
            "num_ventas": num_ventas,
        }