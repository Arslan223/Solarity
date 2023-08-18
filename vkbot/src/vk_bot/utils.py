from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard, ShowSnackbarEvent, KeyboardButtonColor
from vkbottle import API

from .models import User, Chat
from .config import VKSettings, DBSettings

import typing as tp


class VKCommunicator:
    def __init__(self, api: API, settings: VKSettings = VKSettings()):
        self.api = api
        self.settings = settings

    async def delete_message(self, message_id: int, peer_id: int) -> bool:
        try:
            await self.api.messages.delete(cmids=[message_id], delete_for_all=True, peer_id=peer_id)
            return True
        except Exception as e:
            print(f"Error while deleting message: {e}")
            return False

    async def kick_user(self, user_id: int, chat_id: int) -> bool:
        try:
            await self.api.messages.remove_chat_user(chat_id=chat_id - 2000000000, member_id=user_id)
            return True
        except Exception as e:
            print(f"Error while kicking user: {e}")
            return False

    async def is_user_admin(self, user_id: int, chat_id: int) -> bool:
        try:
            chat_info = await self.api.messages.get_conversations_by_id(peer_ids=[chat_id])
            return user_id in chat_info.items[0].chat_settings.admin_ids
        except Exception as e:
            print(f"Error while checking if user is admin: {e}")
            return False

    async def get_id_by_username(self, username: str) -> tp.Optional[int]:
        try:
            response = await self.api.users.get(user_ids=[username])
            print(response)
            if len(response) == 0:
                return None
            return response[0].id
        except Exception as e:
            print(f"Error while getting id by username: {e}")
            return None
