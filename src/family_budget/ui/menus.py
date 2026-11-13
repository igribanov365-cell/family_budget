from models.user import User
from services import (
    account_service, category_service, regular_payment_service,
    report_service, transaction_service, user_service,
)
from services.auth_service import register
from services.constants import (
    FREQUENCIES, PAYMENT_METHODS, ROLE_HEAD, ROLES, TYPES,
)
from services.errors import ServiceError
from ui.console import (
    ask, ask_date, ask_float, ask_int, ask_optional_int, choose, money,
)


def _safe(action):
    """Вызывает действие и показывает ошибки бизнес-логики."""
    try:
        action()
    except ServiceError as e:
        print(f"Ошибка: {e}")


def _crud_menu(title: str, handlers: dict[str, tuple[str, callable]]):
    """Универсальный цикл подменю: {'1': ('Название пункта', функция), ...}."""
    while True:
        print(f"\n--- {title} ---")
        for key, (label, _) in handlers.items():
            print(f"{key}. {label}")
        print("0. Назад")
        choice = ask("Выберите действие: ")
        if choice == "0":
            break
        if choice in handlers:
            _safe(handlers[choice][1])
        else:
            print("Неизвестная команда")


# ================= счета =================
def _show_accounts(user: User):
    items = account_service.get_accounts(user)
    if not items:
        print("Счетов пока нет")
        return
    print(f"\n{'ID':<4}{'Название':<22}{'Владелец':<10}Баланс")
    for a in items:
        print(f"{a.account_id:<4}{a.name:<22}{a.owner_name:<10}{money(a.balance, a.currency)}")


def _add_account(user: User):
    name = ask("Название счёта: ")
    balance = ask_float("Начальный баланс: ")
    if balance is None:
        return
    currency = ask("Валюта (Enter — RUB): ") or "RUB"
    owner_id = None
    if user.role == ROLE_HEAD:
        ok, owner_id = ask_optional_int("ID владельца (Enter — вы): ")
        if not ok:
            return
    account_service.create_account(user, name, balance, currency, owner_id)
    print("Счёт добавлен")


def _edit_account(user: User):
    acc_id = ask_int("ID счёта: ")
    if acc_id is None:
        return
    name = ask("Новое название: ")
    currency = ask("Валюта (Enter — RUB): ") or "RUB"
    account_service.update_account(user, acc_id, name, currency)
    print("Счёт обновлён")


def _delete_account(user: User):
    acc_id = ask_int("ID счёта: ")
    if acc_id is None:
        return
    account_service.delete_account(user, acc_id)
    print("Счёт удалён")


def accounts_menu(user: User):
    _crud_menu("Счета", {
        "1": ("Показать список", lambda: _show_accounts(user)),
        "2": ("Добавить", lambda: _add_account(user)),
        "3": ("Изменить название/валюту", lambda: _edit_account(user)),
        "4": ("Удалить", lambda: _delete_account(user)),
    })


# ================= категории =================
def _show_categories():
    for c in category_service.get_all_categories():
        indent = "    " if c.parent_id else ""
        print(f"  {indent}{c.category_id}. {c.name} ({c.type})")


def _add_category(user: User):
    name = ask("Название: ")
    type_ = choose(TYPES, "Тип:")
    if not type_:
        return
    ok, parent_id = ask_optional_int("ID родительской категории (Enter — нет): ")
    if not ok:
        return
    color = ask("Цвет, например #FF9800 (Enter — пропустить): ")
    category_service.create_category(user, name, type_, parent_id, color)
    print("Категория добавлена")


def _edit_category(user: User):
    cid = ask_int("ID категории: ")
    if cid is None:
        return
    name = ask("Новое название: ")
    type_ = choose(TYPES, "Тип:")
    if not type_:
        return
    ok, parent_id = ask_optional_int("ID родительской категории (Enter — нет): ")
    if not ok:
        return
    color = ask("Цвет (Enter — пропустить): ")
    category_service.update_category(user, cid, name, type_, parent_id, color)
    print("Категория обновлена")


def _delete_category(user: User):
    cid = ask_int("ID категории: ")
    if cid is None:
        return
    category_service.delete_category(user, cid)
    print("Категория удалена")


def categories_menu(user: User):
    if user.role != ROLE_HEAD:
        print("\nКатегории семьи:")
        _show_categories()
        return
    _crud_menu("Категории", {
        "1": ("Показать список", _show_categories),
        "2": ("Добавить категорию/подкатегорию", lambda: _add_category(user)),
        "3": ("Изменить", lambda: _edit_category(user)),
        "4": ("Удалить", lambda: _delete_category(user)),
    })


