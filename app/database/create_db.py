import sqlite3

# Ruta centralizada
DB_PATH = "app/database/abarrotes.db"

conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# Activar soporte de claves foráneas en SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

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
    tipo_venta TEXT DEFAULT 'PIEZA',
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,
    existencia REAL DEFAULT 0,
    stock_minimo REAL DEFAULT 0,
    activo INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
    FOREIGN KEY(marca_id) REFERENCES marcas(id) ON DELETE SET NULL,
    FOREIGN KEY(proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
)
""")

# ==========================
# TABLA VENTAS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    subtotal REAL NOT NULL,
    descuento REAL DEFAULT 0,
    total REAL NOT NULL,
    metodo_pago TEXT DEFAULT 'EFECTIVO',
    estado TEXT DEFAULT 'COMPLETADA'
)
""")

# ==========================
# DETALLE DE VENTA
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS detalle_venta(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_codigo TEXT NOT NULL,
    producto_nombre TEXT NOT NULL,
    cantidad REAL NOT NULL,
    unidad TEXT NOT NULL,
    precio_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_codigo) REFERENCES productos(codigo) ON DELETE RESTRICT
)
""")

conexion.commit()
conexion.close()

print("Base de datos creada y configurada correctamente.")