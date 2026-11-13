import calendar
from datetime import date, datetime, timedelta

from repositories import category_repository, regular_payment_repository
from models.regular_payment import RegularPayment
from models.user import User
from services import transaction_service
from services.constants import DATE_FORMAT, FREQUENCIES, ROLE_HEAD
from services.errors import ServiceError


def _validate(amount: float, frequency: str, next_date: str, category_id: int):
    if amount <= 0:
        raise ServiceError("Сумма должна быть больше нуля")
    if frequency not in FREQUENCIES:
        raise ServiceError("Периодичность: 'месяц' или 'неделя'")
    try:
        datetime.strptime(next_date, DATE_FORMAT)
    except ValueError:
        raise ServiceError("Дата должна быть в формате ГГГГ-ММ-ДД")
    if not category_repository.get_by_id(category_id):
        raise ServiceError("Категория не найдена")


def _get_editable(actor: User, payment_id: int) -> RegularPayment:
    payment = regular_payment_repository.get_by_id(payment_id)
    if not payment:
        raise ServiceError("Регулярный платёж не найден")
    if actor.role != ROLE_HEAD and payment.user_id != actor.user_id:
        raise ServiceError("Можно работать только со своими регулярными платежами")
    return payment


def add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year, month = d.year + month_index // 12, month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_occurrence(current: date, frequency: str) -> date:
    return add_months(current, 1) if frequency == "месяц" else current + timedelta(weeks=1)


def get_payments(actor: User) -> list[RegularPayment]:
    if actor.role == ROLE_HEAD:
        return regular_payment_repository.get_all()
    return regular_payment_repository.get_by_user(actor.user_id)


def create_payment(actor: User, category_id: int, amount: float,
                   frequency: str, next_date: str) -> int:
    _validate(amount, frequency, next_date, category_id)
    return regular_payment_repository.create(actor.user_id, category_id, amount, frequency, next_date)


def update_payment(actor: User, payment_id: int, category_id: int, amount: float,
                   frequency: str, next_date: str):
    _get_editable(actor, payment_id)
    _validate(amount, frequency, next_date, category_id)
    regular_payment_repository.update(payment_id, category_id, amount, frequency, next_date)


def delete_payment(actor: User, payment_id: int):
    _get_editable(actor, payment_id)
    regular_payment_repository.delete(payment_id)


def execute_payment(actor: User, payment_id: int, account_id: int,
                    payment_method: str, today: date | None = None) -> int:
    """Проводит регулярный платёж как обычную транзакцию и сдвигает дату следующего платежа."""
    payment = _get_editable(actor, payment_id)
    if payment.user_id != actor.user_id:
        raise ServiceError("Провести платёж может только его владелец")
    today = today or date.today()
    tr_id = transaction_service.add_transaction(
        actor, account_id, payment.category_id, payment.amount,
        today.isoformat(), payment_method, "Регулярный платёж",
    )
    nxt = datetime.strptime(payment.next_date, DATE_FORMAT).date()
    nxt = next_occurrence(nxt, payment.frequency)
    while nxt <= today:
        nxt = next_occurrence(nxt, payment.frequency)
    regular_payment_repository.set_next_date(payment_id, nxt.isoformat())
    return tr_id
