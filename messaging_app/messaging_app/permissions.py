"""
Custom permissions for the chats app.
Ensures users can only access their own messages and conversations.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed to any authenticated user.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.owner == request.user


class IsMessageOwner(permissions.BasePermission):
    """
    Permission to ensure users can only access their own messages.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the sender or receiver of the message
        return obj.sender == request.user or obj.receiver == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to ensure users can only access conversations they are part of.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        return request.user in obj.participants.all()


class IsOwner(permissions.BasePermission):
    """
    Permission to ensure users can only access their own objects.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the object
        # This assumes the object has a 'user' or 'owner' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        return False


class CanAccessOwnData(permissions.BasePermission):
    """
    Permission to ensure users can access their own messages and conversations.
    This is a more general permission that can be used for various models.
    """
    
    def has_permission(self, request, view):
        # Only authenticated users can access
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For messages: check if user is sender or receiver
        if hasattr(obj, 'sender') and hasattr(obj, 'receiver'):
            return obj.sender == request.user or obj.receiver == request.user
        
        # For conversations: check if user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For generic objects: check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Default: deny access if we can't determine ownership
        return False

