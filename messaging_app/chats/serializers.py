"""
Serializers for the chats app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='receiver',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'receiver',
            'sender_id', 'receiver_id', 'content',
            'created_at', 'is_read'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='participants',
        many=True,
        write_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids',
            'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

