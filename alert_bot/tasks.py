import datetime
import os
import random

from asgiref.sync import sync_to_async
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from joke_bot.models import User, Joke


async def get_user_list():
    return await sync_to_async(list)(User.objects.all().filter(absent=False))


async def get_random_joke():
    jokes = await sync_to_async(list)(Joke.objects.filter(used=False))
    if not jokes:
        await sync_to_async(Joke.reset_all)()
        jokes = await sync_to_async(list)(Joke.objects.all())
    return random.choice(jokes)


async def send_telegram():
    bot_token = "6242307150:AAEmGth3OFS036PNEen1bjTUapjrvxZSfzY"
    chat_id = '-4055169739'
    bot = Bot(token=bot_token)
    current_day_of_week = datetime.datetime.today().weekday()
    user_list = await get_user_list()
    user_list = random.sample(user_list, len(user_list))
    if current_day_of_week in [0, 2]:  # Понедельник или среда
        backend_users = await get_user_list()
        backend_users = random.sample(backend_users, len(backend_users))
        backend_users_for_release = [user for user in backend_users if user.backend]
        if backend_users:
            chosen_user = random.choice(backend_users_for_release)
            message_text = "Порядок проведения дейли:\n{}".format("\n".join([user.username for user in backend_users]))
            message_text += f"\n\nСегодня релиз RAFINAD собирает: {chosen_user.username}"
            chosen_user_kitcpa = random.choice(backend_users_for_release)
            while chosen_user_kitcpa == chosen_user:
                chosen_user_kitcpa = random.choice(backend_users_for_release)
            message_text += f"\n\nСегодня релиз KITCPA собирает: '{chosen_user_kitcpa}\n"

    else:
        joke = await get_random_joke()

        if current_day_of_week == 4:  # Пятница
            message_text = ("Сегодня нет дейли. \n"
                            "Шутка дня:\n{}").format(joke.text)
        else:
            random_users = random.sample(user_list, len(user_list))  # Выбираем случайные пользователей из списка
            message_text = "Порядок проведения дейли:\n{}".format("\n".join([user.username for user in random_users]))
            message_text += "\n\n"

    # Отправка сообщения с изображением
    message_text += "\n\n"
    message_text += "ССЫЛКА НА ДЕЙЛИ: https://meet.google.com/izk-wghu-sdg"
    with open('img.png', 'rb') as img:
        media = InputMediaPhoto(media=img, caption=message_text, parse_mode='HTML')
        await bot.send_media_group(chat_id=chat_id, media=[media])
