# controllers/chat_controller.py
from typing import Tuple, List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError


from database.db_handler import DatabaseHandler
from database.models import Chat, ChatMessage, MessageRole


class ChatController:
    """
    Контроллер для работы с чатами текущего пользователя.
    Возвращает (ok: bool, payload: Any), где payload — либо данные, либо сообщение об ошибке.
    """
    def __init__(self):
        self.db = DatabaseHandler()

    # ---------- Чаты ----------
    def create_chat(self, user_id: int, title: str = "Новый чат") -> Tuple[bool, Any]:
        if not user_id:
            return False, "user_id обязателен"
        title = (title or "").strip() or "Новый чат"

        try:
            chat = self.db.create_chat(user_id=user_id, title=title)
            if not chat:
                return False, "Не удалось создать чат"
            return True, {"id": chat.id, "title": chat.title}
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    def list_user_chats(self, user_id: int) -> Tuple[bool, Any]:
        if not user_id:
            return False, "user_id обязателен"
        try:
            chats: List[Chat] = self.db.get_chats_by_user(user_id=user_id)
            data = [
                {"id": c.id, "title": c.title, "created_at": getattr(c, "created_at", None)}
                for c in chats
            ]
            return True, data
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    def rename_chat(self, user_id: int, chat_id: int, new_title: str) -> Tuple[bool, Any]:
        if not (user_id and chat_id and new_title):
            return False, "user_id, chat_id и new_title обязательны"
        try:
            chat: Optional[Chat] = self.db.get_chat_by_id(chat_id=chat_id)
            if not chat or chat.user_id != user_id:
                return False, "Чат не найден или вам не принадлежит"

            chat = self.db.rename_chat(chat_id=chat_id, title=new_title.strip())
            if not chat:
                return False, "Не удалось переименовать чат"
            return True, {"id": chat.id, "title": chat.title}
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    def delete_chat(self, user_id: int, chat_id: int) -> Tuple[bool, Any]:
        if not (user_id and chat_id):
            return False, "user_id и chat_id обязательны"
        try:
            chat: Optional[Chat] = self.db.get_chat_by_id(chat_id=chat_id)
            if not chat or chat.user_id != user_id:
                return False, "Чат не найден или вам не принадлежит"

            ok = self.db.delete_chat(chat_id=chat_id)
            return (True, "Чат удалён") if ok else (False, "Не удалось удалить чат")
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    # ---------- Сообщения ----------
    def list_messages(self, user_id: int, chat_id: int) -> Tuple[bool, Any]:
        if not (user_id and chat_id):
            return False, "user_id и chat_id обязательны"
        try:
            chat: Optional[Chat] = self.db.get_chat_by_id(chat_id=chat_id)
            if not chat or chat.user_id != user_id:
                return False, "Чат не найден или вам не принадлежит"

            msgs: List[ChatMessage] = self.db.get_messages_by_chat(chat_id=chat_id)
            data = [
                {
                    "id": m.id,
                    "role": m.role.value if hasattr(m.role, "value") else str(m.role),
                    "content": m.content,
                    "created_at": getattr(m, "created_at", None)
                }
                for m in msgs
            ]
            return True, data
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    def add_message(self, user_id: int, chat_id: int, role: str, content: str) -> Tuple[bool, Any]:
        if not (user_id and chat_id and role and content):
            return False, "user_id, chat_id, role, content обязательны"

        # нормализуем роль
        role = role.strip().lower()
        if role not in ("user", "assistant", "system"):
            return False, "role должен быть 'user' | 'assistant' | 'system'"

        try:
            chat: Optional[Chat] = self.db.get_chat_by_id(chat_id=chat_id)
            if not chat or chat.user_id != user_id:
                return False, "Чат не найден или вам не принадлежит"

            msg = self.db.add_message(
                chat_id=chat_id,
                role=MessageRole(role),   # enum
                content=content.strip()
            )
            if not msg:
                return False, "Не удалось добавить сообщение"
            return True, {
                "id": msg.id,
                "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                "content": msg.content
            }
        except SQLAlchemyError as e:
            return False, f"DB error: {e}"

    # ---------- Утилиты ----------
    def close(self):
        self.db.close_connection()
