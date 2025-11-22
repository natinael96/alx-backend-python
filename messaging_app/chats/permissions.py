from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class that:
    - Allows only authenticated users to access the API
    - Allows only participants in a conversation to send, view, update and delete messages
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated.
        Only authenticated users can access the API.
        For POST requests (creating messages), check if user is participant in the conversation.
        """
        if not (request.user and request.user.is_authenticated):
            return False
        
        # For POST requests (creating messages), check conversation participation
        if request.method == 'POST' and hasattr(view, 'get_serializer_class'):
            # Check if this is a message creation
            if hasattr(view, 'serializer_class') and view.serializer_class.__name__ == 'MessageSerializer':
                conversation_id = request.data.get('conversation_id')
                if conversation_id:
                    try:
                        conversation = Conversation.objects.get(conversation_id=conversation_id)
                        # User must be a participant to send messages
                        return conversation.participants.filter(user_id=request.user.user_id).exists()
                    except Conversation.DoesNotExist:
                        return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the object.
        - For messages: user must be a participant in the conversation to view, update, or delete
        - For conversations: user must be a participant
        - PUT, PATCH, DELETE methods require participant status
        """
        # If user is admin or staff, allow access
        if request.user.is_staff or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return True
        
        # For PUT, PATCH, DELETE methods, ensure user is participant
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # For Message objects
            if isinstance(obj, Message):
                # User must be a participant in the conversation to update or delete
                return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            
            # For Conversation objects
            if isinstance(obj, Conversation):
                # User must be a participant to update or delete
                return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # For Message objects (GET, PUT, PATCH, DELETE)
        if isinstance(obj, Message):
            # User must be a participant in the conversation to view, update, or delete
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # For Conversation objects
        if isinstance(obj, Conversation):
            # User must be a participant
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        return False


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

