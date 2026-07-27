import sqlite3

conexion = sqlite3.connect("app/database/abarrotes.db")
cursor = conexion.cursor()

try:
    cursor.execute("""
        ALTER TABLE productos
        ADD COLUMN activo INTEGER NOT NULL DEFAULT 1
    """)
    print("Columna 'activo' agregada correctamente.")
except sqlite3.OperationalError:
    print("La columna 'activo' ya existe.")

conexion.commit()
conexion.close()