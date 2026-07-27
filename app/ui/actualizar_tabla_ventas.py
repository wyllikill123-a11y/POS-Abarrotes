import sqlite3

conexion = sqlite3.connect("app/database/abarrotes.db")
cursor = conexion.cursor()

def agregar_columna(nombre, tipo):
    try:
        cursor.execute(f"ALTER TABLE ventas ADD COLUMN {nombre} {tipo}")
        print(f"✓ Columna '{nombre}' agregada.")
    except sqlite3.OperationalError:
        print(f"- La columna '{nombre}' ya existe.")

agregar_columna("subtotal", "REAL DEFAULT 0")
agregar_columna("descuento", "REAL DEFAULT 0")
agregar_columna("metodo_pago", "TEXT DEFAULT 'EFECTIVO'")
agregar_columna("monto_recibido", "REAL DEFAULT 0")
agregar_columna("cambio", "REAL DEFAULT 0")

conexion.commit()
conexion.close()

print("Tabla ventas actualizada.")