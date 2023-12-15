import json
from typing import Union


# Chats, number of functions: 6
async def get_main_chat_id() -> int:
    """Getting the main chat ID"""
    with open("database/bot.json") as file:
        data = json.load(file)

    admin_id = int(data['main_chat_id'])

    return admin_id


async def get_chat_ids() -> list[str, ...]:
    """Get chats IDs for mailing"""
    with open("database/data.json") as file:
        data = json.load(file)

    data_chats: dict = data['chats']
    chat_ids = data_chats.keys()

    return chat_ids


async def get_chats() -> list[(str, str), ...]:
    """Get chat IDs and names for mailing [(chat id, chat name), ...]"""
    with open("database/data.json") as file:
        data = json.load(file)

    data_chats: dict = data['chats']
    chats = [(key, value) for key, value in data_chats.items()]

    return chats


async def get_chat_name(chat_id: Union[int, str]) -> Union[None, str]:
    """Get chat IDs and names for mailing chat name"""
    with open("database/data.json") as file:
        data = json.load(file)

    data_chats: dict = data['chats']

    for key, value in data_chats.items():
        if key == str(chat_id):
            chat_name = value

            return chat_name

    return None


async def add_chat(chat_id: Union[int, str], chat_name: str) -> None:
    """Adding a new chat for mailing"""
    with open("database/data.json") as file:
        data = json.load(file)

    data['chats'][str(chat_id)] = chat_name

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def del_chat(chat_id: Union[int, str]) -> None:
    """Deleting a chat for mailing"""
    with open("database/data.json") as file:
        data = json.load(file)

    chat_ids = await get_chat_ids()

    if str(chat_id) in chat_ids:
        del data['chats'][str(chat_id)]

        with open("database/data.json", "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


# Mailing message, number of functions: 4
async def get_message_id() -> list[int, str, str]:
    """Get mailing message ID and from chat ID and start date"""
    with open("database/data.json") as file:
        data = json.load(file)

    msg_id = int(data['message_id'])
    from_chat_id = data['from_chat_id']
    date = data['date']

    return [msg_id, from_chat_id, date]


async def set_message_id(message_id: Union[int, str], from_chat_id: str, date: str) -> None:
    """Change mailing message ID"""
    msg_id = int(message_id)

    with open("database/data.json") as file:
        data = json.load(file)

    data['message_id'] = msg_id
    data['from_chat_id'] = from_chat_id
    data['date'] = date

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def set_flag(flag: bool) -> None:
    """Changing the mailing flag (True or False)"""
    with open("database/data.json") as file:
        data = json.load(file)

    data['flag'] = int(flag)

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def set_to_true_flag() -> None:
    """Changing the mailing flag (True or False)"""
    with open("database/data.json") as file:
        data = json.load(file)

    data['flag'] = int(True)

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def get_flag() -> bool:
    """Get permission to send mails"""
    with open("database/data.json") as file:
        data = json.load(file)

    flag = int(data['flag'])

    return bool(flag)


# Sending interval, number of functions: 4
async def get_intervals() -> list[int, int]:
    """Get mailing intervals [interval chat, interval chats]"""
    with open("database/data.json") as file:
        data = json.load(file)

    interval_chat = int(data['int_chat_minutes'])
    interval_chats = int(data['int_chats_minutes'])

    return [interval_chat, interval_chats]


async def set_interval_chat(interval: int) -> None:
    """Changing the sending interval between chats"""
    interval = int(interval)

    with open("database/data.json") as file:
        data = json.load(file)

    data['int_chat_minutes'] = interval

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def set_interval_chats(interval: int) -> None:
    """Changing the mailing interval after a full mailing"""
    interval = int(interval)

    with open("database/data.json") as file:
        data = json.load(file)

    data['int_chats_minutes'] = interval

    with open("database/data.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