# ================= транзакции =================
def _show_transactions(user: User):
    items = transaction_service.get_transactions(user)
    if not items:
        print("Транзакций пока нет")
        return
    print(f"\n{'ID':<4}{'Дата':<12}{'Тип':<8}{'Категория':<20}{'Сумма':<16}"
          f"{'Счёт':<18}{'Оплата':<10}{'Кто':<8}Описание")
    for t in items:
        print(f"{t.transaction_id:<4}{t.transaction_date:<12}{t.category_type:<8}"
              f"{t.category_name:<20}{money(t.amount):<16}{t.account_name:<18}"
              f"{t.payment_method:<10}{t.username:<8}{t.description or ''}")


def _pick_account(user: User) -> int | None:
    accounts = [a for a in account_service.get_accounts(user) if a.user_id == user.user_id]
    if not accounts:
        print("У вас нет счетов. Сначала добавьте счёт в разделе «Счета».")
        return None
    print("Ваши счета:")
    for a in accounts:
        print(f"  {a.account_id}. {a.name} — {money(a.balance, a.currency)}")
    return ask_int("ID счёта: ")


def _pick_category() -> int | None:
    print("Категории:")
    _show_categories()
    return ask_int("ID категории: ")


def _add_transaction(user: User):
    account_id = _pick_account(user)
    if account_id is None:
        return
    category_id = _pick_category()
    amount = ask_float("Сумма: ")
    if category_id is None or amount is None:
        return
    date_value = ask_date("Дата ГГГГ-ММ-ДД")
    method = choose(PAYMENT_METHODS, "Способ оплаты:")
    if not method:
        return
    description = ask("Описание (можно пустое): ")
    transaction_service.add_transaction(
        user, account_id, category_id, amount, date_value, method, description
    )
    print("Транзакция добавлена, баланс счёта обновлён")


def _edit_transaction(user: User):
    tr_id = ask_int("ID транзакции: ")
    if tr_id is None:
        return
    category_id = _pick_category()
    amount = ask_float("Новая сумма: ")
    if category_id is None or amount is None:
        return
    date_value = ask_date("Новая дата ГГГГ-ММ-ДД")
    method = choose(PAYMENT_METHODS, "Способ оплаты:")
    if not method:
        return
    description = ask("Новое описание: ")
    transaction_service.update_transaction(
        user, tr_id, category_id, amount, date_value, method, description
    )
    print("Транзакция обновлена, баланс счёта пересчитан")


def _delete_transaction(user: User):
    tr_id = ask_int("ID транзакции: ")
    if tr_id is None:
        return
    transaction_service.delete_transaction(user, tr_id)
    print("Транзакция удалена, баланс счёта пересчитан")


def transactions_menu(user: User):
    _crud_menu("Транзакции", {
        "1": ("Показать список", lambda: _show_transactions(user)),
        "2": ("Добавить", lambda: _add_transaction(user)),
        "3": ("Изменить", lambda: _edit_transaction(user)),
        "4": ("Удалить", lambda: _delete_transaction(user)),
    })


# ================= регулярные платежи =================
def _show_payments(user: User):
    items = regular_payment_service.get_payments(user)
    if not items:
        print("Регулярных платежей пока нет")
        return
    print(f"\n{'ID':<4}{'Тип':<8}{'Категория':<22}{'Сумма':<16}{'Период':<9}{'Следующий':<12}Кто")
    for p in items:
        print(f"{p.payment_id:<4}{p.category_type:<8}{p.category_name:<22}"
              f"{money(p.amount):<16}{p.frequency:<9}{p.next_date:<12}{p.username}")


def _read_payment_fields():
    category_id = _pick_category()
    amount = ask_float("Сумма: ")
    if category_id is None or amount is None:
        return None
    frequency = choose(FREQUENCIES, "Периодичность:")
    if not frequency:
        return None
    next_date = ask_date("Дата следующего платежа ГГГГ-ММ-ДД")
    return category_id, amount, frequency, next_date


def _add_payment(user: User):
    fields = _read_payment_fields()
    if fields:
        regular_payment_service.create_payment(user, *fields)
        print("Регулярный платёж добавлен")


def _edit_payment(user: User):
    pid = ask_int("ID платежа: ")
    if pid is None:
        return
    fields = _read_payment_fields()
    if fields:
        regular_payment_service.update_payment(user, pid, *fields)
        print("Регулярный платёж обновлён")


