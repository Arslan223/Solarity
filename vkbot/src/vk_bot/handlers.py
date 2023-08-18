from vkbottle import Callback, GroupEventType, GroupTypes, Keyboard, ShowSnackbarEvent
from vkbottle.bot import Bot, MessageEvent, Message, rules
from vkbottle.dispatch.rules.base import CommandRule, ChatActionRule

from .models import User, Chat, ChatMember
from .config import VKSettings, DBSettings
from .utils import VKCommunicator

import typing as tp

vk_settings = VKSettings()

bot = Bot(vk_settings.api_token)
vk_comm = VKCommunicator(bot.api, vk_settings)


async def prepare_command(message, args: tp.Tuple[str]) -> tp.Optional[
    tp.Tuple[str, tp.Union[None, tp.Dict[str, tp.Any]]]]:
    chat = Chat.get_or_none(vk_id=message.peer_id)
    if chat is None:
        chat = Chat.create(vk_id=message.peer_id)

    if await vk_comm.is_user_admin(message.from_id, message.peer_id):
        return "Вы не являетесь администратором чата.", None

    vk_id = None
    if len(args) == 1:
        username = args[0]
        vk_id = await vk_comm.get_id_by_username(username)
        if vk_id is None:
            return "Пользователь не найден.", None
    else:
        # replied message user
        if message.reply_message is None:
            return "Вы не указали пользователя.", None
        vk_id = message.reply_message.from_id

    if vk_id is None:
        return "Пользователь не найден.", None

    user = User.get_or_none(vk_id=vk_id)
    if user is None:
        user = User.create(vk_id=vk_id)

    chat_member = ChatMember.get_or_none(user=user, chat=chat)

    return "ok", {
        "user": user,
        "chat": chat,
        "chat_member": chat_member
    }


@bot.on.chat_message(CommandRule("readonly", ["!"], 0))
async def readonly_command_handler(message) -> tp.Optional[str]:
    chat = Chat.get_or_none(vk_id=message.peer_id)
    if chat is None:
        chat = Chat.create(vk_id=message.peer_id)

    if await vk_comm.is_user_admin(message.from_id, message.peer_id):
        return "Вы не являетесь администратором чата."

    chat.set_readonly(not chat.is_readonly)

    answer_text = ""
    if chat.is_readonly:
        answer_text = "Теперь всем пользователям кроме администраторов чат доступен только для чтения."
    else:
        answer_text = "Теперь все могут писать в чат."

    return answer_text


@bot.on.chat_message(CommandRule("mute", ["!"], 1))
async def mute_command_handler(message, args: tp.Tuple[str]) -> tp.Optional[str]:
    prep = await prepare_command(message, args)
    if prep[1] is None:
        return prep[0]
    user, chat, chat_member = prep[1]["user"], prep[1]["chat"], prep[1]["chat_member"]

    chat_member.set_mute(True)

    return "Пользователю выдан mute."


@bot.on.chat_message(CommandRule("ban", ["!"], 1))
async def ban_command_handler(message, args: tp.Tuple[str]) -> tp.Optional[str]:
    prep = await prepare_command(message, args)
    if prep[1] is None:
        return prep[0]
    user, chat, chat_member = prep[1]["user"], prep[1]["chat"], prep[1]["chat_member"]

    chat_member.set_ban(True)
    await vk_comm.kick_user(user.vk_id, chat.vk_id)

    return "Пользователю выдан ban."


@bot.on.chat_message(CommandRule("kick", ["!"], 1))
async def kick_command_handler(message, args: tp.Tuple[str]) -> tp.Optional[str]:
    prep = await prepare_command(message, args)
    if prep[1] is None:
        return prep[0]
    user, chat, chat_member = prep[1]["user"], prep[1]["chat"], prep[1]["chat_member"]

    await vk_comm.kick_user(user.vk_id, chat.vk_id)

    return "Пользователь кикнут."


@bot.on.chat_message(CommandRule("unmute", ["!"], 1))
async def unmute_command_handler(message, args: tp.Tuple[str]) -> tp.Optional[str]:
    prep = await prepare_command(message, args)
    if prep[1] is None:
        return prep[0]
    user, chat, chat_member = prep[1]["user"], prep[1]["chat"], prep[1]["chat_member"]

    chat_member.set_mute(False)

    return "Пользователю снят mute."


@bot.on.chat_message(CommandRule("unban", ["!"], 1))
async def unban_command_handler(message, args: tp.Tuple[str]) -> tp.Optional[str]:
    prep = await prepare_command(message, args)
    if prep[1] is None:
        return prep[0]
    user, chat, chat_member = prep[1]["user"], prep[1]["chat"], prep[1]["chat_member"]

    chat_member.set_ban(False)

    return "Пользователю снят ban."


# Message handlers

@bot.on.chat_message(ChatActionRule("chat_invite_user"))
async def chat_invite_user_handler(message) -> tp.Optional[str]:
    chat = Chat.get_or_none(vk_id=message.peer_id)
    if chat is None:
        chat = Chat.create(vk_id=message.peer_id)

    invited_user_id = message.action.member_id
    invited_user = User.get_or_none(vk_id=invited_user_id)
    if invited_user is None:
        invited_user = User.create(vk_id=invited_user_id)
    chat_member = ChatMember.get_or_none(user=invited_user, chat=chat)
    if chat_member is None:
        chat_member = ChatMember.create(user=invited_user, chat=chat)

    if chat_member.is_banned:
        if vk_comm.is_user_admin(message.from_id, message.peer_id):
            chat_member.set_ban(False)
            return f"Пользователь {invited_user_id} разбанен, так как он был приглашен администратором."

        await vk_comm.kick_user(invited_user_id, message.peer_id)

    return


@bot.on.chat_message()
async def chat_message_handler(message) -> tp.Optional[str]:
    chat = Chat.get_or_none(vk_id=message.peer_id)
    if chat is None:
        chat = Chat.create(vk_id=message.peer_id)

    user = User.get_or_none(vk_id=message.from_id)
    if user is None:
        user = User.create(vk_id=message.from_id)

    chat_member = ChatMember.get_or_none(user=user, chat=chat)
    if chat_member is None:
        chat_member = ChatMember.create(user=user, chat=chat)

    if chat_member.is_banned:
        await vk_comm.kick_user(message.from_id, message.peer_id)

    if chat.is_readonly:
        await vk_comm.delete_message(message.message_id, message.peer_id)
        return

    if chat_member.is_muted:
        await vk_comm.delete_message(message.message_id, message.peer_id)
        return

    return
