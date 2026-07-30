import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from app.models.producto import Producto
from app.models.venta import Venta
from app.printing.ticket_printer import TicketPrinter

class CobroEfectivoDialog(ctk.CTkToplevel):
    def __init__(self, parent, total_a_pagar):
        super().__init__(parent)
        self.title("Cobro en Efectivo")
        self.geometry("400x450")
        self.resizable(False, False)

        self.total = total_a_pagar
        self.monto_recibido = 0.0
        self.cambio = 0.0
        self.confirmado = False

        self.transient(parent)
        self.grab_set()

        self.crear_widgets()

        self.bind("<Return>", lambda e: self.confirmar_cobro())
        self.bind("<Escape>", lambda e: self.destroy())

        self.after(100, lambda: self.txt_recibido.focus())

    def crear_widgets(self):
        ctk.CTkLabel(
            self,
            text="TOTAL A PAGAR",
            font=("Segoe UI", 12, "bold"),
            text_color="gray"
        ).pack(pady=(20, 2))

        ctk.CTkLabel(
            self,
            text=f"${self.total:.2f}",
            font=("Segoe UI", 32, "bold"),
            text_color="#81C784"
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            self,
            text="Efectivo Recibido ($):",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(5, 5))

        self.txt_recibido = ctk.CTkEntry(
            self,
            font=("Segoe UI", 22, "bold"),
            justify="center",
            height=45,
            width=220
        )
        self.txt_recibido.pack(pady=5)
        self.txt_recibido.bind("<KeyRelease>", self.calcular_cambio)

        frame_billetes = ctk.CTkFrame(self, fg_color="transparent")
        frame_billetes.pack(pady=10)

        for valor in [50, 100, 200, 500]:
            btn = ctk.CTkButton(
                frame_billetes,
                text=f"${valor}",
                width=65,
                height=30,
                fg_color="#444444",
                hover_color="#555555",
                command=lambda v=valor: self.set_monto(v)
            )
            btn.pack(side="left", padx=3)

        btn_exacto = ctk.CTkButton(
            frame_billetes,
            text="Exacto",
            width=65,
            height=30,
            fg_color="#1A73E8",
            hover_color="#1557B0",
            command=lambda: self.set_monto(self.total)
        )
        btn_exacto.pack(side="left", padx=3)

        ctk.CTkLabel(
            self,
            text="CAMBIO A ENTREGAR",
            font=("Segoe UI", 12, "bold"),
            text_color="gray"
        ).pack(pady=(15, 2))

        self.lbl_cambio = ctk.CTkLabel(
            self,
            text="$0.00",
            font=("Segoe UI", 32, "bold"),
            text_color="#64B5F6"
        )
        self.lbl_cambio.pack(pady=(0, 15))

        self.btn_confirmar = ctk.CTkButton(
            self,
            text="✔ Confirmar Cobro (Enter)",
            font=("Segoe UI", 14, "bold"),
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            state="disabled",
            command=self.confirmar_cobro
        )
        self.btn_confirmar.pack(fill="x", padx=30, pady=10)

    def set_monto(self, monto):
        self.txt_recibido.delete(0, "end")
        self.txt_recibido.insert(0, f"{monto:.2f}")
        self.calcular_cambio()

    def calcular_cambio(self, event=None):
        try:
            texto = self.txt_recibido.get().strip()
            if not texto:
                self.lbl_cambio.configure(text="$0.00", text_color="#64B5F6")
                self.btn_confirmar.configure(state="disabled")
                return

            self.monto_recibido = float(texto)
            self.cambio = self.monto_recibido - self.total

            if self.cambio >= 0:
                self.lbl_cambio.configure(text=f"${self.cambio:.2f}", text_color="#81C784")
                self.btn_confirmar.configure(state="normal")
            else:
                falta = abs(self.cambio)
                self.lbl_cambio.configure(text=f"Faltan ${falta:.2f}", text_color="#E57373")
                self.btn_confirmar.configure(state="disabled")

        except ValueError:
            self.lbl_cambio.configure(text="Monto inválido", text_color="#E57373")
            self.btn_confirmar.configure(state="disabled")

    def confirmar_cobro(self):
        if self.monto_recibido >= self.total and self.cambio >= 0:
            self.confirmado = True
            self.destroy()


