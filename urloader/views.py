"""Django views for the URL summarizer app."""

import logging

from django.conf import settings
from django.shortcuts import render

from .services import (
    SUPPORTED_LANGUAGES,
    SummarizerError,
    process_url_question,
    run_ollama_diagnostics,
    validate_url,
)

logger = logging.getLogger("urloader")


def _render_index(request, error=None, url="", question="", language="english"):
    """Render the index form, preserving user input and showing an optional error."""
    return render(
        request,
        "index.html",
        {
            "error": error,
            "url": url,
            "question": question,
            "language": language,
            "languages": SUPPORTED_LANGUAGES,
        },
    )


def index(request):
    """Render the main input form."""
    return _render_index(request)


def summary(request):
    """Process a URL + question and display the generated answer."""
    if request.method != "POST":
        return _render_index(request)

    url = request.POST.get("url", "").strip()
    question = request.POST.get("question", "").strip()
    language = request.POST.get("language", "english").strip().lower()

    # Basic client-side-friendly validation before hitting the network.
    if not url:
        return _render_index(request, "Please enter a URL.", url, question, language)

    if not question:
        return _render_index(request, "Please enter a question.", url, question, language)

    if language not in SUPPORTED_LANGUAGES:
        language = "english"

    try:
        # Validate the URL format before doing any network or model work.
        validate_url(url)
    except SummarizerError as exc:
        return _render_index(request, exc.message, url, question, language)

    try:
        result = process_url_question(url, question, language)
    except SummarizerError as exc:
        logger.warning("Summarizer error: %s", exc.detail or exc.message)
        return render(
            request,
            "error.html",
            {
                "error_title": "Couldn’t process that page",
                "error_message": exc.message,
                "error_detail": exc.detail,
            },
        )
    except Exception as exc:
        logger.exception("Unexpected error processing URL %s", url)
        return render(
            request,
            "error.html",
            {
                "error_title": "Something went wrong",
                "error_message": "An unexpected error occurred. Please try again in a moment.",
                "error_detail": str(exc) if settings.DEBUG else None,
            },
        )

    return render(request, "summary_display.html", result)


def test_ollama(request):
    """Render diagnostics for both Ollama connections."""
    diagnostics = run_ollama_diagnostics()
    any_missing_model = any(d["ok"] and not d["model_found"] for d in diagnostics)
    return render(
        request,
        "test_ollama.html",
        {
            "diagnostics": diagnostics,
            "any_missing_model": any_missing_model,
        },
    )


