
## Лабораторная работа №5

### Форматы данных: JSON, CSV, XML, YAML

Скрипт `src/family_budget/export_data.py` извлекает все записи таблицы
`transactions` (связана с `users` и `categories`) и сохраняет их в папку `out/`:
`data.json`, `data.csv`, `data.xml`, `data.yaml`.

- JSON, XML, YAML: связанные данные вложены в объекты `user` и `category`;
- CSV: связанные поля объединены в одну строку (`user_username`, `category_name`, ...);
- внешние ключи определяются автоматически (`PRAGMA foreign_key_list`), JOIN строится динамически,
  поэтому для другой таблицы достаточно передать её имя.

```
pip install -r requirements.txt
cd src/family_budget
python export_data.py            # таблица transactions
python export_data.py users      # любая другая таблица
```
