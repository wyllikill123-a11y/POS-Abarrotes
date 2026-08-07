from datetime import datetime


class TicketBuilder:

    WIDTH = 32

    @staticmethod
    def linea():
        return "-" * TicketBuilder.WIDTH

    @staticmethod
    def centrar(texto):
        return texto.center(TicketBuilder.WIDTH)

    @staticmethod
    def derecha(texto):
        return texto.rjust(TicketBuilder.WIDTH)

    @staticmethod
    def construir(venta, detalle):
        texto = ""

        texto += TicketBuilder.centrar("ABARROTES") + "\n"
        texto += TicketBuilder.centrar("ROSITA-ANDREA") + "\n"
        texto += TicketBuilder.linea() + "\n"

        texto += f"Folio : {venta['id']}\n"
        texto += f"Fecha : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"

        texto += TicketBuilder.linea() + "\n"

        for item in detalle:
            nombre = item["nombre"][:18]

            texto += (
                f"{item['cantidad']} "
                f"{nombre}\n"
            )

            texto += TicketBuilder.derecha(
                f"${item['subtotal']:.2f}"
            ) + "\n"

        texto += TicketBuilder.linea() + "\n"

        texto += TicketBuilder.derecha(
            f"TOTAL ${venta['total']:.2f}"
        ) + "\n"

        texto += TicketBuilder.derecha(
            f"PAGO {venta['metodo_pago']}"
        ) + "\n"

        texto += TicketBuilder.derecha(
            f"RECIBIÓ ${venta['monto_recibido']:.2f}"
        ) + "\n"

        texto += TicketBuilder.derecha(
            f"CAMBIO ${venta['cambio']:.2f}"
        ) + "\n"

        texto += TicketBuilder.linea() + "\n"

        texto += TicketBuilder.centrar(
            "¡GRACIAS POR SU COMPRA!"
        ) + "\n"  # Ajustado a solo un salto de línea

        return texto