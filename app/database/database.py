import sqlite3
from pathlib import Path

# Carpeta donde está instalado el programa
BASE_DIR = Path(__file__).resolve().parent

DB_FOLDER = BASE_DIR
DB_FILE = DB_FOLDER / "abarrotes.db"

def conectar():
    """Abre y retorna una conexión a la base de datos SQLite."""
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

def inicializar_bd():
    """Crea las tablas necesarias si no existen."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabla de Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            precio_venta REAL NOT NULL,
            stock REAL DEFAULT 0,
            unidad TEXT DEFAULT 'PZA',
            activo INTEGER DEFAULT 1
        )
    """)

    # 2. Tabla Encabezado de Ventas
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

    # 3. Tabla Detalle de Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.commit()
    conn.close()

# Ejecutar inicialización si se ejecuta directamente este archivo
if __name__ == "__main__":
    inicializar_bd()
    print("¡Base de datos e inicialización de tablas listas!")