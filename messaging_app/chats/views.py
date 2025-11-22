from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsOwnerOrParticipant, CanSendMessage
from .filters import MessageFilter
from .pagination import MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing conversations and creating new ones.
    
    - GET /conversations/ - List all conversations the user is part of
    - POST /conversations/ - Create a new conversation
    - GET /conversations/{id}/ - Retrieve a specific conversation
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    
    def get_queryset(self):
        """Return conversations where the authenticated user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages__sender').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a conversation and automatically add the current user as a participant"""
        conversation = serializer.save()
        # Automatically add the current user to participants if not already included
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override create to ensure current user is added to participant_ids"""
        # Get participant_ids from request data
        participant_ids = request.data.get('participant_ids', [])
        
        # Ensure current user is in the participant list
        current_user_id = str(request.user.user_id)
        if current_user_id not in participant_ids:
            participant_ids.append(current_user_id)
        
        # Update request data
        request.data['participant_ids'] = participant_ids
        
        return super().create(request, *args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing messages and sending messages to existing conversations.
    
    - GET /messages/ - List all messages (optionally filtered by conversation)
    - POST /messages/ - Send a new message to a conversation
    - GET /messages/{id}/ - Retrieve a specific message
    
    Filtering:
    - ?user=<user_id> - Filter by user (sender or participant)
    - ?sender=<user_id> - Filter by sender
    - ?participants=<user_id1,user_id2> - Filter by conversation participants
    - ?sent_at__gte=<datetime> - Messages sent after date
    - ?sent_at__lte=<datetime> - Messages sent before date
    - ?conversation=<conversation_id> - Filter by conversation
    """
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body']
    ordering_fields = ['sent_at', 'message_id']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Return messages filtered by conversation if provided, or all user's messages"""
        # Use Message.objects.filter to get messages
        queryset = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').order_by('-sent_at')
        
        # Filter by conversation if conversation_id is provided
        conversation_id = self.request.query_params.get('conversation_id', None)
        if conversation_id:
            # Ensure user is a participant in the conversation
            conversation = get_object_or_404(
                Conversation.objects.filter(participants=self.request.user),
                conversation_id=conversation_id
            )
            queryset = Message.objects.filter(conversation=conversation)
        else:
            # Only show messages from conversations the user is part of
            user_conversations = Conversation.objects.filter(
                participants=self.request.user
            )
            queryset = Message.objects.filter(conversation__in=user_conversations)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a message with the current user as sender"""
        # Get conversation_id from request data
        conversation_id = self.request.data.get('conversation_id')
        
        if not conversation_id:
            raise ValidationError({
                'conversation_id': 'This field is required.'
            })
        
        # Verify user is a participant in the conversation
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_id
        )
        
        # Check if user is participant, return 403 if not
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied(detail="You are not a participant in this conversation", code=status.HTTP_403_FORBIDDEN)
        
        # Save message with authenticated user as sender
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
    
    def perform_update(self, serializer):
        """Update a message - ensure user is participant"""
        message = self.get_object()
        if not message.conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied(detail="You are not a participant in this conversation", code=status.HTTP_403_FORBIDDEN)
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete a message - ensure user is participant"""
        if not instance.conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied(detail="You are not a participant in this conversation", code=status.HTTP_403_FORBIDDEN)
        instance.delete()
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """
        Custom action to send a message to a conversation.
        POST /messages/send/
        """
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not message_body:
            return Response(
                {'error': 'message_body is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user is a participant in the conversation
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=request.user),
            conversation_id=conversation_id
        )
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )
        
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
