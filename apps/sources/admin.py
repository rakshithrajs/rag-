from django.contrib import admin

from apps.sources.models import KnowledgeSource
from apps.sources.tasks import process_source


@admin.action(description="Re-process selected sources")
def reprocess_sources(modeladmin, request, queryset):
    for source in queryset:
        process_source.enqueue(source.id)


@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ["title", "source_type", "status", "created_at", "updated_at"]
    list_filter = ["source_type", "status"]
    search_fields = ["title"]
    actions = [reprocess_sources]
