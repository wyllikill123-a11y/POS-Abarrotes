import sqlite3
from pathlib import Path

# ==========================================
# CREAR CARPETA DATABASE
# ==========================================
DB_FOLDER = Path("app/database")
DB_FOLDER.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_FOLDER / "abarrotes.db"

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

# ===================================================
# CATEGORIAS
# ===================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS categorias(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# ===================================================
# MARCAS
# ===================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS marcas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# ===================================================
# PROVEEDORES
# ===================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS proveedores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    telefono TEXT,
    contacto TEXT
)
""")

# ===================================================
# PRODUCTOS
# ===================================================
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
    tipo_venta TEXT NOT NULL DEFAULT 'PIEZA',

    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,

    existencia REAL DEFAULT 0,
    stock_minimo REAL DEFAULT 0,

    activo INTEGER DEFAULT 1,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(categoria_id)
        REFERENCES categorias(id),

    FOREIGN KEY(marca_id)
        REFERENCES marcas(id),

    FOREIGN KEY(proveedor_id)
        REFERENCES proveedores(id)
)
""")

# ===================================================
# VENTAS
# ===================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    subtotal REAL NOT NULL,

    descuento REAL DEFAULT 0,

    total REAL NOT NULL,

    metodo_pago TEXT NOT NULL,

    monto_recibido REAL DEFAULT 0,

    cambio REAL DEFAULT 0,

    estado TEXT DEFAULT 'COMPLETADA'
)
""")

# ===================================================
# DETALLE VENTA
# ===================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS detalle_venta(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    venta_id INTEGER NOT NULL,

    producto_codigo TEXT NOT NULL,

    producto_nombre TEXT NOT NULL,

    unidad TEXT,

    cantidad REAL NOT NULL,

    precio_unitario REAL NOT NULL,

    subtotal REAL NOT NULL,

    FOREIGN KEY(venta_id)
        REFERENCES ventas(id)
        ON DELETE CASCADE
)
""")

conexion.commit()
conexion.close()

print("========================================")
print(" BASE DE DATOS V2 CREADA CORRECTAMENTE ")
print("========================================")