import customtkinter as ctk
from app.models.producto import Producto

class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0, 1), weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Bienvenido a Abarrotes Rosita-Andrea (WI)",
            font=("Segoe UI", 24, "bold")
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # ESTRUCTURA DE TARJETAS: (Texto Titulo, Valor Inicial, Color de Titulo Personalizado)
        # Usamos colores más vivos y claros para que resalten perfectamente
        tarjetas = [
            ("💰 Ventas del día", "$0.00", "#81C784"),        # Verde claro alegre
            ("📦 Productos", "0", "#64B5F6"),                 # Azul claro nítido
            ("⚠ Inventario bajo", "0", "#FFB74D"),            # Naranja/Amarillo de advertencia
            ("🧾 Última venta", "Sin ventas", "#E0E0E0")       # Blanco grisáceo limpio
        ]

        fila = 1
        columna = 0
        self.lbl_valores = []

        for titulo_texto, valor, color_titulo in tarjetas:

            # Se subió el tono a #3A3A3A para crear un contraste ideal en modo oscuro
            card = ctk.CTkFrame(
                self,
                width=250,
                height=120,
                corner_radius=12,
                fg_color="#3A3A3A" 
            )

            card.grid(
                row=fila,
                column=columna,
                padx=20,
                pady=20,
                sticky="nsew"
            )

            lblTitulo = ctk.CTkLabel(
                card,
                text=titulo_texto,
                font=("Segoe UI", 18, "bold"),
                text_color=color_titulo # 👈 Ahora aplica el color único asignado arriba
            )
            lblTitulo.pack(pady=(20, 10))

            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI", 26, "bold"),
                text_color="#FFFFFF" # Forzamos a que el número/valor sea blanco puro brillante
            )
            lblValor.pack()

            self.lbl_valores.append(lblValor)

            columna += 1
            if columna > 1:
                columna = 0
                fila += 1  
        
        self.actualizar()

    def actualizar(self):
        from app.models.venta import Venta

        # Productos
        total_productos = Producto.contar_productos()
        inventario_bajo = Producto.contar_stock_bajo()

        # Ventas
        total_hoy = Venta.total_hoy()
        ultima = Venta.ultima_venta()

        # ==========================
        # TARJETA 1 - Ventas del día
        # ==========================
        self.lbl_valores[0].configure(
            text=f"${total_hoy:,.2f}"
        )

        # ==========================
        # TARJETA 2 - Productos
        # ==========================
        self.lbl_valores[1].configure(
            text=str(total_productos)
        )

        # ==========================
        # TARJETA 3 - Inventario bajo
        # ==========================
        if inventario_bajo > 0:
            self.lbl_valores[2].configure(
                text=str(inventario_bajo),
                text_color="#FF5252"
            )
        else:
            self.lbl_valores[2].configure(
                text="0",
                text_color="#FFFFFF"
            )

        # ==========================
        # TARJETA 4 - Última venta
        # ==========================
        if ultima:
            self.lbl_valores[3].configure(
                text=f"Folio #{ultima['id']}"
            )
        else:
            self.lbl_valores[3].configure(
                text="Sin ventas"
            )