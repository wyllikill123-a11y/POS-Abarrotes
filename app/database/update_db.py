import sqlite3

DB_PATH = "app/database/abarrotes.db"

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# Activar Foreign Keys
cursor.execute("PRAGMA foreign_keys = ON;")

# 1. Crear tablas auxiliares si no existen
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS marcas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    telefono TEXT,
    contacto TEXT
)
""")

# Insertar categoría por defecto
cursor.execute("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (1, 'General')")

# 2. Obtener columnas existentes en la tabla productos
cursor.execute("PRAGMA table_info(productos)")
columnas = [col[1] for col in cursor.fetchall()]

# 3. Agregar columnas que falten de forma dinámica
columnas_a_agregar = {
    "categoria_id": "INTEGER DEFAULT 1",
    "marca_id": "INTEGER",
    "proveedor_id": "INTEGER",
    "activo": "INTEGER DEFAULT 1"
}

for columna, definicion in columnas_a_agregar.items():
    if columna not in columnas:
        cursor.execute(f"ALTER TABLE productos ADD COLUMN {columna} {definicion}")
        print(f"✓ Columna '{columna}' agregada correctamente.")
    else:
        print(f"✓ Columna '{columna}' ya existe.")

conexion.commit()
conexion.close()

print("\nBase de datos actualizada y migrada correctamente.")