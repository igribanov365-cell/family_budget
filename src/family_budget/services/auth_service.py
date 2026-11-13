import hashlib
import os

from repositories import user_repository
from models.user import User
from services.constants import ROLES, ROLE_MEMBER
from services.errors import ServiceError

_ITERATIONS = 100_000


def hash_password(password: str, salt_hex: str | None = None) -> str:
    salt_hex = salt_hex or os.urandom(8).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS
    ).hex()
    return f"{salt_hex}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex = stored.split("$", 1)[0]
    return hash_password(password, salt_hex) == stored


def authenticate(login: str, password: str) -> User | None:
    user = user_repository.get_by_login(login.strip())
    if user and verify_password(password, user.password_hash):
        return user
    return None


def check_email(email: str | None) -> str | None:
    email = (email or "").strip()
    if not email:
        return None
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ServiceError("Некорректный email")
    return email


def register(username: str, login: str, password: str,
             email: str | None = None, role: str = ROLE_MEMBER) -> int:
    username, login = username.strip(), login.strip()
    if not username:
        raise ServiceError("Имя не может быть пустым")
    if not login:
        raise ServiceError("Логин не может быть пустым")
    if len(password) < 4:
        raise ServiceError("Пароль должен содержать минимум 4 символа")
    if role not in ROLES:
        raise ServiceError("Недопустимая роль")
    email = check_email(email)
    if user_repository.get_by_login(login):
        raise ServiceError("Пользователь с таким логином уже существует")
    return user_repository.create(login, hash_password(password), username, email, role)
