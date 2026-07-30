def imprimir_ticket(self):
    try:
        TicketPrinter.imprimir_ticket_venta(
            self.venta_id, self.carrito, self.total, 
            self.recibido, self.cambio, self.metodo
        )
        messagebox.showinfo("Impresión", "Ticket impreso correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo imprimir el ticket:\n{e}")