"""DRF API views for knowledge sources."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.core import chroma
from apps.sources.models import KnowledgeSource
from apps.sources.serializers import KnowledgeSourceSerializer
from apps.sources.tasks import process_source


class KnowledgeSourceViewSet(ModelViewSet):
    """List, create, retrieve, update, and delete knowledge sources."""

    queryset = KnowledgeSource.objects.all()
    serializer_class = KnowledgeSourceSerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer: KnowledgeSourceSerializer) -> None:
        source = serializer.save()
        process_source.enqueue(source.id)

    def perform_destroy(self, instance: KnowledgeSource) -> None:
        source_id = instance.id
        super().perform_destroy(instance)
        chroma.delete_source(source_id)


@api_view(["POST"])
def reprocess_source(request: Request, pk: int) -> Response:
    """Queue a source for re-processing."""
    try:
        source = KnowledgeSource.objects.get(pk=pk)
    except KnowledgeSource.DoesNotExist:
        return Response({"detail": "Source not found."}, status=status.HTTP_404_NOT_FOUND)

    source.status = KnowledgeSource.STATUS_PENDING
    source.save(update_fields=["status"])
    process_source.enqueue(source.id)
    return Response({"detail": "Re-processing queued."}, status=status.HTTP_202_ACCEPTED)
