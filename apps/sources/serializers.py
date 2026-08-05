"""Serializers for knowledge source API."""

from rest_framework import serializers

from apps.sources.models import KnowledgeSource


class KnowledgeSourceSerializer(serializers.ModelSerializer):
    """Serializer for KnowledgeSource model."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_type_display = serializers.CharField(source="get_source_type_display", read_only=True)

    class Meta:
        model = KnowledgeSource
        fields = [
            "id",
            "title",
            "source_type",
            "source_type_display",
            "file",
            "url",
            "status",
            "status_display",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "metadata"]
