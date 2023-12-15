import datetime
import asyncio
import sys
from typing import Union

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid
from pyrogram.types import Message

from config import HELP_COMMANDS
from filters import is_admin, texts_filter
from fsm.fsm import main_fsm
from database.functions import get_chats, get_chat_ids, get_chat_name, add_chat, del_chat, get_message_id, \
    set_message_id, get_intervals, set_interval_chat, set_interval_chats, set_flag, get_flag, set_to_true_flag, \
    get_main_chat_id
from logger.create_logger import logger
from client import app, scheduler

'''______________________________| MAILING |______________________________'''


# Function: Mailing, number of functions: 5
async def mailing_starter_scheduler(chats_interval: int = None) -> None:
    """Launches a mailing at a specific time"""
    chat_ids = await get_chat_ids()

    if not chat_ids:
        return

    flag = await mailing_check()

    if not flag:
        return

    if chats_interval is None:
        intervals = await get_intervals()
        chats_interval = int(intervals[1])

    run_date = datetime.datetime.now() + datetime.timedelta(minutes=chats_interval)

    try:
        scheduler.add_job(func=mailing, trigger="date", run_date=run_date, id="mailing")

    except:
        return

    logger.info(f"[MAILING] The next mailing will take effect in \"{chats_interval}\" minutes.")


async def mailing_check() -> None:
    """Checking whether mailing can continue"""
    flag = await get_flag()

    logger.info("[MAILING] It is not possible to start sending yet, the flag is set to False.")

    return flag


async def sleeping(chat_id: Union[int, str], chat_name: str, type_spam: Union[str, None] = None) -> None:
    """type_spam in ["chat", ...]"""
    intervals = await get_intervals()

    if type_spam == "chat":
        chat_interval = int(intervals[0]) * 60

        logger.info(f"[MAILING] Sent to mail chat with id - {chat_id}, and name - {chat_name}.")

        await asyncio.sleep(chat_interval)


async def check_chat(chat_id: Union[int, str], chat_name: str) -> bool:
    """Check the chat to see if you can send a mail there"""
    try:
        await app.get_chat(chat_id=chat_id)

    except:
        logger.info(
            f"[MAILING] No mail was sent to the chat with ID - {chat_id}, and name {chat_name}. Please delete this chat or check if this account is present in this chat.")

        await app.send_message(chat_id=chat_id,
                               text=f"В чат с идентификатором — {chat_id} и именем {chat_name} не было отправлена рассылка. "
                                    f"Пожалуйста, удалите этот чат или проверьте, присутствует ли этот аккаунт в этом чате.")

        return False

    else:
        return True


async def mailing() -> None:
    """Main mailing function"""
    chat_ids = await get_chat_ids()
    message_id, from_chat_id = (await get_message_id())[:2]

    for chat_id in chat_ids:
        chat_name = await get_chat_name(chat_id)

        if not await mailing_check():
            return

        if not await check_chat(chat_id, chat_name):
            continue

        try:
            logger.info(
                f"[MAILING] We send the newsletter to the chat with ID - {chat_id} and name - {chat_name} . . .")
            await app.forward_messages(chat_id=chat_id,
                                       from_chat_id=from_chat_id,
                                       message_ids=message_id)

        except MessageIdInvalid:
            text = "<i><b>Текущий текст для рассылки потерян или был удален из чата, по этому, рассылка остановится.</b></i>"

            await set_flag(False)

            return await app.send_message(chat_id=await get_main_chat_id(),
                                          text=text)

        await sleeping(chat_id, chat_name, "chat")

    intervals = await get_intervals()
    chats_interval = int(intervals[1])
    chat_interval = int(intervals[0])

    await mailing_starter_scheduler(chats_interval - chat_interval)


'''______________________________| HANDLERS |______________________________'''

'''____________________| START |____________________'''


