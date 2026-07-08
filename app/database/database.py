import sqlite3
from pathlib import Path

DB_FOLDER = Path("app/database")
DB_FILE = DB_FOLDER / "abarrotes.db"

def conectar():
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_FILE)