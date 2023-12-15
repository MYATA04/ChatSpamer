from typing import Union

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery

from database.functions import get_main_chat_id


async def is_admin_func(_, __, query_or_message: Union[Message, CallbackQuery]) -> bool:
    """Checking if this chat is the main one"""
    admin_id = await get_main_chat_id()

    try:
        return int(query_or_message.chat.id) == int(admin_id)

    except:
        return False


is_admin = filters.create(is_admin_func)


def texts_filter(texts: Union[list[str, ...], str]) -> bool:
    """Custom Filter: check state FSM"""

    async def state_filter_check(_, __, message: Message) -> bool:
        try:
            if isinstance(texts, list):
                return message.text in texts

            return message.text == texts

        except:
            return False

    return filters.create(state_filter_check)
