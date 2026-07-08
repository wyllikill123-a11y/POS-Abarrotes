import customtkinter as ctk


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

        for titulo, valor in tarjetas:

            card = ctk.CTkFrame(self,width=250,height=120)

            card.grid(row=fila,column=columna,padx=20,pady=20,sticky="nsew")

            lblTitulo = ctk.CTkLabel(
                card,
                text=titulo,
                font=("Segoe UI",18,"bold")
            )

            lblTitulo.pack(pady=(20,10))

            lblValor = ctk.CTkLabel(
                card,
                text=valor,
                font=("Segoe UI",22)
            )

            lblValor.pack()

            columna += 1

            if columna > 1:

                columna = 0

                fila += 1