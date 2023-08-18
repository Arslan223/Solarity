from peewee import (
    ForeignKeyField,
    CharField,
    IntegerField,
    BooleanField,
    TextField,
    DateTimeField,
    Model,
    PostgresqlDatabase,
)
from .config import DBSettings
import os

db_settings = DBSettings()
db = PostgresqlDatabase(
    db_settings.db_name,
    user=db_settings.db_user,
    password=db_settings.db_password,
    host=db_settings.db_host,
    port=db_settings.db_port
)


class Chat(Model):
    vk_id = IntegerField(unique=True, verbose_name="Chat ID")

    is_readonly = BooleanField(default=False, verbose_name="Is readonly")

    class Meta:
        database = db
        table_name = "chats"

    def set_readonly(self, readonly: bool):
        self.is_readonly = readonly
        self.save()


class User(Model):
    vk_id = IntegerField(unique=True, verbose_name="VK ID")

    class Meta:
        database = db
        table_name = "users"


class ChatMember(Model):
    user = ForeignKeyField(User, backref="member_instances", verbose_name="User")
    chat = ForeignKeyField(Chat, backref="members", verbose_name="Chat")

    is_muted = BooleanField(default=False, verbose_name="Is muted")
    is_banned = BooleanField(default=False, verbose_name="Is banned")

    class Meta:
        database = db
        table_name = "chat_members"

    def set_mute(self, is_muted: bool):
        self.is_muted = is_muted
        self.save()

    def set_ban(self, is_banned: bool):
        self.is_banned = is_banned
        self.save()


db.create_tables([Chat, User, ChatMember])
