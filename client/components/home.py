"""Home screen showing a welcome message and profile info."""
from functools import partial

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from ..services.api import APIClient
from ..state import AppState
from .messages import MessageList


class HomeScreen(Screen):
    """Shows the authenticated user's profile information."""

    def __init__(self, *, state: AppState, manager, **kwargs):
        super().__init__(**kwargs)
        self.state = state
        self.manager = manager
        self.api = APIClient()
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.welcome_label = Label(text="Welcome", font_size=24, size_hint=(1, None), height=40)
        self.profile_label = Label(text="", size_hint=(1, None), height=30)
        self.refresh_button = Button(text="Refresh profile", size_hint=(1, None), height=44)
        self.logout_button = Button(text="Log out", size_hint=(1, None), height=44)
        self.refresh_button.bind(on_release=lambda *_: self.refresh_profile())
        self.logout_button.bind(on_release=lambda *_: self.logout())
        self.message_list = MessageList(messages=self.state.messages)
        self.layout.add_widget(self.welcome_label)
        self.layout.add_widget(self.profile_label)
        self.layout.add_widget(self.refresh_button)
        self.layout.add_widget(self.logout_button)
        self.layout.add_widget(self.message_list)
        self.add_widget(self.layout)

    def on_pre_enter(self, *_args) -> None:
        Clock.schedule_once(lambda *_: self.refresh_profile())

    def refresh_profile(self) -> None:
        if not self.state.token:
            self.profile_label.text = "Not authenticated"
            return
        Clock.schedule_once(partial(self._fetch_profile), 0)

    def _fetch_profile(self, *_args) -> None:
        try:
            profile = self.api.get_profile(token=self.state.token)
        except Exception as exc:  # pragma: no cover - runtime feedback
            message = f"Failed to fetch profile: {exc}"
            self.state.add_message(message)
            self.profile_label.text = message
            self._refresh_messages()
            return
        self.profile_label.text = f"User: {profile['username']} (joined {profile['joined']})"
        self.state.add_message("Profile refreshed")
        self._refresh_messages()

    def logout(self) -> None:
        self.state.clear()
        self.manager.show_login()
        self.state.add_message("Logged out")
        self._refresh_messages()

    def _refresh_messages(self) -> None:
        self.layout.remove_widget(self.message_list)
        self.message_list = MessageList(messages=self.state.messages)
        self.layout.add_widget(self.message_list)
