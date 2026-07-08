import customtkinter as ctk
from tkinter import messagebox
from app.models.producto import Producto


class NuevoProducto(ctk.CTkToplevel):

    def __init__(self, master, datos=None):
        super().__init__(master)

        self.editando = False
        self.codigo_original = None

        self.title("Nuevo Producto")
        self.geometry("700x600")
        self.grab_set()

        titulo = ctk.CTkLabel(
            self,
            text="➕ Registrar Producto",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=20)

        # Código
        ctk.CTkLabel(self, text="Código interno").pack(anchor="w", padx=20)
        self.codigo = ctk.CTkEntry(self, width=300)
        self.codigo.pack(padx=20, pady=5)

        # Nombre
        ctk.CTkLabel(self, text="Nombre").pack(anchor="w", padx=20)
        self.nombre = ctk.CTkEntry(self, width=500)
        self.nombre.pack(padx=20, pady=5)

        # Unidad
        ctk.CTkLabel(self, text="Unidad").pack(anchor="w", padx=20)

        self.unidad = ctk.CTkComboBox(
            self,
            values=[
                "Pieza",
                "Kilogramo",
                "Gramo",
                "Litro",
                "Mililitro",
                "Caja",
                "Paquete",
                "Bolsa",
                "Botella",
                "Lata"
            ]
        )

        self.unidad.pack(padx=20, pady=5)
        self.unidad.set("Pieza")

        # Precio compra
        ctk.CTkLabel(self, text="Precio compra").pack(anchor="w", padx=20)
        self.precio_compra = ctk.CTkEntry(self, width=200)
        self.precio_compra.pack(padx=20, pady=5)

        # Precio venta
        ctk.CTkLabel(self, text="Precio venta").pack(anchor="w", padx=20)
        self.precio_venta = ctk.CTkEntry(self, width=200)
        self.precio_venta.pack(padx=20, pady=5)

        # Existencia
        ctk.CTkLabel(self, text="Existencia").pack(anchor="w", padx=20)
        self.existencia = ctk.CTkEntry(self, width=200)
        self.existencia.pack(padx=20, pady=5)

        boton = ctk.CTkButton(
            self,
            text="💾 Guardar Producto",
            command=self.guardar_producto
        )
        boton.pack(pady=30)

        # ========= MODO EDICIÓN =========

        if datos:

            self.editando = True
            self.codigo_original = datos[0]

            self.codigo.insert(0, datos[0])
            self.nombre.insert(0, datos[1])
            self.unidad.set(datos[2])
            self.precio_compra.insert(0, datos[3])
            self.precio_venta.insert(0, datos[4])
            self.existencia.insert(0, datos[5])

            self.codigo.configure(state="disabled")

            self.title("Editar Producto")
            titulo.configure(text="✏ Editar Producto")

    def guardar_producto(self):

        try:

            producto = Producto(
                self.codigo.get(),
                self.nombre.get(),
                self.unidad.get(),
                float(self.precio_compra.get()),
                float(self.precio_venta.get()),
                float(self.existencia.get())
            )

            if self.editando:
                producto.actualizar()
                mensaje = "Producto actualizado correctamente."
            else:
                producto.guardar()
                mensaje = "Producto guardado correctamente."

            messagebox.showinfo(
                "Correcto",
                mensaje
            )

            self.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )