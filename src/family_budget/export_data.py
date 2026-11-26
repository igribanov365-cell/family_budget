"""Лабораторная работа №5. Форматы данных: JSON, CSV, XML, YAML.

Скрипт извлекает все записи выбранной таблицы из БД проекта (SQLite) и сохраняет их
в папку out/ в четырёх форматах: data.json, data.csv, data.xml, data.yaml.

Код универсальный: связи (внешние ключи) таблицы определяются автоматически
через PRAGMA foreign_key_list, JOIN-запрос строится динамически, связанные
данные вкладываются во вложенные объекты (JSON, XML, YAML) или «разворачиваются»
в одну строку (CSV). Чтобы экспортировать другую таблицу, достаточно изменить
параметр TABLE_NAME (или передать его аргументом командной строки).

Запуск:
    cd src/family_budget
    python export_data.py [имя_таблицы]
"""

import csv
import json
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
OUT_DIR = PROJECT_ROOT / "out"

TABLE_NAME = "transactions"

# Колонки, в имени которых есть эти слова, в файлы не попадают (пароли и т.п.)
SENSITIVE_WORDS = ("password", "passwd", "pwd", "hash", "salt", "token")


# ---------------------------------------------------------------------------
# Работа с базой данных
# ---------------------------------------------------------------------------
def open_project_db():
    """Открывает реальную БД проекта (database/database.py) с row_factory=Row."""
    from database.database import get_connection, init_db

    init_db()  # создаёт БД из schema.sql, если её ещё нет
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn


def get_primary_key(conn, table):
    """Возвращает имя первичного ключа таблицы."""
    for col in conn.execute(f'PRAGMA table_info("{table}")'):
        if col["pk"] == 1:
            return col["name"]
    return "rowid"  # у таблицы нет явного первичного ключа


def get_columns(conn, table):
    """Список колонок таблицы (без секретных, например password_hash)."""
    return [
        c["name"]
        for c in conn.execute(f'PRAGMA table_info("{table}")')
        if not any(w in c["name"].lower() for w in SENSITIVE_WORDS)
    ]


def get_foreign_keys(conn, table):
    """Список внешних ключей таблицы: (колонка, связанная_таблица, колонка_в_ней)."""
    return [
        (fk["from"], fk["table"], fk["to"])
        for fk in conn.execute(f'PRAGMA foreign_key_list("{table}")')
    ]


def relation_name(fk_column, ref_table):
    """Имя вложенного объекта: user_id -> user, category_id -> category."""
    if fk_column.endswith("_id"):
        return fk_column[:-3]
    return ref_table


def build_query(conn, table):
    """Строит SELECT с LEFT JOIN по всем внешним ключам таблицы.

    Возвращает SQL и список связей. Колонки главной таблицы получают
    префикс m__, колонки связанных таблиц - префикс <имя_связи>__.
    """
    all_main = [c["name"] for c in conn.execute(f'PRAGMA table_info("{table}")')]
    select_parts = [f'm."{c}" AS "m__{c}"' for c in all_main]
    joins = []
    relations = []

    for fk_col, ref_table, ref_col in get_foreign_keys(conn, table):
        name = relation_name(fk_col, ref_table)
        alias = f"r_{name}"
        ref_columns = get_columns(conn, ref_table)
        select_parts += [f'{alias}."{c}" AS "{name}__{c}"' for c in ref_columns]
        joins.append(
            f'LEFT JOIN "{ref_table}" {alias} '
            f'ON m."{fk_col}" = {alias}."{ref_col}"'
        )
        relations.append({"name": name, "fk_column": fk_col, "columns": ref_columns})

    pk = get_primary_key(conn, table)
    sql = (
        f'SELECT {", ".join(select_parts)} FROM "{table}" m '
        f'{" ".join(joins)} ORDER BY m."{pk}"'
    )
    return sql, relations


def fetch_records(conn, table):
    """Извлекает все записи таблицы и собирает вложенные структуры.

    Внешние ключи (user_id, category_id) заменяются вложенными объектами
    (user, category) с данными из связанных таблиц.
    """
    sql, relations = build_query(conn, table)
    fk_columns = {r["fk_column"] for r in relations}
    main_columns = get_columns(conn, table)

    records = []
    for row in conn.execute(sql):
        record = {}
        for col in main_columns:
            if col not in fk_columns:
                record[col] = row[f"m__{col}"]
        for rel in relations:
            if row[f'm__{rel["fk_column"]}'] is None:
                record[rel["name"]] = None
            else:
                record[rel["name"]] = {
                    c: row[f'{rel["name"]}__{c}'] for c in rel["columns"]
                }
        records.append(record)
    return records


# ---------------------------------------------------------------------------
# Вспомогательные функции для сериализации
# ---------------------------------------------------------------------------
def flatten(record, parent="", sep="_"):
    """Разворачивает вложенный словарь в плоский (для CSV).

    {"user": {"username": "Папа"}} -> {"user_username": "Папа"}
    Списки объединяются в одну строку через ';'.
    """
    flat = {}
    for key, value in record.items():
        name = f"{parent}{sep}{key}" if parent else key
        if isinstance(value, dict):
            flat.update(flatten(value, name, sep))
        elif isinstance(value, list):
            flat[name] = ";".join(str(v) for v in value)
        else:
            flat[name] = value
    return flat


def singular(name):
    """Простейшее получение единственного числа: transactions -> transaction."""
    return name[:-1] if name.endswith("s") and len(name) > 1 else name + "_item"


def to_xml_element(parent, key, value):
    """Рекурсивно добавляет значение в XML-дерево."""
    if isinstance(value, dict):
        element = ET.SubElement(parent, key)
        for k, v in value.items():
            to_xml_element(element, k, v)
    elif isinstance(value, list):
        element = ET.SubElement(parent, key)
        for item in value:
            to_xml_element(element, singular(key), item)
    else:
        element = ET.SubElement(parent, key)
        if value is not None:
            element.text = str(value)


# ---------------------------------------------------------------------------
# Сохранение в форматы
# ---------------------------------------------------------------------------
def save_json(records, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def save_csv(records, path):
    flat_records = [flatten(r) for r in records]
    fieldnames = list(flat_records[0].keys()) if flat_records else []
    # utf-8-sig, чтобы кириллица корректно открывалась в Excel
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)


def save_xml(records, path, root_name, item_name):
    root = ET.Element(root_name)
    for record in records:
        item = ET.SubElement(root, item_name)
        for key, value in record.items():
            to_xml_element(item, key, value)
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def save_yaml(records, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            records, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )


def export_table(conn, table, out_dir=OUT_DIR):
    """Экспортирует таблицу в data.json, data.csv, data.xml, data.yaml."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)  # создаём out, если её нет

    records = fetch_records(conn, table)

    save_json(records, out_dir / "data.json")
    save_csv(records, out_dir / "data.csv")
    save_xml(records, out_dir / "data.xml", table, singular(table))
    save_yaml(records, out_dir / "data.yaml")
    return records


def main():
    table = sys.argv[1] if len(sys.argv) > 1 else TABLE_NAME
    conn = open_project_db()
    try:
        records = export_table(conn, table)
    finally:
        conn.close()
    print(f"Экспортировано записей: {len(records)}")
    print(f"Файлы сохранены в папку: {OUT_DIR}")


if __name__ == "__main__":
    main()
