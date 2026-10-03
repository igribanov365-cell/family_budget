class Budget:
    """Класс для учёта семейного бюджета."""

    def __init__(self):
        self.incomes = []
        self.expenses = []

    def add_income(self, category, amount):
        if amount <= 0:
            raise ValueError("Сумма дохода должна быть больше нуля")
        self.incomes.append({"category": category, "amount": amount})

    def add_expense(self, category, amount):
        if amount <= 0:
            raise ValueError("Сумма расхода должна быть больше нуля")
        self.expenses.append({"category": category, "amount": amount})

    def total_income(self):
        return sum(item["amount"] for item in self.incomes)

    def total_expense(self):
        return sum(item["amount"] for item in self.expenses)

    def balance(self):
        return self.total_income() - self.total_expense()

    def report(self):
        lines = ["=== Отчёт по семейному бюджету ==="]
        lines.append(f"Доходы:  {self.total_income():.2f} руб.")
        lines.append(f"Расходы: {self.total_expense():.2f} руб.")
        lines.append(f"Баланс:  {self.balance():.2f} руб.")
        return "\n".join(lines)