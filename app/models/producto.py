import sqlite3


class Producto:

    def __init__(
        self,
        codigo,
        nombre,
        unidad,
        precio_compra,
        precio_venta,
        existencia
    ):

        self.codigo = codigo
        self.nombre = nombre
        self.unidad = unidad
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.existencia = existencia

    def guardar(self):

        conexion = sqlite3.connect("app/database/abarrotes.db")

        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO productos(
                codigo,
                nombre,
                unidad,
                precio_compra,
                precio_venta,
                existencia
            )
            VALUES(?,?,?,?,?,?)
        """, (
            self.codigo,
            self.nombre,
            self.unidad,
            self.precio_compra,
            self.precio_venta,
            self.existencia
        ))

        conexion.commit()
        conexion.close()

    @staticmethod
    def obtener_todos():

        conexion = sqlite3.connect("app/database/abarrotes.db")

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                codigo,
                nombre,
                unidad,
                precio_compra,
                precio_venta,
                existencia
            FROM productos
            ORDER BY nombre
        """)

        productos = cursor.fetchall()

        conexion.close()

        return productos

    @staticmethod
    def buscar_por_codigo(codigo):

        conexion = sqlite3.connect("app/database/abarrotes.db")

        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                codigo,
                nombre,
                unidad,
                precio_compra,
                precio_venta,
                existencia
            FROM productos
            WHERE codigo = ?
        """, (codigo,))

        producto = cursor.fetchone()

        conexion.close()

        return producto
    
    def actualizar(self):

        conexion = sqlite3.connect("app/database/abarrotes.db")

        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET
                nombre = ?,
                unidad = ?,
                precio_compra = ?,
                precio_venta = ?,
                existencia = ?
            WHERE codigo = ?
        """, (
            self.nombre,
            self.unidad,
            self.precio_compra,
            self.precio_venta,
            self.existencia,
            self.codigo
        ))

        conexion.commit()
        conexion.close()