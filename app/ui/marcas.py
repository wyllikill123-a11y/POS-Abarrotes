import tkinter as tk
from tkinter import messagebox, ttk

# Importamos la clase Marca del modelo
from app.models.marca import Marca


class AdminMarcas(tk.Toplevel):

    def __init__(self, parent=None, al_seleccionar_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.al_seleccionar_callback = al_seleccionar_callback  # Callback para uso modal
        self.id_seleccionado = None  # Almacena el ID si estamos en modo edición

        self.title("Administrar Marcas")
        self.geometry("550x450")
        self.resizable(False, False)

        # Si viene con padre, se comporta como ventana modal
        if parent:
            self.transient(parent)
            self.grab_set()

        self.crear_widgets()
        self.cargar_marcas()

        # Vinculación de eventos teclado
        self.txt_buscar.bind("<KeyRelease>", self.filtrar_marcas)
        self.txt_nombre.bind("<Return>", lambda e: self.guardar_marca())

        # Focus inicial
        self.txt_buscar.focus_set()

    # ==========================================================
    # INTERFAZ Y WIDGETS
    # ==========================================================
    def crear_widgets(self):
        main_container = ttk.Frame(self, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SECCIÓN 1: FORMULARIO (EDICIÓN / CREACIÓN) ---
        frame_form = ttk.LabelFrame(main_container, text=" Datos de Marca ", padding=10)
        frame_form.pack(fill=tk.X, pady=(0, 10))
        frame_form.columnconfigure(1, weight=1)

        ttk.Label(frame_form, text="Nombre *:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.txt_nombre = ttk.Entry(frame_form)
        self.txt_nombre.grid(row=0, column=1, sticky=tk.EW, padx=5)

        self.btn_guardar = ttk.Button(
            frame_form, text="💾 Guardar", command=self.guardar_marca
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
        self.tree.heading("nombre", text="Nombre de la Marca")

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
            frame_acciones, text="🗑️ Eliminar", command=self.eliminar_marca
        )
        btn_eliminar.pack(side=tk.LEFT)

        btn_cerrar = ttk.Button(
            frame_acciones, text="Cerrar", command=self.destroy
        )
        btn_cerrar.pack(side=tk.RIGHT)

    # ==========================================================
    # LÓGICA DE DATOS
    # ==========================================================
    def cargar_marcas(self, lista_datos=None):
        """Limpia y llena el Treeview con marcas."""
        self.tree.delete(*self.tree.get_children())

        registros = lista_datos if lista_datos is not None else Marca.obtener_todas()

        for m in registros:
            self.tree.insert("", tk.END, values=(m["id"], m["nombre"]))

    def filtrar_marcas(self, event=None):
        """Filtra en tiempo real al escribir en la caja de búsqueda."""
        termino = self.txt_buscar.get().strip()
        resultados = Marca.buscar(termino)
        self.cargar_marcas(resultados)

    def guardar_marca(self):
        """Agrega o actualiza una marca previa validación."""
        nombre = self.txt_nombre.get().strip()

        if not nombre:
            messagebox.showerror(
                "Error de Validación",
                "El nombre de la marca no puede estar vacío.",
                parent=self,
            )
            return

        try:
            if self.id_seleccionado:
                # Actualizar existente
                Marca.actualizar(self.id_seleccionado, nombre)
                messagebox.showinfo(
                    "Éxito", "Marca actualizada correctamente.", parent=self
                )
            else:
                # Agregar nueva
                Marca.agregar(nombre)
                messagebox.showinfo(
                    "Éxito", "Marca creada correctamente.", parent=self
                )

            # Si viene invocada como modal desde NuevoProducto, notifica y cierra
            if self.al_seleccionar_callback:
                self.al_seleccionar_callback(nombre)
                self.destroy()
                return

            self.limpiar_formulario()
            self.cargar_marcas()

        except Exception as e:
            messagebox.showerror(
                "Error de BD", f"No se pudo guardar la marca:\n{e}", parent=self
            )

    def cargar_para_editar(self):
        """Carga el ítem seleccionado de la tabla al formulario superior."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Seleccione una marca de la lista para editar.", parent=self
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

    def eliminar_marca(self):
        """Elimina la marca seleccionada previa confirmación."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Seleccione una marca para eliminar.", parent=self
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        id_marca, nombre = valores[0], valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la marca '{nombre}'?\n\n"
            "Nota: Si hay productos asignados a esta marca, la operación podría fallar.",
            parent=self,
        )

        if confirmar:
            try:
                Marca.eliminar(id_marca)
                messagebox.showinfo(
                    "Éxito", "Marca eliminada correctamente.", parent=self
                )
                self.limpiar_formulario()
                self.cargar_marcas()
            except Exception as e:
                messagebox.showerror(
                    "Error al Eliminar",
                    f"No se puede eliminar la marca. Asegúrese de que no esté en uso por ningún producto.\n\nDetalle: {e}",
                    parent=self,
                )

    def limpiar_formulario(self):
        """Restablece los campos de entrada."""
        self.id_seleccionado = None
        self.txt_nombre.delete(0, tk.END)
        self.btn_guardar.config(text="💾 Guardar")