import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd

from app.models.producto import Producto
from app.ui.nuevo_producto import NuevoProducto


class ProductosWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        # ========= AJUSTE DE GEOMETRÍA SEGURO =========
        master.update_idletasks()
        
        self.title("Productos")
        self.geometry("1080x650")
        
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.lift()

        # ========= CONFIGURACIÓN DE ESTILO NEGRO PARA LA TABLA =========
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Treeview",
            background="#242424",
            fieldbackground="#242424",
            foreground="white",
            rowheight=28,
            font=("Segoe UI", 11)
        )
        
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )
        
        style.configure(
            "Treeview.Heading",
            background="#1A1A1A",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            borderwidth=1,
            relief="flat"
        )
        
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

        self.btn_editar = ctk.CTkButton(
            barra_botones,
            text="✏ Editar",
            width=120,
            command=self.editar_producto_boton
        )
        self.btn_editar.pack(side="left", padx=5, pady=8)

        self.btn_accion = ctk.CTkButton(
            barra_botones,
            text="❌ Desactivar",
            width=120,
            command=self.desactivar_producto_boton
        )
        self.btn_accion.pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="📤 Exportar Excel",
            width=120,
            fg_color="#0F9D58", 
            hover_color="#0B7542",
            command=self.exportar_a_excel
        ).pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            barra_botones,
            text="📥 Importar Excel",
            width=120,
            fg_color="#FF9800", 
            hover_color="#E68A00",
            command=self.importar_desde_excel
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
                
        self.mostrar_desactivados = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            barra,
            text="Mostrar desactivados",
            variable=self.mostrar_desactivados,
            command=self.cargar_productos
        ).pack(side="left", padx=20)

        # CONFIGURACIÓN DE TABLA (TREEVIEW)
        columns = (
            "codigo",
            "nombre",
            "unidad",
            "tipo_venta",
            "precio_compra",
            "precio_venta",
            "existencia",
            "stock_minimo",
            "estado"
        )

        self.tabla = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=18,
            selectmode='extended'
        )

        self.tabla.bind(
            "<Double-1>",
            self.editar_producto
        )
        
        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.verificar_estado_seleccionado
        )
        
        self.tabla.heading("codigo", text="Código", command=lambda: self.ordenar_por_columna("codigo", False))
        self.tabla.heading("nombre", text="Producto", command=lambda: self.ordenar_por_columna("nombre", False))
        self.tabla.heading("unidad", text="Unidad", command=lambda: self.ordenar_por_columna("unidad", False))
        self.tabla.heading("tipo_venta", text="Tipo Venta", command=lambda: self.ordenar_por_columna("tipo_venta", False))
        self.tabla.heading("precio_compra", text="Compra", command=lambda: self.ordenar_por_columna("precio_compra", False))
        self.tabla.heading("precio_venta", text="Venta", command=lambda: self.ordenar_por_columna("precio_venta", False))
        self.tabla.heading("existencia", text="Stock", command=lambda: self.ordenar_por_columna("existencia", False))
        self.tabla.heading("stock_minimo", text="Stock mín.", command=lambda: self.ordenar_por_columna("stock_minimo", False))
        self.tabla.heading("estado", text="Estado", command=lambda: self.ordenar_por_columna("estado", False))

        self.tabla.column("codigo", width=100, anchor="center")
        self.tabla.column("nombre", width=300)
        self.tabla.column("unidad", width=90, anchor="center")
        self.tabla.column("tipo_venta", width=100, anchor="center")
        self.tabla.column("precio_compra", width=90, anchor="e")
        self.tabla.column("precio_venta", width=90, anchor="e")
        self.tabla.column("existencia", width=80, anchor="center")
        self.tabla.column("stock_minimo", width=90, anchor="center")
        self.tabla.column("estado", width=110, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_total = ctk.CTkLabel(
            self,
            text=""
        )
        self.lbl_total.pack(anchor="e", padx=20, pady=(0, 10))

        self.cargar_productos()
        self.buscar.focus()

    def verificar_estado_seleccionado(self, event=None):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return

        datos = self.tabla.item(seleccionado[0], "values")
        estado = datos[8]  # El estado está en el índice 8

        if "🔴 Desactivado" in estado:
            self.btn_editar.configure(state="disabled", fg_color="#555555")
            self.btn_accion.configure(
                text="♻️ Reactivar",
                fg_color="#2E7D32",
                hover_color="#1B5E20",
                command=self.reactivar_producto_boton
            )
        else:
            self.btn_editar.configure(state="normal", fg_color="#2196F3")
            self.btn_accion.configure(
                text="❌ Desactivar",
                fg_color="#D32F2F",
                hover_color="#C62828",
                command=self.desactivar_producto_boton
            )

    def editar_producto(self, event=None):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return

        datos = self.tabla.item(seleccionado[0], "values")
        
        if "🔴 Desactivado" in datos[8]:
            return

        codigo = datos[0]
        producto = Producto.buscar_por_codigo(codigo)

        ventana = NuevoProducto(self, producto)
        self.wait_window(ventana)
        self.cargar_productos()
        self.master.dashboard.actualizar()

    def editar_producto_boton(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Por favor, seleccione un producto de la lista para editar.")
            return
        self.editar_producto(event=None)

    def desactivar_producto_boton(self):
        seleccionados = self.tabla.selection()
        if not seleccionados:
            messagebox.showwarning("Atención", "Por favor, seleccione uno o más productos de la lista para desactivar.")
            return

        productos_a_desactivar = []
        for item_id in seleccionados:
            datos = self.tabla.item(item_id, "values")
            codigo = datos[0]
            nombre = datos[1]
            productos_a_desactivar.append({'codigo': codigo, 'nombre': nombre})

        if len(productos_a_desactivar) == 1:
            mensaje = f"¿Está seguro de que desea desactivar el producto:\n\n👉 {productos_a_desactivar[0]['nombre']} ({productos_a_desactivar[0]['codigo']})?"
        else:
            lista_nombres = "\n".join([f"👉 {p['nombre']} ({p['codigo']})" for p in productos_a_desactivar])
            mensaje = f"¿Está seguro de que desea desactivar {len(productos_a_desactivar)} productos?\n\n{lista_nombres}"

        mensaje += "\n\nNo se borrarán del historial de ventas, pero ya no estarán disponibles para la venta."
        confirmar = messagebox.askyesno("Confirmar acción", mensaje)

        if confirmar:
            errores = 0
            desactivados = 0
            for producto in productos_a_desactivar:
                try:
                    Producto.desactivar(producto['codigo'])
                    desactivados += 1
                except Exception as e:
                    errores += 1
                    print(f"Error al desactivar {producto['codigo']}: {e}")

            if errores == 0:
                messagebox.showinfo("Éxito", f"Se desactivaron {desactivados} productos correctamente.")
            else:
                messagebox.showwarning("Completado con errores", f"Se desactivaron {desactivados} productos.\nFallaron {errores}. Revisa la consola.")
            
            self.cargar_productos()
            self.master.dashboard.actualizar()
            
    def reactivar_producto_boton(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return

        datos = self.tabla.item(seleccionado[0], "values")
        codigo = datos[0]
        nombre = datos[1]

        confirmar = messagebox.askyesno(
            "Confirmar acción",
            f"¿Desea reactivar el producto:\n\n👉 {nombre} ({codigo})?\n\nVolverá a aparecer inmediatamente en el catálogo de ventas de la tienda."
        )

        if confirmar:
            try:
                Producto.reactivar(codigo)
                messagebox.showinfo("Éxito", "Producto reactivado correctamente.")
                self.cargar_productos()
                self.master.dashboard.actualizar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reactivar el producto: {e}")

    def cargar_productos(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        productos = Producto.obtener_todos(
            self.mostrar_desactivados.get()
        )

        for producto in productos:
            estado = "🟢 Activo"
            if producto["activo"] == 0:
                estado = "🔴 Desactivado"
            else:
                estado = "🟢 Activo"

            self.tabla.insert(
                "",
                "end",
                values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['unidad'],
                    producto['tipo_venta'],
                    f"${float(producto['precio_compra']):.2f}",
                    f"${float(producto['precio_venta']):.2f}",
                    producto['existencia'],
                    producto['stock_minimo'],
                    estado
                )
            )

        self.lbl_total.configure(
            text=f"Productos registrados: {len(productos)}"
        )
        
        self.btn_editar.configure(state="normal", fg_color="#2196F3")
        self.btn_accion.configure(
            text="❌ Desactivar",
            fg_color="#D32F2F",
            hover_color="#C62828",
            command=self.desactivar_producto_boton
        )

    def abrir_nuevo_producto(self):
        ventana = NuevoProducto(self)
        self.wait_window(ventana)
        self.cargar_productos()
        self.master.dashboard.actualizar()

    def buscar_producto(self, event=None):
        texto = self.buscar.get()

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        productos = Producto.buscar(
            texto,
            self.mostrar_desactivados.get()
        )

        for producto in productos:
            estado = "🟢 Activo"
            if producto['activo'] == 0:
                estado = "🔴 Desactivado"

            self.tabla.insert(
                "",
                "end",
                values=(
                    producto['codigo'],
                    producto['nombre'],
                    producto['unidad'],
                    producto['tipo_venta'],
                    f"${float(producto['precio_compra']):.2f}",
                    f"${float(producto['precio_venta']):.2f}",
                    producto['existencia'],
                    producto['stock_minimo'],
                    estado
                )
            )

        self.lbl_total.configure(
            text=f"Productos encontrados: {len(productos)}"
        )

    def exportar_a_excel(self):
        try:
            datos_raw = Producto.obtener_todos_para_excel()
            
            if not datos_raw:
                messagebox.showwarning("Atención", "No hay productos registrados para exportar.")
                return

            ruta_archivo = filedialog.asksaveasfilename(
                title="Guardar inventario como",
                defaultextension=".xlsx",
                filetypes=[("Archivos de Excel", "*.xlsx")]
            )
            
            if not ruta_archivo:
                return
            
            datos_dict = [dict(fila) for fila in datos_raw]
            df = pd.DataFrame(datos_dict)
            
            df = df.rename(columns={
                "codigo": "Código",
                "codigo_barras": "Código Barras",
                "nombre": "Producto",
                "unidad": "Unidad",
                "tipo_venta": "Tipo Venta",
                "precio_compra": "Precio Compra",
                "precio_venta": "Precio Venta",
                "existencia": "Stock",
                "stock_minimo": "Stock Mínimo",
                "categoria_id": "Categoría ID",
                "activo": "Activo"
            })

            df.to_excel(ruta_archivo, index=False, sheet_name="Inventario")
            
            messagebox.showinfo("Éxito", f"Inventario exportado correctamente en:\n{ruta_archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    def importar_desde_excel(self):
        try:
            ruta_archivo = filedialog.askopenfilename(
                title="Seleccionar archivo de inventario",
                filetypes=[("Archivos de Excel", "*.xlsx")]
            )
            
            if not ruta_archivo:
                return

            df = pd.read_excel(ruta_archivo)
            df = df.fillna("")  # Reemplaza NaN por cadenas vacías

            # Normalizar columnas esperadas
            if "Código Barras" in df.columns:
                columnas = [
                    "Código", "Código Barras", "Producto", "Unidad", 
                    "Tipo Venta", "Precio Compra", "Precio Venta", 
                    "Stock", "Stock Mínimo", "Categoría ID", "Activo"
                ]
            else:
                df["Código Barras"] = ""
                columnas = [
                    "Código", "Código Barras", "Producto", "Unidad", 
                    "Tipo Venta", "Precio Compra", "Precio Venta", 
                    "Stock", "Stock Mínimo", "Categoría ID", "Activo"
                ]

            # Asignar Categoría ID si no viene en el excel
            if "Categoría ID" not in df.columns:
                df["Categoría ID"] = 1

            lista_productos = df[[
                "Código", "Código Barras", "Producto", "Unidad", 
                "Tipo Venta", "Precio Compra", "Precio Venta", 
                "Stock", "Stock Mínimo", "Categoría ID", "Activo"
            ]].values.tolist()

            confirmar = messagebox.askyesno(
                "Confirmar Importación", 
                f"Se detectaron {len(lista_productos)} productos en el archivo.\n\n¿Desea importarlos a la base de datos?\nNota: Si un código ya existe, se sobrescribirá."
            )

            if confirmar:
                Producto.importar_desde_lista(lista_productos)
                messagebox.showinfo("Éxito", f"¡Se han importado/actualizado {len(lista_productos)} productos correctamente!")
                
                self.cargar_productos()
                self.master.dashboard.actualizar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo de Excel.\n\nDetalle: {e}")

    def ordenar_por_columna(self, columna, reverso):
        filas = [(self.tabla.set(fila, columna), fila) for fila in self.tabla.get_children("")]

        def limpiar_y_convertir(valor):
            valor_limpio = valor.replace('$', '').strip()
            try:
                if '.' in valor_limpio:
                    return float(valor_limpio)
                return int(valor_limpio)
            except ValueError:
                return valor.lower()

        filas.sort(key=lambda el: limpiar_y_convertir(el[0]), reverse=reverso)

        for indice, (valor, fila) in enumerate(filas):
            self.tabla.move(fila, "", indice)

        self.tabla.heading(columna, command=lambda: self.ordenar_por_columna(columna, not reverso))