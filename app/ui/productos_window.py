import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox

from app.models.producto import Producto
from app.ui.nuevo_producto import NuevoProducto

class ProductosWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        # ========= AJUSTE DE GEOMETRÍA SEGURO =========
        master.update_idletasks()
        
        self.title("Productos")
        self.geometry("1000x650")
        
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.lift()

        # ========= CONFIGURACIÓN DE ESTILO NEGRO PARA LA TABLA =========
        style = ttk.Style()
        # Usamos el tema 'clam' como base porque permite modificar los bordes y colores del Treeview
        style.theme_use("clam")
        
        # Color de fondo general de la aplicación (#242424 es el oscuro estándar de CustomTkinter)
        style.configure(
            "Treeview",
            background="#242424",
            fieldbackground="#242424",
            foreground="white",
            rowheight=28,
            font=("Segoe UI", 11)
        )
        
        # Color cuando el usuario selecciona una fila (Azul moderno de CustomTkinter)
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )
        
        # Estilo para los encabezados de la tabla (Código, Producto, etc.)
        style.configure(
            "Treeview.Heading",
            background="#1A1A1A",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            borderwidth=1,
            relief="flat"
        )
        
        # Cambio de color cuando pasas el mouse sobre los encabezados
        style.map(
            "Treeview.Heading",
            background=[("active", "#2D2D2D")],
            foreground=[("active", "white")]
        )
        # ===============================================================

        titulo = ctk.CTkLabel(
            self,
            text="📦 Administración de Productos",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=15)
        
        barra = ctk.CTkFrame(self)
        barra.pack(fill="x", padx=20, pady=10)

        barra_botones = ctk.CTkFrame(self)
        barra_botones.pack(fill="x", padx=20, pady=(0, 10))

        # BOTONES DE ACCIÓN
        ctk.CTkButton(
            barra_botones,
            text="➕ Nuevo",
            width=120,
            command=self.abrir_nuevo_producto
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="✏ Editar",
            width=120,
            command=self.editar_producto_boton
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="❌ Desactivar",
            width=120
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="📥 Excel",
            width=120
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="🔄 Actualizar",
            width=120,
            command=self.cargar_productos
        ).pack(side="right", padx=5, pady=8)

        ctk.CTkLabel(
            barra,
            text="🔍 Buscar:"
        ).pack(side="left", padx=(10, 5))

        self.buscar = ctk.CTkEntry(
            barra,
            width=250,
            placeholder_text="Nombre o código..."
        )
        self.buscar.pack(side="left")
        self.buscar.bind("<KeyRelease>", self.buscar_producto)
        
        # CONFIGURACIÓN DE TABLA (TREEVIEW)
        columns = (
            "codigo",
            "nombre",
            "unidad",
            "precio_compra",
            "precio_venta",
            "existencia"
        )

        self.tabla = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=18
        )

        self.tabla.bind(
            "<Double-1>",
            self.editar_producto
        )

        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("unidad", text="Unidad")
        self.tabla.heading("precio_compra", text="Compra")
        self.tabla.heading("precio_venta", text="Venta")
        self.tabla.heading("existencia", text="Stock")

        self.tabla.column("codigo", width=110, anchor="center")
        self.tabla.column("nombre", width=360)
        self.tabla.column("unidad", width=100, anchor="center")
        self.tabla.column("precio_compra", width=100, anchor="e")
        self.tabla.column("precio_venta", width=100, anchor="e")
        self.tabla.column("existencia", width=90, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_total = ctk.CTkLabel(
            self,
            text=""
        )
        self.lbl_total.pack(anchor="e", padx=20, pady=(0, 10))

        self.cargar_productos()
        self.buscar.focus()

    def editar_producto(self, event=None):
        seleccionado = self.tabla.selection()

        if not seleccionado:
            return

        datos = self.tabla.item(
            seleccionado[0],
            "values"
        )

        codigo = datos[0]
        producto = Producto.buscar_por_codigo(codigo)

        ventana = NuevoProducto(self, producto)
        self.wait_window(ventana)
        self.cargar_productos()

    def editar_producto_boton(self):
        seleccionado = self.tabla.selection()
        
        if not seleccionado:
            messagebox.showwarning("Atención", "Por favor, seleccione un producto de la lista para editar.")
            return
            
        self.editar_producto()

    def cargar_productos(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        productos = Producto.obtener_todos()

        for producto in productos:
            datos = (
                producto[0],
                producto[1],
                producto[2],
                f"${float(producto[3]):.2f}",
                f"${float(producto[4]):.2f}",
                producto[5]
            )
            self.tabla.insert("", "end", values=datos)

        self.lbl_total.configure(
            text=f"Productos registrados: {len(productos)}"
        )

    def abrir_nuevo_producto(self):
        ventana = NuevoProducto(self)
        self.wait_window(ventana)
        self.cargar_productos()

    def buscar_producto(self, event):
        texto = self.buscar.get()

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        productos = Producto.buscar(texto)

        for producto in productos:
            datos = (
                producto[0],
                producto[1],
                producto[2],
                f"${float(producto[3]):.2f}",
                f"${float(producto[4]):.2f}",
                producto[5]
            )
            self.tabla.insert("", "end", values=datos)

        self.lbl_total.configure(
            text=f"Productos encontrados: {len(productos)}"
        )