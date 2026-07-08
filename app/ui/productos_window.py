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

        barra_botones = ctk.CTkFrame(self)
        barra_botones.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(
            barra_botones,
            text="➕ Nuevo",
            width=120,
            command=self.abrir_nuevo_producto
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="✏ Editar",
            width=120
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

        # Limpiar la tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        # Obtener los productos de la base de datos
        productos = Producto.obtener_todos()

        # Insertarlos en la tabla con formato
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

        # Actualizar contador
        self.lbl_total.configure(
            text=f"Productos registrados: {len(productos)}"
        )

    def abrir_nuevo_producto(self):

        NuevoProducto(self)

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