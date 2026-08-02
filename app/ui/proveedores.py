import tkinter as tk
from tkinter import messagebox, ttk

# Importamos la clase Proveedor del modelo
from app.models.proveedor import Proveedor


class AdminProveedores(tk.Toplevel):

    def __init__(self, parent=None, al_seleccionar_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.al_seleccionar_callback = al_seleccionar_callback  # Callback para uso modal
        self.id_seleccionado = None  # Almacena el ID si estamos en modo edición

        self.title("Administrar Proveedores")
        self.geometry("550x450")
        self.resizable(False, False)

        # Si viene con padre, se comporta como ventana modal
        if parent:
            self.transient(parent)
            self.grab_set()

        self.crear_widgets()
        self.cargar_proveedores()

        # Vinculación de eventos de teclado
        self.txt_buscar.bind("<KeyRelease>", self.filtrar_proveedores)
        self.txt_nombre.bind("<Return>", lambda e: self.guardar_proveedor())

        # Focus inicial
        self.txt_buscar.focus_set()

    # ==========================================================
    # INTERFAZ Y WIDGETS
    # ==========================================================
    def crear_widgets(self):
        main_container = ttk.Frame(self, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SECCIÓN 1: FORMULARIO (EDICIÓN / CREACIÓN) ---
        frame_form = ttk.LabelFrame(
            main_container, text=" Datos de Proveedor ", padding=10
        )
        frame_form.pack(fill=tk.X, pady=(0, 10))
        frame_form.columnconfigure(1, weight=1)

        ttk.Label(frame_form, text="Nombre *:").grid(
            row=0, column=0, sticky=tk.W, padx=5
        )
        self.txt_nombre = ttk.Entry(frame_form)
        self.txt_nombre.grid(row=0, column=1, sticky=tk.EW, padx=5)

        self.btn_guardar = ttk.Button(
            frame_form, text="💾 Guardar", command=self.guardar_proveedor
        )
        self.btn_guardar.grid(row=0, column=2, padx=5)

        self.btn_limpiar = ttk.Button(
            frame_form,
            text="🧹 Nuevo / Cancelar",
            command=self.limpiar_formulario,
        )
        self.btn_limpiar.grid(row=0, column=3, padx=5)

        # --- SECCIÓN 2: BUSCADOR ---
        frame_buscar = ttk.Frame(main_container)
        frame_buscar.pack(fill=tk.X, pady=(0, 10))
        frame_buscar.columnconfigure(1, weight=1)

        ttk.Label(frame_buscar, text="🔍 Buscar:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
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
        self.tree.heading("nombre", text="Nombre del Proveedor")

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
            frame_acciones,
            text="✏️ Editar Seleccionado",
            command=self.cargar_para_editar,
        )
        btn_editar.pack(side=tk.LEFT, padx=(0, 5))

        btn_eliminar = ttk.Button(
            frame_acciones, text="🗑️ Eliminar", command=self.eliminar_proveedor
        )
        btn_eliminar.pack(side=tk.LEFT)

        btn_cerrar = ttk.Button(
            frame_acciones, text="Cerrar", command=self.destroy
        )
        btn_cerrar.pack(side=tk.RIGHT)

    # ==========================================================
    # LÓGICA DE DATOS
    # ==========================================================
    def cargar_proveedores(self, lista_datos=None):
        """Limpia y llena el Treeview con proveedores."""
        self.tree.delete(*self.tree.get_children())

        registros = (
            lista_datos
            if lista_datos is not None
            else Proveedor.obtener_todos()
        )

        for p in registros:
            self.tree.insert("", tk.END, values=(p["id"], p["nombre"]))

    def filtrar_proveedores(self, event=None):
        """Filtra en tiempo real al escribir en la caja de búsqueda."""
        termino = self.txt_buscar.get().strip()
        resultados = Proveedor.buscar(termino)
        self.cargar_proveedores(resultados)

    def guardar_proveedor(self):
        """Agrega o actualiza un proveedor previa validación."""
        nombre = self.txt_nombre.get().strip()

        if not nombre:
            messagebox.showerror(
                "Error de Validación",
                "El nombre del proveedor no puede estar vacío.",
                parent=self,
            )
            return

        try:
            if self.id_seleccionado:
                # Actualizar existente
                Proveedor.actualizar(self.id_seleccionado, nombre)
                messagebox.showinfo(
                    "Éxito", "Proveedor actualizado correctamente.", parent=self
                )
            else:
                # Agregar nuevo
                Proveedor.agregar(nombre)
                messagebox.showinfo(
                    "Éxito", "Proveedor creado correctamente.", parent=self
                )

            # Si viene invocada como modal desde NuevoProducto, notifica y cierra
            if self.al_seleccionar_callback:
                self.al_seleccionar_callback(nombre)
                self.destroy()
                return

            self.limpiar_formulario()
            self.cargar_proveedores()

        except Exception as e:
            messagebox.showerror(
                "Error de BD",
                f"No se pudo guardar el proveedor:\n{e}",
                parent=self,
            )

    def cargar_para_editar(self):
        """Carga el ítem seleccionado de la tabla al formulario superior."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención",
                "Seleccione un proveedor de la lista para editar.",
                parent=self,
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        self.id_seleccionado = valores[0]

        self.txt_nombre.delete(0, tk.END)
        self.txt_nombre.insert(0, valores[1])

        self.btn_guardar.config(text="💾 Actualizar")
        self.txt_nombre.focus_set()

    def al_doble_clic(self, event):
        """Manejador para el evento doble clic sobre la fila."""
        self.cargar_para_editar()

    def eliminar_proveedor(self):
        """Elimina el proveedor seleccionado previa confirmación."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Seleccione un proveedor para eliminar.", parent=self
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        id_prov, nombre = valores[0], valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el proveedor '{nombre}'?\n\n"
            "Nota: Si hay productos asignados a este proveedor, la operación podría fallar.",
            parent=self,
        )

        if confirmar:
            try:
                Proveedor.eliminar(id_prov)
                messagebox.showinfo(
                    "Éxito", "Proveedor eliminado correctamente.", parent=self
                )
                self.limpiar_formulario()
                self.cargar_proveedores()
            except Exception as e:
                messagebox.showerror(
                    "Error al Eliminar",
                    f"No se puede eliminar el proveedor. Asegúrese de que no esté en uso por ningún producto.\n\nDetalle: {e}",
                    parent=self,
                )

    def limpiar_formulario(self):
        """Restablece los campos de entrada."""
        self.id_seleccionado = None
        self.txt_nombre.delete(0, tk.END)
        self.btn_guardar.config(text="💾 Guardar")