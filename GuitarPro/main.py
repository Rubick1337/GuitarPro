# main.py
import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# --- важно: гарантируем импорт пакетов по относительным путям проекта ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from components.welcome_screen import WelcomeScreen
from components.login_screen import LoginScreen
from components.register_screen import RegisterScreen
from components.main_menu import MainMenuScreen
from database.db_handler import DatabaseHandler


class GuitarProApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseHandler()
        self.current_user_id = None  # сюда положим id после логина

    def build(self):
        Window.clearcolor = get_color_from_hex('#000000')
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome', db=self.db))
        sm.add_widget(LoginScreen(name='login', db=self.db))
        sm.add_widget(RegisterScreen(name='register', db=self.db))
        # ВАЖНО: MainMenuScreen НЕ создаём здесь, пока не знаем user_id.
        return sm

    # вызывать из LoginScreen при успешном входе
    def open_main_menu(self, user_id: int):
        self.current_user_id = user_id
        sm: ScreenManager = self.root
        if not sm.has_screen('menu'):
            menu = MainMenuScreen(name='menu', db=self.db, user_id=user_id)
            sm.add_widget(menu)
        else:
            menu = sm.get_screen('menu')
            menu.user_id = user_id
            # если ассистент уже создавался — передадим и ему
            if menu._panels.get('assistant'):
                menu._panels['assistant'].set_user(user_id)
        sm.current = 'menu'

    def on_stop(self):
        if hasattr(self, 'db'):
            self.db.close_connection()


if __name__ == '__main__':
    GuitarProApp().run()
