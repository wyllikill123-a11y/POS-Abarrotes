import sqlite3

DB_PATH = "app/database/abarrotes.db"


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
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
        activo=1
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
        cursor = conexion.cursor()

        cursor.execute("""
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
        """, (
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
            self.activo
        ))

        conexion.commit()
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
        activo=1
    ):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
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
        """, (
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
            codigo_original
        ))

        conexion.commit()
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
            cursor = conexion.cursor()
            cursor.execute(sql, (cantidad, codigo))
            conexion.commit()
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
            cursor = conexion.cursor()
            cursor.execute(sql, (cantidad, codigo))
            conexion.commit()
            conexion.close()

    # =====================================================
    # BUSCAR POR CODIGO
    # =====================================================

    @staticmethod
    def buscar_por_codigo(codigo):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT *
            FROM productos
            WHERE codigo=?
               OR codigo_barras=?
        """, (codigo, codigo))

        producto = cursor.fetchone()
        conexion.close()

        return producto

    # =====================================================
    # OBTENER TODOS
    # =====================================================

    @staticmethod
    def obtener_todos(incluir_desactivados=False):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
            SELECT *
            FROM productos
        """

        if not incluir_desactivados:
            sql += " WHERE activo=1"

        sql += " ORDER BY nombre"

        cursor.execute(sql)
        datos = cursor.fetchall()
        conexion.close()

        return datos

    # =====================================================
    # BUSCAR
    # =====================================================

    @staticmethod
    def buscar(texto, incluir_desactivados=False):
        conexion = obtener_conexion()
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

        cursor.execute(sql, (
            parametro,
            parametro,
            parametro
        ))

        datos = cursor.fetchall()
        conexion.close()

        return datos

    # =====================================================
    # ACTIVAR / DESACTIVAR
    # =====================================================

    @staticmethod
    def cambiar_estado(codigo, estado):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET activo=?
            WHERE codigo=?
        """, (
            estado,
            codigo
        ))

        conexion.commit()
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
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM productos
            WHERE activo=1
        """)

        total = cursor.fetchone()[0]
        conexion.close()

        return total

    @staticmethod
    def contar_stock_bajo():
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM productos
            WHERE activo=1
            AND existencia<=stock_minimo
        """)

        total = cursor.fetchone()[0]
        conexion.close()

        return total

    # =====================================================
    # EXPORTAR / IMPORTAR
    # =====================================================

    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(True)

    @staticmethod
    def importar_desde_lista(lista):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.executemany("""
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
        """, lista)

        conexion.commit()
        conexion.close()