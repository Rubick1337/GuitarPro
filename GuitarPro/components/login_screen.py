# components/login_screen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.app import App
import re


class RoundedButton(Button):
    bg_color = ListProperty([0.2, 0.6, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.bind(pos=self._update_canvas, size=self._update_canvas, bg_color=self._update_canvas)

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[25])


class LoginScreen(Screen):
    # Инстанс DatabaseHandler прокидывается из App/Router
    db = ObjectProperty(None)

    def __init__(self, **kwargs):
        # Вытаскиваем db из kwargs до super()
        if 'db' in kwargs:
            self.db = kwargs.pop('db')
        super().__init__(**kwargs)

        Window.clearcolor = get_color_from_hex('#000000')

        main_layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        # Кнопка "Назад"
        back_button = Button(
            text="Назад",
            size_hint=(None, None),
            size=(100, 40),
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#FFFFFF'),
            bold=True
        )
        back_button.bind(on_press=self.go_back)

        back_container = BoxLayout(size_hint=(1, 0.1))
        back_container.add_widget(back_button)
        back_container.add_widget(Label())
        main_layout.add_widget(back_container)

        # Картинка
        guitar_image = Image(
            source='guitar.png',
            size_hint=(1, 0.3),
            allow_stretch=True,
            keep_ratio=True
        )
        main_layout.add_widget(guitar_image)

        # Заголовок
        title_label = Label(
            text="Введите данные",
            font_size=32,
            size_hint=(1, 0.1),
            color=get_color_from_hex('#FFFFFF'),
            bold=True
        )
        main_layout.add_widget(title_label)

        # Форма
        form_container = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint=(1, 0.5),
            padding=[50, 0, 50, 0]
        )

        # Email
        email_label = Label(
            text="Введите почту",
            font_size=16,
            size_hint=(1, 0.2),
            color=get_color_from_hex('#E0E0E0'),
            halign='left'
        )
        form_container.add_widget(email_label)

        self.email_input = TextInput(
            hint_text="example@mail.com",
            size_hint=(1, 0.7),
            multiline=False,
            font_size=16,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            padding=[15, 10],
            cursor_color=(0, 0, 0, 1)
        )
        form_container.add_widget(self.email_input)

        form_container.add_widget(BoxLayout(size_hint=(1, 0.1)))

        # Пароль
        password_label = Label(
            text="Введите пароль",
            font_size=16,
            size_hint=(1, 0.2),
            color=get_color_from_hex('#E0E0E0'),
            halign='left'
        )
        form_container.add_widget(password_label)

        self.password_input = TextInput(
            hint_text="Ваш пароль",
            size_hint=(1, 0.7),
            password=True,
            multiline=False,
            font_size=16,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.4, 0.4, 0.4, 1),
            padding=[15, 10],
            cursor_color=(0, 0, 0, 1)
        )
        form_container.add_widget(self.password_input)

        form_container.add_widget(BoxLayout(size_hint=(1, 0.2)))

        # Кнопка входа
        btn_login = RoundedButton(
            text="ВХОД",
            size_hint=(1, 0.6),
            color=get_color_from_hex('#FFFFFF'),
            font_size=20,
            bg_color=get_color_from_hex('#6A4CA4'),
            bold=True
        )
        btn_login.bind(on_press=self.perform_login)
        form_container.add_widget(btn_login)

        main_layout.add_widget(form_container)
        self.add_widget(main_layout)

    # --- Навигация ---
    def go_back(self, _instance):
        self.manager.current = 'welcome'

    # --- Вспомогалки UI ---
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn_ok = Button(text='OK', size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.4))
        btn_ok.bind(on_press=popup.dismiss)
        content.add_widget(btn_ok)
        popup.open()

    # --- Основная логика входа ---
    def perform_login(self, _instance):
        email = (self.email_input.text or "").strip().lower()
        password = self.password_input.text or ""
        if not email or not password:
            self.show_message("Ошибка", "Заполните все поля")
            return

        if not self.db:
            self.show_message("Ошибка", "База данных не доступна")
            return

        success, payload = self.db.login_user(email, password)

        if not success:
            # payload — это текст ошибки
            self.show_message("Ошибка", str(payload))
            return

        # ПОЛУЧАЕМ user_id:
        user_id = None

        # 1) Пытаемся достать пользователя напрямую (предпочтительно)
        if hasattr(self.db, "get_user_by_email"):
            try:
                user_obj = self.db.get_user_by_email(email)
                if user_obj and getattr(user_obj, "id", None) is not None:
                    user_id = int(user_obj.id)
            except Exception:
                user_id = None

        # 2) Резерв: пробуем вытащить ID из текстового сообщения (если login_user его возвращает в тексте)
        if user_id is None and isinstance(payload, str):
            # ожидаем шаблон вида: "... (ID: 1)" — выдёргиваем число
            m = re.search(r"\(ID:\s*(\d+)\)", payload)
            if m:
                user_id = int(m.group(1))

        if user_id is None:
            self.show_message("Ошибка", "Не удалось определить ID пользователя после входа.")
            return

        # Чистим поля после удачного входа
        self.email_input.text = ""
        self.password_input.text = ""

        # Открываем главное меню с передачей user_id
        app = App.get_running_app()
        try:
            app.open_main_menu(user_id)  # создаст/обновит MainMenuScreen и пробросит user_id в AssistantPanel
        except Exception as e:
            self.show_message("Ошибка", f"Не удалось открыть главное меню: {e}")
