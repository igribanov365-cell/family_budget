import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "family_budget"))

import export_data  # noqa: E402


@pytest.fixture
def exported(tmp_path):
    conn = export_data.create_connection()
    out = tmp_path / "out"  # папки ещё нет - должна создаться
    records = export_data.export_table(conn, "transactions", out)
    conn.close()
    return out, records


def test_out_dir_and_files_created(exported):
    out, _ = exported
    for name in ("data.json", "data.csv", "data.xml", "data.yaml"):
        assert (out / name).exists()


def test_json_nested(exported):
    out, records = exported
    data = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert len(data) == len(records) == 6
    assert data[0]["user"]["username"] == "Папа"
    assert data[0]["category"]["name"] == "Зарплата"
    assert "user_id" not in data[0]


def test_csv_flat(exported):
    out, _ = exported
    with open(out / "data.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 6
    assert rows[0]["user_username"] == "Папа"


def test_xml_parses(exported):
    out, _ = exported
    root = ET.parse(out / "data.xml").getroot()
    assert root.tag == "transactions"
    assert len(root.findall("transaction")) == 6
    assert root.find("transaction/user/username").text == "Папа"


def test_yaml_equals_json(exported):
    out, _ = exported
    y = yaml.safe_load((out / "data.yaml").read_text(encoding="utf-8"))
    j = json.loads((out / "data.json").read_text(encoding="utf-8"))
    assert y == j


def test_other_table_works(tmp_path):
    """Универсальность: экспорт таблицы без внешних ключей."""
    conn = export_data.create_connection()
    records = export_data.export_table(conn, "users", tmp_path / "o")
    assert len(records) == 3 and records[0]["username"] == "Папа"
