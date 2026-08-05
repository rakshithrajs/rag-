"""Views for listing and adding knowledge sources."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.sources.forms import KnowledgeSourceForm
from apps.sources.models import KnowledgeSource
from apps.sources.tasks import process_source


def source_list(request: HttpRequest) -> HttpResponse:
    """Display all knowledge sources."""
    sources = KnowledgeSource.objects.all()
    return render(request, "sources/source_list.html", {"sources": sources})


def add_source(request: HttpRequest) -> HttpResponse:
    """Create a knowledge source and queue it for processing."""
    form = KnowledgeSourceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        source = form.save()
        process_source.enqueue(source.id)
        return redirect("sources:source_list")

    return render(request, "sources/add_source.html", {"form": form})
