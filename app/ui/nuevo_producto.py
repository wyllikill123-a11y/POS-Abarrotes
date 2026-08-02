import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from app.ui.marcas import AdminMarcas
from app.models.producto import Producto, obtener_conexion
from app.ui.categorias import AdminCategorias
from app.ui.proveedores import AdminProveedores

class NuevoProducto(tk.Toplevel):

    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.parent = parent
        self.producto = producto  # Si viene con datos EDITAMOS; si es None, CREAMOS

        # Diccionarios para mapear "Nombre Visible" -> "ID en BD"
        self.mapa_categorias = {}
        self.mapa_marcas = {}
        self.mapa_proveedores = {}

        self.title("Editar Producto" if self.producto else "Nuevo Producto")
        self.geometry("520x680")
        self.resizable(False, False)

        # Configuración modal
        self.transient(parent)
        self.grab_set()

        # Cargar catálogos
        self.cargar_catalogos()

        # Construir interfaz
        self.crear_widgets()

        # Cargar datos o seleccionar valor por defecto
        if self.producto:
            self.cargar_datos_producto()
        else:
            self.seleccionar_primeros_elementos()

        # MEJORA 1: Focus inicial en el primer campo de texto
        self.txt_codigo.focus_set()

        # MEJORA 5: Vinculación de la tecla Return (Enter) para guardar
        self.bind("<Return>", lambda event: self.guardar_producto())

    # ==========================================================
    # CARGAR CATÁLOGOS DESDE LA BD
    # ==========================================================
    def cargar_catalogos(self):
        """Consulta la base de datos para obtener Categorías, Marcas y Proveedores."""
        self.mapa_categorias.clear()
        self.mapa_marcas.clear()
        self.mapa_proveedores.clear()

        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
                for row in cursor.fetchall():
                    self.mapa_categorias[row["nombre"]] = row["id"]

                cursor.execute("SELECT id, nombre FROM marcas ORDER BY nombre")
                for row in cursor.fetchall():
                    self.mapa_marcas[row["nombre"]] = row["id"]

                cursor.execute("SELECT id, nombre FROM proveedores ORDER BY nombre")
                for row in cursor.fetchall():
                    self.mapa_proveedores[row["nombre"]] = row["id"]

        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudieron cargar los catálogos:\n{e}",
                parent=self,
            )

    def seleccionar_primeros_elementos(self):
        """Si es registro nuevo, selecciona el primer ítem disponible."""
        if self.mapa_categorias:
            self.cmb_categoria.set(list(self.mapa_categorias.keys())[0])
        if self.mapa_marcas:
            self.cmb_marca.set(list(self.mapa_marcas.keys())[0])
        if self.mapa_proveedores:
            self.cmb_proveedor.set(list(self.mapa_proveedores.keys())[0])

    # ==========================================================
    # CREAR INTERFAZ Y WIDGETS
    # ==========================================================
    def crear_widgets(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        container.columnconfigure(1, weight=1)

        row_idx = 0

        # 1. Código interno
        ttk.Label(container, text="Código Interno *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_codigo = ttk.Entry(container)
        self.txt_codigo.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 2. Código de barras
        ttk.Label(container, text="Código de Barras:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_codigo_barras = ttk.Entry(container)
        self.txt_codigo_barras.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 3. Nombre
        ttk.Label(container, text="Nombre *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_nombre = ttk.Entry(container)
        self.txt_nombre.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 4. Categoría
        ttk.Label(container, text="Categoría *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        frame_cat = ttk.Frame(container)
        frame_cat.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        frame_cat.columnconfigure(0, weight=1)

        self.cmb_categoria = ttk.Combobox(
            frame_cat, values=list(self.mapa_categorias.keys()), state="readonly"
        )
        self.cmb_categoria.grid(row=0, column=0, sticky=tk.EW)

        btn_add_cat = ttk.Button(
            frame_cat, text="➕", width=3, command=self.abrir_nueva_categoria
        )
        btn_add_cat.grid(row=0, column=1, padx=(5, 0))
        row_idx += 1

        # 5. Marca
        ttk.Label(container, text="Marca *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        frame_marca = ttk.Frame(container)
        frame_marca.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        frame_marca.columnconfigure(0, weight=1)

        self.cmb_marca = ttk.Combobox(
            frame_marca, values=list(self.mapa_marcas.keys()), state="readonly"
        )
        self.cmb_marca.grid(row=0, column=0, sticky=tk.EW)

        btn_add_marca = ttk.Button(
            frame_marca, text="➕", width=3, command=self.abrir_nueva_marca
        )
        btn_add_marca.grid(row=0, column=1, padx=(5, 0))
        row_idx += 1

        # 6. Proveedor
        ttk.Label(container, text="Proveedor *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        frame_prov = ttk.Frame(container)
        frame_prov.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        frame_prov.columnconfigure(0, weight=1)

        self.cmb_proveedor = ttk.Combobox(
            frame_prov, values=list(self.mapa_proveedores.keys()), state="readonly"
        )
        self.cmb_proveedor.grid(row=0, column=0, sticky=tk.EW)

        btn_add_prov = ttk.Button(
            frame_prov, text="➕", width=3, command=self.abrir_nuevo_proveedor
        )
        btn_add_prov.grid(row=0, column=1, padx=(5, 0))
        row_idx += 1

        # 7. Unidad de medida (MEJORA 4: Catálogo expandido de unidades)
        ttk.Label(container, text="Unidad:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        unidades_expandidas = [
            "Pieza",
            "Kg",
            "Gramo",
            "Litro",
            "Mililitro",
            "Paquete",
            "Caja",
            "Lata",
            "Botella",
            "Bolsa",
            "Costal",
            "Metro",
        ]
        self.cmb_unidad = ttk.Combobox(
            container,
            values=unidades_expandidas,
            state="readonly",
        )
        self.cmb_unidad.set("Pieza")
        self.cmb_unidad.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 8. Tipo de Venta
        ttk.Label(container, text="Tipo Venta:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.cmb_tipo_venta = ttk.Combobox(
            container, values=["Unidad", "A granel"], state="readonly"
        )
        self.cmb_tipo_venta.set("Unidad")
        self.cmb_tipo_venta.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 9. Precio Compra
        ttk.Label(container, text="Precio Compra ($):").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_precio_compra = ttk.Entry(container)
        self.txt_precio_compra.insert(0, "0.00")
        self.txt_precio_compra.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 10. Precio Venta
        ttk.Label(container, text="Precio Venta ($) *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_precio_venta = ttk.Entry(container)
        self.txt_precio_venta.insert(0, "0.00")
        self.txt_precio_venta.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 11. Existencia / Stock actual
        ttk.Label(container, text="Existencia Actual:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_existencia = ttk.Entry(container)
        self.txt_existencia.insert(0, "0")
        self.txt_existencia.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 12. Stock Mínimo
        ttk.Label(container, text="Stock Mínimo:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_stock_minimo = ttk.Entry(container)
        self.txt_stock_minimo.insert(0, "5")
        self.txt_stock_minimo.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # BOTONES DE ACCIÓN
        frame_botones = ttk.Frame(container)
        frame_botones.grid(row=row_idx, column=0, columnspan=2, pady=(15, 0))

        btn_guardar = ttk.Button(
            frame_botones, text="Guardar", command=self.guardar_producto
        )
        btn_guardar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)

# ==========================================================
# AGREGAR NUEVA CATEGORÍA DESDE PRODUCTO
# ==========================================================
    def abrir_nueva_categoria(self):
            def actualizar_despues_de_crear(nuevo_nombre=None):
                # Recargar catálogos desde la BD
                self.cargar_catalogos()
                
                # Actualizar opciones del Combobox
                self.cmb_categoria["values"] = list(self.mapa_categorias.keys())
                
                # Seleccionar la nueva categoría
                if nuevo_nombre and nuevo_nombre in self.mapa_categorias:
                    self.cmb_categoria.set(nuevo_nombre)
                elif self.mapa_categorias:
                    self.cmb_categoria.set(list(self.mapa_categorias.keys())[0])

            AdminCategorias(
                parent=self, al_seleccionar_callback=actualizar_despues_de_crear
            )

    def abrir_nueva_marca(self):
        def actualizar_despues_de_crear(nuevo_nombre=None):
            self.cargar_catalogos()
            self.cmb_marca["values"] = list(self.mapa_marcas.keys())
            
            if nuevo_nombre and nuevo_nombre in self.mapa_marcas:
                self.cmb_marca.set(nuevo_nombre)
            elif self.mapa_marcas:
                self.cmb_marca.set(list(self.mapa_marcas.keys())[0])

        AdminMarcas(parent=self, al_seleccionar_callback=actualizar_despues_de_crear)

    def abrir_nuevo_proveedor(self):
        def actualizar_despues_de_crear(nuevo_nombre=None):
            self.cargar_catalogos()
            self.cmb_proveedor["values"] = list(self.mapa_proveedores.keys())

            if nuevo_nombre and nuevo_nombre in self.mapa_proveedores:
                self.cmb_proveedor.set(nuevo_nombre)
            elif self.mapa_proveedores:
                self.cmb_proveedor.set(list(self.mapa_proveedores.keys())[0])

        AdminProveedores(
            parent=self, al_seleccionar_callback=actualizar_despues_de_crear
        )

    def cargar_datos_producto(self):
        prod = dict(self.producto) if hasattr(self.producto, "keys") else self.producto

        self.txt_codigo.insert(0, prod["codigo"])
        self.codigo_anterior = prod["codigo"]

        self.txt_codigo_barras.insert(0, prod.get("codigo_barras") or "")
        self.txt_nombre.insert(0, prod["nombre"])

        cat_nombre = prod.get("categoria_nombre")
        if cat_nombre and cat_nombre in self.mapa_categorias:
            self.cmb_categoria.set(cat_nombre)

        marca_nom = prod.get("marca_nombre")
        if marca_nom and marca_nom in self.mapa_marcas:
            self.cmb_marca.set(marca_nom)

        prov_nom = prod.get("proveedor_nombre")
        if prov_nom and prov_nom in self.mapa_proveedores:
            self.cmb_proveedor.set(prov_nom)

        self.cmb_unidad.set(prod.get("unidad", "Pieza"))
        self.cmb_tipo_venta.set(prod.get("tipo_venta", "Unidad"))

        self.txt_precio_compra.delete(0, tk.END)
        self.txt_precio_compra.insert(0, str(prod.get("precio_compra", 0.0)))

        self.txt_precio_venta.delete(0, tk.END)
        self.txt_precio_venta.insert(0, str(prod.get("precio_venta", 0.0)))

        self.txt_existencia.delete(0, tk.END)
        self.txt_existencia.insert(0, str(prod.get("existencia", 0)))

        self.txt_stock_minimo.delete(0, tk.END)
        self.txt_stock_minimo.insert(0, str(prod.get("stock_minimo", 5)))

    # ==========================================================
    # GUARDAR / ACTUALIZAR
    # ==========================================================
    def guardar_producto(self):
        codigo = self.txt_codigo.get().strip()
        codigo_barras = self.txt_codigo_barras.get().strip() or None
        nombre = self.txt_nombre.get().strip()
        unidad = self.cmb_unidad.get()
        tipo_venta = self.cmb_tipo_venta.get()

        categoria_id = self.mapa_categorias.get(self.cmb_categoria.get())
        marca_id = self.mapa_marcas.get(self.cmb_marca.get())
        proveedor_id = self.mapa_proveedores.get(self.cmb_proveedor.get())

        # Validaciones de presencia
        if not codigo or not nombre:
            messagebox.showerror(
                "Error de Validación",
                "El Código Interno y el Nombre son obligatorios.",
                parent=self,
            )
            return

        if not categoria_id or not marca_id or not proveedor_id:
            messagebox.showerror(
                "Error de Validación",
                "Debe seleccionar una Categoría, Marca y Proveedor válidos.",
                parent=self,
            )
            return

        # Conversión numérica
        try:
            precio_compra = float(self.txt_precio_compra.get().strip())
            precio_venta = float(self.txt_precio_venta.get().strip())
            existencia = float(self.txt_existencia.get().strip())
            stock_minimo = float(self.txt_stock_minimo.get().strip())
        except ValueError:
            messagebox.showerror(
                "Error de Formato",
                "Los precios y existencias deben ser valores numéricos válidos.",
                parent=self,
            )
            return

        # MEJORA 2: Validación de precios negativos
        if precio_compra < 0 or precio_venta < 0:
            messagebox.showerror(
                "Error de Validación",
                "Los precios (compra y venta) no pueden ser negativos.",
                parent=self,
            )
            return

        # MEJORA 3: Validación de existencias negativas
        if existencia < 0 or stock_minimo < 0:
            messagebox.showerror(
                "Error de Validación",
                "La existencia y el stock mínimo no pueden ser negativos.",
                parent=self,
            )
            return

        # Guardar en Base de Datos
        try:
            if self.producto:
                prod = dict(self.producto) if hasattr(self.producto, "keys") else self.producto

                Producto.actualizar(
                    codigo_original=self.codigo_anterior,
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    categoria_id=categoria_id,
                    marca_id=marca_id,
                    proveedor_id=proveedor_id,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    activo=prod.get("activo", 1),
                )
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.", parent=self)
            else:
                nuevo = Producto(
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    categoria_id=categoria_id,
                    marca_id=marca_id,
                    proveedor_id=proveedor_id,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    activo=1,
                )
                nuevo.guardar()
                messagebox.showinfo("Éxito", "Producto guardado correctamente.", parent=self)

            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error en Base de Datos",
                f"No se pudo procesar la solicitud:\n{e}",
                parent=self,
            )