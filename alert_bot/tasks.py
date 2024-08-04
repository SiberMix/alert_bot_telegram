import datetime
import os
import random
import requests
import logging

from asgiref.sync import sync_to_async
from telegram import Bot, InputMediaPhoto
from joke_bot.models import User, Joke
from dotenv import load_dotenv

load_dotenv()

VK_API_VERSION = '5.131'
VK_ACCESS_TOKEN = os.getenv('API_HASH')
VK_GROUP_ID = os.getenv('SOURCE_CHANNEL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_list():
    return await sync_to_async(list)(User.objects.all().filter(absent=False))


async def get_random_joke():
    jokes = await sync_to_async(list)(Joke.objects.filter(used=False))
    if not jokes:
        await sync_to_async(Joke.reset_all)()
        jokes = await sync_to_async(list)(Joke.objects.all())
    return random.choice(jokes)


def get_random_vk_image():
    logger.info("Fetching images from VK group...")
    url = f"https://api.vk.com/method/wall.get?owner_id=-{VK_GROUP_ID}&count=100&access_token={VK_ACCESS_TOKEN}&v={VK_API_VERSION}"
    try:
        response = requests.get(url, timeout=30)  # Увеличиваем тайм-аут до 30 секунд
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from VK: {e}")
        return None

    if 'error' in response_json:
        logger.error(f"Error fetching from VK: {response_json['error']}")
        return None

    posts = response_json.get('response', {}).get('items', [])
    image_urls = []

    for post in posts:
        if 'attachments' in post:
            for attachment in post['attachments']:
                if attachment['type'] == 'photo':
                    sizes = attachment['photo']['sizes']
                    image_url = sizes[-1]['url']  # Выбираем изображение наибольшего размера
                    image_urls.append(image_url)

    if image_urls:
        chosen_image = random.choice(image_urls)
        logger.info(f"Chosen image URL: {chosen_image}")
        return chosen_image
    else:
        logger.info("No images found in VK group.")
        return None


async def send_telegram():
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
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
            message_text += f"\n\nСегодня релиз KITCPA собирает: {chosen_user_kitcpa}\n"
    else:
        joke = await get_random_joke()

        if current_day_of_week == 4:  # Пятница
            message_text = ("Сегодня нет дейли. \n"
                            "Шутка дня:\n{}").format(joke.text)
        else:
            random_users = random.sample(user_list, len(user_list))  # Выбираем случайных пользователей из списка
            message_text = "Порядок проведения дейли:\n{}".format("\n".join([user.username for user in random_users]))
            message_text += "\n\n"

    image_url = get_random_vk_image()
    if image_url:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open('img.png', 'wb') as img_file:
                img_file.write(response.content)

            logger.info("Image successfully downloaded.")

            with open('img.png', 'rb') as img:
                media = InputMediaPhoto(media=img, caption=message_text, parse_mode='HTML')
                await bot.send_media_group(chat_id=chat_id, media=[media])
                logger.info("Message with image sent to Telegram.")
        else:
            logger.error(f"Failed to download image. Status code: {response.status_code}")
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML')
    else:
        await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='HTML')
        logger.info("Message without image sent to Telegram.")
