import tkinter as tk
from tkinter import ttk, messagebox
from app.models.producto import Producto


class NuevoProducto(tk.Toplevel):
    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.parent = parent
        self.producto = producto  # Si viene con datos, estamos EDITANDO; si es None, estamos CREANDO

        # Configuración de la ventana modal
        self.title("Editar Producto" if self.producto else "Nuevo Producto")
        self.geometry("450x520")
        self.resizable(False, False)
        
        # Hacer la ventana modal (bloquea la ventana principal hasta cerrar)
        self.transient(parent)
        self.grab_set()

        self.crear_widgets()

        # Si nos pasaron un producto, llenamos los campos para editar
        if self.producto:
            self.cargar_datos_producto()

    def crear_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Configuración de filas y columnas del grid
        container.columnconfigure(1, weight=1)

        # CAMPOS DEL FORMULARIO
        # 1. Código interno
        ttk.Label(container, text="Código Interno *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.txt_codigo = ttk.Entry(container)
        self.txt_codigo.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # 2. Código de barras
        ttk.Label(container, text="Código de Barras:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.txt_codigo_barras = ttk.Entry(container)
        self.txt_codigo_barras.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # 3. Nombre
        ttk.Label(container, text="Nombre *:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.txt_nombre = ttk.Entry(container)
        self.txt_nombre.grid(row=2, column=1, sticky=tk.EW, pady=5)

        # 4. Unidad de medida
        ttk.Label(container, text="Unidad:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cmb_unidad = ttk.Combobox(container, values=["Pieza", "Kg", "Litro", "Paquete", "Caja"], state="readonly")
        self.cmb_unidad.set("Pieza")
        self.cmb_unidad.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # 5. Tipo de Venta
        ttk.Label(container, text="Tipo Venta:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.cmb_tipo_venta = ttk.Combobox(container, values=["Unidad", "A granel"], state="readonly")
        self.cmb_tipo_venta.set("Unidad")
        self.cmb_tipo_venta.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # 6. Precio Compra
        ttk.Label(container, text="Precio Compra ($):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.txt_precio_compra = ttk.Entry(container)
        self.txt_precio_compra.insert(0, "0.00")
        self.txt_precio_compra.grid(row=5, column=1, sticky=tk.EW, pady=5)

        # 7. Precio Venta
        ttk.Label(container, text="Precio Venta ($) *:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.txt_precio_venta = ttk.Entry(container)
        self.txt_precio_venta.insert(0, "0.00")
        self.txt_precio_venta.grid(row=6, column=1, sticky=tk.EW, pady=5)

        # 8. Existencia / Stock actual
        ttk.Label(container, text="Existencia Actual:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.txt_existencia = ttk.Entry(container)
        self.txt_existencia.insert(0, "0")
        self.txt_existencia.grid(row=7, column=1, sticky=tk.EW, pady=5)

        # 9. Stock Mínimo
        ttk.Label(container, text="Stock Mínimo:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.txt_stock_minimo = ttk.Entry(container)
        self.txt_stock_minimo.insert(0, "5")
        self.txt_stock_minimo.grid(row=8, column=1, sticky=tk.EW, pady=5)

        # BOTONES
        frame_botones = ttk.Frame(container)
        frame_botones.grid(row=9, column=0, columnspan=2, pady=(20, 0))

        btn_guardar = ttk.Button(frame_botones, text="Guardar", command=self.guardar_producto)
        btn_guardar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = ttk.Button(frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=10)

    def cargar_datos_producto(self):
        """Si es edición, rellena los campos con los valores del producto enviado."""
        prod = self.producto
        
        self.txt_codigo.insert(0, prod["codigo"])
        # Guardamos el código original por si el usuario cambia el código al editar
        self.codigo_anterior = prod["codigo"]

        self.txt_codigo_barras.insert(0, prod["codigo_barras"] or "")
        self.txt_nombre.insert(0, prod["nombre"])
        self.cmb_unidad.set(prod["unidad"])
        self.cmb_tipo_venta.set(prod["tipo_venta"])

        self.txt_precio_compra.delete(0, tk.END)
        self.txt_precio_compra.insert(0, str(prod["precio_compra"]))

        self.txt_precio_venta.delete(0, tk.END)
        self.txt_precio_venta.insert(0, str(prod["precio_venta"]))

        self.txt_existencia.delete(0, tk.END)
        self.txt_existencia.insert(0, str(prod["existencia"]))

        self.txt_stock_minimo.delete(0, tk.END)
        self.txt_stock_minimo.insert(0, str(prod["stock_minimo"]))

    def guardar_producto(self):
        # 1. Obtener valores y limpiar espacios
        codigo = self.txt_codigo.get().strip()
        codigo_barras = self.txt_codigo_barras.get().strip() or None
        nombre = self.txt_nombre.get().strip()
        unidad = self.cmb_unidad.get()
        tipo_venta = self.cmb_tipo_venta.get()

        # 2. Validaciones básicas
        if not codigo or not nombre:
            messagebox.showerror("Error de Validación", "El Código y el Nombre son obligatorios.", parent=self)
            return

        try:
            precio_compra = float(self.txt_precio_compra.get().strip())
            precio_venta = float(self.txt_precio_venta.get().strip())
            existencia = float(self.txt_existencia.get().strip())
            stock_minimo = float(self.txt_stock_minimo.get().strip())
        except ValueError:
            messagebox.showerror("Error de Formato", "Los precios y existencias deben ser números válidos.", parent=self)
            return

        # 3. Guardar o Actualizar usando el modelo Producto
        try:
            if self.producto:
                # MODO EDITAR
                Producto.actualizar(
                    codigo_anterior=self.codigo_anterior,
                    codigo_nuevo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    categoria_id=self.producto["categoria_id"]
                )
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.", parent=self)
            else:
                # MODO NUEVO
                nuevo = Producto(
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    categoria_id=1,
                    activo=1
                )
                nuevo.guardar()
                messagebox.showinfo("Éxito", "Producto guardado correctamente.", parent=self)

            self.destroy()  # Cierra la ventana emergente

        except Exception as e:
            messagebox.showerror("Error en Base de Datos", f"No se pudo procesar la solicitud:\n{e}", parent=self)