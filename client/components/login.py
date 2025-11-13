"""Login screen implementation."""
from functools import partial

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from ..services.api import APIClient
from ..state import AppState
from .messages import MessageList


class LoginForm(BoxLayout):
    """Vertical form containing username/password inputs."""

    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    def __init__(self, *, on_submit, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)
        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False)
        submit_button = Button(text="Log In", size_hint=(1, None), height=44)
        submit_button.bind(on_release=lambda *_: on_submit(self.username_input.text, self.password_input.text))
        self.add_widget(self.username_input)
        self.add_widget(self.password_input)
        self.add_widget(submit_button)


class LoginScreen(Screen):
    """Screen that allows the user to log in and fetch a JWT token."""

    def __init__(self, *, state: AppState, manager, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.manager = manager
        self.api = APIClient()
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.status_label = Label(text="Please sign in to continue", size_hint=(1, None), height=30)
        self.form = LoginForm(on_submit=self.on_submit)
        self.message_list = MessageList(messages=self.state.messages)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.form)
        self.layout.add_widget(self.message_list)
        self.add_widget(self.layout)

    def on_submit(self, username: str, password: str) -> None:
        """Handle form submission asynchronously."""
        self.status_label.text = "Logging in..."
        Clock.schedule_once(partial(self._process_login, username, password), 0)

    def _process_login(self, username: str, password: str, *_args) -> None:
        try:
            token = self.api.login(username=username, password=password)
        except Exception as exc:  # pragma: no cover - runtime feedback
            message = f"Login failed: {exc}"
            self.status_label.text = message
            self.state.add_message(message)
            self._refresh_messages()
            return
        self.state.set_credentials(token=token, username=username)
        self.state.add_message("Login successful")
        self.status_label.text = "Success!"
        self.manager.show_home()
        self._refresh_messages()

    def _refresh_messages(self) -> None:
        self.layout.remove_widget(self.message_list)
        self.message_list = MessageList(messages=self.state.messages)
        self.layout.add_widget(self.message_list)
