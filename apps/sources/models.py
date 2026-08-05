from django.db import models

from apps.core.models import TimeStampedModel


class KnowledgeSource(TimeStampedModel):
    SOURCE_TYPE_PDF = "pdf"
    SOURCE_TYPE_TXT = "txt"
    SOURCE_TYPE_URL = "url"
    SOURCE_TYPES = [
        (SOURCE_TYPE_PDF, "PDF"),
        (SOURCE_TYPE_TXT, "Text"),
        (SOURCE_TYPE_URL, "URL"),
    ]

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_READY = "ready"
    STATUS_ERROR = "error"
    STATUSES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_READY, "Ready"),
        (STATUS_ERROR, "Error"),
    ]

    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUSES, default=STATUS_PENDING)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
