from database.database import get_connection
from models.category import Category

_SELECT = """
    SELECT c.category_id, c.parent_id, c.name, c.type, c.color, p.name
    FROM categories c
    LEFT JOIN categories p ON p.category_id = c.parent_id
"""


def _map(row) -> Category:
    return Category(*row)


def create(parent_id: int | None, name: str, type_: str, color: str | None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO categories(parent_id, name, type, color) VALUES (?, ?, ?, ?)",
        (parent_id, name, type_, color),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(category_id: int) -> Category | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE c.category_id = ?", (category_id,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[Category]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " ORDER BY c.type, COALESCE(c.parent_id, c.category_id), c.parent_id IS NOT NULL, c.name")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(category_id: int, parent_id: int | None, name: str,
           type_: str, color: str | None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE categories
        SET parent_id = ?, name = ?, type = ?, color = ?
        WHERE category_id = ?
    """, (parent_id, name, type_, color, category_id))
    conn.commit()
    conn.close()


def delete(category_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
    conn.commit()
    conn.close()


def count_usage(category_id: int) -> int:
    """Сколько записей (транзакции, регулярные платежи, подкатегории) ссылаются на категорию."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT (SELECT COUNT(*) FROM transactions WHERE category_id = ?)
             + (SELECT COUNT(*) FROM regular_payments WHERE category_id = ?)
             + (SELECT COUNT(*) FROM categories WHERE parent_id = ?)
    """, (category_id, category_id, category_id))
    count = cur.fetchone()[0]
    conn.close()
    return count
