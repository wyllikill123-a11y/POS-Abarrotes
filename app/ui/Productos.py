import sqlite3
import sys
from pathlib import Path

# Configuración de ruta base
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "datos" / "abarrotes.db"


def obtener_conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        marca_id,
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        activo=1,
    ):
        self.codigo = str(codigo).strip()
        self.codigo_barras = (
            str(codigo_barras).strip() if codigo_barras else ""
        )
        self.nombre = str(nombre).strip()
        self.marca_id = marca_id
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
        if Producto.existe_codigo(self.codigo):
            raise ValueError(
                f"Ya existe un producto registrado con el código '{self.codigo}'."
            )

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO productos(
                    codigo, codigo_barras, nombre, marca_id,
                    unidad, tipo_venta, precio_compra,
                    precio_venta, existencia, stock_minimo, activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    self.codigo,
                    self.codigo_barras,
                    self.nombre,
                    self.marca_id,
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
        marca_id,
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        activo=1,
    ):
        codigo = str(codigo).strip()
        codigo_original = str(codigo_original).strip()

        # Si cambió el código, verificar que el nuevo no exista en otro producto
        if codigo != codigo_original and Producto.existe_codigo(codigo):
            raise ValueError(
                f"El nuevo código '{codigo}' ya pertenece a otro producto."
            )

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                UPDATE productos
                SET
                    codigo=?,
                    codigo_barras=?,
                    nombre=?,
                    marca_id=?,
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
                    str(codigo_barras).strip() if codigo_barras else "",
                    str(nombre).strip(),
                    marca_id,
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
    # BUSCAR POR CODIGO O CODIGO DE BARRAS
    # =====================================================
    @staticmethod
    def buscar_por_codigo(codigo):
        codigo = str(codigo).strip()
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT 
                    p.*,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre
                FROM productos p
                LEFT JOIN marcas m ON p.marca_id = m.id
                WHERE p.codigo=? OR p.codigo_barras=?
            """,
                (codigo, codigo),
            )
            return cursor.fetchone()

    # =====================================================
    # OBTENER TODOS
    # =====================================================
    @staticmethod
    def obtener_todos(incluir_desactivados=False):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            sql = """
                SELECT 
                    p.*,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre
                FROM productos p
                LEFT JOIN marcas m ON p.marca_id = m.id
            """

            if not incluir_desactivados:
                sql += " WHERE p.activo=1"

            sql += " ORDER BY p.nombre"

            cursor.execute(sql)
            return cursor.fetchall()

    # =====================================================
    # BUSCAR POR TEXTO
    # =====================================================
    @staticmethod
    def buscar(texto, incluir_desactivados=False):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            sql = """
                SELECT 
                    p.*,
                    COALESCE(m.nombre, 'Sin Marca') AS marca_nombre
                FROM productos p
                LEFT JOIN marcas m ON p.marca_id = m.id
                WHERE (
                    p.codigo LIKE ?
                    OR p.codigo_barras LIKE ?
                    OR p.nombre LIKE ?
                    OR m.nombre LIKE ?
                )
            """

            if not incluir_desactivados:
                sql += " AND p.activo=1"

            sql += " ORDER BY p.nombre"

            parametro = f"%{texto.strip()}%"
            cursor.execute(
                sql, (parametro, parametro, parametro, parametro)
            )
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
    # EXPORTAR / IMPORTAR / VALIDACIONES
    # =====================================================
    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(incluir_desactivados=True)

    @staticmethod
    def importar_desde_lista(lista):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO productos(
                    codigo, codigo_barras, nombre, marca_id,
                    unidad, tipo_venta, precio_compra,
                    precio_venta, existencia, stock_minimo, activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
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
                (str(codigo).strip(),),
            )

            return cursor.fetchone() is not None