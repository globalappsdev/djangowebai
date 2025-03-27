# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chatbot.js', views.chatbot_js, name='chatbot_js'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
]