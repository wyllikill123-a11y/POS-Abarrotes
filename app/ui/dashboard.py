import customtkinter as ctk
from app.models.producto import Producto
from app.views.historial_ventas import HistorialVentasWindow


class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0, 1), weight=1)

        # Título
        titulo = ctk.CTkLabel(
            self,
            text="Bienvenido a Abarrotes Rosita-Andrea (WI)",
            font=("Segoe UI", 24, "bold"),
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # ESTRUCTURA DE TARJETAS
        tarjetas = [
            ("💰 Ventas del día", "$0.00", "#81C784"),
            ("📦 Productos", "0", "#64B5F6"),
            ("⚠ Inventario bajo", "0", "#FFB74D"),
            ("🧾 Última venta", "Sin ventas", "#E0E0E0"),
        ]

        fila = 1
        columna = 0
        self.lbl_valores = []

        for titulo_texto, valor, color_titulo in tarjetas:

            card = ctk.CTkFrame(
                self, width=250, height=120, corner_radius=12, fg_color="#3A3A3A"
            )

            card.grid(
                row=fila,
                column=columna,
                padx=20,
                pady=15,
                sticky="nsew",
            )

            lblTitulo = ctk.CTkLabel(
                card,
                text=titulo_texto,
                font=("Segoe UI", 18, "bold"),
                text_color=color_titulo,
            )
            lblTitulo.pack(pady=(20, 10))

            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI", 26, "bold"),
                text_color="#FFFFFF",
            )
            lblValor.pack()

            self.lbl_valores.append(lblValor)

            columna += 1
            if columna > 1:
                columna = 0
                fila += 1

        # =========================================================
        # SECCIÓN DE ACCIONES RÁPIDAS (BOTONES DE ACCESO DIRECTO)
        # =========================================================
        self._crear_panel_acciones(fila)

        # Cargar métricas
        self.actualizar()

    def _crear_panel_acciones(self, fila_inicio):
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(
            row=fila_inicio,
            column=0,
            columnspan=2,
            pady=(25, 10),
            padx=20,
            sticky="ew",
        )

        actions_frame.grid_columnconfigure((0, 1), weight=1)

        # Botón 1: Historial de Ventas y Reportes
        btn_historial = ctk.CTkButton(
            actions_frame,
            text="📋 Historial y Reportes de Ventas",
            font=("Segoe UI", 14, "bold"),
            height=45,
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.abrir_historial_ventas,
        )
        btn_historial.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Botón 2: Corte de Caja Directo
        btn_corte = ctk.CTkButton(
            actions_frame,
            text="💵 Corte de Caja (Arqueo)",
            font=("Segoe UI", 14, "bold"),
            height=45,
            fg_color="#D97706",
            hover_color="#B45309",
            command=self.abrir_corte_caja_directo,
        )
        btn_corte.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # =========================================================
    # FUNCIONES DE NAVEGACIÓN Y CONEXIÓN
    # =========================================================

    def abrir_historial_ventas(self):
        """Abre la ventana completa de Historial de Ventas."""
        ventana_historial = HistorialVentasWindow(self)
        ventana_historial.focus()

    def abrir_corte_caja_directo(self):
        """Abre directamente la ventana modal de Arqueo / Corte de Caja."""
        ventana_historial = HistorialVentasWindow(self)
        ventana_historial.withdraw()  # Oculta la lista completa
        ventana_historial.abrir_corte_caja()  # Dispara el modal de corte de caja

    def actualizar(self):
        from app.models.venta import Venta

        # Productos
        total_productos = Producto.contar_productos()
        inventario_bajo = Producto.contar_stock_bajo()

        # Ventas
        total_hoy = Venta.total_hoy()
        ultima = Venta.ultima_venta()

        # Ventas del día
        self.lbl_valores[0].configure(text=f"${total_hoy:,.2f}")

        # Productos
        self.lbl_valores[1].configure(text=str(total_productos))

        # Inventario bajo
        if inventario_bajo > 0:
            self.lbl_valores[2].configure(
                text=str(inventario_bajo), text_color="#FF5252"
            )
        else:
            self.lbl_valores[2].configure(text="0", text_color="#FFFFFF")

        # Última venta
        if ultima:
            self.lbl_valores[3].configure(text=f"Folio #{ultima['id']}")
        else:
            self.lbl_valores[3].configure(text="Sin ventas")