import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from app.models.producto import Producto
from app.models.venta import Venta
from app.printing.ticket_printer import TicketPrinter
from app.models.turno import Turno
from app.ui.corte_window import CorteWindow

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

    def ejecutar_cobro(self):
        # 1. Validar si la caja/turno está abierto
        if not Turno.obtener_activo():
            # Llama directamente a la ventana para obligar a abrir la caja primero
            CorteWindow(self)
            return

        # 2. Si la caja está abierta, continúa con el proceso normal de cobro
        # ... tu código de cobro existente ...

class VentaExitosaDialog(ctk.CTkToplevel):
    def __init__(self, parent, venta_id, carrito, total, recibido, cambio, metodo):
        super().__init__(parent)
        self.title("Venta Exitosa")
        self.geometry("380x480")
        self.resizable(False, False)

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

        card = ctk.CTkFrame(self, fg_color="#2B2D31", corner_radius=10)
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
        self.geometry("1050x680")
        self.minsize(950, 580)
        
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

        # Panel Derecho Stilizado con Fondo Oscuro Elegante
        self.frame_derecho = ctk.CTkFrame(self, width=320, fg_color="#2B2D31", corner_radius=12, border_width=1, border_color="#1E1F22")
        self.frame_derecho.pack(side="right", fill="both", padx=(10, 15), pady=15)
        self.frame_derecho.pack_propagate(False)

    def crear_barra_busqueda(self):
        barra_superior = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        barra_superior.pack(fill="x", pady=(0, 12))

        self.txt_buscar = ctk.CTkEntry(
            barra_superior,
            placeholder_text="Escanea o escribe el código de barras...",
            font=("Segoe UI", 14),
            height=42,
            border_width=1,
            corner_radius=8
        )
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.txt_buscar.bind("<Return>", lambda event: self.agregar_producto_click())

        btn_agregar = ctk.CTkButton(
            barra_superior,
            text="➕ AGREGAR",
            font=("Segoe UI", 13, "bold"),
            width=130,
            height=42,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.agregar_producto_click
        )
        btn_agregar.pack(side="right")

    def crear_tabla_carrito(self):
        tabla_frame = ctk.CTkFrame(self.frame_izquierdo, corner_radius=8)
        tabla_frame.pack(fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background="#2B2D31",
            foreground="white",
            fieldbackground="#2B2D31",
            rowheight=32,
            font=("Segoe UI", 11)
        )
        estilo.configure(
            "Treeview.Heading",
            background="#1E1F22",
            foreground="#38BDF8",
            relief="flat",
            font=("Segoe UI", 11, "bold")
        )
        estilo.map("Treeview", background=[("selected", "#2563EB")])

        columnas = ("codigo", "nombre", "cantidad", "unidad", "precio", "subtotal")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("cantidad", text="Cant.")
        self.tabla.heading("unidad", text="Unidad")
        self.tabla.heading("precio", text="Precio U.")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("codigo", width=120, anchor="center")
        self.tabla.column("nombre", width=240, anchor="w")
        self.tabla.column("cantidad", width=80, anchor="center")
        self.tabla.column("unidad", width=80, anchor="center")
        self.tabla.column("precio", width=90, anchor="e")
        self.tabla.column("subtotal", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabla.bind("<Double-1>", lambda e: self.cambiar_cantidad_seleccionada())

    def crear_panel_totales(self):
        # 1. ENCABEZADO DE RESUMEN
        lbl_resumen = ctk.CTkLabel(
            self.frame_derecho,
            text="🧾 RESUMEN DE VENTA",
            font=("Segoe UI", 15, "bold"),
            text_color="#38BDF8"
        )
        lbl_resumen.pack(pady=(15, 5))

        self.lbl_articulos = ctk.CTkLabel(
            self.frame_derecho,
            text="Productos dist.: 0",
            font=("Segoe UI", 13, "bold"),
            text_color="#94A3B8"
        )
        self.lbl_articulos.pack(pady=(0, 10))

        # 2. CUADRO DE TOTAL MONETARIO
        frame_total = ctk.CTkFrame(self.frame_derecho, fg_color="#1E1F22", corner_radius=10)
        frame_total.pack(fill="x", padx=15, pady=5)

        lbl_total_titulo = ctk.CTkLabel(
            frame_total,
            text="TOTAL A PAGAR",
            font=("Segoe UI", 11, "bold"),
            text_color="#4ADE80"
        )
        lbl_total_titulo.pack(pady=(10, 2))

        self.lbl_total_numero = ctk.CTkLabel(
            frame_total,
            text="$0.00",
            font=("Segoe UI", 34, "bold"),
            text_color="#FFFFFF"
        )
        self.lbl_total_numero.pack(pady=(0, 10))

        # 3. MÉTODO DE PAGO
        ctk.CTkLabel(
            self.frame_derecho,
            text="Método de Pago",
            font=("Segoe UI", 12, "bold"),
            text_color="#E2E8F0"
        ).pack(pady=(12, 4))

        self.metodo_pago = ctk.CTkComboBox(
            self.frame_derecho,
            values=["EFECTIVO", "TARJETA", "TRANSFERENCIA"],
            height=35,
            font=("Segoe UI", 12, "bold"),
            dropdown_font=("Segoe UI", 12)
        )
        self.metodo_pago.pack(fill="x", padx=15)
        self.metodo_pago.set("EFECTIVO")

        # 4. BOTÓN COBRAR
        self.btn_cobrar = ctk.CTkButton(
            self.frame_derecho,
            text="💳 COBRAR  [F12]",
            command=self.cobrar,
            font=("Segoe UI", 16, "bold"),
            height=46,
            corner_radius=8,
            fg_color="#16A34A",
            hover_color="#15803D",
            state="disabled"
        )
        self.btn_cobrar.pack(fill="x", padx=15, pady=(15, 10))

        # =========================================================
        # 5. GUÍA VISUAL DE ATAJOS DE TECLADO (LLAMATIVA)
        # =========================================================
        frame_atajos = ctk.CTkFrame(self.frame_derecho, fg_color="#1E1F22", corner_radius=10)
        frame_atajos.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        lbl_atajos_titulo = ctk.CTkLabel(
            frame_atajos,
            text="⌨️ ATAJOS DE TECLADO",
            font=("Segoe UI", 12, "bold"),
            text_color="#FBBF24"
        )
        lbl_atajos_titulo.pack(pady=(8, 6))

        atajos_lista = [
            ("ENTER", "Agregar / Escanear"),
            ("F2", "Modificar Cantidad"),
            ("SUPR", "Quitar Producto"),
            ("F12", "Cobrar Venta"),
            ("ESC", "Cerrar Ventana")
        ]

        for tecla, accion in atajos_lista:
            row = ctk.CTkFrame(frame_atajos, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)

            # Insignia de la Tecla (Badge)
            badge = ctk.CTkLabel(
                row,
                text=tecla,
                font=("Consolas", 11, "bold"),
                text_color="#0F172A",
                fg_color="#E2E8F0",
                corner_radius=4,
                width=55,
                height=22
            )
            badge.pack(side="left")

            # Descripción de la Acción
            lbl_desc = ctk.CTkLabel(
                row,
                text=accion,
                font=("Segoe UI", 11, "bold"),
                text_color="#CBD5E1"
            )
            lbl_desc.pack(side="left", padx=(8, 0))

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
            prod_dict = dict(producto_db) if not isinstance(producto_db, dict) else producto_db

            prod_id = prod_dict.get("id") or prod_dict.get("codigo")
            prod_codigo = prod_dict.get("codigo")
            prod_nombre = prod_dict.get("nombre")
            prod_precio = float(prod_dict.get("precio_venta", prod_dict.get("precio", 0.0)))
            unidad = str(prod_dict.get("unidad", "PZA")).upper()

            if unidad not in ["PZA", "PIEZA", "UNIDAD"]:
                cantidad = self.solicitar_peso_granel(prod_nombre, unidad)
                if cantidad is None or cantidad <= 0:
                    self.after(100, lambda: self.txt_buscar.focus())
                    return
            else:
                cantidad = 1.0

            self.agregar_al_carrito({
                "id": prod_id,
                "codigo": prod_codigo,
                "nombre": prod_nombre,
                "unidad": unidad,
                "precio": prod_precio
            }, cantidad=cantidad)

            self.actualizar_tabla()
            self.txt_buscar.delete(0, "end")
            self.txt_buscar.focus()
        else:
            messagebox.showwarning("No Encontrado", f"No se encontró ningún producto activo con el término: '{busqueda}'")
            self.after(100, lambda: self.txt_buscar.focus())

    def solicitar_peso_granel(self, nombre_prod, unidad):
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
                if self.winfo_exists():
                    self.after(100, lambda: self.txt_buscar.focus() if self.winfo_exists() else None)
                return

            monto_recibido = dialogo.monto_recibido
            cambio = dialogo.cambio
        else:
            if not messagebox.askyesno("Confirmar Cobro", f"¿Confirmar cobro de ${total_venta:.2f} con {metodo}?"):
                if self.winfo_exists():
                    self.after(100, lambda: self.txt_buscar.focus() if self.winfo_exists() else None)
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
            
            if hasattr(self, 'txt_buscar') and self.txt_buscar.winfo_exists():
                self.txt_buscar.delete(0, "end")

            if hasattr(self.master, 'dashboard') and hasattr(self.master.dashboard, 'actualizar'):
                self.master.dashboard.actualizar()

            dlg_exito = VentaExitosaDialog(
                self, 
                venta_id=venta_id, 
                carrito=items_carrito,
                total=total_venta, 
                recibido=monto_recibido, 
                cambio=cambio, 
                metodo=metodo
            )
            self.wait_window(dlg_exito)
            
            if self.winfo_exists():
                try:
                    self.metodo_pago.set("EFECTIVO")
                except Exception:
                    pass
                
                self.after(100, lambda: self.txt_buscar.focus() if self.winfo_exists() else None)

        except ValueError as err_val:
            messagebox.showwarning("Atención", str(err_val))
            if self.winfo_exists():
                self.after(100, lambda: self.txt_buscar.focus() if self.winfo_exists() else None)

        except Exception as err:
            import traceback
            print("ERROR DETALLADO EN REGISTRAR VENTA:")
            traceback.print_exc()
            messagebox.showerror("Error al Registrar Venta", f"Detalle del error:\n{str(err)}")
            if self.winfo_exists():
                self.after(100, lambda: self.txt_buscar.focus() if self.winfo_exists() else None)