from django.contrib import admin

from apps.sources.models import KnowledgeSource


@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ["title", "source_type", "status", "created_at", "updated_at"]
    list_filter = ["source_type", "status"]
    search_fields = ["title"]
