import sqlite3
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # Cuando corre como EXE
    BASE_DIR = Path(sys.executable).parent
else:
    # Cuando corre con Python en desarrollo
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_FOLDER = BASE_DIR / "datos"
DB_FILE = DB_FOLDER / "abarrotes.db"


def conectar():
    """Abre y retorna una conexión a la base de datos SQLite."""
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_bd():
    """Crea las tablas necesarias si no existen y aplica migraciones."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabla Categorías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # 2. Tabla Marcas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # 3. Tabla Proveedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            telefono TEXT,
            contacto TEXT
        )
    """)

    # 4. Tabla Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            codigo_barras TEXT,
            nombre TEXT NOT NULL,

            categoria_id INTEGER,
            marca_id INTEGER,
            proveedor_id INTEGER,

            precio_compra REAL DEFAULT 0,
            precio_venta REAL NOT NULL,

            existencia REAL DEFAULT 0,
            stock_minimo REAL DEFAULT 0,

            unidad TEXT DEFAULT 'PZA',
            tipo_venta TEXT DEFAULT 'Unidad' CHECK(tipo_venta IN ('Unidad', 'Granel')),
            activo INTEGER DEFAULT 1,

            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
            FOREIGN KEY (marca_id) REFERENCES marcas(id) ON DELETE SET NULL,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
        )
    """)

    # 5. Tabla Turnos / Cajas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_apertura TEXT NOT NULL,
            fecha_cierre TEXT,
            monto_inicial REAL DEFAULT 0,
            monto_final REAL DEFAULT 0,
            monto_efectivo REAL DEFAULT 0,
            monto_tarjeta REAL DEFAULT 0,
            monto_transferencia REAL DEFAULT 0,
            total_ventas REAL DEFAULT 0,
            estado TEXT DEFAULT 'ABIERTO' CHECK(estado IN ('ABIERTO', 'CERRADO'))
        )
    """)

    # 6. Tabla Encabezado de Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            turno_id INTEGER,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            descuento REAL DEFAULT 0,
            monto_recibido REAL NOT NULL,
            cambio REAL NOT NULL,
            estatus TEXT DEFAULT 'ACTIVA',
            fecha TEXT DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (turno_id) REFERENCES turnos(id) ON DELETE SET NULL
        )
    """)

    # 7. Tabla Detalle de Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # -------------------------------------------------------------
    # MIGRACIONES AUTOMÁTICAS
    # -------------------------------------------------------------
    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN tipo_venta TEXT DEFAULT 'Unidad'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN turno_id INTEGER REFERENCES turnos(id)")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN estatus TEXT DEFAULT 'ACTIVA'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


if __name__ == "__main__":
    inicializar_bd()
    print("¡Base de datos e inicialización de tablas listas!")