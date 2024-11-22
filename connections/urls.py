from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('send_interest/<int:recipient_id>/', views.send_interest, name='send_interest'),
    path('interests/', views.interest_list, name='interest_list'),
    path('interest/<int:interest_id>/', views.accept_reject_interest, name='accept_reject_interest'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('save_message/', views.save_message, name='save_message'),
    path('load_chat/<int:user_id>/', views.load_chat, name='load_chat'),
]