def _delete_payment(user: User):
    pid = ask_int("ID платежа: ")
    if pid is None:
        return
    regular_payment_service.delete_payment(user, pid)
    print("Регулярный платёж удалён")


def _execute_payment(user: User):
    pid = ask_int("ID платежа: ")
    if pid is None:
        return
    account_id = _pick_account(user)
    if account_id is None:
        return
    method = choose(PAYMENT_METHODS, "Способ оплаты:")
    if not method:
        return
    regular_payment_service.execute_payment(user, pid, account_id, method)
    print("Платёж проведён как транзакция, дата следующего платежа сдвинута")


def payments_menu(user: User):
    _crud_menu("Регулярные платежи", {
        "1": ("Показать список", lambda: _show_payments(user)),
        "2": ("Добавить", lambda: _add_payment(user)),
        "3": ("Изменить", lambda: _edit_payment(user)),
        "4": ("Удалить", lambda: _delete_payment(user)),
        "5": ("Провести платёж сейчас", lambda: _execute_payment(user)),
    })


# ================= пользователи (Глава) =================
def _show_users(user: User):
    for u in user_service.get_all_users(user):
        print(f"  {u.user_id}. {u.username} [{u.role}] логин: {u.login}, email: {u.email or '—'}")


def _add_user(user: User):
    username, login_value = ask("Имя: "), ask("Логин: ")
    email, password = ask("Email (можно пропустить): "), ask("Пароль: ")
    role = choose(ROLES, "Роль:")
    if role:
        register(username, login_value, password, email, role)
        print("Пользователь добавлен")


def _edit_user(user: User):
    uid = ask_int("ID пользователя: ")
    if uid is None:
        return
    username, email = ask("Новое имя: "), ask("Новый email (можно пустой): ")
    role = choose(ROLES, "Роль:")
    if role:
        user_service.update_user(user, uid, username, email, role)
        print("Пользователь обновлён")


def _delete_user(user: User):
    uid = ask_int("ID пользователя: ")
    if uid is None:
        return
    user_service.delete_user(user, uid)
    print("Пользователь удалён")


def users_menu(user: User):
    _crud_menu("Члены семьи", {
        "1": ("Показать список", lambda: _show_users(user)),
        "2": ("Добавить", lambda: _add_user(user)),
        "3": ("Изменить", lambda: _edit_user(user)),
        "4": ("Удалить", lambda: _delete_user(user)),
    })


# ================= отчёт =================
def show_report(user: User):
    r = report_service.get_report(user)
    print(f"\n=== Отчёт по семейному бюджету ({r['scope']}) ===")
    print(f"Доходы:             {money(r['income'])}")
    print(f"Расходы:            {money(r['expense'])}")
    print(f"Доходы − расходы:   {money(r['balance'])}")
    print(f"Остаток на счетах:  {money(r['accounts_total'])}")
    if r["by_category"]:
        print("\nПо категориям:")
        for type_, name, total in r["by_category"]:
            print(f"  [{type_}] {name}: {money(total)}")


# ================= главные меню по ролям =================
def _main_menu(title: str, items: list[tuple[str, callable]]):
    while True:
        print(f"\n===== {title} =====")
        for i, (label, _) in enumerate(items, 1):
            print(f"{i}. {label}")
        print("0. Выход")
        choice = ask("Выберите действие: ")
        if choice == "0":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(items):
            items[int(choice) - 1][1]()
        else:
            print("Неизвестная команда")


def head_menu(user: User):
    _main_menu(f"Глава семьи ({user.username})", [
        ("Транзакции (вся семья)", lambda: transactions_menu(user)),
        ("Счета", lambda: accounts_menu(user)),
        ("Категории", lambda: categories_menu(user)),
        ("Регулярные платежи", lambda: payments_menu(user)),
        ("Члены семьи", lambda: users_menu(user)),
        ("Отчёт по семье", lambda: show_report(user)),
    ])


def member_menu(user: User):
    _main_menu(f"Член семьи ({user.username})", [
        ("Мои транзакции", lambda: transactions_menu(user)),
        ("Мои счета", lambda: accounts_menu(user)),
        ("Категории (просмотр)", lambda: categories_menu(user)),
        ("Мои регулярные платежи", lambda: payments_menu(user)),
        ("Мой отчёт", lambda: show_report(user)),
    ])


def user_menu(user: User):
    (head_menu if user.role == ROLE_HEAD else member_menu)(user)
