import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "abarrotes.db"


def obtener_conexion():
    conexion = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False,
    )

    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.execute("PRAGMA journal_mode=WAL")

    return conexion


class Proveedor:

    @staticmethod
    def obtener_todos():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM proveedores
                ORDER BY nombre
            """)

            return cursor.fetchall()

    @staticmethod
    def obtener_por_id(id_proveedor):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM proveedores
                WHERE id=?
            """, (id_proveedor,))

            return cursor.fetchone()

    @staticmethod
    def agregar(nombre, telefono="", contacto=""):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO proveedores(
                    nombre,
                    telefono,
                    contacto
                )
                VALUES(?,?,?)
            """, (
                nombre,
                telefono,
                contacto,
            ))

            conexion.commit()

    @staticmethod
    def actualizar(
        id_proveedor,
        nombre,
        telefono,
        contacto,
    ):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE proveedores
                SET
                    nombre=?,
                    telefono=?,
                    contacto=?
                WHERE id=?
            """, (
                nombre,
                telefono,
                contacto,
                id_proveedor,
            ))

            conexion.commit()

    @staticmethod
    def eliminar(id_proveedor):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                DELETE FROM proveedores
                WHERE id=?
            """, (id_proveedor,))

            conexion.commit()
    @classmethod
    def buscar(cls, termino=""):
        """Busca proveedores por nombre que coincidan con el término."""
        if not termino:
            return cls.obtener_todos()
        
        # Ajusta esta consulta según la estructura de tu BD/ORM
        sql = "SELECT id, nombre FROM proveedores WHERE nombre LIKE ? ORDER BY nombre ASC"
        # Supongamos que usas tu manejador de BD (ej. Database.ejecutar_consulta):
        # return Database.ejecutar_consulta(sql, (f"%{termino}%",))