from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    user_id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at',
            'password',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': False},
            'created_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic User serializer for nested relationships (read-only)"""
    user_id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with nested sender information"""
    message_id = serializers.UUIDField(read_only=True)
    sender = UserBasicSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    conversation_id = serializers.UUIDField(write_only=True, required=False)
    sent_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'conversation_id',
            'message_body',
            'sent_at',
        ]
        extra_kwargs = {
            'conversation': {'read_only': True},
            'message_body': {'required': True},
        }
    
    def validate_message_body(self, value):
        """Validate message body"""
        if not value or not value.strip():
            raise ValidationError("Message body cannot be empty.")
        return value
    
    def validate_conversation_id(self, value):
        """Validate conversation ID"""
        if value:
            try:
                conversation = Conversation.objects.get(conversation_id=value)
            except Conversation.DoesNotExist:
                raise ValidationError("Conversation does not exist.")
        return value
    
    def create(self, validated_data):
        """Create a new message"""
        sender_id = validated_data.pop('sender_id', None)
        conversation_id = validated_data.pop('conversation_id', None)
        
        # Get sender from request context if not provided
        if not sender_id:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                sender_id = request.user.user_id
        
        if not sender_id:
            raise ValidationError("Sender ID is required.")
        
        if not conversation_id:
            raise ValidationError("Conversation ID is required.")
        
        validated_data['sender_id'] = sender_id
        validated_data['conversation_id'] = conversation_id
        
        return Message.objects.create(**validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested participants and messages"""
    conversation_id = serializers.UUIDField(read_only=True)
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at',
        ]
    
    def get_messages(self, obj):
        """Get messages for the conversation with proper nested relationships"""
        messages = obj.messages.all().select_related('sender')
        return MessageSerializer(messages, many=True, context=self.context).data
    
    def validate_participant_ids(self, value):
        """Validate participant IDs"""
        if value:
            # Check if all participant IDs exist
            existing_users = User.objects.filter(user_id__in=value)
            if existing_users.count() != len(value):
                raise ValidationError("One or more participant IDs are invalid.")
        return value
    
    def create(self, validated_data):
        """Create a new conversation with participants"""
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation
    
    def update(self, instance, validated_data):
        """Update conversation, handling participants"""
        participant_ids = validated_data.pop('participant_ids', None)
        
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            instance.participants.set(participants)
        
        instance.save()
        return instance

