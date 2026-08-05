"""DRF API views for chat conversations."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.chat.models import Conversation, Message
from apps.chat.rag import generate_answer
from apps.chat.serializers import ConversationSerializer, MessageSerializer


@api_view(["GET", "POST"])
def conversation_list_create(request: Request) -> Response:
    """List conversations or create a new one."""
    if request.method == "GET":
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    title = request.data.get("title", "")
    conversation = Conversation.objects.create(title=title)
    if initial_question := request.data.get("initial_question", "").strip():
        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content=initial_question,
        )

    serializer = ConversationSerializer(conversation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def conversation_detail(request: Request, pk: int) -> Response:
    """Retrieve a single conversation with messages."""
    try:
        conversation = Conversation.objects.prefetch_related("messages").get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ConversationSerializer(conversation)
    return Response(serializer.data)


@api_view(["POST"])
def ask(request: Request, pk: int) -> Response:
    """Handle a follow-up question and return the assistant answer."""
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

    question = request.data.get("question", "")
    if not question.strip():
        return Response({"detail": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

    language = request.data.get("output_language", "English")

    Message.objects.create(
        conversation=conversation, role=Message.ROLE_USER, content=question
    )

    answer, source_chunks = generate_answer(conversation, question, language)

    assistant_message = Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_ASSISTANT,
        content=answer,
        source_chunks=source_chunks,
    )

    serializer = MessageSerializer(assistant_message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
