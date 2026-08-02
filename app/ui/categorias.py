import tkinter as tk
from tkinter import messagebox, ttk

# Importamos la clase Categoria del modelo
from app.models.categoria import Categoria


class AdminCategorias(tk.Toplevel):

    def __init__(self, parent=None, al_seleccionar_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.al_seleccionar_callback = al_seleccionar_callback  # Callback para uso modal
        self.id_seleccionado = None  # Almacena el ID si estamos en modo edición

        self.title("Administrar Categorías")
        self.geometry("550x450")
        self.resizable(False, False)

        # Si viene con padre, se comporta como ventana modal
        if parent:
            self.transient(parent)
            self.grab_set()

        self.crear_widgets()
        self.cargar_categorias()

        # Vincular tecla Enter para buscar o guardar rápido
        self.txt_buscar.bind("<KeyRelease>", self.filtrar_categorias)
        self.txt_buscar.bind("<Return>", self.filtrar_categorias)
        self.txt_nombre.bind("<Return>", lambda e: self.guardar_categoria())
        
        # Focus en el campo de búsqueda
        self.txt_buscar.focus_set()
        self.centrar()

    # ==========================================================
    # INTERFAZ Y WIDGETS
    # ==========================================================
    def crear_widgets(self):
        main_container = ttk.Frame(self, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SECCIÓN 1: FORMULARIO (EDICIÓN / CREACIÓN) ---
        frame_form = ttk.LabelFrame(main_container, text=" Datos de Categoría ", padding=10)
        frame_form.pack(fill=tk.X, pady=(0, 10))
        frame_form.columnconfigure(1, weight=1)

        ttk.Label(frame_form, text="Nombre *:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.txt_nombre = ttk.Entry(frame_form)
        self.txt_nombre.grid(row=0, column=1, sticky=tk.EW, padx=5)

        self.btn_guardar = ttk.Button(
            frame_form, text="💾 Guardar", command=self.guardar_categoria
        )
        self.btn_guardar.grid(row=0, column=2, padx=5)

        self.btn_limpiar = ttk.Button(
            frame_form, text="🧹 Nuevo / Cancelar", command=self.limpiar_formulario
        )
        self.btn_limpiar.grid(row=0, column=3, padx=5)

        # --- SECCIÓN 2: BUSCADOR ---
        frame_buscar = ttk.Frame(main_container)
        frame_buscar.pack(fill=tk.X, pady=(0, 10))
        frame_buscar.columnconfigure(1, weight=1)

        ttk.Label(frame_buscar, text="🔍 Buscar:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.txt_buscar = ttk.Entry(frame_buscar)
        self.txt_buscar.grid(row=0, column=1, sticky=tk.EW)

        # --- SECCIÓN 3: TABLA (TREEVIEW) ---
        frame_tabla = ttk.Frame(main_container)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "nombre")
        self.tree = ttk.Treeview(
            frame_tabla, columns=columns, show="headings", selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre de la Categoría")

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("nombre", width=380, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            frame_tabla, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Eventos del Treeview
        self.tree.bind("<Double-1>", self.al_doble_clic)

        # --- SECCIÓN 4: BOTONES DE ACCIÓN (TABLA) ---
        frame_acciones = ttk.Frame(main_container)
        frame_acciones.pack(fill=tk.X, pady=(10, 0))

        btn_editar = ttk.Button(
            frame_acciones, text="✏️ Editar Seleccionado", command=self.cargar_para_editar
        )
        btn_editar.pack(side=tk.LEFT, padx=(0, 5))

        btn_eliminar = ttk.Button(
            frame_acciones, text="🗑️ Eliminar", command=self.eliminar_categoria
        )
        btn_eliminar.pack(side=tk.LEFT)

        btn_cerrar = ttk.Button(
            frame_acciones, text="Cerrar", command=self.destroy
        )
        btn_cerrar.pack(side=tk.RIGHT)

    # ==========================================================
    # LÓGICA DE DATOS
    # ==========================================================
    def cargar_categorias(self, lista_datos=None):
        """Limpia y llena el Treeview con categorías."""
        self.tree.delete(*self.tree.get_children())

        registros = lista_datos if lista_datos is not None else Categoria.obtener_todas()

        for cat in registros:
            # Los registros de sqlite3.Row permiten acceso por clave o indice
            self.tree.insert("", tk.END, values=(cat["id"], cat["nombre"]))

    def filtrar_categorias(self, event=None):
        """Filtra en tiempo real al escribir en la caja de búsqueda."""
        termino = self.txt_buscar.get().strip()
        resultados = Categoria.buscar(termino)
        self.cargar_categorias(resultados)

    def guardar_categoria(self):
            """Agrega o actualiza una categoría previa validación."""
            nombre = self.txt_nombre.get().strip()

            if not nombre:
                messagebox.showerror(
                    "Error de Validación",
                    "El nombre de la categoría no puede estar vacío.",
                    parent=self,
                )
                return

            try:
                if self.id_seleccionado:
                    # Actualizar existente
                    Categoria.actualizar(self.id_seleccionado, nombre)
                    messagebox.showinfo(
                        "Éxito", "Categoría actualizada correctamente.", parent=self
                    )
                else:
                    # Agregar nueva
                    Categoria.agregar(nombre)
                    messagebox.showinfo(
                        "Éxito", "Categoría creada correctamente.", parent=self
                    )

                # ✅ CORRECCIÓN: Si hay callback, pasamos 'nombre' en ambos casos (nuevo o actualización)
                if self.al_seleccionar_callback:
                    self.al_seleccionar_callback(nombre)
                    self.destroy()
                    return

                self.limpiar_formulario()
                self.cargar_categorias()

            except Exception as e:
                messagebox.showerror(
                    "Error de BD", f"No se pudo guardar la categoría:\n{e}", parent=self
                )

    def cargar_para_editar(self):
        """Carga el ítem seleccionado de la tabla al formulario de arriba."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Seleccione una categoría de la lista para editar.", parent=self
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        self.id_seleccionado = valores[0]

        self.txt_nombre.delete(0, tk.END)
        self.txt_nombre.insert(0, valores[1])

        self.btn_guardar.config(text="💾 Actualizar")
        self.txt_nombre.focus_set()

    def al_doble_clic(self, event):
        if self.al_seleccionar_callback:
            item = self.tree.selection()

            if item:
                nombre = self.tree.item(item[0])["values"][1]
                self.al_seleccionar_callback(nombre)
                self.destroy()

        else:
            self.cargar_para_editar()

    def eliminar_categoria(self):
        """Elimina la categoría seleccionada previa confirmación."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Seleccione una categoría para eliminar.", parent=self
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        id_cat, nombre = valores[0], valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la categoría '{nombre}'?\n\n"
            "Nota: Si hay productos asignados a esta categoría, la operación podría fallar.",
            parent=self,
        )

        if confirmar:
            try:
                Categoria.eliminar(id_cat)
                messagebox.showinfo(
                    "Éxito", "Categoría eliminada correctamente.", parent=self
                )
                self.limpiar_formulario()
                self.cargar_categorias()
            except Exception as e:
                messagebox.showerror(
                    "Error al Eliminar",
                    f"No se puede eliminar la categoría. Asegúrese de que no esté en uso por algún producto.\n\nDetalle: {e}",
                    parent=self,
                )

    def limpiar_formulario(self):
        """Restablece los campos de entrada."""
        self.id_seleccionado = None
        self.txt_nombre.delete(0, tk.END)
        self.btn_guardar.config(text="💾 Guardar")

    def centrar(self):
        self.update_idletasks()

        ancho = self.winfo_width()
        alto = self.winfo_height()

        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)

        self.geometry(f"{ancho}x{alto}+{x}+{y}")