import customtkinter as ctk
from datetime import datetime
from app.ui.dashboard import Dashboard
from app.ui.productos_window import ProductosWindow

class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Abarrotes Rosita-Andrea (WI)")
        self.geometry("1300x750")

        # ========= AJUSTE PARA PANTALLA COMPLETA =========
        self.state("zoomed")  # Abre la ventana maximizada automáticamente
        # =================================================

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_encabezado()
        self.crear_menu()
        self.crear_dashboard()
        self.crear_estado()

        self.actualizar_reloj()
        
        # ========= SEGURO DE DIMENSIONES REALES =========
        self.update_idletasks()  # Registra el tamaño completo para las ventanas flotantes
        # ================================================

    def abrir_productos(self):
        ProductosWindow(self)

    def crear_encabezado(self):

        self.header = ctk.CTkFrame(
            self,
            height=70,
            fg_color="#1A1A1A"
        )
        self.header.grid(row=0,column=0,columnspan=2,sticky="ew")

        self.titulo = ctk.CTkLabel(
            self.header,
            text="🏪 ABARROTES ROSITA-ANDREA (WI)",
            font=("Segoe UI", 25, "bold"),
            text_color="#4FC3F7"
        )

        self.titulo.pack(side="left",padx=20,pady=15)

        self.reloj = ctk.CTkLabel(
            self.header,
            text="",
            font=("Segoe UI",16,"bold"),
            text_color="#7FDBFF"
        )

        self.reloj.pack(side="right",padx=20)

    def crear_menu(self):

        self.menu = ctk.CTkFrame(
            self,
            width=230,
            fg_color="#222222"
        )
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
                height=50,
                corner_radius=10,
                font=("Segoe UI",15,"bold"),
                fg_color="#2B2B2B",
                hover_color="#2196F3",
                border_width=1,
                border_color="#505050",
                text_color="white",
                command=comando
            )

            boton.pack(fill="x", padx=15, pady=8)

    def crear_dashboard(self):

        self.dashboard = Dashboard(self)

        self.dashboard.grid(row=1,column=1,sticky="nsew")

    def crear_estado(self):

        barra = ctk.CTkFrame(
            self,
            height=30,
            fg_color="#1A1A1A"
        )
        barra.grid(row=2,column=0,columnspan=2,sticky="ew")

        estado = ctk.CTkLabel(
            barra,
            text="🟢 Base de datos conectada | Versión 0.2.0",
            text_color="#CFCFCF"
        )

        estado.pack(side="left",padx=15)

    def actualizar_reloj(self):

        ahora = datetime.now()

        self.reloj.configure(
            text=ahora.strftime("🗓 %d/%m/%Y    🕒 %I:%M:%S %p")
        )

        self.after(1000,self.actualizar_reloj)