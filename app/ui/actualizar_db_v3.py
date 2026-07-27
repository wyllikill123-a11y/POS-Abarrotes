import sqlite3

conexion = sqlite3.connect("app/database/abarrotes.db")
cursor = conexion.cursor()

try:
    cursor.execute("""
        ALTER TABLE productos
        ADD COLUMN stock_minimo REAL DEFAULT 5
    """)
    print("Columna 'stock_minimo' agregada correctamente.")
except sqlite3.OperationalError:
    print("La columna 'stock_minimo' ya existe.")

conexion.commit()
conexion.close()