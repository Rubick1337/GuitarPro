"""Widget that renders messages stored in the shared state."""
from typing import Iterable

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class MessageList(BoxLayout):
    """Vertical list of informational messages."""

    def __init__(self, *, messages: Iterable[str], **kwargs):
        super().__init__(orientation="vertical", spacing=4, size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        for message in messages:
            self.add_widget(Label(text=message, size_hint_y=None, height=24))
