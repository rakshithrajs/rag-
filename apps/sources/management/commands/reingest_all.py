"""Wipe Chroma chunks for sources and re-enqueue them for re-processing."""

from django.core.management.base import BaseCommand

from apps.core import chroma
from apps.sources.models import KnowledgeSource
from apps.sources.tasks import process_source


class Command(BaseCommand):
    help = "Wipe all Chroma chunks and re-enqueue every source for re-ingestion."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-id",
            type=int,
            action="append",
            help="Limit to specific source ids (may be repeated).",
        )

    def handle(self, *args, **options):
        ids = options.get("source_id")
        qs = KnowledgeSource.objects.all()
        if ids:
            qs = qs.filter(id__in=ids)
        sources = list(qs)
        if not sources:
            self.stdout.write("No sources found.")
            return

        for source in sources:
            chroma.delete_source(source.id)
            source.status = KnowledgeSource.STATUS_PENDING
            source.save(update_fields=["status"])
            process_source.enqueue(source.id)
            self.stdout.write(
                f"Queued {source.id} ({source.title}) for re-ingestion"
            )
        self.stdout.write(
            self.style.SUCCESS(f"Re-ingested {len(sources)} sources")
        )
