from django.db import models

from apps.core.models import TimeStampedModel
from apps.sources.models import KnowledgeSource


class Conversation(TimeStampedModel):
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation {self.id}"


class Message(TimeStampedModel):
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

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
