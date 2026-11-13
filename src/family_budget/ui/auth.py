from services.auth_service import authenticate, register
from services.errors import ServiceError
from ui.console import ask


def login():
    login_value = ask("Логин: ")
    password_value = ask("Пароль: ")
    user = authenticate(login_value, password_value)
    if not user:
        print("Неверный логин или пароль")
        return None
    return user


def register_member():
    """Регистрация нового члена семьи (роль 'Член семьи')."""
    username = ask("Имя: ")
    login_value = ask("Логин: ")
    email = ask("Email (можно пропустить): ")
    password_value = ask("Пароль (мин. 4 символа): ")
    try:
        register(username, login_value, password_value, email)
        print("Регистрация прошла успешно. Теперь можно войти.")
    except ServiceError as e:
        print(f"Ошибка: {e}")
