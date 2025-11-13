# components/main_menu.py
import os
from pathlib import Path

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import (
    ObjectProperty, NumericProperty, StringProperty,
    BooleanProperty, ListProperty
)
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.resources import resource_add_path, resource_find

# Панели
from components.autotune_screen import AutoTunePanel
from components.chords_screen import ChordsPanel
from components.assistant_screen import AssistantPanel
from components.profile_screen import ProfilePanel  # должен существовать

# --- Цвета/стили ---
ACCENT_ON  = (1.00, 0.90, 0.40, 1)  # жёлтый (активная подпись)
ACCENT_OFF = (0.75, 0.75, 0.78, 1)  # серый (неактивная подпись)
BAR_BG     = (0.05, 0.05, 0.05, 1)  # фон нижней плашки
TAB_BG     = (0.10, 0.10, 0.10, 1)  # фон кнопки

# --- База путей к иконкам (как у тебя) ---
ICON = {
    "autotune": ("assets/icons/guitar.png",     "assets/icons/autotune_active.png"),
    "chords":   ("assets/icons/accord.png",     "assets/icons/chords_active.png"),
    "assistant":("assets/icons/gpt.png",        "assets/icons/assistant_active.png"),
    "profile":  ("assets/icons/profile.png",    "assets/icons/profile_active.png"),
}

# Зарегистрируем папку ресурсов, чтобы относительные пути тоже находились
APP_DIR = Path(__file__).resolve().parents[1]     # .../GuitarPro
ASSETS_DIR = APP_DIR / "assets" / "icons"
resource_add_path(str(ASSETS_DIR))


def _resolve_icon(path_str: str) -> str:
    """Вернуть рабочий путь к картинке или '' если файла нет."""
    if not path_str:
        return ""
    # 1) через resource_find (ищет и по registered paths)
    found = resource_find(path_str)
    if found and os.path.exists(found):
        return found
    # 2) пробуем абсолютный путь внутри assets/icons/
    candidate = (ASSETS_DIR / Path(path_str).name).as_posix()
    if os.path.exists(candidate):
        return candidate
    return ""


class TabButton(ButtonBehavior, BoxLayout):
    """Кнопка нижней навигации: иконка + подпись, со сменой активной иконки и цвета."""
    key = StringProperty("")
    text = StringProperty("")
    icon_src = StringProperty("")
    icon_src_active = StringProperty("")
    active = BooleanProperty(False)
    active_color = ListProperty(ACCENT_ON)
    inactive_color = ListProperty(ACCENT_OFF)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = 1
        self.padding = [0, 6, 0, 6]
        self.spacing = 2

        # фон кнопки
        with self.canvas.before:
            Color(*TAB_BG)
            self._bg = RoundedRectangle(radius=[14, 14, 0, 0])

        # иконка
        self.img = Image(
            source="",
            size_hint_y=None,
            height=24,
            allow_stretch=True,
            keep_ratio=True
        )
        # подпись
        self.lbl_text = Label(text=self.text, font_size=12, color=self._color())

        # нижний индикатор-акцент (тонкая полоска)
        with self.canvas.after:
            Color(*ACCENT_ON)
            self._underline = Rectangle(size=(0, 0), pos=(0, 0))

        self.add_widget(Widget(size_hint_y=None, height=2))
        self.add_widget(self.img)
        self.add_widget(self.lbl_text)
        self.add_widget(Widget(size_hint_y=None, height=2))

        self.bind(pos=self._update_bg, size=self._update_bg)
        self.bind(active=self._on_active)
        self._apply_icon()
        Clock.schedule_once(lambda *_: self._update_underline(), 0)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._update_underline()

    def _update_underline(self):
        # Показываем полосу только когда активна
        if self.active:
            self._underline.size = (self.width * 0.6, 3)
            self._underline.pos = (self.x + self.width * 0.2, self.y + 2)
        else:
            self._underline.size = (0, 0)

    def _color(self):
        return self.active_color if self.active else self.inactive_color

    def _on_active(self, *args):
        self.lbl_text.color = self._color()
        self._apply_icon()
        self._update_underline()

    def _apply_icon(self):
        src_active = _resolve_icon(self.icon_src_active)
        src_inactive = _resolve_icon(self.icon_src)

        if self.active:
            self.img.source = src_active or src_inactive or ""
        else:
            self.img.source = src_inactive or src_active or ""

        # если файла нет — спрячем, чтобы не было белого квадрата
        self.img.opacity = 1.0 if self.img.source else 0.0

    def on_press(self):
        self.img.opacity = 0.7
        self.lbl_text.opacity = 0.7

    def on_release(self):
        self.img.opacity = 1
        self.lbl_text.opacity = 1


