import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from app.database.database import obtener_conexion

class HistorialVentasWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Historial de Ventas")
        self.geometry("850x500")

        self.crear_widgets()
        self.cargar_ventas()

    def crear_widgets(self):
        # Barra superior de controles
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=10)

        self.txt_buscar = ctk.CTkEntry(
            top_frame, 
            placeholder_text="Buscar por Folio de Venta...", 
            width=250
        )
        self.txt_buscar.pack(side="left", padx=(0, 10))
        self.txt_buscar.bind("<KeyRelease>", lambda e: self.cargar_ventas())

        btn_reimprimir = ctk.CTkButton(
            top_frame,
            text="🖨 Reimprimir Ticket",
            fg_color="#1A73E8",
            command=self.reimprimir_seleccionado
        )
        btn_reimprimir.pack(side="right")

        # Tabla de ventas
        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columnas = ("id", "fecha", "total", "metodo", "recibido", "cambio")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        self.tabla.heading("id", text="Folio #")
        self.tabla.heading("fecha", text="Fecha y Hora")
        self.tabla.heading("total", text="Total")
        self.tabla.heading("metodo", text="Método Pago")
        self.tabla.heading("recibido", text="Monto Recibido")
        self.tabla.heading("cambio", text="Cambio")

        self.tabla.column("id", width=80, anchor="center")
        self.tabla.column("fecha", width=180, anchor="center")
        self.tabla.column("total", width=100, anchor="e")
        self.tabla.column("metodo", width=120, anchor="center")
        self.tabla.column("recibido", width=110, anchor="e")
        self.tabla.column("cambio", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def cargar_ventas(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        query = "SELECT id, fecha, total, metodo_pago, monto_recibido, cambio FROM ventas"
        filtro = self.txt_buscar.get().strip()

        if filtro.isdigit():
            query += f" WHERE id = {int(filtro)}"
        query += " ORDER BY id DESC LIMIT 100"

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query)

        for venta in cursor.fetchall():
            self.tabla.insert("", "end", values=(
                venta[0],
                venta[1],
                f"${venta[2]:.2f}",
                venta[3],
                f"${venta[4]:.2f}",
                f"${venta[5]:.2f}"
            ))
        conn.close()

    def reimprimir_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione una venta de la lista para reimprimir.")
            return

        folio = self.tabla.item(seleccion[0], "values")[0]
        # Aquí puedes recuperar los detalles de la venta desde 'detalle_ventas' e invocar TicketPrinter
        messagebox.showinfo("Reimpresión", f"Enviando reimpresión del folio #{folio} a la impresora...")