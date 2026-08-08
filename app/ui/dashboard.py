import customtkinter as ctk
from app.models.producto import Producto
from app.models.turno import Turno


class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")

        self.grid_columnconfigure((0, 1, 2), weight=1)

        # TÍTULO PRINCIPAL
        titulo = ctk.CTkLabel(
            self,
            text="SISTEMA DE CONTROL DE ABARROTES",
            font=("Segoe UI", 22, "bold"),
            text_color="#0F172A",
        )
        titulo.grid(row=0, column=0, columnspan=3, pady=(20, 25))

        # ESTRUCTURA DE TARJETAS (9 Métricas clave distribuidas en 3 columnas)
        tarjetas = [
            # Fila 1: Métodos de Pago
            ("💵 VENTAS EFECTIVO", "$0.00", "#4ADE80"),
            ("🏦 TRANSFERENCIA", "$0.00", "#38BDF8"),
            ("💳 VENTAS TARJETA", "$0.00", "#FBBF24"),
            # Fila 2: Inventario
            ("📦 PRODUCTOS", "0", "#38BDF8"),
            ("⚠️ INVENTARIO BAJO", "0", "#F87171"),
            ("🧾 ÚLTIMA VENTA", "SIN VENTAS", "#E2E8F0"),
            # Fila 3: Caja y Turno
            ("💰 TOTAL DEL DÍA", "$0.00", "#4ADE80"),
            ("🔑 ESTADO DE CAJA", "CERRADA", "#F87171"),
            ("🕒 TURNO ACTIVO", "SIN TURNO", "#A78BFA"),
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
                padx=10,
                pady=10,
                sticky="nsew",
            )

            # Título de la tarjeta
            lblTitulo = ctk.CTkLabel(
                card,
                text=titulo_texto,
                font=("Segoe UI", 14, "bold"),
                text_color=color_titulo,
            )
            lblTitulo.pack(pady=(15, 5), padx=10)

            # Valor métrico
            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI", 20, "bold"),
                text_color="#FFFFFF",
            )
            lblValor.pack(pady=(0, 15), padx=10)

            self.lbl_valores.append(lblValor)

            columna += 1
            if columna > 2:
                columna = 0
                fila += 1

        # Cargar métricas al iniciar
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
        turno_activo = Turno.obtener_activo()

        # Desglose de ventas por método de pago
        id_turno = turno_activo["id"] if turno_activo else None
        desglose_pagos = Venta.obtener_ventas_por_metodo_pago(id_turno=id_turno)

        # 1. Métodos de Pago
        self.lbl_valores[0].configure(
            text=f"${desglose_pagos.get('EFECTIVO', 0.0):,.2f}"
        )
        self.lbl_valores[1].configure(
            text=f"${desglose_pagos.get('TRANSFERENCIA', 0.0):,.2f}"
        )
        self.lbl_valores[2].configure(
            text=f"${desglose_pagos.get('TARJETA', 0.0):,.2f}"
        )

        # 2. Productos registrados
        self.lbl_valores[3].configure(text=str(total_productos))

        # 3. Alerta de Inventario bajo
        if inventario_bajo > 0:
            self.lbl_valores[4].configure(
                text=str(inventario_bajo), text_color="#F87171"
            )
        else:
            self.lbl_valores[4].configure(text="0", text_color="#FFFFFF")

        # 4. Última venta realizada
        if ultima:
            self.lbl_valores[5].configure(text=f"FOLIO #{ultima['id']}")
        else:
            self.lbl_valores[5].configure(text="SIN VENTAS")

        # 5. Total acumulado del día
        self.lbl_valores[6].configure(text=f"${total_hoy:,.2f}")

        # 6. Estado de la Caja y Turno Activo
        if turno_activo:
            self.lbl_valores[7].configure(text="ABIERTA", text_color="#4ADE80")
            self.lbl_valores[8].configure(text=f"TURNO #{turno_activo['id']}")
        else:
            self.lbl_valores[7].configure(text="CERRADA", text_color="#F87171")
            self.lbl_valores[8].configure(text="SIN TURNO")