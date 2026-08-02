import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

# Importamos la clase Marca del modelo
from app.models.marca import Marca


class AdminMarcas(ctk.CTkToplevel):

    def __init__(self, parent=None, al_seleccionar_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.al_seleccionar_callback = (
            al_seleccionar_callback  # Callback para uso modal
        )
        self.id_seleccionado = None  # Almacena el ID si estamos en modo edición

        self.title("Administración de Marcas")
        self.geometry("580x500")
        self.resizable(False, False)

        # Configuración para ventana modal
        if parent:
            parent.update_idletasks()
            self.transient(parent)
            self.grab_set()
            self.focus_set()

        self.configurar_estilo_tabla()
        self.crear_widgets()
        self.cargar_marcas()

        # Vinculación de eventos
        self.txt_buscar.bind("<KeyRelease>", self.filtrar_marcas)
        self.txt_nombre.bind("<Return>", lambda e: self.guardar_marca())

        # Focus inicial
        self.txt_buscar.focus_set()

    def configurar_estilo_tabla(self):
        """Aplica el estilo oscuro coherente con CustomTkinter para la tabla."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#242424",
            fieldbackground="#242424",
            foreground="white",
            rowheight=28,
            font=("Segoe UI", 10),
        )

        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")],
        )

        style.configure(
            "Treeview.Heading",
            background="#1A1A1A",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
            relief="flat",
        )

        style.map(
            "Treeview.Heading",
            background=[("active", "#2D2D2D")],
            foreground=[("active", "white")],
        )

    # ==========================================================
    # INTERFAZ Y WIDGETS
    # ==========================================================
    def crear_widgets(self):
        # --- SECCIÓN 1: FORMULARIO (EDICIÓN / CREACIÓN) ---
        frame_form = ctk.CTkFrame(self)
        frame_form.pack(fill="x", padx=15, pady=(15, 10))

        lbl_titulo = ctk.CTkLabel(
            frame_form,
            text="Datos de la Marca",
            font=("Segoe UI", 12, "bold"),
        )
        lbl_titulo.grid(
            row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(8, 4)
        )

        ctk.CTkLabel(frame_form, text="Nombre *:").grid(
            row=1, column=0, padx=(10, 5), pady=10, sticky="w"
        )

        self.txt_nombre = ctk.CTkEntry(
            frame_form, placeholder_text="Nombre de la marca"
        )
        self.txt_nombre.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        frame_form.columnconfigure(1, weight=1)

        self.btn_guardar = ctk.CTkButton(
            frame_form, text="💾 Guardar", width=100, command=self.guardar_marca
        )
        self.btn_guardar.grid(row=1, column=2, padx=5, pady=10)

        self.btn_limpiar = ctk.CTkButton(
            frame_form,
            text="🧹 Cancelar",
            width=100,
            fg_color="#555555",
            hover_color="#333333",
            command=self.limpiar_formulario,
        )
        self.btn_limpiar.grid(row=1, column=3, padx=(5, 10), pady=10)

        # --- SECCIÓN 2: BUSCADOR ---
        frame_buscar = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscar.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(frame_buscar, text="🔍 Buscar:").pack(
            side="left", padx=(0, 5)
        )

        self.txt_buscar = ctk.CTkEntry(
            frame_buscar, placeholder_text="Filtrar por nombre..."
        )
        self.txt_buscar.pack(side="left", fill="x", expand=True)

        # --- SECCIÓN 3: TABLA (TREEVIEW) ---
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        columns = ("id", "nombre")
        self.tree = ttk.Treeview(
            frame_tabla, columns=columns, show="headings", selectmode="browse"
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre de la Marca")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=420, anchor="w")

        scrollbar = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Eventos del Treeview
        self.tree.bind("<Double-1>", self.al_doble_clic)

        # --- SECCIÓN 4: BOTONES DE ACCIÓN (TABLA) ---
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=15, pady=(0, 15))

        self.btn_editar = ctk.CTkButton(
            frame_acciones,
            text="✏️ Editar",
            width=100,
            command=self.cargar_para_editar,
        )
        self.btn_editar.pack(side="left", padx=(0, 5))

        self.btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="🗑️ Eliminar",
            width=100,
            fg_color="#D32F2F",
            hover_color="#C62828",
            command=self.eliminar_marca,
        )
        self.btn_eliminar.pack(side="left")

        btn_cerrar = ctk.CTkButton(
            frame_acciones,
            text="Cerrar",
            width=90,
            fg_color="#555555",
            hover_color="#333333",
            command=self.destroy,
        )
        btn_cerrar.pack(side="right")

    # ==========================================================
    # LÓGICA DE DATOS
    # ==========================================================
    def cargar_marcas(self, lista_datos=None):
        """Limpia y llena el Treeview con marcas."""
        for fila in self.tree.get_children():
            self.tree.delete(fila)

        registros = (
            lista_datos if lista_datos is not None else Marca.obtener_todas()
        )

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
                Marca.actualizar(self.id_seleccionado, nombre)
                messagebox.showinfo(
                    "Éxito", "Marca actualizada correctamente.", parent=self
                )
            else:
                nuevo_id = Marca.agregar(nombre)
                messagebox.showinfo(
                    "Éxito", "Marca creada correctamente.", parent=self
                )

                # Si viene invocada como modal desde otro formulario, notifica dict completo y cierra
                if self.al_seleccionar_callback:
                    self.al_seleccionar_callback(
                        {"id": nuevo_id, "nombre": nombre}
                    )
                    self.destroy()
                    return

            self.limpiar_formulario()
            self.cargar_marcas()

        except Exception as e:
            messagebox.showerror(
                "Error de BD",
                f"No se pudo guardar la marca:\n{e}",
                parent=self,
            )

    def cargar_para_editar(self):
        """Carga el ítem seleccionado de la tabla al formulario superior."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención",
                "Seleccione una marca de la lista para editar.",
                parent=self,
            )
            return

        valores = self.tree.item(seleccion[0], "values")
        self.id_seleccionado = valores[0]

        self.txt_nombre.delete(0, tk.END)
        self.txt_nombre.insert(0, valores[1])

        self.btn_guardar.configure(text="💾 Actualizar")
        self.txt_nombre.focus_set()

    def al_doble_clic(self, event):
        """Manejador para el evento doble clic sobre la fila."""
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0], "values")

        # Si viene con callback modal, el doble clic selecciona la marca y cierra
        if self.al_seleccionar_callback:
            self.al_seleccionar_callback(
                {"id": valores[0], "nombre": valores[1]}
            )
            self.destroy()
        else:
            self.cargar_para_editar()

    def eliminar_marca(self):
        """Elimina la marca seleccionada previa confirmación."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención",
                "Seleccione una marca para eliminar.",
                parent=self,
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
        self.btn_guardar.configure(text="💾 Guardar")