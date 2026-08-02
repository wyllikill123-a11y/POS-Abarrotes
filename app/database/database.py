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

    # 4. Tabla Productos (Permite 'Unidad' o 'Granel' en tipo_venta)
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

    # -------------------------------------------------------------
    # MIGRACIÓN AUTOMÁTICA: Agregar tipo_venta si la BD ya existía
    # -------------------------------------------------------------
    try:
        cursor.execute(
            "ALTER TABLE productos ADD COLUMN tipo_venta TEXT DEFAULT 'Unidad'"
        )
    except sqlite3.OperationalError:
        # La columna 'tipo_venta' ya existe en la tabla, ignorar error.
        pass

    # 5. Tabla Encabezado de Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL,
            descuento REAL DEFAULT 0,
            monto_recibido REAL NOT NULL,
            cambio REAL NOT NULL,
            fecha TEXT DEFAULT (DATETIME('now', 'localtime'))
        )
    """)

    # 6. Tabla Detalle de Ventas
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

    conn.commit()
    conn.close()


if __name__ == "__main__":
    inicializar_bd()
    print("¡Base de datos e inicialización de tablas listas!")