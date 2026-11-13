-- Удаляем старые таблицы в правильном порядке (сначала зависимые)
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- 1. Таблица пользователей (добавлены login и password_hash для авторизации)
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Глава', 'Член семьи')),
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- 2. Таблица категорий
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Доход', 'Расход'))
);

-- 3. Таблица транзакций (связана с users и categories)
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    transaction_date TEXT NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Тестовые пользователи (пароль у всех: 1234)
INSERT INTO users (username, role, login, password_hash) VALUES
('Папа', 'Глава', 'papa', 'a1b2c3d4e5f60718$c2d089e84e1c931b27cfd1d36aee13912a02460404d0a7a5d0aeda75b946287e'),
('Мама', 'Член семьи', 'mama', '0f1e2d3c4b5a6978$285ca590cf4ef757163e92b5228450ab8a439cb0f8fa10018543c7b5196d839b'),
('Сын', 'Член семьи', 'son', '1122334455667788$286eb6cda9bcda66eb2499be4bb94c44c19f4cc505d42cb7a70b7270c5da632b');

-- Тестовые категории
INSERT INTO categories (name, type) VALUES
('Зарплата', 'Доход'),
('Пособие', 'Доход'),
('Продукты', 'Расход'),
('Коммунальные услуги', 'Расход'),
('Развлечения', 'Расход');

-- Тестовые транзакции
INSERT INTO transactions (amount, transaction_date, description, user_id, category_id) VALUES
(80000, '2023-10-01', 'Зарплата папы', 1, 1),
(65000, '2023-10-01', 'Зарплата мамы', 2, 1),
(12000, '2023-10-05', 'Пособие на ребенка', 2, 2),
(25000, '2023-10-06', 'Продукты на месяц', 2, 3),
(8000, '2023-10-10', 'Коммуналка', 1, 4),
(5000, '2023-10-15', 'Поход в кино', 3, 5);
