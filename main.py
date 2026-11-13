from database.database import init_db
from ui.auth import login, register_member
from ui.menus import user_menu


def main():
    init_db()
    while True:
        print("\n===== Учёт семейного бюджета =====")
        print("1. Войти")
        print("2. Зарегистрироваться")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            user = login()
            if user:
                user_menu(user)
        elif choice == "2":
            register_member()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()
