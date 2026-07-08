import customtkinter as ctk
from datetime import datetime
from app.ui.dashboard import Dashboard
from app.ui.productos_window import ProductosWindow

class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Abarrotes Rosita-Andrea (WI)")
        self.geometry("1300x750")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_encabezado()
        self.crear_menu()
        self.crear_dashboard()
        self.crear_estado()

        self.actualizar_reloj()

    def abrir_productos(self):
        ProductosWindow(self)

    def crear_encabezado(self):

        self.header = ctk.CTkFrame(self,height=70)

        self.header.grid(row=0,column=0,columnspan=2,sticky="ew")

        self.titulo = ctk.CTkLabel(
            self.header,
            text="ABARROTES ROSITA-ANDREA (WI)",
            font=("Segoe UI",24,"bold")
        )

        self.titulo.pack(side="left",padx=20,pady=15)

        self.reloj = ctk.CTkLabel(self.header,text="")

        self.reloj.pack(side="right",padx=20)

    def crear_menu(self):

        self.menu = ctk.CTkFrame(self,width=220)

        self.menu.grid(row=1,column=0,sticky="ns")

        botones = [
            "🛒 Nueva Venta",
            "📦 Productos",
            "📥 Compras",
            "📊 Inventario",
            "👨‍💼 Proveedores",
            "📈 Reportes",
            "💲 Corte de Caja",
            "⚙ Configuración"
        ]
        for texto in botones:

            comando = None

            if texto == "📦 Productos":
                comando = self.abrir_productos

            boton = ctk.CTkButton(
                self.menu,
                text=texto,
                height=45,
                command=comando
            )

            boton.pack(fill="x", padx=15, pady=8)

    def crear_dashboard(self):

        self.dashboard = Dashboard(self)

        self.dashboard.grid(row=1,column=1,sticky="nsew")

    def crear_estado(self):

        barra = ctk.CTkFrame(self,height=30)

        barra.grid(row=2,column=0,columnspan=2,sticky="ew")

        estado = ctk.CTkLabel(
            barra,
            text="🟢 Base de datos conectada | Versión 0.2.0"
        )

        estado.pack(side="left",padx=15)

    def actualizar_reloj(self):

        ahora = datetime.now()

        self.reloj.configure(
            text=ahora.strftime("%d/%m/%Y  %H:%M:%S")
        )

        self.after(1000,self.actualizar_reloj)