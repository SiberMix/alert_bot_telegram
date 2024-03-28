from django.db import models


class Joke(models.Model):
    text = models.TextField()
    used = models.BooleanField(default=False)

    @classmethod
    def reset_all(cls):
        cls.objects.update(used=False)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Шутка'
        verbose_name_plural = 'Шутки'


class User(models.Model):
    username = models.CharField(max_length=255)
    absent = models.BooleanField(verbose_name='Отсутствие', default=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Юзер в чате'
        verbose_name_plural = 'Юзеры в чате'
