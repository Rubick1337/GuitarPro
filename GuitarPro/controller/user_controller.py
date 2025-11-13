from database.db_handler import DatabaseHandler



class UserController:
    def __init__(self):
        self.db_handler = DatabaseHandler()

    def register_user(self, email, password, username=""):
        """Регистрация нового пользователя"""
        # Валидация входных данных
        if not email or not password:
            return False, "Email и пароль обязательны"

        email = email.strip().lower()

        # Проверяем существование пользователя
        existing_user = self.db_handler.get_user_by_email(email)
        if existing_user:
            return False, "Пользователь с таким email уже существует"

        # Создаем пользователя
        new_user = self.db_handler.create_user(email, password, username)

        if new_user:
            return True, f"Пользователь создан с ID: {new_user.id}"
        else:
            return False, "Ошибка при создании пользователя"

    def login_user(self, email, password):
        """Аутентификация пользователя"""
        if not email or not password:
            return False, "Email и пароль обязательны"

        email = email.strip().lower()

        # Для отладки покажем всех пользователей
        all_users = self.db_handler.get_all_users()
        print(f"👥 Все пользователи в БД ({len(all_users)}):")
        for user in all_users:
            print(f"   - '{user.email}' -> '{user.password}'")

        # Ищем пользователя
        user = self.db_handler.get_user_by_email(email)

        if not user:
            print(f"❌ Пользователь с email '{email}' не найден")
            return False, "Пользователь с таким email не найден"

        print(f"✅ Пользователь найден: ID={user.id}, Email='{user.email}'")
        print(f"🔑 Сравнение паролей: '{password}' vs '{user.password}'")

        # Проверяем пароль
        if user.password == password:
            welcome_name = user.username or user.email
            return True, f"Добро пожаловать, {welcome_name}! (ID: {user.id})"
        else:
            return False, "Неверный пароль"

    def test_database_connection(self):
        """Проверка соединения с БД"""
        return self.db_handler.test_connection()

    def close_connection(self):
        """Закрытие соединения"""
        self.db_handler.close_connection()