class BottomNav(BoxLayout):
    """Нижняя панель с 4 вкладками: АвтоТюн / Обучалка / Ассистент / Профиль."""
    on_tab_select = ObjectProperty(None)
    _tabs = ObjectProperty({})

    def __init__(self, on_tab_select, **kwargs):
        super().__init__(**kwargs)
        self.on_tab_select = on_tab_select
        self.size_hint_y = None
        self.height = 72
        self.orientation = 'horizontal'
        self.spacing = 10
        self.padding = [12, 8, 12, 10]

        with self.canvas.before:
            Color(*BAR_BG)
            self._bg = RoundedRectangle(radius=[16, 16, 0, 0])
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        self._tabs = {
            'autotune': TabButton(
                key='autotune', text='АвтоТюн',
                icon_src=ICON['autotune'][0],
                icon_src_active=ICON['autotune'][1]
            ),
            'chords': TabButton(
                key='chords', text='Обучалка',
                icon_src=ICON['chords'][0],
                icon_src_active=ICON['chords'][1]
            ),
            'assistant': TabButton(
                key='assistant', text='Ассистент',
                icon_src=ICON['assistant'][0],
                icon_src_active=ICON['assistant'][1]
            ),
            'profile': TabButton(
                key='profile', text='Профиль',
                icon_src=ICON['profile'][0],
                icon_src_active=ICON['profile'][1]
            ),
        }

        for key, tab in self._tabs.items():
            tab.bind(on_release=lambda t, k=key: self._select(k))
            self.add_widget(tab)

        self.set_active('autotune')

    def _upd_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _select(self, key: str):
        self.set_active(key)
        if self.on_tab_select:
            self.on_tab_select(key)

    def set_active(self, key: str):
        for k, tab in self._tabs.items():
            tab.active = (k == key)


class MainMenuScreen(Screen):
    """Главный экран приложения с нижней навигацией."""
    db = ObjectProperty(None)
    user_id = NumericProperty(0)  # 0 = гость

    def __init__(self, db=None, user_id=0, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.user_id = int(user_id or 0)

        root = BoxLayout(orientation='vertical', spacing=0, padding=0)

        # Контент
        self.content = BoxLayout(orientation='vertical')
        root.add_widget(self.content)

        # Нижняя навигация
        self.navbar = BottomNav(on_tab_select=self.on_tab_select)
        root.add_widget(self.navbar)

        self.add_widget(root)

        # Ленивые панели
        self._panels = {
            'autotune': None,
            'chords': None,
            'assistant': None,
            'profile': None,
        }

        Clock.schedule_once(lambda *_: self.on_tab_select('autotune'), 0)

    def on_tab_select(self, key: str):
        self.content.clear_widgets()

        # останов фоновых задач у предыдущих панелей
        for p in self._panels.values():
            if p and hasattr(p, 'on_leave_panel'):
                try:
                    p.on_leave_panel()
                except Exception:
                    pass

        if key == 'autotune':
            if self._panels['autotune'] is None:
                self._panels['autotune'] = AutoTunePanel()
            self.content.add_widget(self._panels['autotune'])

        elif key == 'chords':
            if self._panels['chords'] is None:
                self._panels['chords'] = ChordsPanel()
            self.content.add_widget(self._panels['chords'])

        elif key == 'assistant':
            if self._panels['assistant'] is None:
                self._panels['assistant'] = AssistantPanel(user_id=self.user_id)
            else:
                if getattr(self._panels['assistant'], 'user_id', 0) in (0, None) and self.user_id:
                    try:
                        self._panels['assistant'].set_user(self.user_id)
                    except Exception:
                        pass
            self.content.add_widget(self._panels['assistant'])

        elif key == 'profile':
            if self._panels['profile'] is None:
                self._panels['profile'] = ProfilePanel(user_id=self.user_id, db=self.db)
            else:
                self._panels['profile'].set_user(self.user_id)
            self.content.add_widget(self._panels['profile'])

        self.navbar.set_active(key)
