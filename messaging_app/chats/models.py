import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model extending AbstractUser"""
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Override email to ensure it's unique
    email = models.EmailField(unique=True, null=False, blank=False)
    
    # Make username nullable since we're using email
    username = models.CharField(max_length=150, null=True, blank=True, unique=True)
    
    # Override username to use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """Conversation model tracking participants"""
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'
        indexes = [
            models.Index(fields=['conversation_id']),
        ]
    
    def __str__(self):
        participant_count = self.participants.count()
        return f"Conversation {self.conversation_id} ({participant_count} participants)"


class Message(models.Model):
    """Message model containing sender and conversation"""
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
        ]
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
