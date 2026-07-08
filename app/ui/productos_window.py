import customtkinter as ctk
from tkinter import ttk

from app.models.producto import Producto
from app.ui.nuevo_producto import NuevoProducto


class ProductosWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Productos")
        self.geometry("1000x650")

        titulo = ctk.CTkLabel(
            self,
            text="📦 Administración de Productos",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=15)
        
        barra = ctk.CTkFrame(self)
        barra.pack(fill="x", padx=20, pady=10)

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

        ctk.CTkButton(
            barra,
            text="🔄 Actualizar",
            width=120,
            command=self.cargar_productos
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            barra,
            text="➕ Nuevo Producto",
            width=160,
            command=self.abrir_nuevo_producto
        ).pack(side="right", padx=5)
        
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
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("unidad", text="Unidad")
        self.tabla.heading("precio_compra", text="Compra")
        self.tabla.heading("precio_venta", text="Venta")
        self.tabla.heading("existencia", text="Existencia")

        self.tabla.column("codigo", width=100)
        self.tabla.column("nombre", width=350)
        self.tabla.column("unidad", width=100)
        self.tabla.column("precio_compra", width=100)
        self.tabla.column("precio_venta", width=100)
        self.tabla.column("existencia", width=100)

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.cargar_productos()

    def editar_producto(self, event):

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

    def cargar_productos(self):

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        productos = Producto.obtener_todos()

        for producto in productos:
            self.tabla.insert("", "end", values=producto)

    def abrir_nuevo_producto(self):

        NuevoProducto(self)