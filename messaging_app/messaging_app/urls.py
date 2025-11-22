"""
URL configuration for the chats app.
"""
from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    # Add your chat-related URL patterns here
    # Example:
    # path('messages/', views.MessageListCreateView.as_view(), name='message-list'),
    # path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
]

