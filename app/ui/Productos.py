import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "abarrotes.db"


def obtener_conexion():
    conexion = sqlite3.connect(
        DB_PATH, timeout=30, check_same_thread=False
    )
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA journal_mode=WAL")
    return conexion


class Producto:

    def __init__(
        self,
        codigo,
        codigo_barras,
        nombre,
        categoria_id,
        marca_id,
        proveedor_id,
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        activo=1,
    ):
        self.codigo = codigo
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.categoria_id = categoria_id
        self.marca_id = marca_id
        self.proveedor_id = proveedor_id
        self.unidad = unidad
        self.tipo_venta = tipo_venta
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.existencia = existencia
        self.stock_minimo = stock_minimo
        self.activo = activo

    # =====================================================
    # GUARDAR
    # =====================================================
    def guardar(self):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO productos(
                    codigo, codigo_barras, nombre, categoria_id, marca_id,
                    proveedor_id, unidad, tipo_venta, precio_compra,
                    precio_venta, existencia, stock_minimo, activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    self.codigo,
                    self.codigo_barras,
                    self.nombre,
                    self.categoria_id,
                    self.marca_id,
                    self.proveedor_id,
                    self.unidad,
                    self.tipo_venta,
                    self.precio_compra,
                    self.precio_venta,
                    self.existencia,
                    self.stock_minimo,
                    self.activo,
                ),
            )
            conexion.commit()

    # =====================================================
    # ACTUALIZAR
    # =====================================================
    @staticmethod
    def actualizar(
        codigo_original,
        codigo,
        codigo_barras,
        nombre,
        categoria_id,
        marca_id,
        proveedor_id,
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        activo=1,
    ):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE productos
                SET
                    codigo=?,
                    codigo_barras=?,
                    nombre=?,
                    categoria_id=?,
                    marca_id=?,
                    proveedor_id=?,
                    unidad=?,
                    tipo_venta=?,
                    precio_compra=?,
                    precio_venta=?,
                    existencia=?,
                    stock_minimo=?,
                    activo=?,
                    fecha_actualizacion=CURRENT_TIMESTAMP
                WHERE codigo=?
            """,
                (
                    codigo,
                    codigo_barras,
                    nombre,
                    categoria_id,
                    marca_id,
                    proveedor_id,
                    unidad,
                    tipo_venta,
                    precio_compra,
                    precio_venta,
                    existencia,
                    stock_minimo,
                    activo,
                    codigo_original,
                ),
            )
            conexion.commit()

    # =====================================================
    # INVENTARIO / STOCK
    # =====================================================
    @staticmethod
    def descontar_stock(codigo, cantidad, cursor_externo=None):
        sql = """
            UPDATE productos
            SET existencia = existencia - ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo = ?
        """
        if cursor_externo:
            cursor_externo.execute(sql, (cantidad, codigo))
        else:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()
                cursor.execute(sql, (cantidad, codigo))
                conexion.commit()

    @staticmethod
    def devolver_stock(codigo, cantidad, cursor_externo=None):
        sql = """
            UPDATE productos
            SET existencia = existencia + ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo = ?
        """
        if cursor_externo:
            cursor_externo.execute(sql, (cantidad, codigo))
        else:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()
                cursor.execute(sql, (cantidad, codigo))
                conexion.commit()

    # =====================================================
    # BUSCAR POR CODIGO
    # =====================================================
    @staticmethod
    def buscar_por_codigo(codigo):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    p.*,
                    COALESCE(c.nombre, 'Sin Categoria') AS categoria_nombre,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre,
                    COALESCE(pr.nombre, 'Sin Proveedor') AS proveedor_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN marcas m ON p.marca_id = m.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                WHERE p.codigo=? OR p.codigo_barras=?
            """,
                (codigo, codigo),
            )
            return cursor.fetchone()

    # =====================================================
    # OBTENER TODOS (CON NOMBRES DE CATEGORÍA, MARCA Y PROVEEDOR)
    # =====================================================
    @staticmethod
    def obtener_todos(incluir_desactivados=False):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            sql = """
                SELECT 
                    p.*,
                    COALESCE(c.nombre, 'Sin Categoria') AS categoria_nombre,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre,
                    COALESCE(pr.nombre, 'Sin Proveedor') AS proveedor_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN marcas m ON p.marca_id = m.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            """

            if not incluir_desactivados:
                sql += " WHERE p.activo=1"

            sql += " ORDER BY p.nombre"

            cursor.execute(sql)
            return cursor.fetchall()

    # =====================================================
    # BUSCAR
    # =====================================================
    @staticmethod
    def buscar(texto, incluir_desactivados=False):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            sql = """
                SELECT 
                    p.*,
                    COALESCE(c.nombre, 'Sin Categoria') AS categoria_nombre,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre,
                    COALESCE(pr.nombre, 'Sin Proveedor') AS proveedor_nombre
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN marcas m ON p.marca_id = m.id
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                WHERE (
                    p.codigo LIKE ?
                    OR p.codigo_barras LIKE ?
                    OR p.nombre LIKE ?
                    OR c.nombre LIKE ?
                    OR m.nombre LIKE ?
                )
            """

            if not incluir_desactivados:
                sql += " AND p.activo=1"

            sql += " ORDER BY p.nombre"

            parametro = f"%{texto}%"
            cursor.execute(sql, (parametro, parametro, parametro, parametro, parametro))
            return cursor.fetchall()

    # =====================================================
    # ACTIVAR / DESACTIVAR
    # =====================================================
    @staticmethod
    def cambiar_estado(codigo, estado):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE productos
                SET activo=?
                WHERE codigo=?
            """,
                (estado, codigo),
            )
            conexion.commit()

    @staticmethod
    def desactivar(codigo):
        Producto.cambiar_estado(codigo, 0)

    @staticmethod
    def reactivar(codigo):
        Producto.cambiar_estado(codigo, 1)

    # =====================================================
    # CONTADORES
    # =====================================================
    @staticmethod
    def contar_productos():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM productos WHERE activo=1
            """)
            return cursor.fetchone()[0]

    @staticmethod
    def contar_stock_bajo():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM productos
                WHERE activo=1 AND existencia<=stock_minimo
            """)
            return cursor.fetchone()[0]

    # =====================================================
    # EXPORTAR / IMPORTAR
    # =====================================================
    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(True)

    @staticmethod
    def importar_desde_lista(lista):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO productos(
                    codigo, codigo_barras, nombre, categoria_id, marca_id,
                    proveedor_id, unidad, tipo_venta, precio_compra,
                    precio_venta, existencia, stock_minimo, activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                lista,
            )
            conexion.commit()

    @staticmethod
    def existe_codigo(codigo):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT 1
                FROM productos
                WHERE codigo=?
                """,
                (codigo,),
            )

            return cursor.fetchone() is not None  
            