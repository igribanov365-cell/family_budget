import csv
import json
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "family_budget"))

import export_data  # noqa: E402

# Своя небольшая БД для тестов, не зависит от схемы проекта
TEST_SCHEMA = """
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT
);
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
INSERT INTO users (username, password_hash) VALUES ('Папа', 'secret1'), ('Мама', 'secret2');
INSERT INTO categories (name) VALUES ('Зарплата'), ('Продукты');
INSERT INTO transactions (amount, description, user_id, category_id) VALUES
    (80000, 'Зарплата папы', 1, 1),
    (25000, 'Продукты на месяц', 2, 2),
    (5000, 'Подработка', 1, 1);
"""


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(TEST_SCHEMA)
    yield c
    c.close()


@pytest.fixture
def exported(conn, tmp_path):
    out = tmp_path / "out"  # папки ещё нет - должна создаться
    records = export_data.export_table(conn, "transactions", out)
    return out, records


def test_out_dir_and_files_created(exported):
    out, _ = exported
    for name in ("data.json", "data.csv", "data.xml", "data.yaml"):
        assert (out / name).exists()


def test_json_nested(exported):
    out, records = exported
    data = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert len(data) == len(records) == 3
    assert data[0]["user"]["username"] == "Папа"
    assert data[0]["category"]["name"] == "Зарплата"
    assert "user_id" not in data[0]


def test_sensitive_columns_not_exported(exported):
    out, _ = exported
    assert "secret" not in (out / "data.json").read_text(encoding="utf-8")


def test_csv_flat(exported):
    out, _ = exported
    with open(out / "data.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert rows[0]["user_username"] == "Папа"


def test_xml_parses(exported):
    out, _ = exported
    root = ET.parse(out / "data.xml").getroot()
    assert root.tag == "transactions"
    assert len(root.findall("transaction")) == 3
    assert root.find("transaction/user/username").text == "Папа"


def test_yaml_equals_json(exported):
    out, _ = exported
    y = yaml.safe_load((out / "data.yaml").read_text(encoding="utf-8"))
    j = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert y == j


def test_other_table_works(conn, tmp_path):
    """Универсальность: экспорт таблицы без внешних ключей."""
    records = export_data.export_table(conn, "users", tmp_path / "o")
    assert len(records) == 2 and records[0]["username"] == "Папа"
