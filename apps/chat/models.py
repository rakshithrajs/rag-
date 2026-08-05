from django.db import models

from apps.core.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """A sequence of messages about one or more knowledge sources."""

    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title or f"Conversation {self.id}"


class Message(TimeStampedModel):
    """A single turn in a conversation."""

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLES)
    content = models.TextField()
    source_chunks = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}"
