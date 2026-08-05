from django.shortcuts import get_object_or_404, redirect, render

from apps.chat.models import Conversation, Message


def conversation_list(request):
    conversations = Conversation.objects.all()
    return render(request, "chat/conversation_list.html", {"conversations": conversations})


def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    return render(request, "chat/conversation_detail.html", {"conversation": conversation})


def new_conversation(request):
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


def ask(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.method == "POST":
        question = request.POST.get("question", "")
        Message.objects.create(
            conversation=conversation, role=Message.ROLE_USER, content=question
        )
        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content="This is a placeholder answer. RAG integration is coming next.",
        )
        return redirect("conversation_detail", pk=conversation.pk)
    return redirect("conversation_detail", pk=conversation.pk)
