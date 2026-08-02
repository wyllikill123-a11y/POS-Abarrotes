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


class Marca:

    @staticmethod
    def obtener_todas():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM marcas
                ORDER BY nombre
            """)

            return cursor.fetchall()

    @staticmethod
    def obtener_por_id(id_marca):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM marcas
                WHERE id=?
            """, (id_marca,))

            return cursor.fetchone()

    @staticmethod
    def agregar(nombre):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO marcas(nombre)
                VALUES(?)
            """, (nombre,))

            conexion.commit()

    @staticmethod
    def actualizar(id_marca, nombre):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE marcas
                SET nombre=?
                WHERE id=?
            """, (nombre, id_marca))

            conexion.commit()

    @staticmethod
    def eliminar(id_marca):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                DELETE FROM marcas
                WHERE id=?
            """, (id_marca,))

            conexion.commit()
    @classmethod
    def buscar(cls, termino=""):
        """Busca marcas por nombre que coincidan con el término."""
        if not termino:
            return cls.obtener_todas()

        sql = "SELECT id, nombre FROM marcas WHERE nombre LIKE ? ORDER BY nombre ASC"
        # Ajusta según la forma en que tu modelo ejecuta las consultas