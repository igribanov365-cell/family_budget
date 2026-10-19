import sqlite3
import os

DB_NAME = "family_budget.db"
# Путь к файлу schema.sql (он лежит в корне проекта, на 2 уровня выше)
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "schema.sql")

def init_db():
    """Создает базу данных и таблицы на основе schema.sql"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Читаем SQL скрипт
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Выполняем скрипт
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("✅ База данных успешно создана и заполнена!")

def get_report_data():
    """Получает все транзакции с расшифровкой категорий и имен"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
    SELECT t.transaction_date, u.username, c.name, c.type, t.amount
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    JOIN categories c ON t.category_id = c.category_id
    ORDER BY t.transaction_date;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result