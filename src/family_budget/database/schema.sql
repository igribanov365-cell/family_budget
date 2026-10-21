DROP TABLE IF EXISTS regular_payments;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- 1. Пользователи
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    username TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL DEFAULT 'Член семьи',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Счета (Карты, Наличные)
CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0.0,
    currency TEXT DEFAULT 'RUB',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Категории (с поддержкой подкатегорий)
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Доход', 'Расход')),
    color TEXT,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- 4. Транзакции
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    transaction_date DATETIME NOT NULL,
    payment_method TEXT DEFAULT 'Карта',
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- 5. Регулярные платежи (Подписки, аренда)
CREATE TABLE regular_payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    frequency TEXT NOT NULL CHECK(frequency IN ('Ежемесячно', 'Еженедельно')),
    next_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- --- ТЕСТОВЫЕ ДАННЫЕ ---

-- Хеши: папа (admin), мама (12345)
INSERT INTO users (login, password_hash, username, email, role) VALUES 
('papa', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Папа', 'papa@mail.ru', 'Глава семьи'),
('mama', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 'Мама', 'mama@mail.ru', 'Член семьи');

INSERT INTO accounts (user_id, name, balance) VALUES 
(1, 'Зарплатная карта', 150000.00),
(2, 'Наличные', 5000.00);

-- Родительские категории
INSERT INTO categories (category_id, name, type, color) VALUES 
(1, 'Зарплата', 'Доход', '#00FF00'),
(2, 'Продукты', 'Расход', '#FF0000'),
(3, 'Коммуналка', 'Расход', '#0000FF');

-- Подкатегории (parent_id = 2)
INSERT INTO categories (parent_id, name, type, color) VALUES 
(2, 'Мясо и рыба', 'Расход', '#FF8888'),
(2, 'Овощи и фрукты', 'Расход', '#88FF88');

INSERT INTO transactions (user_id, account_id, category_id, amount, transaction_date, payment_method, description) VALUES 
(1, 1, 1, 80000.00, '2025-10-01 10:00:00', 'Карта', 'Аванс'),
(2, 2, 4, 1500.00, '2025-10-10 18:30:00', 'Наличные', 'Купила мясо на ужин');

INSERT INTO regular_payments (user_id, category_id, amount, frequency, next_date) VALUES 
(1, 3, 5000.00, 'Ежемесячно', '2025-11-10');