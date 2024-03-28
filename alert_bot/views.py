from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from alert_bot.tasks import send_telegram


class SendTelegramView(View):
    @method_decorator(csrf_exempt)
    async def dispatch(self, *args, **kwargs):
        return await super().dispatch(*args, **kwargs)

    async def get(self, request, *args, **kwargs):
        await send_telegram()
        return HttpResponse("Telegram сообщение отправлено!")
