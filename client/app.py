"""Entry point for the Kivy application."""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

from .components.home import HomeScreen
from .components.login import LoginScreen
from .state import AppState


class GuitarProScreenManager(ScreenManager):
    """Simple screen manager that toggles between login and home."""

    def __init__(self, state: AppState, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.login_screen = LoginScreen(name="login", state=state, manager=self)
        self.home_screen = HomeScreen(name="home", state=state, manager=self)
        self.add_widget(self.login_screen)
        self.add_widget(self.home_screen)
        self.show_login()

    def show_login(self) -> None:
        self.current = "login"

    def show_home(self) -> None:
        self.current = "home"


class GuitarProApp(App):
    """Main Kivy application class."""

    def build(self) -> Screen:
        self.state = AppState()
        return GuitarProScreenManager(state=self.state)


if __name__ == "__main__":
    GuitarProApp().run()