class VentaExitosaDialog(ctk.CTkToplevel):
    def __init__(self, parent, venta_id, carrito, total, recibido, cambio, metodo):
        super().__init__(parent)
        self.title("Venta Exitosa")
        self.geometry("380x480")
        self.resizable(False, False)

        # --- GUARDAR ATRIBUTOS PARA SU USO EN IMPRIMIR_TICKET ---
        self.venta_id = venta_id
        self.carrito = carrito
        self.total = total
        self.recibido = recibido
        self.cambio = cambio
        self.metodo = metodo

        self.transient(parent)
        self.grab_set()

        self.bind("<F12>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())

        self.crear_widgets(venta_id, total, recibido, cambio, metodo)
        self.after(100, lambda: self.focus_set())

    def crear_widgets(self, venta_id, total, recibido, cambio, metodo):
        ctk.CTkLabel(
            self,
            text="✔ VENTA EXITOSA",
            font=("Segoe UI", 20, "bold"),
            text_color="#81C784"
        ).pack(pady=(20, 2))

        ctk.CTkLabel(
            self,
            text=f"Folio de Venta #{venta_id}",
            font=("Segoe UI", 12),
            text_color="gray"
        ).pack(pady=(0, 15))

        card = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        card.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(card, text="TOTAL", font=("Segoe UI", 11, "bold"), text_color="gray").pack(pady=(15, 2))
        ctk.CTkLabel(card, text=f"${total:.2f}", font=("Segoe UI", 26, "bold"), text_color="#FFFFFF").pack(pady=(0, 10))

        ctk.CTkLabel(card, text=f"RECIBIÓ ({metodo})", font=("Segoe UI", 11, "bold"), text_color="gray").pack(pady=(5, 2))
        ctk.CTkLabel(card, text=f"${recibido:.2f}", font=("Segoe UI", 22, "bold"), text_color="#E0E0E0").pack(pady=(0, 10))

        ctk.CTkLabel(card, text="CAMBIO A ENTREGAR", font=("Segoe UI", 11, "bold"), text_color="gray").pack(pady=(5, 2))
        ctk.CTkLabel(card, text=f"${cambio:.2f}", font=("Segoe UI", 28, "bold"), text_color="#64B5F6").pack(pady=(0, 15))

        btn_imprimir = ctk.CTkButton(
            self,
            text="🖨 Imprimir Ticket",
            font=("Segoe UI", 13, "bold"),
            height=38,
            fg_color="#444444",
            hover_color="#555555",
            command=self.imprimir_ticket
        )
        btn_imprimir.pack(fill="x", padx=30, pady=(15, 5))

        btn_nueva_venta = ctk.CTkButton(
            self,
            text="Nueva Venta (F12)",
            font=("Segoe UI", 14, "bold"),
            height=42,
            fg_color="#1A73E8",
            hover_color="#1557B0",
            command=self.destroy
        )
        btn_nueva_venta.pack(fill="x", padx=30, pady=(5, 15))

    def imprimir_ticket(self):
        try:
            TicketPrinter.imprimir_ticket_venta(
                venta_id=self.venta_id,
                carrito=self.carrito,
                total=self.total,
                recibido=self.recibido,
                cambio=self.cambio,
                metodo=self.metodo
            )
            messagebox.showinfo("Impresión", "El ticket se ha enviado a la impresora.")
        except Exception as e:
            messagebox.showerror("Error de Impresión", f"{str(e)}")

class NuevaVentaWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Nueva Venta - Abarrotes Rosita-Andrea")
        self.geometry("950x600")
        self.minsize(850, 500)
        
        master.update_idletasks()
        self.transient(master)
        self.grab_set()
        self.focus_set()

        self.carrito = {}

        # Redirección de escáner y accesos directos
        self.bind("<Key>", self._redireccionar_escanner)
        self.bind("<F12>", lambda e: self.cobrar())
        self.bind("<F2>", lambda e: self.cambiar_cantidad_seleccionada())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Delete>", lambda e: self.eliminar_seleccionado())

        self.configurar_layout()
        self.crear_barra_busqueda()
        self.crear_tabla_carrito()
        self.crear_panel_totales()

        self.after(100, lambda: self.txt_buscar.focus())

    def _redireccionar_escanner(self, event):
        widget_actual = self.focus_get()
        
        if widget_actual == self.txt_buscar._entry:
            return

        if event.keysym in ("F12", "F2", "Escape", "Delete", "BackSpace", "Return", "Tab"):
            return

        if event.char and event.char.isprintable():
            self.txt_buscar.focus()
            self.txt_buscar.insert("end", event.char)

    def configurar_layout(self):
        self.frame_izquierdo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_izquierdo.pack(side="left", fill="both", expand=True, padx=(15, 10), pady=15)

        self.frame_derecho = ctk.CTkFrame(self, width=280, fg_color="#3A3A3A", corner_radius=12)
        self.frame_derecho.pack(side="right", fill="both", padx=(10, 15), pady=15)
        self.frame_derecho.pack_propagate(False)

    def crear_barra_busqueda(self):
        barra_superior = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        barra_superior.pack(fill="x", pady=(0, 15))

        self.txt_buscar = ctk.CTkEntry(
            barra_superior,
            placeholder_text="Escanea o escribe el código de barras...",
            font=("Segoe UI", 14),
            height=38
        )
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.txt_buscar.bind("<Return>", lambda event: self.agregar_producto_click())

        btn_agregar = ctk.CTkButton(
            barra_superior,
            text="➕ Agregar",
            font=("Segoe UI", 14, "bold"),
            width=120,
            height=38,
            fg_color="#1A73E8",
            hover_color="#1557B0",
            command=self.agregar_producto_click
        )
        btn_agregar.pack(side="right")

    def crear_tabla_carrito(self):
        tabla_frame = ctk.CTkFrame(self.frame_izquierdo)
        tabla_frame.pack(fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            rowheight=30,
            font=("Segoe UI", 11)
        )
        estilo.configure(
            "Treeview.Heading",
            background="#3E3E3E",
            foreground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold")
        )
        estilo.map("Treeview", background=[("selected", "#1A73E8")])

        columnas = ("codigo", "nombre", "cantidad", "unidad", "precio", "subtotal")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("cantidad", text="Cant.")
        self.tabla.heading("unidad", text="Unidad")
        self.tabla.heading("precio", text="Precio U.")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("codigo", width=120, anchor="center")
        self.tabla.column("nombre", width=250, anchor="w")
        self.tabla.column("cantidad", width=80, anchor="center")
        self.tabla.column("unidad", width=80, anchor="center")
        self.tabla.column("precio", width=90, anchor="e")
        self.tabla.column("subtotal", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Doble clic permite modificar la cantidad rápidamente
        self.tabla.bind("<Double-1>", lambda e: self.cambiar_cantidad_seleccionada())

    def crear_panel_totales(self):
        lbl_resumen = ctk.CTkLabel(
            self.frame_derecho,
            text="Resumen de Venta",
            font=("Segoe UI", 16, "bold"),
            text_color="#64B5F6"
        )
        lbl_resumen.pack(pady=20)

        self.lbl_articulos = ctk.CTkLabel(
            self.frame_derecho,
            text="Artículos: 0",
            font=("Segoe UI", 14)
        )
        self.lbl_articulos.pack(pady=10)

        lbl_total_titulo = ctk.CTkLabel(
            self.frame_derecho,
            text="TOTAL A PAGAR",
            font=("Segoe UI", 14, "bold"),
            text_color="#81C784"
        )
        lbl_total_titulo.pack(pady=(20, 5))

        self.lbl_total_numero = ctk.CTkLabel(
            self.frame_derecho,
            text="$0.00",
            font=("Segoe UI", 36, "bold"),
            text_color="#FFFFFF"
        )
        self.lbl_total_numero.pack(pady=5)

        ctk.CTkLabel(
            self.frame_derecho,
            text="Método de pago",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(20, 5))

        self.metodo_pago = ctk.CTkComboBox(
            self.frame_derecho,
            values=["EFECTIVO", "TARJETA", "TRANSFERENCIA"]
        )
        self.metodo_pago.pack(fill="x", padx=20)
        self.metodo_pago.set("EFECTIVO")

        self.btn_cobrar = ctk.CTkButton(
            self.frame_derecho,
            text="💳 Cobrar  F12",
            command=self.cobrar,
            font=("Segoe UI", 16, "bold"),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            state="disabled"
        )
        self.btn_cobrar.pack(side="bottom", fill="x", padx=20, pady=25)

    def agregar_producto_click(self):
        busqueda = self.txt_buscar.get().strip()
        if not busqueda:
            return

        producto_db = Producto.buscar_por_codigo(busqueda)

        if not producto_db:
            resultados = Producto.buscar(busqueda, incluir_desactivados=False)
            if resultados:
                producto_db = resultados[0]

        if producto_db:
            # Convertir sqlite3.Row / tuple a dict para homogeneizar el acceso a campos
            prod_dict = dict(producto_db) if not isinstance(producto_db, dict) else producto_db

            # Obtener campos de forma segura
            prod_id = prod_dict.get("id") or prod_dict.get("codigo")
            prod_codigo = prod_dict.get("codigo")
            prod_nombre = prod_dict.get("nombre")
            prod_precio = float(prod_dict.get("precio_venta", prod_dict.get("precio", 0.0)))
            unidad = str(prod_dict.get("unidad", "PZA")).upper()

            # Si el producto es a granel, solicitar peso
            if unidad not in ["PZA", "PIEZA", "UNIDAD"]:
                cantidad = self.solicitar_peso_granel(prod_nombre, unidad)
                if cantidad is None or cantidad <= 0:
                    self.after(100, lambda: self.txt_buscar.focus())
                    return
            else:
                cantidad = 1.0

            # Agregar un solo elemento al carrito
            self.agregar_al_carrito({
                "id": prod_id,
                "codigo": prod_codigo,
                "nombre": prod_nombre,
                "unidad": unidad,
                "precio": prod_precio
            }, cantidad=cantidad)

            # Refrescar la interfaz y limpiar la caja de texto
            self.actualizar_tabla()
            self.txt_buscar.delete(0, "end")
            self.txt_buscar.focus()
        else:
            messagebox.showwarning("No Encontrado", f"No se encontró ningún producto activo con el término: '{busqueda}'")
            self.after(100, lambda: self.txt_buscar.focus())

    def solicitar_peso_granel(self, nombre_prod, unidad):
        """Abre un diálogo simple para ingresar peso o decimales de un producto a granel."""
        val = simpledialog.askfloat(
            "Venta a Granel",
            f"Ingrese la cantidad ({unidad}) para:\n{nombre_prod}",
            minvalue=0.001,
            maxvalue=999.0,
            parent=self
        )
        return val

    def agregar_al_carrito(self, producto, cantidad=1.0):
        codigo = producto["codigo"]

        if codigo in self.carrito:
            self.carrito[codigo]["cantidad"] += cantidad
            self.carrito[codigo]["subtotal"] = (
                self.carrito[codigo]["cantidad"] * self.carrito[codigo]["precio"]
            )
        else:
            self.carrito[codigo] = {
                "id": producto["id"],
                "codigo": producto["codigo"],
                "nombre": producto["nombre"],
                "unidad": producto["unidad"],
                "cantidad": cantidad,
                "precio": producto["precio"],
                "subtotal": cantidad * producto["precio"]
            }

    def cambiar_cantidad_seleccionada(self):
        """Permite modificar la cantidad del producto seleccionado en la tabla (F2 o Doble Clic)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        datos = self.tabla.item(seleccion[0], "values")
        codigo = datos[0]

        if codigo in self.carrito:
            item = self.carrito[codigo]
            nueva_cant = simpledialog.askfloat(
                "Modificar Cantidad",
                f"Modificar cantidad para {item['nombre']} ({item['unidad']}):",
                initialvalue=item["cantidad"],
                minvalue=0.0,
                parent=self
            )

            if nueva_cant is not None:
                if nueva_cant <= 0:
                    del self.carrito[codigo]
                else:
                    self.carrito[codigo]["cantidad"] = nueva_cant
                    self.carrito[codigo]["subtotal"] = nueva_cant * item["precio"]

                self.actualizar_tabla()
        
        self.after(100, lambda: self.txt_buscar.focus())

    def eliminar_seleccionado(self):
        """Elimina por completo el ítem seleccionado con la tecla Supr / Delete."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        datos = self.tabla.item(seleccion[0], "values")
        codigo = datos[0]

        if codigo in self.carrito:
            del self.carrito[codigo]
            self.actualizar_tabla()

        self.after(100, lambda: self.txt_buscar.focus())

    def actualizar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        for producto in self.carrito.values():
            cant = producto["cantidad"]
            cant_str = f"{cant:.3f}" if isinstance(cant, float) and not cant.is_integer() else f"{int(cant)}"
            
            self.tabla.insert(
                "",
                "end",
                values=(
                    producto["codigo"],
                    producto["nombre"],
                    cant_str,
                    producto["unidad"],
                    f"${producto['precio']:.2f}",
                    f"${producto['subtotal']:.2f}"
                )
            )
        self.actualizar_totales()

    def actualizar_totales(self):
        total = sum(item["subtotal"] for item in self.carrito.values())
        articulos = len(self.carrito)

        self.lbl_articulos.configure(text=f"Productos dist.: {articulos}")
        self.lbl_total_numero.configure(text=f"${total:.2f}")

        if total > 0:
            self.btn_cobrar.configure(state="normal")
        else:
            self.btn_cobrar.configure(state="disabled")

    def cobrar(self):
        if not self.carrito:
            messagebox.showwarning("Venta Vacía", "No hay productos en el carrito para procesar.")
            return

        total_venta = sum(item["subtotal"] for item in self.carrito.values())
        metodo = self.metodo_pago.get()

        monto_recibido = total_venta
        cambio = 0.0

        if metodo == "EFECTIVO":
            dialogo = CobroEfectivoDialog(self, total_venta)
            self.wait_window(dialogo)

            if not dialogo.confirmado:
                self.after(100, lambda: self.txt_buscar.focus())
                return

            monto_recibido = dialogo.monto_recibido
            cambio = dialogo.cambio
        else:
            if not messagebox.askyesno("Confirmar Cobro", f"¿Confirmar cobro de ${total_venta:.2f} con {metodo}?"):
                self.after(100, lambda: self.txt_buscar.focus())
                return

        try:
            items_carrito = list(self.carrito.values())

            venta_id = Venta.registrar_venta(
                carrito=items_carrito,
                metodo_pago=metodo,
                descuento=0,
                monto_recibido=monto_recibido,
                cambio=cambio
            )

            self.carrito.clear()
            self.actualizar_tabla()
            self.txt_buscar.delete(0, "end")

            if hasattr(self.master, 'dashboard') and hasattr(self.master.dashboard, 'actualizar'):
                self.master.dashboard.actualizar()

          # Instanciar pasando también el parámetro 'carrito'
            dlg_exito = VentaExitosaDialog(
                self, 
                venta_id=venta_id, 
                carrito=items_carrito,  # <--- AGREGAR ESTA LÍNEA
                total=total_venta, 
                recibido=monto_recibido, 
                cambio=cambio, 
                metodo=metodo
            )
            self.wait_window(dlg_exito)
            
            self.metodo_pago.set("EFECTIVO")
            self.after(100, lambda: self.txt_buscar.focus())

        except ValueError as err_val:
            messagebox.showwarning("Atención", str(err_val))
            self.after(100, lambda: self.txt_buscar.focus())

        except Exception as err:
                    import traceback
                    print("ERROR DETALLADO EN REGISTRAR VENTA:")
                    traceback.print_exc()  # Esto imprimirá la falla exacta en la consola
                    messagebox.showerror("Error al Registrar Venta", f"Detalle del error:\n{str(err)}")
                    self.after(100, lambda: self.txt_buscar.focus())