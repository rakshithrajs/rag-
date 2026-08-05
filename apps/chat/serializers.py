"""Serializers for chat API."""

from rest_framework import serializers

from apps.chat.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""

    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "role",
            "role_display",
            "content",
            "source_chunks",
            "created_at",
        ]


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations with nested messages."""

    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "messages",
            "created_at",
            "updated_at",
        ]
