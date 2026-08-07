# app/ui/corte_window.py
import customtkinter as ctk
from tkinter import messagebox
from app.models.turno import Turno
from app.printing.corte_ticket_builder import CorteTicketBuilder


class CorteWindow(ctk.CTkToplevel):

    def __init__(self, master, impresora_service=None):
        super().__init__(master)
        self.impresora = impresora_service

        self.title("Control de Caja y Turnos")
        self.geometry("400x350")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.turno_actual = Turno.obtener_activo()
        self._construir_ui()

    def _construir_ui(self):
        if not self.turno_actual:
            # UI para Abrir Turno
            ctk.CTkLabel(
                self, text="🔓 Apertura de Turno", font=("Segoe UI", 18, "bold")
            ).pack(pady=15)
            ctk.CTkLabel(
                self, text="Ingrese el fondo inicial de la caja:"
            ).pack(pady=5)

            self.txt_fondo = ctk.CTkEntry(
                self, placeholder_text="0.00", width=180
            )
            self.txt_fondo.pack(pady=10)
            self.txt_fondo.insert(0, "0.00")

            ctk.CTkButton(
                self,
                text="Abrir Caja",
                fg_color="#2E7D32",
                hover_color="#1B5E20",
                command=self.abrir_caja,
            ).pack(pady=20)
        else:
            # UI para Corte / Cerrar Turno
            ctk.CTkLabel(
                self, text="🔒 Corte de Turno", font=("Segoe UI", 18, "bold")
            ).pack(pady=15)
            ctk.CTkLabel(
                self,
                text=f"Turno Activo ID: #{self.turno_actual['id']}\nAbierto el: {self.turno_actual['fecha_apertura'][:16]}",
            ).pack(pady=10)

            ctk.CTkButton(
                self,
                text="📊 Realizar Corte y Imprimir",
                fg_color="#D32F2F",
                hover_color="#C62828",
                command=self.realizar_corte,
            ).pack(pady=20)

    def abrir_caja(self):
        try:
            monto = float(self.txt_fondo.get().strip() or 0)
            Turno.abrir(monto)
            messagebox.showinfo(
                "Éxito", "Turno iniciado correctamente. ¡Buena jornada!"
            )
            self.destroy()
        except ValueError as e:
            messagebox.showerror(
                "Error", f"Ingresa un valor numérico válido: {e}"
            )

    def realizar_corte(self):
        confirmar = messagebox.askyesno(
            "Confirmar Corte",
            "¿Desea cerrar el turno actual y generar el ticket de corte?",
        )
        if confirmar:
            try:
                datos_corte = Turno.realizar_corte()
                texto_ticket = CorteTicketBuilder.construir(datos_corte)

                # Si tienes integrado el servicio de impresora:
                if self.impresora:
                    self.impresora.imprimir(texto_ticket)

                messagebox.showinfo(
                    "Corte Completado",
                    f"Turno #{datos_corte['id_turno']} cerrado.\n\nTotal Ventas: ${datos_corte['total_ventas']:.2f}\nEfectivo en Caja: ${datos_corte['monto_total_caja']:.2f}",
                )
                self.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo realizar el corte: {e}"
                )