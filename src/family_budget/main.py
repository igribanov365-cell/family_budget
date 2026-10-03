from budget import Budget


def main():
    budget = Budget()

    budget.add_income("Зарплата папы", 80000)
    budget.add_income("Зарплата мамы", 65000)
    budget.add_income("Пособие", 12000)

    budget.add_expense("Продукты", 25000)
    budget.add_expense("Коммунальные услуги", 8000)
    budget.add_expense("Транспорт", 4000)
    budget.add_expense("Образование", 15000)
    budget.add_expense("Развлечения", 5000)

    print("Hello, first-year student!")
    print()
    print(budget.report())

if __name__ == "__main__":
    main()