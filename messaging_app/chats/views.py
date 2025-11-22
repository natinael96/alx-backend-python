"""
Views for the chats app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import CanAccessOwnData, IsMessageOwner, IsConversationParticipant


class BaseChatViewSet(viewsets.ModelViewSet):
    """
    Base viewset for chat-related models with authentication and permissions.
    """
    permission_classes = [IsAuthenticated, CanAccessOwnData]
    
    def get_queryset(self):
        """
        Filter queryset to only return objects the user has access to.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Filter based on model type
        if hasattr(queryset.model, 'sender'):
            # For messages: return messages where user is sender or receiver
            return queryset.filter(sender=user) | queryset.filter(receiver=user)
        elif hasattr(queryset.model, 'participants'):
            # For conversations: return conversations where user is a participant
            return queryset.filter(participants=user)
        elif hasattr(queryset.model, 'user'):
            # For generic objects with user field
            return queryset.filter(user=user)
        elif hasattr(queryset.model, 'owner'):
            # For generic objects with owner field
            return queryset.filter(owner=user)
        
        return queryset

