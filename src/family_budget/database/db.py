import sqlite3
import os
import hashlib

# Пути к файлам (база данных создастся в этой же папке)
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'family_budget.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')


def init_db():
    """Создает базу данных и таблицы из файла schema.sql."""
    # Если хочешь удалять базу при каждом запуске для теста, раскомментируй строку ниже:
    # if os.path.exists(DB_PATH): os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("База данных успешно инициализирована (таблицы созданы, данные добавлены).")
    except sqlite3.Error as e:
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        conn.close()


def hash_password(password):
    """Хеширует пароль (SHA-256)."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(login, password, username, email, role='Член семьи'):
    """Регистрирует нового пользователя."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        p_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (login, password_hash, username, email, role) VALUES (?, ?, ?, ?, ?)",
            (login, p_hash, username, email, role)
        )
        conn.commit()
        print(f"Пользователь '{username}' успешно зарегистрирован!")
        return True
    except sqlite3.IntegrityError:
        print(f"Ошибка: Логин '{login}' уже занят!")
        return False
    finally:
        conn.close()


def authenticate_user(login, password):
    """Проверяет логин и пароль."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    p_hash = hash_password(password)
    
    cursor.execute(
        "SELECT user_id, username, role FROM users WHERE login = ? AND password_hash = ?",
        (login, p_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"Успешный вход! Добро пожаловать, {user[1]} (Роль: {user[2]}).")
        return user
    else:
        print("Неверный логин или пароль.")
        return None


def get_all_transactions():
    """Возвращает список всех транзакций с расшифровкой (JOIN)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            t.transaction_date, 
            u.username, 
            a.name AS account_name,
            c.name AS category, 
            c.type,
            t.amount, 
            t.description
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        JOIN accounts a ON t.account_id = a.account_id
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.transaction_date DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return rows