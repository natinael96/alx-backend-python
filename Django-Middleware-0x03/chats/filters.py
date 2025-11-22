from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
    """
    Filter class for messages.
    Allows filtering by:
    - conversation participants (users)
    - time range (sent_at)
    """
    # Filter by specific user (sender or participant in conversation)
    user = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method='filter_by_user',
        label='User (sender or participant)'
    )
    
    # Filter by sender
    sender = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        label='Message sender'
    )
    
    # Filter by conversation participants
    participants = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        method='filter_by_participants',
        label='Conversation participants'
    )
    
    # Time range filters
    sent_at__gte = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        label='Sent after (ISO 8601 format)'
    )
    
    sent_at__lte = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        label='Sent before (ISO 8601 format)'
    )
    
    # Filter by conversation
    conversation = filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        label='Conversation'
    )
    
    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_at__gte', 'sent_at__lte']
    
    def filter_by_user(self, queryset, name, value):
        """
        Filter messages where the user is either the sender
        or a participant in the conversation.
        """
        if value:
            return queryset.filter(
                Q(sender=value) |
                Q(conversation__participants=value)
            ).distinct()
        return queryset
    
    def filter_by_participants(self, queryset, name, value):
        """
        Filter messages from conversations that include all specified participants.
        """
        if value:
            for user in value:
                queryset = queryset.filter(conversation__participants=user)
            return queryset.distinct()
        return queryset

