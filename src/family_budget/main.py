from db import init_db, get_report_data

def main():
    print("Hello, first-year student!")
    
    # 1. Инициализируем базу данных (создаем таблицы и данные)
    init_db()
    
    # 2. Получаем данные из БД
    transactions = get_report_data()
    
    # 3. Считаем итоги и выводим
    total_income = 0
    total_expense = 0
    
    print("\n=== Список всех транзакций ===")
    for row in transactions:
        date, user, category, t_type, amount = row
        print(f"[{date}] {user} | {category} ({t_type}): {amount:.2f} руб.")
        
        if t_type == "Доход":
            total_income += amount
        else:
            total_expense += amount

    print("-" * 40)
    print(f"Общий доход:  {total_income:.2f} руб.")
    print(f"Общий расход: {total_expense:.2f} руб.")
    print(f"Баланс:       {total_income - total_expense:.2f} руб.")

if __name__ == "__main__":
    main()