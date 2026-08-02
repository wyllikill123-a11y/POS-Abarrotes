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

    conexion = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
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

    # ==========================================================
    # BUSCAR POR NOMBRE
    # ==========================================================
    @staticmethod
    def buscar(termino=""):
        """Busca marcas por coincidencia en el nombre."""
        termino_like = f"%{termino.strip()}%"

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT *
                FROM marcas
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
                FROM marcas
                WHERE UPPER(nombre)=UPPER(?)
            """, (nombre,))

            if cursor.fetchone():
                raise ValueError("Ya existe una marca con ese nombre.")

            cursor.execute("""
                INSERT INTO marcas(nombre)
                VALUES(?)
            """, (nombre,))

            conexion.commit()

    @staticmethod
    def actualizar(id_marca, nombre):
        nombre = nombre.strip()

        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id
                FROM marcas
                WHERE UPPER(nombre)=UPPER(?)
                AND id<>?
            """, (nombre, id_marca))

            if cursor.fetchone():
                raise ValueError("Ya existe una marca con ese nombre.")

            cursor.execute("""
                UPDATE marcas
                SET nombre=?
                WHERE id=?
            """, (nombre, id_marca))

            conexion.commit()

    @staticmethod
    def eliminar(id_marca):
        try:
            with obtener_conexion() as conexion:
                cursor = conexion.cursor()

                cursor.execute("""
                    DELETE FROM marcas
                    WHERE id=?
                """, (id_marca,))

                conexion.commit()

        except sqlite3.IntegrityError:
            raise ValueError(
                "No se puede eliminar la marca porque está siendo utilizada por uno o más productos."
            )