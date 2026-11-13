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


def ask_date(prompt: str) -> str:
    raw = ask(f"{prompt} (Enter — сегодня): ")
    return raw or date.today().isoformat()


def money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ") + " руб."
