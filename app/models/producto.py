import sqlite3
from pathlib import Path

import sys

if getattr(sys, 'frozen', False):
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
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO productos(
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
                    activo
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
        finally:
            conexion.close()

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
        conexion = obtener_conexion()
        try:
            # 'with conexion' maneja automáticamente el commit (o rollback si falla)
            with conexion:
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
        finally:
            # Garantiza el cierre explícito del socket/conexión
            conexion.close()

    # =====================================================
    # INVENTARIO / STOCK
    # =====================================================

    @staticmethod
    def descontar_stock(codigo, cantidad, cursor_externo=None):
        """
        Resta la cantidad vendida al stock/existencia.
        Acepta un cursor externo para ejecutarse dentro de una transacción activa.
        """
        sql = """
            UPDATE productos
            SET existencia = existencia - ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo = ?
        """
        if cursor_externo:
            cursor_externo.execute(sql, (cantidad, codigo))
        else:
            conexion = obtener_conexion()
            try:
                cursor = conexion.cursor()
                cursor.execute(sql, (cantidad, codigo))
                conexion.commit()
            finally:
                conexion.close()

    @staticmethod
    def devolver_stock(codigo, cantidad, cursor_externo=None):
        """
        Devuelve la cantidad al stock/existencia (útil para cancelaciones).
        """
        sql = """
            UPDATE productos
            SET existencia = existencia + ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo = ?
        """
        if cursor_externo:
            cursor_externo.execute(sql, (cantidad, codigo))
        else:
            conexion = obtener_conexion()
            try:
                cursor = conexion.cursor()
                cursor.execute(sql, (cantidad, codigo))
                conexion.commit()
            finally:
                conexion.close()

    # =====================================================
    # BUSCAR POR CODIGO
    # =====================================================

    @staticmethod
    def buscar_por_codigo(codigo):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT *
                FROM productos
                WHERE codigo=?
                   OR codigo_barras=?
            """,
                (codigo, codigo),
            )

            producto = cursor.fetchone()
            return producto
        finally:
            conexion.close()

    # =====================================================
    # OBTENER TODOS
    # =====================================================

    @staticmethod
    def obtener_todos(incluir_desactivados=False):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            sql = """
                SELECT 
                    p.*,
                    c.nombre AS categoria,
                    m.nombre AS marca,
                    pr.nombre AS proveedor
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
        finally:
            conexion.close()

    # =====================================================
    # BUSCAR
    # =====================================================

    @staticmethod
    def buscar(texto, incluir_desactivados=False):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            sql = """
                SELECT *
                FROM productos
                WHERE
                (
                    codigo LIKE ?
                    OR codigo_barras LIKE ?
                    OR nombre LIKE ?
                )
            """

            if not incluir_desactivados:
                sql += " AND activo=1"

            sql += " ORDER BY nombre"

            parametro = f"%{texto}%"

            cursor.execute(
                sql, (parametro, parametro, parametro)
            )

            datos = cursor.fetchall()
            return datos
        finally:
            conexion.close()

    # =====================================================
    # ACTIVAR / DESACTIVAR
    # =====================================================

    @staticmethod
    def cambiar_estado(codigo, estado):
        conexion = obtener_conexion()
        try:
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
        finally:
            conexion.close()

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
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE activo=1
            """)

            total = cursor.fetchone()[0]
            return total
        finally:
            conexion.close()

    @staticmethod
    def contar_stock_bajo():
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE activo=1
                AND existencia<=stock_minimo
            """)

            total = cursor.fetchone()[0]
            return total
        finally:
            conexion.close()

    # =====================================================
    # EXPORTAR / IMPORTAR
    # =====================================================

    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(True)

    @staticmethod
    def importar_desde_lista(lista):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            cursor.executemany(
                """
                INSERT OR REPLACE INTO productos(
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
                    activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                lista,
            )

            conexion.commit()
        finally:
            conexion.close()