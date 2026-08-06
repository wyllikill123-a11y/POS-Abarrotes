import os
import tempfile
import win32api
import win32print


class TicketPrinter:

    @staticmethod
    def obtener_impresora():
        """Devuelve el nombre de la impresora predeterminada de Windows."""
        return win32print.GetDefaultPrinter()

    @staticmethod
    def imprimir_ticket_venta(
        venta_id, carrito, total, recibido, cambio, metodo
    ):
        """Genera el formato de texto e imprime el ticket utilizando la impresora predeterminada."""
        impresora = TicketPrinter.obtener_impresora()

        texto = ""
        texto += "================================\n"
        texto += "      ABARROTES ROSITA-ANDREA\n"
        texto += "================================\n\n"

        texto += f"FOLIO : #{venta_id}\n"
        texto += f"METODO: {metodo}\n"
        texto += "--------------------------------\n"

        for item in carrito:
            nombre = str(item.get("nombre", "Producto"))[:20]
            cantidad = item.get("cantidad", 1)
            precio = float(item.get("precio", 0.0) or 0.0)
            subtotal = float(item.get("subtotal", 0.0) or 0.0)

            texto += f"{nombre}\n"
            texto += f"  {cantidad} x ${precio:.2f}    ${subtotal:.2f}\n"

        texto += "--------------------------------\n"
        texto += f"TOTAL      : ${float(total or 0.0):.2f}\n"
        texto += f"RECIBIDO   : ${float(recibido or 0.0):.2f}\n"
        texto += f"CAMBIO     : ${float(cambio or 0.0):.2f}\n\n"

        texto += "   ¡¡GRACIAS POR SU COMPRA!!\n"
        texto += "\n\n\n\n\n"

        # Crear archivo temporal para mandar a imprimir
        fd, archivo = tempfile.mkstemp(suffix=".txt")
        try:
            with open(fd, "w", encoding="utf-8") as f:
                f.write(texto)

            win32api.ShellExecute(
                0,
                "print",
                archivo,
                f'/d:"{impresora}"',
                ".",
                0
            )
        except Exception as e:
            raise Exception(f"No se pudo enviar la impresión a {impresora}:\n{e}")

    # Alias para mantener compatibilidad si se invoca como 'imprimir_ticket'
    imprimir_ticket = imprimir_ticket_venta