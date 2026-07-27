import tkinter as tk
from tkinter import ttk, messagebox

from app.models.producto import Producto
from app.ui.nuevo_producto import NuevoProducto


class VistaProductos(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)

        self.crear_widgets()
        self.cargar_productos()

    # ==========================================================
    # INTERFAZ
    # ==========================================================
    def crear_widgets(self):

        frame_superior = ttk.Frame(self, padding=10)
        frame_superior.pack(fill=tk.X)

        ttk.Label(frame_superior, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))

        self.txt_buscar = ttk.Entry(frame_superior, width=30)
        self.txt_buscar.pack(side=tk.LEFT, padx=5)
        self.txt_buscar.bind("<KeyRelease>", self.filtrar_productos)
        # Mostrar desactivados
        self.mostrar_desactivados = tk.BooleanVar(value=False)

        chk_desactivados = ttk.Checkbutton(
            frame_superior,
            text="Mostrar productos desactivados",
            variable=self.mostrar_desactivados,
            command=self.cargar_productos
        )

        chk_desactivados.pack(side=tk.LEFT, padx=15)

        ttk.Button(
            frame_superior,
            text="Nuevo Producto",
            command=self.abrir_nuevo
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_superior,
            text="Editar",
            command=self.abrir_editar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_superior,
            text="Activar / Desactivar",
            command=self.cambiar_estado_producto
        ).pack(side=tk.LEFT, padx=5)

        columnas = (
            "codigo",
            "codigo_barras",
            "nombre",
            "unidad",
            "tipo_venta",
            "precio_compra",
            "precio_venta",
            "existencia",
            "stock_minimo",
            "categoria",
            "activo",
        )

        self.tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tabla.tag_configure(
            "desactivado",
            foreground="gray"
        )

        encabezados = (
            "Código",
            "C. Barras",
            "Nombre",
            "Unidad",
            "Tipo Venta",
            "P. Compra",
            "P. Venta",
            "Existencia",
            "Stock Mín.",
            "Categoría",
            "Activo"
        )

        for columna, titulo in zip(columnas, encabezados):
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=100, anchor=tk.CENTER)

        self.tabla.column("nombre", width=180, anchor=tk.W)
        self.tabla.column("codigo", width=90)

        scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tabla.yview
        )

        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=(10, 0),
            pady=10
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
            padx=(0, 10),
            pady=10
        )

        self.tabla.bind("<Double-1>", lambda e: self.abrir_editar())

    # ==========================================================
    # CARGAR PRODUCTOS
    # ==========================================================
    def cargar_productos(self, texto_busqueda=None):

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        incluir = self.mostrar_desactivados.get()

        if texto_busqueda:
            productos = Producto.buscar(
                texto_busqueda,
                incluir_desactivados=incluir
            )
        else:
            productos = Producto.obtener_todos(
                incluir_desactivados=incluir
            )

        for prod in productos:

            tag = ()

            if prod["activo"] == 0:
                tag = ("desactivado",)

            self.tabla.insert(
                "",
                tk.END,
                iid=prod["codigo"],
                values=(
                    prod["codigo"],
                    prod["codigo_barras"] or "",
                    prod["nombre"],
                    prod["unidad"],
                    prod["tipo_venta"],
                    f"${prod['precio_compra']:.2f}",
                    f"${prod['precio_venta']:.2f}",
                    prod["existencia"],
                    prod["stock_minimo"],
                    prod["categoria_id"],
                    "Sí" if prod["activo"] else "No",
                ),
                tags=tag
            )

    def cambiar_estado_producto(self):

        seleccionado = self.tabla.selection()

        if not seleccionado:
            messagebox.showwarning(
                "Atención",
                "Seleccione un producto."
            )
            return

        codigo = seleccionado[0]

        producto = Producto.buscar_por_codigo(codigo)

        if not producto:
            messagebox.showerror(
                "Error",
                "No se encontró el producto."
            )
            return

        if producto["activo"] == 1:
            accion = "desactivar"
        else:
            accion = "reactivar"

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"¿Desea {accion} este producto?"
        )

        if not confirmar:
            return

        if producto["activo"] == 1:
            Producto.desactivar(codigo)
            mensaje = "Producto desactivado correctamente."
        else:
            Producto.reactivar(codigo)
            mensaje = "Producto reactivado correctamente."

        self.cargar_productos(self.txt_buscar.get().strip() or None)

        messagebox.showinfo(
            "Correcto",
            mensaje
        )

    # ==========================================================
    # NUEVO PRODUCTO
    # ==========================================================
    def abrir_nuevo(self):

        ventana = NuevoProducto(self)

        self.wait_window(ventana)

        self.cargar_productos()

    # ==========================================================
    # EDITAR
    # ==========================================================
    def abrir_editar(self):

        seleccionado = self.tabla.selection()

        if not seleccionado:
            messagebox.showwarning(
                "Atención",
                "Seleccione un producto."
            )
            return

        codigo = seleccionado[0]

        datos = Producto.buscar_por_codigo(codigo)

        if datos:

            ventana = NuevoProducto(self, datos)

            self.wait_window(ventana)

            self.cargar_productos()

    # ==========================================================
    # ACTIVAR / DESACTIVAR
    # ==========================================================
    def cambiar_estado_producto(self):

        seleccionado = self.tabla.selection()

        if not seleccionado:
            messagebox.showwarning(
                "Atención",
                "Seleccione un producto."
            )
            return

        codigo = seleccionado[0]

        producto = Producto.buscar_por_codigo(codigo)

        if not producto:
            messagebox.showerror(
                "Error",
                "No se encontró el producto."
            )
            return

        if producto["activo"] == 1:

            confirmar = messagebox.askyesno(
                "Confirmar",
                "¿Desea desactivar este producto?"
            )

            if confirmar:
                Producto.desactivar(codigo)
                messagebox.showinfo(
                    "Correcto",
                    "Producto desactivado."
                )

        else:

            confirmar = messagebox.askyesno(
                "Confirmar",
                "¿Desea reactivar este producto?"
            )

            if confirmar:
                Producto.reactivar(codigo)
                messagebox.showinfo(
                    "Correcto",
                    "Producto reactivado."
                )

        self.cargar_productos()
        