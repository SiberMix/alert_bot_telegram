import datetime
import os
import random

from asgiref.sync import sync_to_async
from telegram import Bot

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
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    bot = Bot(token=bot_token)
    current_day_of_week = datetime.datetime.today().weekday()

    user_list = await get_user_list()
    joke = await get_random_joke()

    if current_day_of_week == 4:  # Пятница
        message_text = ("Сегодня нет дейли. \n"
                        "Шутка дня:\n{}").format(joke.text)

    else:
        message_text = "Порядок проведения дейли:\n{}".format("\n".join([user.username for user in user_list]))
        message_text += "\n\n"
        message_text += "Шутка дня:\n{}".format(joke.text)
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML')
