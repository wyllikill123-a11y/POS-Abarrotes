import customtkinter as ctk
from app.models.producto import Producto

class Dashboard(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0,1), weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Bienvenido a Abarrotes Rosita-Andrea (WI)",
            font=("Segoe UI",24,"bold")
        )

        titulo.grid(row=0,column=0,columnspan=2,pady=(20,30))

        tarjetas = [
            ("💰 Ventas del día", "$0.00"),
            ("📦 Productos", "0"),
            ("⚠ Inventario bajo", "0"),
            ("🧾 Última venta", "Sin ventas")
        ]

        fila = 1

        columna = 0

        self.lbl_valores = []

        for titulo, valor in tarjetas:

            card = ctk.CTkFrame(
                self,
                width=250,
                height=120,
                corner_radius=12,
                fg_color="#2A2A2A"
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
                text=titulo,
                font=("Segoe UI", 18, "bold"),
                text_color="#4FC3F7"
            )

            lblTitulo.pack(pady=(20,10))

            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI", 26, "bold")
            )

            lblValor.pack()

            self.lbl_valores.append(lblValor)

            columna += 1

            if columna > 1:
                columna = 0
                fila += 1  
        
        self.actualizar()

    def actualizar(self):

        total = Producto.contar_productos()
        bajos = Producto.contar_stock_bajo()

        self.lbl_valores[0].configure(text="$0.00")
        self.lbl_valores[1].configure(text=str(total))
        self.lbl_valores[2].configure(text=str(bajos))
        self.lbl_valores[3].configure(text="Sin ventas")              