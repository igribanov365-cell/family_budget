from models.user import User
from services import category_service, transaction_service, user_service
from services.auth_service import register
from services.constants import ROLE_HEAD, ROLES, TYPES
from services.errors import ServiceError
from ui.console import ask, ask_date, ask_float, ask_int, money


def _safe(action):
    """Вызывает действие и красиво показывает ошибки бизнес-логики."""
    try:
        action()
    except ServiceError as e:
        print(f"Ошибка: {e}")


def _choose(options: tuple[str, ...], title: str) -> str | None:
    print(title)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    idx = ask_int("Номер: ")
    if idx is None or not 1 <= idx <= len(options):
        print("Ошибка: неверный выбор")
        return None
    return options[idx - 1]


# ---------- транзакции ----------
def _show_transactions(user: User):
    items = transaction_service.get_transactions(user)
    if not items:
        print("Транзакций пока нет")
        return
    print(f"\n{'ID':<4}{'Дата':<12}{'Тип':<8}{'Категория':<22}{'Сумма':<16}{'Кто':<10}Описание")
    for t in items:
        print(f"{t.transaction_id:<4}{t.transaction_date:<12}{t.category_type:<8}"
              f"{t.category_name:<22}{money(t.amount):<16}{t.username:<10}{t.description or ''}")


def _pick_category() -> int | None:
    cats = category_service.get_all_categories()
    print("Категории:")
    for c in cats:
        print(f"  {c.category_id}. {c.name} ({c.type})")
    return ask_int("ID категории: ")


def _add_transaction(user: User):
    category_id = _pick_category()
    amount = ask_float("Сумма: ")
    if category_id is None or amount is None:
        return
    date_value = ask_date("Дата ГГГГ-ММ-ДД")
    description = ask("Описание (можно пустое): ")
    transaction_service.add_transaction(user, amount, date_value, description, category_id)
    print("Транзакция добавлена")


def _edit_transaction(user: User):
    tr_id = ask_int("ID транзакции: ")
    if tr_id is None:
        return
    category_id = _pick_category()
    amount = ask_float("Новая сумма: ")
    if category_id is None or amount is None:
        return
    date_value = ask_date("Новая дата ГГГГ-ММ-ДД")
    description = ask("Новое описание: ")
    transaction_service.update_transaction(user, tr_id, amount, date_value, description, category_id)
    print("Транзакция обновлена")


def _delete_transaction(user: User):
    tr_id = ask_int("ID транзакции: ")
    if tr_id is None:
        return
    transaction_service.delete_transaction(user, tr_id)
    print("Транзакция удалена")


def transactions_menu(user: User):
    while True:
        print("\n--- Транзакции ---")
        print("1. Показать список")
        print("2. Добавить")
        print("3. Изменить")
        print("4. Удалить")
        print("0. Назад")
        choice = ask("Выберите действие: ")
        if choice == "1":
            _safe(lambda: _show_transactions(user))
        elif choice == "2":
            _safe(lambda: _add_transaction(user))
        elif choice == "3":
            _safe(lambda: _edit_transaction(user))
        elif choice == "4":
            _safe(lambda: _delete_transaction(user))
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


# ---------- отчёт ----------
def show_report():
    r = transaction_service.get_report()
    print("\n=== Отчёт по семейному бюджету ===")
    print(f"Доходы:  {money(r['income'])}")
    print(f"Расходы: {money(r['expense'])}")
    print(f"Баланс:  {money(r['balance'])}")
    if r["by_category"]:
        print("\nПо категориям:")
        for type_, name, total in r["by_category"]:
            print(f"  [{type_}] {name}: {money(total)}")


# ---------- категории (Глава) ----------
def categories_menu(user: User):
    while True:
        print("\n--- Категории ---")
        print("1. Показать список")
        print("2. Добавить")
        print("3. Изменить")
        print("4. Удалить")
        print("0. Назад")
        choice = ask("Выберите действие: ")
        if choice == "1":
            for c in category_service.get_all_categories():
                print(f"  {c.category_id}. {c.name} ({c.type})")
        elif choice == "2":
            name = ask("Название: ")
            type_ = _choose(TYPES, "Тип:")
            if type_:
                _safe(lambda: (category_service.create_category(user, name, type_),
                               print("Категория добавлена")))
        elif choice == "3":
            cid = ask_int("ID категории: ")
            name = ask("Новое название: ")
            type_ = _choose(TYPES, "Тип:")
            if cid is not None and type_:
                _safe(lambda: (category_service.update_category(user, cid, name, type_),
                               print("Категория обновлена")))
        elif choice == "4":
            cid = ask_int("ID категории: ")
            if cid is not None:
                _safe(lambda: (category_service.delete_category(user, cid),
                               print("Категория удалена")))
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


# ---------- пользователи (Глава) ----------
def users_menu(user: User):
    while True:
        print("\n--- Члены семьи ---")
        print("1. Показать список")
        print("2. Добавить")
        print("3. Изменить имя/роль")
        print("4. Удалить")
        print("0. Назад")
        choice = ask("Выберите действие: ")
        if choice == "1":
            _safe(lambda: [print(f"  {u.user_id}. {u.username} [{u.role}] логин: {u.login}")
                           for u in user_service.get_all_users(user)])
        elif choice == "2":
            username, login_value = ask("Имя: "), ask("Логин: ")
            password = ask("Пароль: ")
            role = _choose(ROLES, "Роль:")
            if role:
                _safe(lambda: (register(username, login_value, password, role),
                               print("Пользователь добавлен")))
        elif choice == "3":
            uid = ask_int("ID пользователя: ")
            username = ask("Новое имя: ")
            role = _choose(ROLES, "Роль:")
            if uid is not None and role:
                _safe(lambda: (user_service.update_user(user, uid, username, role),
                               print("Пользователь обновлён")))
        elif choice == "4":
            uid = ask_int("ID пользователя: ")
            if uid is not None:
                _safe(lambda: (user_service.delete_user(user, uid),
                               print("Пользователь удалён")))
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


# ---------- главные меню по ролям ----------
def head_menu(user: User):
    while True:
        print(f"\n===== Глава семьи ({user.username}) =====")
        print("1. Транзакции (вся семья)")
        print("2. Категории")
        print("3. Члены семьи")
        print("4. Отчёт")
        print("0. Выход")
        choice = ask("Выберите действие: ")
        if choice == "1":
            transactions_menu(user)
        elif choice == "2":
            categories_menu(user)
        elif choice == "3":
            users_menu(user)
        elif choice == "4":
            show_report()
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


def member_menu(user: User):
    while True:
        print(f"\n===== Член семьи ({user.username}) =====")
        print("1. Мои транзакции")
        print("2. Отчёт")
        print("0. Выход")
        choice = ask("Выберите действие: ")
        if choice == "1":
            transactions_menu(user)
        elif choice == "2":
            show_report()
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


def user_menu(user: User):
    (head_menu if user.role == ROLE_HEAD else member_menu)(user)
