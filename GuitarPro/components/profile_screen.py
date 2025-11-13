# components/profile_screen.py
from pathlib import Path
import os

from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.resources import resource_add_path, resource_find
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex

APP_DIR   = Path(__file__).resolve().parents[1]
ICONS_DIR = APP_DIR / "assets" / "icons"
resource_add_path(str(ICONS_DIR))

PROFILE_ICON_PATH = "assets/icons/profile.png"

class ProfilePanel(BoxLayout):
    user_id = NumericProperty(0)
    db = ObjectProperty(None)

    user_name  = StringProperty("Пользователь")
    user_email = StringProperty("email не указан")

    def __init__(self, user_id=0, db=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [16, 16, 16, 16]
        self.spacing = 12

        self.user_id = int(user_id or 0)
        self.db = db
        self._load_user()

        # ===== Весь контент по центру =====
        root_center = AnchorLayout(anchor_x="center", anchor_y="center")
        column = BoxLayout(orientation="vertical", spacing=16,
                           size_hint=(None, None), width=420)
        # высота колонны будет подстраиваться под контент
        root_center.add_widget(column)

        # ----- Аватар строго по центру -----
        avatar_holder = AnchorLayout(size_hint=(1, None), height=140)
        avatar_bg = AnchorLayout(size_hint=(None, None), width=120, height=120)

        with avatar_bg.canvas.before:
            self._av_bg_c = Color(1, 1, 1, 0.08)
            self._av_bg = RoundedRectangle(radius=[60, 60, 60, 60])

        def _paint_av_bg(*_):
            self._av_bg.pos = avatar_bg.pos
            self._av_bg.size = avatar_bg.size
        avatar_bg.bind(pos=_paint_av_bg, size=_paint_av_bg)

        self.avatar = Image(
            source=self._resolve_img(PROFILE_ICON_PATH),
            allow_stretch=False, keep_ratio=True,
            size_hint=(None, None)
        )

        def _fit_avatar(*_):
            side = max(1, min(avatar_bg.width, avatar_bg.height) - 12)
            self.avatar.size = (side, side)
        avatar_bg.bind(size=_fit_avatar)
        _fit_avatar()

        avatar_bg.add_widget(self.avatar)
        avatar_holder.add_widget(avatar_bg)
        column.add_widget(avatar_holder)

        # ----- Имя и email по центру -----
        self.lbl_name = Label(
            text=self.user_name,
            font_size=24, bold=True,
            color=get_color_from_hex("#FFFFFF"),
            halign="center", valign="middle",
            size_hint=(1, None), height=34
        )
        self.lbl_email = Label(
            text=self.user_email,
            font_size=16,
            color=get_color_from_hex("#BBBBBB"),
            halign="center", valign="middle",
            size_hint=(1, None), height=26
        )
        self.lbl_name.bind(size=lambda *_: setattr(self.lbl_name, "text_size", self.lbl_name.size))
        self.lbl_email.bind(size=lambda *_: setattr(self.lbl_email, "text_size", self.lbl_email.size))
        column.add_widget(self.lbl_name)
        column.add_widget(self.lbl_email)

        # ----- Кнопка выхода (пилюля) -----
        self.btn_logout = Button(
            text="Выйти из аккаунта",
            font_size=18, bold=True,
            size_hint=(1, None), height=56,
            background_normal="", background_down="", background_color=(0, 0, 0, 0),
            color=get_color_from_hex("#FFFFFF")
        )
        with self.btn_logout.canvas.before:
            self._sh_c = Color(0, 0, 0, 0.35)
            self._sh = RoundedRectangle(radius=[28, 28, 28, 28])
            self._bg_c = Color(*get_color_from_hex("#6A1B9A"))
            self._bg = RoundedRectangle(radius=[28, 28, 28, 28])
            self._ring_c = Color(1, 1, 1, 0.08)
            self._ring = RoundedRectangle(radius=[28, 28, 28, 28])

        def _repaint_btn(*_):
            # центр кнопки в пределах column
            self._sh.pos = (self.btn_logout.x, self.btn_logout.y - 3)
            self._sh.size = (self.btn_logout.width, self.btn_logout.height)
            self._bg.pos = self.btn_logout.pos
            self._bg.size = self.btn_logout.size
            self._ring.pos = (self.btn_logout.x + 1, self.btn_logout.y + 1)
            self._ring.size = (self.btn_logout.width - 2, self.btn_logout.height - 2)

        def _state_btn(*_):
            self._bg_c.rgba = get_color_from_hex("#5A1784") if self.btn_logout.state == "down" else get_color_from_hex("#6A1B9A")
            self._ring_c.a = 0.14 if self.btn_logout.state == "down" else 0.08

        self.btn_logout.bind(pos=_repaint_btn, size=_repaint_btn, state=_state_btn)
        _repaint_btn(); _state_btn()

        self.btn_logout.bind(on_release=lambda *_: self._logout())
        column.add_widget(self.btn_logout)

        # добавляем центрирующий контейнер в сам экран
        self.add_widget(root_center)

        # обновим тексты из _load_user()
        self._refresh_labels()

    # ---------- API для MainMenu ----------
    def set_user(self, user_id: int):
        self.user_id = int(user_id or 0)
        self._load_user()
        self._refresh_labels()

    def on_leave_panel(self):
        pass

    # ---------- Внутреннее ----------
    def _resolve_img(self, path_str: str) -> str:
        found = resource_find(path_str)
        if found and os.path.exists(found):
            return found
        fallback = (ICONS_DIR / Path(path_str).name).as_posix()
        return fallback if os.path.exists(fallback) else ""

    def _load_user(self):
        """Подтянуть имя и email из БД (ORM-объект User)."""
        name, email = "", ""
        try:
            if self.db and self.user_id:
                rec = None
                if hasattr(self.db, "get_user_by_id"):
                    rec = self.db.get_user_by_id(self.user_id)
                if rec is not None:
                    # ORM объект: читаем атрибуты; запасной дефолт
                    name = getattr(rec, "username", None) or getattr(rec, "name", "") or "Пользователь"
                    email = getattr(rec, "email", None) or getattr(rec, "mail", "") or "email не указан"
        except Exception:
            pass

        self.user_name = name or "Пользователь"
        self.user_email = email or "email не указан"

    def _refresh_labels(self):
        self.lbl_name.text = self.user_name
        self.lbl_email.text = self.user_email

    def _logout(self):
        app = App.get_running_app()
        try:
            app.current_user_id = None
        except Exception:
            pass
        try:
            sm = app.root
            if sm.has_screen('welcome'):
                sm.current = 'welcome'
        except Exception:
            pass
