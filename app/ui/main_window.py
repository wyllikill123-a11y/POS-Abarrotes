from datetime import datetime
import customtkinter as ctk

from app.ui.corte_window import CorteWindow
from app.ui.dashboard import Dashboard
from app.ui.nueva_venta_window import NuevaVentaWindow
from app.ui.productos_window import ProductosWindow
from app.views.historial_ventas import HistorialVentasWindow


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Abarrotes Rosita-Andrea (WI)")
        self.geometry("1300x750")

        # Configuración de apariencia a Tema Claro
        ctk.set_appearance_mode("Light")

        # Maximizar ventana automáticamente
        self.state("zoomed")

        # Configuración de rejilla principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Construcción de la interfaz
        self.crear_encabezado()
        self.crear_menu()
        self.crear_dashboard()
        self.crear_estado()

        self.actualizar_reloj()
        self.update_idletasks()

    # =========================================================
    # ACCIONES DE NAVEGACIÓN
    # =========================================================

    def abrir_productos(self):
        ProductosWindow(self)

    def abrir_ventas(self):
        NuevaVentaWindow(self)

    def abrir_historial_ventas(self):
        ventana_historial = HistorialVentasWindow(self)
        ventana_historial.focus()

    def abrir_caja_corte(self):
        def al_cerrar_modal():
            if hasattr(self, "dashboard") and self.dashboard:
                self.dashboard.actualizar()

        CorteWindow(self, on_close=al_cerrar_modal)

    # =========================================================
    # COMPONENTES VISUALES
    # =========================================================

    def crear_encabezado(self):
        self.header = ctk.CTkFrame(
            self, height=80, corner_radius=0, fg_color="#FFFFFF"
        )
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Título Principal
        self.titulo = ctk.CTkLabel(
            self.header,
            text="🏪 ABARROTES ROSITA-ANDREA",
            font=("Segoe UI", 26, "bold"),
            text_color="#0F172A",
        )
        self.titulo.pack(side="left", padx=25, pady=15)

        # =========================================================
        # RELOJ DIGITAL MULTI-TAMAÑO
        # =========================================================
        self.frame_reloj = ctk.CTkFrame(self.header, fg_color="transparent")
        self.frame_reloj.pack(side="right", padx=25, pady=10)

        # 1. Fecha (Izquierda)
        self.lbl_fecha = ctk.CTkLabel(
            self.frame_reloj,
            text="",
            font=("Segoe UI", 15, "bold"),
            text_color="#64748B",
        )
        self.lbl_fecha.pack(side="left", padx=(0, 15))

        # 2. Hora y Minutos (30pt - Grande)
        self.lbl_hora_min = ctk.CTkLabel(
            self.frame_reloj,
            text="00:00",
            font=("Consolas", 30, "bold"),
            text_color="#0F172A",
        )
        self.lbl_hora_min.pack(side="left")

        # 3. Segundos (14pt - Pequeños)
        self.lbl_segundos = ctk.CTkLabel(
            self.frame_reloj,
            text=":00",
            font=("Consolas", 14, "bold"),
            text_color="#64748B",
        )
        self.lbl_segundos.pack(side="left", anchor="n", pady=(5, 0))

        # 4. AM / PM
        self.lbl_ampm = ctk.CTkLabel(
            self.frame_reloj,
            text="AM",
            font=("Segoe UI", 15, "bold"),
            text_color="#2563EB",
        )
        self.lbl_ampm.pack(side="left", padx=(8, 0))

    def crear_menu(self):
        self.menu = ctk.CTkFrame(
            self, width=320, corner_radius=0, fg_color="#F1F5F9"
        )
        self.menu.grid(row=1, column=0, sticky="ns")
        self.menu.grid_propagate(False)

        # =========================================================
        # ENCABEZADO DESTACADO EN CUADRO OSCURO
        # =========================================================
        frame_titulo_menu = ctk.CTkFrame(
            self.menu,
            fg_color="#0F172A",
            corner_radius=8,
            height=48,
        )
        frame_titulo_menu.pack(fill="x", padx=15, pady=(15, 12))
        frame_titulo_menu.pack_propagate(False)

        lbl_menu = ctk.CTkLabel(
            frame_titulo_menu,
            text="📌 MENÚ PRINCIPAL",
            font=("Segoe UI", 15, "bold"),
            text_color="#FFFFFF",
        )
        lbl_menu.pack(expand=True)

        # =========================================================
        # BOTONES DEL MENÚ EN MAYÚSCULAS Y 17PT
        # =========================================================
        botones = [
            ("🛒  NUEVA VENTA", self.abrir_ventas, "#2563EB", "#1D4ED8", "#FFFFFF"),
            ("🔑  CORTE / CAJA", self.abrir_caja_corte, "#059669", "#047857", "#FFFFFF"),
            ("📦  PRODUCTOS", self.abrir_productos, "transparent", "#E2E8F0", "#1E293B"),
            ("📊  INVENTARIO", None, "transparent", "#E2E8F0", "#1E293B"),
            ("📈  REPORTES / HISTORIAL", self.abrir_historial_ventas, "transparent", "#E2E8F0", "#1E293B"),
            ("⚙  CONFIGURACIÓN", None, "transparent", "#E2E8F0", "#1E293B"),
        ]

        for texto, comando, color_bg, color_hover, color_texto in botones:
            btn = ctk.CTkButton(
                self.menu,
                text=texto,
                height=55,
                corner_radius=8,
                font=("Segoe UI", 17, "bold"),
                anchor="w",
                fg_color=color_bg,
                hover_color=color_hover,
                text_color=color_texto,
                command=comando,
            )
            btn.pack(fill="x", padx=15, pady=6)

    def crear_dashboard(self):
        self.dashboard = Dashboard(self)
        self.dashboard.configure(fg_color="#F8FAFC")
        self.dashboard.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)

    def crear_estado(self):
        barra = ctk.CTkFrame(
            self, height=35, corner_radius=0, fg_color="#E2E8F0"
        )
        barra.grid(row=2, column=0, columnspan=2, sticky="ew")

        estado = ctk.CTkLabel(
            barra,
            text="● BASE DE DATOS CONECTADA | VERSIÓN 0.2.0",
            font=("Segoe UI", 12, "bold"),
            text_color="#059669",
        )
        estado.pack(side="left", padx=20, pady=5)

    # =========================================================
    # LÓGICA DEL RELOJ MULTI-ETIQUETA
    # =========================================================

    def actualizar_reloj(self):
        ahora = datetime.now()

        fecha_str = ahora.strftime("🗓 %d/%m/%Y")
        hora_min_str = ahora.strftime("%I:%M")
        segundos_str = ahora.strftime(":%S")
        ampm_str = ahora.strftime("%p")

        self.lbl_fecha.configure(text=fecha_str)
        self.lbl_hora_min.configure(text=hora_min_str)
        self.lbl_segundos.configure(text=segundos_str)
        self.lbl_ampm.configure(text=ampm_str)

        self.after(1000, self.actualizar_reloj)