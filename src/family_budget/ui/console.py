"""Вспомогательные функции ввода/вывода для консольного интерфейса."""
from datetime import date


def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_float(prompt: str) -> float | None:
    raw = ask(prompt).replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        print("Ошибка: нужно ввести число")
        return None


def ask_int(prompt: str) -> int | None:
    raw = ask(prompt)
    try:
        return int(raw)
    except ValueError:
        print("Ошибка: нужно ввести целое число")
        return None


def ask_optional_int(prompt: str) -> tuple[bool, int | None]:
    """Возвращает (ввод_корректен, значение). Пустой ввод — значение None."""
    raw = ask(prompt)
    if not raw:
        return True, None
    try:
        return True, int(raw)
    except ValueError:
        print("Ошибка: нужно ввести целое число или оставить поле пустым")
        return False, None


def ask_date(prompt: str) -> str:
    raw = ask(f"{prompt} (Enter — сегодня): ")
    return raw or date.today().isoformat()


def choose(options: tuple[str, ...], title: str) -> str | None:
    print(title)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    idx = ask_int("Номер: ")
    if idx is None or not 1 <= idx <= len(options):
        print("Ошибка: неверный выбор")
        return None
    return options[idx - 1]


def money(value: float, currency: str = "руб.") -> str:
    return f"{value:,.2f}".replace(",", " ") + f" {currency}"
