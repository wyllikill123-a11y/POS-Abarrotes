from database import conectar

conexion = conectar()
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
ALTER TABLE productos ADD COLUMN categoria_id INTEGER
""")

conexion.commit()
conexion.close()

print("Base de datos actualizada.")