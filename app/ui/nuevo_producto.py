import tkinter as tk
from tkinter import messagebox, ttk

# Importación de modelos activos
from app.models.marca import Marca
from app.models.producto import Producto

# Importación de subsistemas UI activos
from app.ui.marcas import AdminMarcas


class NuevoProducto(tk.Toplevel):

    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.parent = parent
        self.producto = (
            producto  # Si viene con datos EDITAMOS; si es None, CREAMOS
        )

        # Diccionario para mapear "Nombre Marca" -> "ID en BD"
        self.mapa_marcas = {}

        self.title("Editar Producto" if self.producto else "Nuevo Producto")
        self.geometry("520x640")
        self.resizable(False, False)

        # Configuración modal
        self.transient(parent)
        self.grab_set()

        # Cargar catálogo de Marcas
        self.cargar_catalogos()

        # Construir interfaz
        self.crear_widgets()

        # Cargar datos o seleccionar valor por defecto + Foco inicial optimizado
        if self.producto:
            self.cargar_datos_producto()
            self.txt_nombre.focus_set()
        else:
            self.seleccionar_primeros_elementos()
            self.txt_codigo.focus_set()

    def _on_unidad_changed(self, event=None):
        """Ajusta automáticamente el tipo de venta según la unidad seleccionada."""
        unidad_seleccionada = self.cmb_unidad.get().strip().lower()
        UNIDADES_GRANEL = {"kg", "gramo", "litro", "mililitro"}

        if unidad_seleccionada in UNIDADES_GRANEL:
            self.cmb_tipo_venta.set("Granel")
        else:
            self.cmb_tipo_venta.set("Unidad")

    # ==========================================================
    # CARGAR CATÁLOGOS DESDE LA BD
    # ==========================================================
    def cargar_catalogos(self):
        """Consulta el modelo de Marca para poblar el mapa."""
        self.mapa_marcas.clear()

        try:
            for mar in Marca.obtener_todas():
                self.mapa_marcas[mar["nombre"]] = mar["id"]
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudieron cargar las marcas:\n{e}",
                parent=self,
            )

    def seleccionar_primeros_elementos(self):
        """Si es registro nuevo, selecciona la primera marca disponible."""
        if self.mapa_marcas:
            self.cmb_marca.set(list(self.mapa_marcas.keys())[0])

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
        self.txt_codigo_barras.grid(
            row=row_idx, column=1, sticky=tk.EW, pady=4
        )
        row_idx += 1

        # 3. Nombre
        ttk.Label(container, text="Nombre *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_nombre = ttk.Entry(container)
        self.txt_nombre.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 4. Marca (Catálogo dinámico)
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

        # 5. Unidad de medida
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
        self.cmb_unidad.bind("<<ComboboxSelected>>", self._on_unidad_changed)
        row_idx += 1

        # 6. Tipo de Venta
        ttk.Label(container, text="Tipo Venta:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.cmb_tipo_venta = ttk.Combobox(
            container, values=["Unidad", "Granel"], state="readonly"
        )
        self.cmb_tipo_venta.set("Unidad")
        self.cmb_tipo_venta.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 7. Precio Compra
        ttk.Label(container, text="Precio Compra ($):").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_precio_compra = ttk.Entry(container)
        self.txt_precio_compra.insert(0, "0.00")
        self.txt_precio_compra.grid(
            row=row_idx, column=1, sticky=tk.EW, pady=4
        )
        row_idx += 1

        # 8. Precio Venta
        ttk.Label(container, text="Precio Venta ($) *:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_precio_venta = ttk.Entry(container)
        self.txt_precio_venta.insert(0, "0.00")
        self.txt_precio_venta.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 9. Existencia / Stock actual
        ttk.Label(container, text="Existencia Actual:").grid(
            row=row_idx, column=0, sticky=tk.W, pady=4
        )
        self.txt_existencia = ttk.Entry(container)
        self.txt_existencia.insert(0, "0")
        self.txt_existencia.grid(row=row_idx, column=1, sticky=tk.EW, pady=4)
        row_idx += 1

        # 10. Stock Mínimo
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
    # MODALES / CALLBACKS PROTEGIDOS
    # ==========================================================
    def abrir_nueva_marca(self):
        def actualizar_despues_de_crear(nuevo_nombre=None):
            if isinstance(nuevo_nombre, dict):
                nuevo_nombre = nuevo_nombre.get("nombre")

            self.cargar_catalogos()
            self.cmb_marca["values"] = list(self.mapa_marcas.keys())

            if nuevo_nombre and nuevo_nombre in self.mapa_marcas:
                self.cmb_marca.set(nuevo_nombre)
            elif self.mapa_marcas and not self.cmb_marca.get():
                self.cmb_marca.set(list(self.mapa_marcas.keys())[0])

        AdminMarcas(
            parent=self, al_seleccionar_callback=actualizar_despues_de_crear
        )

    # ==========================================================
    # DATOS Y GUARDADO
    # ==========================================================
    def cargar_datos_producto(self):
        prod = (
            dict(self.producto)
            if hasattr(self.producto, "keys")
            else self.producto
        )

        self.txt_codigo.insert(0, prod["codigo"])
        self.codigo_anterior = prod["codigo"]

        self.txt_codigo_barras.insert(0, prod.get("codigo_barras") or "")
        self.txt_nombre.insert(0, prod["nombre"])

        marca_nom = prod.get("marca")
        if marca_nom and marca_nom in self.mapa_marcas:
            self.cmb_marca.set(marca_nom)

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

    def refrescar_parent(self):
        """Intenta invocar métodos de actualización comunes en el módulo padre."""
        if hasattr(self.parent, "cargar_productos"):
            self.parent.cargar_productos()
        elif hasattr(self.parent, "actualizar_tabla"):
            self.parent.actualizar_tabla()

    def guardar_producto(self):
        codigo = self.txt_codigo.get().strip()
        codigo_barras = self.txt_codigo_barras.get().strip() or None
        nombre = self.txt_nombre.get().strip()
        unidad = self.cmb_unidad.get()
        tipo_venta = self.cmb_tipo_venta.get()

        marca_id = self.mapa_marcas.get(self.cmb_marca.get())

        # Validaciones de presencia
        if not codigo or not nombre:
            messagebox.showerror(
                "Error de Validación",
                "El Código Interno y el Nombre son obligatorios.",
                parent=self,
            )
            return

        if not marca_id:
            messagebox.showerror(
                "Error de Validación",
                "Debe seleccionar una Marca válida.",
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

        # Validaciones de rango
        if precio_compra < 0 or precio_venta < 0:
            messagebox.showerror(
                "Error de Validación",
                "Los precios (compra y venta) no pueden ser negativos.",
                parent=self,
            )
            return

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
                prod = (
                    dict(self.producto)
                    if hasattr(self.producto, "keys")
                    else self.producto
                )

                Producto.actualizar(
                    codigo_original=self.codigo_anterior,
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    marca_id=marca_id,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    activo=prod.get("activo", 1),
                )
                messagebox.showinfo(
                    "Éxito",
                    "Producto actualizado correctamente.",
                    parent=self,
                )
            else:
                nuevo = Producto(
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    marca_id=marca_id,
                    unidad=unidad,
                    tipo_venta=tipo_venta,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    existencia=existencia,
                    stock_minimo=stock_minimo,
                    activo=1,
                )
                nuevo.guardar()
                messagebox.showinfo(
                    "Éxito", "Producto guardado correctamente.", parent=self
                )

            # Notificar al padre y cerrar modal
            self.refrescar_parent()
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error en Base de Datos",
                f"No se pudo procesar la solicitud:\n{e}",
                parent=self,
            )