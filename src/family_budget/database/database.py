import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# schema.sql лежит в корне репозитория: src/family_budget/database -> ../../../schema.sql
SCHEMA_PATH = BASE_DIR.parent.parent / "schema.sql"


def _db_path() -> str:
    # путь можно переопределить переменной окружения (используется в тестах)
    return os.environ.get("FAMILY_BUDGET_DB", str(BASE_DIR / "family_budget.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force: bool = False) -> None:
    """Создаёт БД из schema.sql, если её ещё нет (или force=True)."""
    if not force and os.path.exists(_db_path()):
        return
    conn = get_connection()
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
