import customtkinter as ctk
from app.models.producto import Producto


class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")

        self.grid_columnconfigure((0, 1), weight=1)

        # TÍTULO PRINCIPAL
        titulo = ctk.CTkLabel(
            self,
            text="BIENVENIDO A ABARROTES ROSITA-ANDREA (WI)",
            font=("Segoe UI", 22, "bold"),
            text_color="#0F172A",
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(20, 25))

        # ESTRUCTURA DE TARJETAS (Fondo Gris Oscuro Suave)
        tarjetas = [
            ("💰 VENTAS DEL DÍA", "$0.00", "#4ADE80"),
            ("📦 PRODUCTOS", "0", "#38BDF8"),
            ("⚠️ INVENTARIO BAJO", "0", "#FBBF24"),
            ("🧾 ÚLTIMA VENTA", "SIN VENTAS", "#E2E8F0"),
        ]

        fila = 1
        columna = 0
        self.lbl_valores = []

        for titulo_texto, valor, color_titulo in tarjetas:

            # Tarjeta con fondo gris oscuro profesional (#2B2D31)
            card = ctk.CTkFrame(
                self,
                corner_radius=12,
                fg_color="#2B2D31",
                border_width=1,
                border_color="#1E1F22",
            )

            card.grid(
                row=fila,
                column=columna,
                padx=15,
                pady=12,
                sticky="nsew",
            )

            # Título de la tarjeta (16pt para evitar desbordes)
            lblTitulo = ctk.CTkLabel(
                card,
                text=titulo_texto,
                font=("Segoe UI", 16, "bold"),
                text_color=color_titulo,
            )
            lblTitulo.pack(pady=(18, 6), padx=10)

            # Valor métrico (26pt con ajuste automático de margen)
            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI", 26, "bold"),
                text_color="#FFFFFF",
            )
            lblValor.pack(pady=(0, 18), padx=10)

            self.lbl_valores.append(lblValor)

            columna += 1
            if columna > 1:
                columna = 0
                fila += 1

        # Cargar métricas
        self.actualizar()

    # =========================================================
    # ACTUALIZACIÓN DE MÉTRICAS EN TIEMPO REAL
    # =========================================================

    def actualizar(self):
        from app.models.venta import Venta

        total_productos = Producto.contar_productos()
        inventario_bajo = Producto.contar_stock_bajo()

        total_hoy = Venta.total_hoy()
        ultima = Venta.ultima_venta()

        # 1. Ventas del día
        self.lbl_valores[0].configure(text=f"${total_hoy:,.2f}")

        # 2. Productos registrados
        self.lbl_valores[1].configure(text=str(total_productos))

        # 3. Alerta de Inventario bajo
        if inventario_bajo > 0:
            self.lbl_valores[2].configure(
                text=str(inventario_bajo), text_color="#F87171"
            )
        else:
            self.lbl_valores[2].configure(text="0", text_color="#FFFFFF")

        # 4. Última venta realizada
        if ultima:
            self.lbl_valores[3].configure(text=f"FOLIO #{ultima['id']}")
        else:
            self.lbl_valores[3].configure(text="SIN VENTAS")