# Command: start, number of handlers: 1
@app.on_message(filters.command("start", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_start(_, message: Message):
    """Command: start"""
    text = ("Добрый день 👋\n"
            "\n"
            "Вы являетесь владельцем бота, вот доступные вам команды:\n\n") + HELP_COMMANDS

    text += "\n\nРассылка начнется как только вы создадите (команда - <code>/setmsg</code>) сообщение для рассылки."

    await app.send_message(chat_id=message.chat.id,
                           text=text)


'''____________________| HELP |____________________'''


# Command: help, number of handlers: 1
@app.on_message(filters.command("help", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_help(_, message: Message):
    """Command: help"""
    text = HELP_COMMANDS

    await app.send_message(chat_id=message.chat.id,
                           text=text)


'''____________________| CHATS |____________________'''


# Command: chats, number of handlers: 1
@app.on_message(filters.command("chats", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_chats(_, message: Message):
    """Command: chats"""
    chats = await get_chats()

    if not chats:
        return await app.send_message(chat_id=message.chat.id,
                                      text="Пока чатов для рассылки нет.")

    text = ""
    count = 1

    for chat in chats:
        text += f"\n<b>{count}</b>.  id: <code>{chat[0]}</code>; name: <code>{chat[1]}</code>"
        count += 1

    await app.send_message(chat_id=message.chat.id,
                           text=text)


'''____________________| CANCEL |____________________'''


# Text: ["Отмена", "отмена", "Отменить", "отменить", "о", "О"], number of handlers: 1
@app.on_message(filters.text & texts_filter(["Отмена", "отмена", "Отменить", "отменить", "о", "О"]) & is_admin)
async def text_cancel(_, message: Message):
    """Text: cancel, cleaning fsm"""
    current_state = await main_fsm.get_state()

    if current_state == "chill":
        return

    await main_fsm.clear()

    text = "<i><b>Действия успешно отменены!</b></i>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info("[CUSTOM] Canceled state: %s" % current_state)


'''____________________| ADDCHAT |____________________'''


# Command: addchat, number of handlers: 4
@app.on_message(filters.command("addchat", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_addchat_step_1(_, message: Message):
    """Command: addchat, step 1"""
    text = ("Для добавления чата для рассылки, нужны вот эти данные:\n\n"
            "1. ID чата (его можно получить в этом боте: https://t.me/username_to_id_bot)\n"
            "2. Название чата (можно написать что угодно, просто чат будет хранится под этим названием).")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = "Сперва, отправьте ID чата (числовое значение):"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.add_chat_1)


@app.on_message(filters.text & is_admin & main_fsm.check_state(main_fsm.add_chat_1))
async def cmd_addchat_step_2(_, message: Message):
    """Command: addchat, step 2"""
    chat_ids = await get_chat_ids()

    if message.text[0] != "-" or not message.text[1:].isdigit():
        if message.text[0] == "-":
            text = "<i>Отправьте <b>числовое</b> значение:</i>"

            return await app.send_message(chat_id=message.chat.id,
                                          text=text)

    elif message.text in chat_ids:
        chat_name = await get_chat_name(message.text)

        if chat_name:
            text = f"<i>Данный чат уже присутсвует под названием: <b>{chat_name}</b></i>"

            return await app.send_message(chat_id=message.chat.id,
                                          text=text)

    try:
        await app.get_chat(message.text)

    except:
        text = f"<i>Аккаунт не добавлен в чат или такого чата просто не существует.</i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    await main_fsm.set_data(chat_id=message.text)

    text = "Теперь, отправьте название (любое) чата (текстовое значение):"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.add_chat_2)


@app.on_message(filters.text & is_admin & main_fsm.check_state(main_fsm.add_chat_2))
async def cmd_addchat_step_3(_, message: Message):
    """Command: addchat, step 3"""
    data = await main_fsm.get_data()
    chat_id = data['chat_id']

    await main_fsm.set_data(chat_name=message.text)

    text = f"id: <code>{chat_id}</code>; name: <code>{message.text}</code>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = (
        "Чтобы подтвердить <b>добавление чата</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>добавление чата</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.add_chat_3)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.add_chat_3))
async def cmd_addchat_step_4(_, message: Message):
    """Command: addchat, step 4"""
    data = await main_fsm.get_data()
    chat_id = data['chat_id']
    chat_name = data['chat_name']

    await main_fsm.clear()

    await add_chat(chat_id, chat_name)

    text = (f"<i><b>Чат успешно добавлен!</b></i>\n\n"
            f"          id: <code>{chat_id}</code>; name: <code>{chat_name}</code>")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = "<b>Рассылка вступит в силу в этот чат, после рассылки во все текущие чаты.</b>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    chats = await get_chats()

    text = ""
    count = 1

    for chat in chats:
        text += f"\n<b>{count}</b>.  id: <code>{chat[0]}</code>; name: <code>{chat[1]}</code>"
        count += 1

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(f"[CUSTOM] New chat added: chat_id: {chat_id}; chat_name: {chat_name}")


'''____________________| DELCHAT |____________________'''


# Command: delchat, number of handlers: 3
@app.on_message(filters.command("delchat", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_delchat_step_1(_, message: Message):
    """Command: delchat, step 1"""
    chats = await get_chats()

    text = ""
    count = 1

    for chat in chats:
        text += f"\n<b>{count}</b>.  id: <code>{chat[0]}</code>; name: <code>{chat[1]}</code>"
        count += 1

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = "Отправьте ID чата, которого хотите убрать (в числовом виде):"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.del_chat_1)


@app.on_message(filters.text & is_admin & main_fsm.check_state(main_fsm.del_chat_1))
async def cmd_delchat_step_2(_, message: Message):
    """Command: delchat, step 2"""
    chat_ids = await get_chat_ids()

    if message.text not in chat_ids:
        text = f"<i>Отправьте id чата из списка сверху.</i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    chat_name = await get_chat_name(message.text)
    chat_id = message.text

    await main_fsm.set_data(chat_id=chat_id)
    await main_fsm.set_data(chat_name=chat_name)

    text = f"id: <code>{chat_id}</code>; name: <code>{chat_name}</code>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = (
        "Чтобы подтвердить <b>удаление чата</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>удаление чата</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.del_chat_2)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.del_chat_2))
async def cmd_delchat_step_3(_, message: Message):
    """Command: delchat, step 3"""
    data = await main_fsm.get_data()
    chat_id = data['chat_id']
    chat_name = data['chat_name']

    await main_fsm.clear()

    await del_chat(chat_id)

    text = (f"<i><b>Чат успешно удален!</b></i>\n\n"
            f"          id: <code>{chat_id}</code>; name: <code>{chat_name}</code>")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    text = ("<b>Если идет рассылка, и в этот чат еще не отправлялась рассылка, то сперва "
            "рассылка отправится в этот чат, и после конца полной рассылки, чат удалится.</b>")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    chats = await get_chats()

    text = ""
    count = 1

    for chat in chats:
        text += f"\n<b>{count}</b>.  id: <code>{chat[0]}</code>; name: <code>{chat[1]}</code>"
        count += 1

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(f"[CUSTOM] Chat deleted: chat_id: {chat_id}; chat_name: {chat_name}")


'''____________________| MSG |____________________'''


# Command: msg, number of handlers: 1
@app.on_message(filters.command("msg", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_msg(_, message: Message):
    """Command: msg"""
    message_id, from_chat_id, date = await get_message_id()

    if message_id == 0:
        text = (
            "<i>До этого момента не совершалась рассылка, по этому на данный момент нет сохраненных сообщений рассылки.\n\n"
            "Для создания рассылки, отправьте команду - <code>/setmsg</code>.\n"
            "Вы можете остановить рассылку в любой момент, отправив команду - <code>/stopmsg</code>.</i>")

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    try:
        await app.forward_messages(chat_id=message.chat.id,
                                   from_chat_id=from_chat_id,
                                   message_ids=message_id)

        text = (f"ID данного сообщения: <code>{message_id}</code>\n"
                f"ID чата где было создано данное сообщение: <code>{from_chat_id}</code>\n"
                f"Дата начала рассылки этого сообщения: <code>{date}</code>")

        await app.send_message(chat_id=message.chat.id,
                               text=text)

    except:
        text = f"<i>Сообщение было удалено из чата с ID - <code>{from_chat_id}</code>, или он не действителен.</i>"

        await app.send_message(chat_id=message.chat.id,
                               text=text)


'''____________________| SETMSG |____________________'''


# Command: setmsg, number of handlers: 3
@app.on_message(filters.command("setmsg", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_setmsg_step_1(_, message: Message):
    """Command: setmsg, step 1"""
    text = "Отправьте сообщение для рассылки:"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.set_msg_1)


@app.on_message(is_admin & main_fsm.check_state(main_fsm.set_msg_1))
async def cmd_setmsg_step_2(_, message: Message):
    """Command: setmsg, step 2"""
    message_id = message.id
    from_chat_id = message.chat.id

    await main_fsm.set_data(message_id=message_id)
    await main_fsm.set_data(from_chat_id=from_chat_id)

    try:
        await app.forward_messages(chat_id=message.chat.id,
                                   from_chat_id=from_chat_id,
                                   message_ids=message_id)

    except BaseException as e:
        text = (f"<i>Данное сообщение не подходит для рассылки.\n\n"
                f"Ошибка: {e}</i>")

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    text = (
        "Чтобы подтвердить <b>замену или создание сообщения для рассылки</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>замену или создание сообщения для рассылки</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.set_msg_2)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.set_msg_2))
async def cmd_setmsg_step_3(_, message: Message):
    """Command: setmsg, step 3"""
    data = await main_fsm.get_data()
    message_id = data['message_id']
    from_chat_id = data['from_chat_id']
    date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    await main_fsm.clear()

    await set_message_id(message_id, from_chat_id, date)

    text = ("<b><i>Сообщение рассылки изменено!</i>\n\n"
            "Если ранее не запускалась рассылка, оно вступит в силу сразу, а если запускалась, вступит после того как "
            "закончит текущий цикл рассылки во все чаты, а если рассылка во все чаты закончена, "
            "и рассылка спит, то данное сообщение вступит в силу после спячки.</b>")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(
        f"[CUSTOM] The mailing message has been changed: message_id: {message_id}; from_chat_id: {from_chat_id}; date: {date}")

    if not await get_flag():
        await set_flag(True)
        await mailing()


'''____________________| STARTMSG |____________________'''


# Command: startmsg, number of handlers: 2
@app.on_message(filters.command("startmsg", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_startmsg_step_1(_, message: Message):
    """Command: stopmsg"""
    if await get_flag():
        text = "<i><b>На данный момент, рассылка активна.</b></i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    text = (
        "Чтобы подтвердить <b>старт рассылки</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>старт рассылки</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.start_msg_1)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.start_msg_1))
async def cmd_startmsg_step_2(_, message: Message):
    """Command: startmsg, step 2"""
    await main_fsm.clear()

    text = f"<i><b>Рассылка началась!</b></i>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(f"[CUSTOM] Mailing started")

    await set_flag(True)
    await mailing()


'''____________________| STOPMSG |____________________'''


# Command: stopmsg, number of handlers: 2
@app.on_message(filters.command("stopmsg", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_stopmsg_step_1(_, message: Message):
    """Command: stopmsg"""
    if not await get_flag():
        text = "<i><b>На данный момент, рассылка не активна.<b></i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    text = (
        "Чтобы подтвердить <b>остановку рассылки</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>остановку рассылки</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.stop_msg_1)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.stop_msg_1))
async def cmd_stopmsg_step_2(_, message: Message):
    """Command: stopmsg, step 2"""
    await main_fsm.clear()

    text = f"<i><b>Рассылка остановлена!</b></i>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await set_flag(False)

    try:
        if not scheduler.get_job(job_id="mailing"):
            scheduler.remove_job(job_id="mailing")

    except:
        pass

    logger.info(f"[CUSTOM] Mailing stopped")


'''____________________| INT |____________________'''


# Command: int, number of handlers: 3
@app.on_message(filters.command("int", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_int(_, message: Message):
    """Command: int"""
    chat_interval, chats_interval = await get_intervals()

    text = (f"Интервал рассылки между чатами: <code>{chat_interval}</code> мин.\n"
            f"Интервал рассылки между полными рассылками: <code>{chats_interval}</code> мин.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)


'''____________________| INTCHAT |____________________'''


# Command: intchat, number of handlers: 3
@app.on_message(filters.command("intchat", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_intchat_step_1(_, message: Message):
    """Command: intchat, step 1"""
    text = "Отправьте интервал рассылки между чатами (в минутах, в числовом виде):"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.int_chat_1)


@app.on_message(filters.text & is_admin & main_fsm.check_state(main_fsm.int_chat_1))
async def cmd_intchat_step_2(_, message: Message):
    """Command: intchat, step 2"""
    if not message.text.isdigit():
        text = "<i>Отправьте <b>числовое</b> значение:</i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    interval_chat = int(message.text)

    await main_fsm.set_data(interval_chat=interval_chat)

    text = (
        "Чтобы подтвердить <b>замену интервала рассылки между чатами</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>замену интервала рассылки между чатами</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.int_chat_2)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.int_chat_2))
async def cmd_intchat_step_3(_, message: Message):
    """Command: intchat, step 3"""
    data = await main_fsm.get_data()
    interval_chat = data['interval_chat']

    await main_fsm.clear()

    await set_interval_chat(interval_chat)

    text = f"<i><b>Интервал рассылки между чатами изменен на - {interval_chat} мин.!</b></i>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(f"[CUSTOM] The mailing interval between chats has been changed: {interval_chat}")


'''____________________| INTCHATS |____________________'''


# Command: intchats, number of handlers: 3
@app.on_message(filters.command("intchats", prefixes="/") & is_admin & main_fsm.check_state(main_fsm.chill))
async def cmd_intchats_step_1(_, message: Message):
    """Command: intchat, step 1"""
    text = "Отправьте интервал рассылки между полными рассылками (в минутах, в числовом виде):"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.int_chats_1)


@app.on_message(filters.text & is_admin & main_fsm.check_state(main_fsm.int_chats_1))
async def cmd_intchats_step_2(_, message: Message):
    """Command: intchats, step 2"""
    if not message.text.isdigit():
        text = "<i>Отправьте <b>числовое</b> значение:</i>"

        return await app.send_message(chat_id=message.chat.id,
                                      text=text)

    interval_chats = int(message.text)

    await main_fsm.set_data(interval_chats=interval_chats)

    text = (
        "Чтобы подтвердить <b>замену интервала рассылки между полными рассылками</b>, отправьте одно из этих сообщений: <code>П</code> ; <code>п</code> ; "
        "<code>Подтвердить</code> ; <code>подтвердить</code>.\n\n"
        "Чтобы отменить <b>замену интервала рассылки между полными рассылками</b>, отправьте одно из этих сообщений: <code>О</code> ; <code>о</code> ; <code>Отмена</code> ; "
        "<code>отмена</code> ; <code>Отменить</code> ; <code>отменить</code>.")

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    await main_fsm.set_state(main_fsm.int_chats_2)


@app.on_message(filters.text & texts_filter(["Подтвердить", "подтвердить", "П", "п"]) & is_admin & main_fsm.check_state(
    main_fsm.int_chats_2))
async def cmd_intchats_step_3(_, message: Message):
    """Command: intchats, step 3"""
    data = await main_fsm.get_data()
    interval_chats = data['interval_chats']

    await main_fsm.clear()

    await set_interval_chats(interval_chats)

    text = f"<i><b>Интервал рассылки между полными рассылками изменен на - {interval_chats} мин.!</b></i>"

    await app.send_message(chat_id=message.chat.id,
                           text=text)

    logger.info(f"[CUSTOM] The mailing interval between full mailings has been changed: {interval_chats}")


'''______________________________| RUN |______________________________'''

if __name__ == '__main__':
    try:
        scheduler.start()
        set_to_true_flag()

        try:
            scheduler.remove_job(job_id="mailing")

        except:
            pass

        scheduler.add_job(func=mailing_starter_scheduler, trigger="date",
                          run_date=(datetime.datetime.now() + datetime.timedelta(seconds=30)), id="mailing")

        app.run()

    except (KeyboardInterrupt, SystemExit):
        logger.critical("[BOT] BOT IS STOPPED!")
        sys.exit()

    except BaseException as ex:
        logger.critical(f"[BOT] BOT IS STOPPED! ERROR: {ex}")
        raise ex
