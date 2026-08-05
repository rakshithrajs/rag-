"""Views for chat conversations."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.chat.models import Conversation, Message
from apps.chat.rag import generate_answer


def conversation_list(request: HttpRequest) -> HttpResponse:
    """Display all conversations."""
    conversations = Conversation.objects.all()
    return render(request, "chat/conversation_list.html", {"conversations": conversations})


def conversation_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Display a single conversation with its messages."""
    conversation = get_object_or_404(Conversation, pk=pk)
    return render(request, "chat/conversation_detail.html", {"conversation": conversation})


def new_conversation(request: HttpRequest) -> HttpResponse:
    """Create a new conversation with an initial question."""
    if request.method == "POST":
        title = request.POST.get("title", "")
        conversation = Conversation.objects.create(title=title)
        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content=request.POST.get("initial_question", ""),
        )
        return redirect("conversation_detail", pk=conversation.pk)
    return render(request, "chat/new_conversation.html")


def ask(request: HttpRequest, pk: int) -> HttpResponse:
    """Handle a follow-up question and generate a grounded answer."""
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.method == "POST":
        question = request.POST.get("question", "")
        language = request.POST.get("output_language", "English")

        Message.objects.create(
            conversation=conversation, role=Message.ROLE_USER, content=question
        )

        answer, source_chunks = generate_answer(conversation, question, language)

        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=answer,
            source_chunks=source_chunks,
        )
        return redirect("conversation_detail", pk=conversation.pk)
    return redirect("conversation_detail", pk=conversation.pk)
