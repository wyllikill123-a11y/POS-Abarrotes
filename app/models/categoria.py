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


class Categoria:

    @staticmethod
    def obtener_todas():
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM categorias
                ORDER BY nombre
            """)

            return cursor.fetchall()

    @staticmethod
    def obtener_por_id(id_categoria):
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM categorias
                WHERE id=?
            """, (id_categoria,))

            return cursor.fetchone()

    # ==========================================================
    # NUEVO MÉTODO: BUSCAR POR NOMBRE
    # ==========================================================
    @staticmethod
    def buscar(nombre=""):
        """Busca categorías por coincidencia en el nombre."""
        termino_like = f"%{nombre.strip()}%"

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM categorias
                WHERE nombre LIKE ?
                ORDER BY nombre ASC
            """, (termino_like,))

            return cursor.fetchall()

    @staticmethod
    def agregar(nombre):
        nombre = nombre.strip()

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id
                FROM categorias
                WHERE UPPER(nombre)=UPPER(?)
            """, (nombre,))

            if cursor.fetchone():
                raise ValueError("Ya existe una categoría con ese nombre.")

            cursor.execute("""
                INSERT INTO categorias(nombre)
                VALUES(?)
            """, (nombre,))

            conexion.commit()

    @staticmethod
    def actualizar(id_categoria, nombre):
        nombre = nombre.strip()

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id
                FROM categorias
                WHERE UPPER(nombre)=UPPER(?)
                AND id<>?
            """, (nombre, id_categoria))

            if cursor.fetchone():
                raise ValueError("Ya existe una categoría con ese nombre.")

            cursor.execute("""
                UPDATE categorias
                SET nombre=?
                WHERE id=?
            """, (nombre, id_categoria))

            conexion.commit()

    @staticmethod
    def eliminar(id_categoria):
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute("""
                    DELETE FROM categorias
                    WHERE id=?
                """, (id_categoria,))

                conexion.commit()

        except sqlite3.IntegrityError:
            raise ValueError(
                "No se puede eliminar la categoría porque está siendo utilizada por uno o más productos."
            )