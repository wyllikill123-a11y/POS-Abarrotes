import sqlite3

conexion = sqlite3.connect("app/database/abarrotes.db")
cursor = conexion.cursor()

try:
    cursor.execute("""
        ALTER TABLE productos
        ADD COLUMN tipo_venta TEXT DEFAULT 'PIEZA'
    """)

    print("✅ Campo tipo_venta agregado correctamente.")

except sqlite3.OperationalError as e:

    if "duplicate column name" in str(e):
        print("ℹ️ El campo tipo_venta ya existe.")
    else:
        raise

conexion.commit()
conexion.close()