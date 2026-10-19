-- Удаляем старые таблицы в правильном порядке (сначала зависимые)
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- 1. Таблица пользователей
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Глава', 'Член семьи'))
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

-- Добавляем тестовых пользователей
INSERT INTO users (username, role) VALUES
('Папа', 'Глава'),
('Мама', 'Член семьи'),
('Сын', 'Член семьи');

-- Добавляем тестовые категории
INSERT INTO categories (name, type) VALUES
('Зарплата', 'Доход'),
('Пособие', 'Доход'),
('Продукты', 'Расход'),
('Коммунальные услуги', 'Расход'),
('Развлечения', 'Расход');

-- Добавляем тестовые транзакции
INSERT INTO transactions (amount, transaction_date, description, user_id, category_id) VALUES
(80000, '2023-10-01', 'Зарплата папы', 1, 1),
(65000, '2023-10-01', 'Зарплата мамы', 2, 1),
(12000, '2023-10-05', 'Пособие на ребенка', 2, 2),
(25000, '2023-10-06', 'Продукты на месяц', 2, 3),
(8000, '2023-10-10', 'Коммуналка', 1, 4),
(5000, '2023-10-15', 'Поход в кино', 3, 5);