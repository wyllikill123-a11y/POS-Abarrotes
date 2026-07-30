import tempfile
import os
import win32api
import win32print


class TicketPrinter:

    @staticmethod
    def obtener_impresora():
        """
        Devuelve la impresora predeterminada de Windows.
        """
        return win32print.GetDefaultPrinter()

    @staticmethod
    def imprimir_ticket(
        venta_id,
        carrito,
        total,
        recibido,
        cambio,
        metodo
    ):

        impresora = TicketPrinter.obtener_impresora()

        texto = ""

        texto += "================================\n"
        texto += "      ABARROTES ROSITA-ANDREA\n"
        texto += "================================\n\n"

        texto += f"FOLIO : {venta_id}\n"
        texto += f"METODO: {metodo}\n"

        texto += "--------------------------------\n"

        for item in carrito:

            nombre = item["nombre"][:20]

            texto += f"{nombre}\n"

            texto += (
                f"{item['cantidad']} x "
                f"${item['precio']:.2f}"
                f"    ${item['subtotal']:.2f}\n"
            )

        texto += "--------------------------------\n"

        texto += f"TOTAL      : ${total:.2f}\n"
        texto += f"RECIBIDO   : ${recibido:.2f}\n"
        texto += f"CAMBIO     : ${cambio:.2f}\n"

        texto += "\n"

        texto += "¡¡GRACIAS POR SU COMPRA!!\n"

        texto += "\n\n\n\n\n"

        archivo = tempfile.mktemp(".txt")

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(texto)

        try:

            win32api.ShellExecute(
                0,
                "print",
                archivo,
                None,
                ".",
                0
            )

        except Exception as e:

            raise Exception(
                f"No se pudo imprimir.\n\n{e}"
            )