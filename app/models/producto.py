import sqlite3
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "datos" / "abarrotes.db"


def obtener_conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
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
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        tipo_venta="Unidad",
        activo=1,
    ):
        self.codigo = codigo
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.marca_id = marca_id
        self.unidad = unidad
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.existencia = existencia
        self.stock_minimo = stock_minimo
        self.tipo_venta = tipo_venta
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
                    marca_id,
                    unidad,
                    precio_compra,
                    precio_venta,
                    existencia,
                    stock_minimo,
                    tipo_venta,
                    activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    self.codigo,
                    self.codigo_barras,
                    self.nombre,
                    self.marca_id,
                    self.unidad,
                    self.precio_compra,
                    self.precio_venta,
                    self.existencia,
                    self.stock_minimo,
                    self.tipo_venta,
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
        marca_id,
        unidad,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        tipo_venta="Unidad",
        activo=1,
    ):
        conexion = obtener_conexion()
        try:
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
                    precio_compra=?,
                    precio_venta=?,
                    existencia=?,
                    stock_minimo=?,
                    tipo_venta=?,
                    activo=?
                WHERE codigo=?
            """,
                (
                    codigo,
                    codigo_barras,
                    nombre,
                    marca_id,
                    unidad,
                    precio_compra,
                    precio_venta,
                    existencia,
                    stock_minimo,
                    tipo_venta,
                    activo,
                    codigo_original,
                ),
            )
            conexion.commit()
        finally:
            conexion.close()

    # =====================================================
    # INVENTARIO / STOCK
    # =====================================================

    @staticmethod
    def descontar_stock(codigo, cantidad, cursor_externo=None):
        sql = """
            UPDATE productos
            SET existencia = existencia - ?
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
        sql = """
            UPDATE productos
            SET existencia = existencia + ?
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
            return cursor.fetchone()
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
                    p.codigo,
                    p.codigo_barras,
                    p.nombre,
                    p.marca_id,
                    m.nombre AS marca,
                    p.unidad,
                    p.tipo_venta,
                    p.precio_compra,
                    p.precio_venta,
                    p.existencia,
                    p.stock_minimo,
                    p.activo
                FROM productos p
                LEFT JOIN marcas m ON p.marca_id = m.id
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
            cursor.execute(sql, (parametro, parametro, parametro))
            return cursor.fetchall()
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
            return cursor.fetchone()[0]
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
            return cursor.fetchone()[0]
        finally:
            conexion.close()

    # =====================================================
    # HELPER DE MARCAS (SANEAMIENTO DE LLAVE FORÁNEA)
    # =====================================================

    @staticmethod
    def obtener_o_crear_marca_id(cursor, marca_val):
        """Verifica si la marca existe. Si viene vacía o el ID no existe en la BD,

        crea o retorna una marca válida para evitar 'FOREIGN KEY constraint failed'.
        """
        # Caso 1: Viene un entero/ID válido desde el Excel
        if isinstance(marca_val, int) or (
            isinstance(marca_val, float) and marca_val.is_integer()
        ):
            marca_id = int(marca_val)
            cursor.execute("SELECT id FROM marcas WHERE id=?", (marca_id,))
            res = cursor.fetchone()
            if res:
                return marca_id

        # Caso 2: Viene un texto con el nombre de la marca o un ID inválido
        nombre_marca = str(marca_val).strip() if marca_val else "GENERAL"
        if not nombre_marca or nombre_marca in ["0", "None", "nan"]:
            nombre_marca = "GENERAL"

        cursor.execute(
            "SELECT id FROM marcas WHERE UPPER(nombre)=?", (nombre_marca.upper(),)
        )
        res = cursor.fetchone()

        if res:
            return res[0]
        else:
            cursor.execute("INSERT INTO marcas (nombre) VALUES (?)", (nombre_marca,))
            return cursor.lastrowid

    # =====================================================
    # EXPORTAR / IMPORTAR
    # =====================================================

    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(True)

    @staticmethod
    def importar_desde_lista(lista):
        """Importa productos desde una lista procesada desde Excel.

        Sanitiza la marca_id para evitar errores de Foreign Key.
        """
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()

            # Procesamiento fila por fila asegurando llaves foráneas válidas
            lista_saneada = []
            for fila in lista:
                fila_m = list(fila)
                # La posición 3 corresponde a 'marca_id'
                fila_m[3] = Producto.obtener_o_crear_marca_id(cursor, fila_m[3])
                lista_saneada.append(fila_m)

            cursor.executemany(
                """
                INSERT OR REPLACE INTO productos(
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
                    activo
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
                lista_saneada,
            )
            conexion.commit()
        finally:
            conexion.close()