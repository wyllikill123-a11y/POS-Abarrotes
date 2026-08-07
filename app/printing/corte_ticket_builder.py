# app/printing/corte_ticket_builder.py

class CorteTicketBuilder:

    WIDTH = 32

    @staticmethod
    def linea():
        return "-" * CorteTicketBuilder.WIDTH

    @staticmethod
    def centrar(texto):
        return texto.center(CorteTicketBuilder.WIDTH)

    @staticmethod
    def derecha(texto):
        return texto.rjust(CorteTicketBuilder.WIDTH)

    @staticmethod
    def construir(datos_corte):
        texto = ""
        texto += CorteTicketBuilder.centrar("ABARROTES ROSITA-ANDREA") + "\n"
        texto += CorteTicketBuilder.centrar("*** CORTE DE CAJA / TURNO ***") + "\n"
        texto += CorteTicketBuilder.linea() + "\n"

        texto += f"Turno ID : #{datos_corte['id_turno']}\n"
        texto += f"Apertura : {datos_corte['fecha_apertura'][:16]}\n"
        texto += f"Cierre   : {datos_corte['fecha_cierre'][:16]}\n"
        texto += CorteTicketBuilder.linea() + "\n"

        texto += f"Fondo Inicial : ${datos_corte['monto_inicial']:.2f}\n"
        texto += f"Cant. Ventas  : {datos_corte['num_ventas']}\n"
        texto += CorteTicketBuilder.linea() + "\n"

        texto += "DESGLOSE DE VENTAS:\n"
        texto += f" Efectivo    : ${datos_corte['monto_efectivo']:.2f}\n"
        texto += f" Tarjeta     : ${datos_corte['monto_tarjeta']:.2f}\n"
        texto += f" Transfer.   : ${datos_corte['monto_transferencia']:.2f}\n"
        texto += CorteTicketBuilder.linea() + "\n"

        texto += CorteTicketBuilder.derecha(f"TOTAL VENTAS: ${datos_corte['total_ventas']:.2f}") + "\n"
        texto += CorteTicketBuilder.derecha(f"EFECTIVO EN CAJA: ${datos_corte['monto_total_caja']:.2f}") + "\n"
        texto += CorteTicketBuilder.linea() + "\n"

        texto += CorteTicketBuilder.centrar("FIN DEL TURNO") + "\n"
        return texto
    