import sqlite3

conexion = sqlite3.connect("app/database/abarrotes.db")
cursor = conexion.cursor()

# ==========================
# TABLA CATEGORÍAS
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# ==========================
# TABLA MARCAS
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS marcas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# ==========================
# TABLA PROVEEDORES
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS proveedores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    telefono TEXT,
    contacto TEXT
)
""")

# ==========================
# TABLA PRODUCTOS
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    codigo TEXT UNIQUE NOT NULL,

    codigo_barras TEXT,

    nombre TEXT NOT NULL,

    categoria_id INTEGER,

    marca_id INTEGER,

    proveedor_id INTEGER,

    unidad TEXT NOT NULL,

    precio_compra REAL NOT NULL,

    precio_venta REAL NOT NULL,

    existencia REAL DEFAULT 0,

    stock_minimo REAL DEFAULT 0,

    activo INTEGER DEFAULT 1,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(categoria_id) REFERENCES categorias(id),

    FOREIGN KEY(marca_id) REFERENCES marcas(id),

    FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)

)
""")

conexion.commit()
conexion.close()

print("Base de datos creada correctamente.")