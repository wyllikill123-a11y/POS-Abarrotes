import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from app.models.venta import Venta

class HistorialVentasWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Historial de Ventas")
        self.geometry("1000 x 650")
        self.minsize(900, 550)

        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()

        # Estructura principal
        self._crear_encabezado()
        self._crear_filtros()
        self._crear_tabla()
        self._crear_resumen_y_acciones()

        # Cargar datos iniciales
        self.cargar_ventas_del_dia()

    # =====================================================
    # COMPONENTES DE LA INTERFAZ
    # =====================================================

    def _crear_encabezado(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        lbl_titulo = ctk.CTkLabel(
            header_frame,
            text="📋 Historial y Reporte de Ventas",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        lbl_titulo.pack(side="left")

    def _crear_filtros(self):
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)

        # Buscador por ID o Método
        lbl_buscar = ctk.CTkLabel(filter_frame, text="🔍 Buscar (Folio/Método):")
        lbl_buscar.grid(row=0, column=0, padx=(15, 5), pady=12, sticky="w")

        self.txt_buscar = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Ej. 105 o EFECTIVO...",
            width=180
        )
        self.txt_buscar.grid(row=0, column=1, padx=5, pady=12)
        self.txt_buscar.bind("<KeyRelease>", self._filtrar_por_busqueda)

        # Filtro Fecha Inicio
        lbl_inicio = ctk.CTkLabel(filter_frame, text="📅 Desde (YYYY-MM-DD):")
        lbl_inicio.grid(row=0, column=2, padx=(15, 5), pady=12, sticky="w")

        self.txt_fecha_inicio = ctk.CTkEntry(
            filter_frame,
            placeholder_text="2026-01-01",
            width=110
        )
        self.txt_fecha_inicio.grid(row=0, column=3, padx=5, pady=12)

        # Filtro Fecha Fin
        lbl_fin = ctk.CTkLabel(filter_frame, text="Hasta:")
        lbl_fin.grid(row=0, column=4, padx=(10, 5), pady=12, sticky="w")

        self.txt_fecha_fin = ctk.CTkEntry(
            filter_frame,
            placeholder_text="2026-12-31",
            width=110
        )
        self.txt_fecha_fin.grid(row=0, column=5, padx=5, pady=12)

        # Botón Filtrar Rango
        btn_filtrar = ctk.CTkButton(
            filter_frame,
            text="Filtrar",
            width=80,
            command=self._filtrar_por_rango_fechas
        )
        btn_filtrar.grid(row=0, column=6, padx=10, pady=12)

        # Botón Restablecer (Hoy)
        btn_hoy = ctk.CTkButton(
            filter_frame,
            text="Ver Hoy",
            width=80,
            fg_color="gray",
            hover_color="#555555",
            command=self.cargar_ventas_del_dia
        )
        btn_hoy.grid(row=0, column=7, padx=(0, 15), pady=12)

    def _crear_tabla(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Estilos para el Treeview de Tkinter
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=28,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            font=("Arial", 11, "bold")
        )
        style.map("Treeview", background=[("selected", "#1f538d")])

        columnas = ("id", "fecha", "metodo", "subtotal", "descuento", "total")

        self.tabla = ttk.Treeview(
            table_frame,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tabla.heading("id", text="Folio")
        self.tabla.heading("fecha", text="Fecha y Hora")
        self.tabla.heading("metodo", text="Método de Pago")
        self.tabla.heading("subtotal", text="Subtotal")
        self.tabla.heading("descuento", text="Descuento")
        self.tabla.heading("total", text="Total")

        self.tabla.column("id", width=70, anchor="center")
        self.tabla.column("fecha", width=180, anchor="center")
        self.tabla.column("metodo", width=130, anchor="center")
        self.tabla.column("subtotal", width=110, anchor="e")
        self.tabla.column("descuento", width=110, anchor="e")
        self.tabla.column("total", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tabla.yview
        )
        self.tabla.configure(yscroll=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Doble clic para ver detalle rápido
        self.tabla.bind("<Double-1>", lambda event: self.ver_detalle_venta())

    def _crear_resumen_y_acciones(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=20, pady=(5, 15))

        # Panel de totales acumulados
        self.lbl_conteo = ctk.CTkLabel(
            bottom_frame,
            text="Ventas: 0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_conteo.pack(side="left", padx=15, pady=15)

        self.lbl_total_periodo = ctk.CTkLabel(
            bottom_frame,
            text="Total Período: $0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2FA572"
        )
        self.lbl_total_periodo.pack(side="left", padx=15, pady=15)

        # Botones de Acción
        btn_reimprimir = ctk.CTkButton(
            bottom_frame,
            text="🖨️ Reimprimir Ticket",
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.reimprimir_ticket
        )
        btn_reimprimir.pack(side="right", padx=10, pady=15)

        btn_detalle = ctk.CTkButton(
            bottom_frame,
            text="👁️ Ver Detalle",
            fg_color="#3B8ED0",
            hover_color="#36719F",
            command=self.ver_detalle_venta
        )
        btn_detalle.pack(side="right", padx=5, pady=15)

    # =====================================================
    # LÓGICA Y CONSULTAS DE DATOS
    # =====================================================

    def _poblar_tabla(self, registros):
        """Limpia la tabla actual y la llena con la lista de registros enviada."""
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        suma_total = 0.0

        for venta in registros:
            subtotal = f"${venta['subtotal']:.2f}"
            descuento = f"${venta['descuento']:.2f}"
            total = f"${venta['total']:.2f}"
            suma_total += float(venta['total'])

            self.tabla.insert("", "end", values=(
                venta["id"],
                venta["fecha"],
                venta["metodo_pago"],
                subtotal,
                descuento,
                total
            ))

        self.lbl_conteo.configure(text=f"Ventas en lista: {len(registros)}")
        self.lbl_total_periodo.configure(text=f"Total Período: ${suma_total:.2f}")

    def cargar_ventas_del_dia(self):
        """Carga las ventas realizadas el día de hoy por defecto."""
        self.txt_buscar.delete(0, "end")
        self.txt_fecha_inicio.delete(0, "end")
        self.txt_fecha_fin.delete(0, "end")

        hoy = datetime.now().strftime("%Y-%m-%d")
        self.txt_fecha_inicio.insert(0, hoy)
        self.txt_fecha_fin.insert(0, hoy)

        ventas = Venta.obtener_ventas_del_dia()
        self._poblar_tabla(ventas)

    def _filtrar_por_busqueda(self, event=None):
        texto = self.txt_buscar.get().strip()
        if not texto:
            self.cargar_ventas_del_dia()
            return

        ventas = Venta.buscar(texto)
        self._poblar_tabla(ventas)

    def _filtrar_por_rango_fechas(self):
        f_inicio = self.txt_fecha_inicio.get().strip()
        f_fin = self.txt_fecha_fin.get().strip()

        if not f_inicio or not f_fin:
            messagebox.showwarning("Atención", "Por favor ingresa ambas fechas en formato YYYY-MM-DD.")
            return

        try:
            ventas = Venta.obtener_por_rango(f_inicio, f_fin)
            self._poblar_tabla(ventas)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al filtrar por fechas: {str(e)}")

    def _obtener_id_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona una venta de la lista.")
            return None
        valores = self.tabla.item(seleccion[0], "values")
        return valores[0]  # Retorna el folio (id)

    # =====================================================
    # DETALLE Y REIMPRESIÓN
    # =====================================================

    def ver_detalle_venta(self):
        venta_id = self._obtener_id_seleccionado()
        if not venta_id:
            return

        venta, detalles = Venta.obtener_ticket(venta_id)
        if not venta:
            messagebox.showerror("Error", "No se encontró el detalle de la venta especificada.")
            return

        # Ventana Modal de Detalle
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"Detalle de Venta #{venta_id}")
        dialogo.geometry("550x450")
        dialogo.transient(self)
        dialogo.grab_set()

        # Cabecera
        lbl_info = ctk.CTkLabel(
            dialogo,
            text=f"Folio: #{venta['id']}  |  Fecha: {venta['fecha']}\nMétodo: {venta['metodo_pago']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_info.pack(pady=10)

        # Tabla de productos
        table_frame = ctk.CTkFrame(dialogo)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        cols = ("prod", "cant", "precio", "subtotal")
        tabla_det = ttk.Treeview(table_frame, columns=cols, show="headings")
        tabla_det.heading("prod", text="Producto")
        tabla_det.heading("cant", text="Cant.")
        tabla_det.heading("precio", text="P. Unit")
        tabla_det.heading("subtotal", text="Subtotal")

        tabla_det.column("prod", width=200)
        tabla_det.column("cant", width=60, anchor="center")
        tabla_det.column("precio", width=80, anchor="e")
        tabla_det.column("subtotal", width=90, anchor="e")

        for item in detalles:
            tabla_det.insert("", "end", values=(
                item["producto_nombre"],
                f"{item['cantidad']} {item['unidad']}",
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            ))

        tabla_det.pack(fill="both", expand=True)

        # Totales
        lbl_totales = ctk.CTkLabel(
            dialogo,
            text=f"Subtotal: ${venta['subtotal']:.2f}  |  Descuento: ${venta['descuento']:.2f}  |  Total: ${venta['total']:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#2FA572"
        )
        lbl_totales.pack(pady=10)

    def reimprimir_ticket(self):
        venta_id = self._obtener_id_seleccionado()
        if not venta_id:
            return

        venta, detalles = Venta.obtener_ticket(venta_id)
        if not venta:
            messagebox.showerror("Error", "No se pudo recuperar la información de la venta.")
            return

        # Simulación / Lógica de Reimpresión
        ticket_texto = f"""
========================================
           ABARROTES EL PUERTO          
             TICKET DE VENTA            
========================================
Folio: #{venta['id']}
Fecha: {venta['fecha']}
Método de Pago: {venta['metodo_pago']}
----------------------------------------
"""
        for item in detalles:
            ticket_texto += f"{item['producto_nombre']}\n"
            ticket_texto += f"  {item['cantidad']} x ${item['precio_unitario']:.2f} = ${item['subtotal']:.2f}\n"

        ticket_texto += f"""----------------------------------------
Subtotal:  ${venta['subtotal']:.2f}
Descuento: ${venta['descuento']:.2f}
TOTAL:     ${venta['total']:.2f}
Recibido:  ${venta['monto_recibido']:.2f}
Cambio:    ${venta['cambio']:.2f}
========================================
      ¡GRACIAS POR SU COMPRA!           
========================================
"""
        # Aquí puedes invocar a tu módulo impresor físico o mostrar en consola
        print(ticket_texto)
        messagebox.showinfo("Reimpresión", f"Ticket #{venta_id} enviado a reimprimir con éxito.")