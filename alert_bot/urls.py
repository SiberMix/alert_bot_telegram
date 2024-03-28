from django.contrib import admin
from django.urls import path

from alert_bot.views import SendTelegramView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('send-telegram/', SendTelegramView.as_view(), name='send_telegram'),

]
