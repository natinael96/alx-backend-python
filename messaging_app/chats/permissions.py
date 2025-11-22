from rest_framework import permissions
from .models import Conversation, Message


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own messages
    and conversations they are part of.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the object.
        - For messages: user must be the sender or a participant in the conversation
        - For conversations: user must be a participant
        """
        # If user is admin, allow access
        if request.user.is_staff or request.user.role == 'admin':
            return True
        
        # For Message objects
        if isinstance(obj, Message):
            # User can access if they sent the message
            if obj.sender == request.user:
                return True
            # User can access if they are a participant in the conversation
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # For Conversation objects
        if isinstance(obj, Conversation):
            # User can access if they are a participant
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class CanSendMessage(permissions.BasePermission):
    """
    Permission to check if user can send a message to a conversation.
    User must be a participant in the conversation.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is a participant in the conversation"""
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        return False

