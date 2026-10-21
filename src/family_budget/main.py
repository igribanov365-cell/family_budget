from database.db import init_db, get_all_transactions, register_user, authenticate_user


def main():
    print("=== СИСТЕМА УЧЁТА СЕМЕЙНОГО БЮДЖЕТА ===\n")

    # 1. Инициализируем БД (создаст файл family_budget.db и выполнит schema.sql)
    init_db()
    print()

    # 2. Тест регистрации (сработает при первом запуске)
    # Если запустить второй раз, выведет "Логин занят"
    register_user("son", "qwerty123", "Сын", "son@mail.ru")
    print()

    # 3. Тест авторизации (берем данные Папы из schema.sql)
    print("--- Попытка входа в систему ---")
    user = authenticate_user("papa", "admin")
    print()

    # 4. Вывод транзакций, если вход успешен
    if user:
        transactions = get_all_transactions()
        
        print("=== ИСТОРИЯ ТРАНЗАКЦИЙ ===")
        # Шапка таблицы
        print(f"{'Дата':<12} | {'Кто':<10} | {'Счёт':<16} | {'Категория':<18} | {'Сумма':<10} | {'Тип':<7}")
        print("-" * 85)

        total_income = 0
        total_expense = 0

        for row in transactions:
            date, username, account, category, type_, amount, desc = row
            
            # Обрезаем дату до формата YYYY-MM-DD
            short_date = date[:10]
            
            if type_ == 'Доход':
                total_income += amount
            else:
                total_expense += amount

            print(f"{short_date:<12} | {username:<10} | {account:<16} | {category:<18} | {amount:>8.2f} ₽ | {type_}")

        print("-" * 85)
        print(f"ИТОГО ДОХОДОВ:  {total_income:>10.2f} ₽")
        print(f"ИТОГО РАСХОДОВ: {total_expense:>10.2f} ₽")
        print(f"БАЛАНС:         {total_income - total_expense:>10.2f} ₽")


if __name__ == "__main__":
    main()