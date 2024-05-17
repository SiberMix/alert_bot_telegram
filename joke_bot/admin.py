from django.contrib import admin

from joke_bot.models import Joke, User


@admin.register(Joke)
class Joke(admin.ModelAdmin):
    pass


@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ['username', 'absent', 'backend']
