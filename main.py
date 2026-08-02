import customtkinter as ctk

from app.database.database import inicializar_bd
from app.ui.main_window import MainWindow


# Crear base de datos y tablas si no existen
inicializar_bd()


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

app = MainWindow()
app.mainloop()