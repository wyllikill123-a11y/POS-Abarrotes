import sqlite3

# Ruta centralizada de la base de datos
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
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        categoria_id=1,
        activo=1
    ):
        self.codigo = codigo
        self.codigo_barras = codigo_barras
        self.nombre = nombre
        self.unidad = unidad
        self.tipo_venta = tipo_venta
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.existencia = existencia
        self.stock_minimo = stock_minimo
        self.categoria_id = categoria_id
        self.activo = activo

    # ==========================================
    # GUARDAR PRODUCTO NUEVO
    # ==========================================
    def guardar(self):
        query = """
            INSERT INTO productos (
                codigo, codigo_barras, nombre, unidad, tipo_venta,
                precio_compra, precio_venta, existencia, stock_minimo,
                categoria_id, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, (
                self.codigo,
                self.codigo_barras,
                self.nombre,
                self.unidad,
                self.tipo_venta,
                self.precio_compra,
                self.precio_venta,
                self.existencia,
                self.stock_minimo,
                self.categoria_id,
                self.activo
            ))
            conexion.commit()

    # ==========================================
    # ACTUALIZAR PRODUCTO
    # ==========================================
    @staticmethod
    def actualizar(
        codigo_anterior,
        codigo_nuevo,
        codigo_barras,
        nombre,
        unidad,
        tipo_venta,
        precio_compra,
        precio_venta,
        existencia,
        stock_minimo,
        categoria_id=1
    ):
        query = """
            UPDATE productos
            SET
                codigo = ?,
                codigo_barras = ?,
                nombre = ?,
                unidad = ?,
                tipo_venta = ?,
                precio_compra = ?,
                precio_venta = ?,
                existencia = ?,
                stock_minimo = ?,
                categoria_id = ?,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE codigo = ?
        """

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, (
                codigo_nuevo,
                codigo_barras,
                nombre,
                unidad,
                tipo_venta,
                precio_compra,
                precio_venta,
                existencia,
                stock_minimo,
                categoria_id,
                codigo_anterior
            ))
            conexion.commit()

    # ==========================================
    # DESGLOSAR / DESEMPACAR
    # ==========================================
    @staticmethod
    def desglosar_paquete(codigo_caja, codigo_suelto, cantidad_cajas, unidades_por_caja):
        total_piezas = cantidad_cajas * unidades_por_caja

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("BEGIN TRANSACTION")
                
                cursor.execute("""
                    UPDATE productos
                    SET existencia = existencia - ?
                    WHERE codigo = ?
                """, (cantidad_cajas, codigo_caja))

                cursor.execute("""
                    UPDATE productos
                    SET existencia = existencia + ?
                    WHERE codigo = ?
                """, (total_piezas, codigo_suelto))

                conexion.commit()
            except Exception as e:
                conexion.rollback()
                raise e

    # ==========================================
    # OBTENER PRODUCTOS
    # ==========================================
    @staticmethod
    def obtener_todos(incluir_desactivados=False):
        condicion = "" if incluir_desactivados else "WHERE activo = 1"
        query = f"""
            SELECT id, codigo, codigo_barras, nombre, unidad, tipo_venta,
                   precio_compra, precio_venta, existencia, stock_minimo,
                   categoria_id, activo
            FROM productos
            {condicion}
            ORDER BY nombre
        """
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    # ==========================================
    # BUSCAR PRODUCTOS
    # ==========================================
    @staticmethod
    def buscar(texto, incluir_desactivados=False):
        filtro_activo = "" if incluir_desactivados else "AND activo = 1"
        query = f"""
            SELECT id, codigo, codigo_barras, nombre, unidad, tipo_venta,
                   precio_compra, precio_venta, existencia, stock_minimo,
                   categoria_id, activo
            FROM productos
            WHERE (codigo LIKE ? OR codigo_barras LIKE ? OR nombre LIKE ?)
            {filtro_activo}
            ORDER BY nombre
        """
        param = f"%{texto.strip()}%"
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, (param, param, param))
            return cursor.fetchall()

    @staticmethod
    def buscar_por_codigo(codigo):
        """Busca un producto por su código interno o código de barras (independiente de si está activo o no)."""
        query = """
            SELECT id, codigo, codigo_barras, nombre, unidad, tipo_venta,
                   precio_compra, precio_venta, existencia, stock_minimo,
                   categoria_id, activo
            FROM productos
            WHERE codigo = ? OR codigo_barras = ?
        """
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, (codigo, codigo))
            return cursor.fetchone()

    # ==========================================
    # CONTADORES DASHBOARD
    # ==========================================
    @staticmethod
    def contar_productos():
        query = "SELECT COUNT(*) FROM productos WHERE activo = 1"
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query)
            return cursor.fetchone()[0]

    @staticmethod
    def contar_stock_bajo():
        query = """
            SELECT COUNT(*) FROM productos 
            WHERE activo = 1 AND existencia <= stock_minimo
        """
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query)
            return cursor.fetchone()[0]

    # ==========================================
    # ESTADOS (ACTIVAR / DESACTIVAR)
    # ==========================================
    @staticmethod
    def cambiar_estado(codigo, nuevo_estado):
        """Método unificado para activar (1) o desactivar (0) un producto."""
        query = "UPDATE productos SET activo = ? WHERE codigo = ?"
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, (nuevo_estado, codigo))
            conexion.commit()

    @staticmethod
    def desactivar(codigo):
        Producto.cambiar_estado(codigo, 0)

    @staticmethod
    def reactivar(codigo):
        Producto.cambiar_estado(codigo, 1)

    # ==========================================
    # IMPORT / EXPORT EXCEL
    # ==========================================
    @staticmethod
    def obtener_todos_para_excel():
        return Producto.obtener_todos(incluir_desactivados=True)

    @staticmethod
    def importar_desde_lista(lista_productos):
        query = """
            INSERT OR REPLACE INTO productos (
                codigo, codigo_barras, nombre, unidad, tipo_venta,
                precio_compra, precio_venta, existencia, stock_minimo,
                categoria_id, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.executemany(query, lista_productos)
            conexion.commit()