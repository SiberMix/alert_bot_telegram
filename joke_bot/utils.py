import random
from joke_bot.models import Joke, User


def get_random_joke():
    jokes = Joke.objects.all()
    return random.choice(jokes).text


def get_shuffled_users():
    users = list(User.objects.all())
    random.shuffle(users)
    return [user.username for user in users]
