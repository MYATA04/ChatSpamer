import datetime
import json
import os.path

from pyrogram import Client, errors
from pyrogram.enums import ParseMode


def main():
    print("Добрый день! Для создания или замены текущей сессий нужны вот эти данные:\n\n"
          "1. api id от аккаунта телеграм\n"
          "2. api hash от аккаунта телеграм\n"
          "3. Номер телефона от акканута телеграм\n"
          "4. ID чата где вы будете управлять ботом\n"
          "5. @user_name от вашего телеграм аккаунта\n\n\n"
          "api id и api hash можно получить по этой ссылке с помощью регистрации: https://my.telegram.org/auth;\n"
          "Номер телефона для того что бы вы не вводили и не подтверждали номер телефона;\n"
          "ID чата можно ввести ваш, тогда бот сможет отвечать только на ваши сообщения. Если в качестве аккаунта бота указали свой, то вы сможете общаться в чате \"Избранное\". ID чата можно получить в этом боте: https://t.me/username_to_id_bot;\n"
          "@user_name для того, что бы сессия всегда проверяла работоспособность, отправив вам сегоднешнию дату, при его созданий.")

    while True:
        # Get api id
        api_id = input("\nОтправьте \"api_id\" от аккаунта телеграм данного юзер-бота (в числовом виде: 123456789): ")

        if api_id.isdigit():
            break

    while True:
        # Get api hash
        api_hash = input(
            "\nОтправьте \"api hash\" от аккаунта телеграм данного юзер-бота (в текстовом виде: erjl224124kcsdv21434Hshc): ")

        if not api_hash.isdigit():
            break

    while True:
        # Get num user bot account
        num = input("\nОтправьте номер телефона от аккаунта телеграм данного юзер-бота\n\t\t"
                    "(в числовом виде, без пробелов, без плюсов, если +7 то просто 7, например: 79008009988): ")

        if num.isdigit():
            break

    while True:
        # Get the ID of the chat in which everything will happen with the user_bot
        main_chat = input("\nОтправьте ID чата, в котором будете взаимодействовать с юзер-ботом.\n"
                          "Его можно получить, перейдя по этой ссылке: https://t.me/username_to_id_bot.\n"
                          "Там можно получить ID пользователя, чата, канала или даже бота (отправьте в числовом виде, например: 546789456): ")

        if main_chat.isdigit():
            break

    while True:
        # We receive a link to the owner’s telegram
        main_user_name = input("\nОтправьте @user_name или же ссылку на ваш телеграм\n\t\t"
                               "(не в числовом виде, юзер-бот отправит тестовый текст по этому юзер-нейму, например: https://t.me/username): ")

        if main_user_name.isdigit():
            print("Нужно не числовое значение!")

        elif main_user_name[0] != "@" and "https://t.me/" not in main_user_name:
            print("Отправьте реальный юзер-нейм (@user_name) или ссылку (https://t.me/username)!")

        else:
            if "https://t.me/" in main_user_name:
                main_user_name = main_user_name.replace("https://t.me/", "@")

            break

    text = f"\napi_id:  {api_id}\n" \
           f"api_hash:  {api_hash}\n" \
           f"номер телефона аккаунта юзер-бота:  {num}\n" \
           f"id чата в котором вы будете работать с юзер-ботом:  {main_chat}\n"

    text += "\nВсе правильно? Если да, отправьте - Д, если хотите отменить - О, и заново запустите файл если хотите повторить: "

    while True:
        check = input(text)

        if check == "О":
            return

        if check == "Д":
            break

    print("\nДавайте теперь протестируем нашего юзер бота! Вам нужно будет ввести сперва код который придет на\n"
          "телеграм аккаунт этого главного юзер бота.\n"
          "Если у аккаунта есть двухфакторная аутентификация, вам потребуется ввести пароль от аккаунта бота.\n")

    try:
        if os.path.exists("session.session"):
            os.remove("session.session")

        if os.path.exists("session.session-journal"):
            os.remove("session.session-journal")

    except:
        return print("\nТекущяя сессия занята, невозможно поменять! Прошу удалить или остановить бота, для замены сессий!")

    try:
        app = Client(
            api_id=api_id,
            api_hash=api_hash,
            phone_number=f"+{num}",
            name="session",
            parse_mode=ParseMode.HTML
        )

    except:
        print("\nДумаю, вы указали не верный номер телефона аккаунта юзер-бота. Повторите попытку, перезапустив этот файл."
              "\nНажмите на любую клавишу для закрытия . . .")

        return

    try:
        app.start()

        app.send_message(chat_id=main_user_name,
                         text=f"<pre>{datetime.datetime.now()}</pre>")

    except errors.exceptions.PeerIdInvalid:
        print("\nУвы, но вы указали не верный юзер-нейм. Повторите попытку перезапустив этот файл."
              "\nНажмите на любую клавишу для закрытия . . .")

    except KeyboardInterrupt:
        pass

    except Exception:
        print("\nУвы, но вы указали не верные параметры. Повторите попытку перезапустив этот файл."
              "\nНажмите на любую клавишу для закрытия . . .")

    else:
        print("\nЗапуск успешен! Данные будут сохранены. Нажмите на любую клавишу для закрытия . . .")

        data = {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "phone_number": f"+{num}",
            "name": "session",
            "main_chat_id": int(main_chat)
        }

        with open("database/bot.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    try:
        app.stop()

    except:
        pass


if __name__ == '__main__':
    try:
        main()

    except (KeyboardInterrupt, SystemExit):
        pass
