"""Service layer for fetching URL content and running RAG with Ollama."""

import logging
from urllib.parse import urlparse
import os

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from langchain.chains.combine_documents import create_stuff_documents_chain
from ollama import ResponseError
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ollama import Client, ResponseError

logger = logging.getLogger("urloader")


class SummarizerError(Exception):
    """User-facing error raised by the summarizer services."""

    def __init__(self, message, detail=None):
        super().__init__(message)
        self.message = message
        self.detail = detail


SUPPORTED_LANGUAGES = {
    "english": "English",
    "hindi": "Hindi",
    "tamil": "Tamil",
    "malayalam": "Malayalam",
}


def _ollama_kwargs(host_setting, key_setting):
    """Build kwargs for LangChain Ollama classes including auth headers if configured."""
    kwargs = {"base_url": host_setting}
    if key_setting:
        kwargs["client_kwargs"] = {
            "headers": {"Authorization": f"Bearer {key_setting}"}
        }
    return kwargs


def _get_raw_ollama_client(host, key):
    """Return a low-level Ollama client for health/version checks."""
    kwargs = _ollama_kwargs(host, key)
    return Client(host=kwargs.get("base_url"), **kwargs.get("client_kwargs", {}))


def check_ollama_connection(name, host, key, model):
    """Ping an Ollama host and verify the model exists.

    Returns a dict with status, version, available_models, and the target model.
    """
    result = {
        "name": name,
        "host": host,
        "model": model,
        "ok": False,
        "version": None,
        "available_models": [],
        "model_found": False,
        "error": None,
    }
    try:
        client = _get_raw_ollama_client(host, key)
        # Test connectivity by listing models; the underlying client exposes no version().
        models_response = client.list()
        available = [m.get("model", m.get("name", "unknown")) for m in models_response.get("models", [])]
        result["available_models"] = available
        result["model_found"] = any(
            model == m or (":" not in model and m.startswith(f"{model}:")) for m in available
        )
        result["version"] = "connected"
        result["ok"] = True
    except ResponseError as exc:
        result["error"] = _translate_ollama_error(exc).message
    except Exception as exc:
        logger.exception("Ollama connection check failed for %s", name)
        result["error"] = f"Could not connect: {exc}"
    return result


def run_ollama_diagnostics():
    """Check both the chat and embedding Ollama connections."""
    return [
        check_ollama_connection(
            "Chat / summary / translate",
            os.getenv("OLLAMA_HOST"),
            settings.OLLAMA_API_KEY,
            settings.OLLAMA_DEFAULT_MODEL,
        ),
        check_ollama_connection(
            "Embeddings",
            settings.OLLAMA_EMBED_HOST,
            settings.OLLAMA_EMBED_API_KEY,
            settings.OLLAMA_EMBED_MODEL,
        ),
    ]


def _get_embeddings():
    # Embeddings may run on a local Ollama instance, separate from cloud LLMs.
    return OllamaEmbeddings(
        model=settings.OLLAMA_EMBED_MODEL,
        **_ollama_kwargs(settings.OLLAMA_EMBED_HOST, settings.OLLAMA_EMBED_API_KEY),
    )


def _get_llm(temperature=0.4):
    return ChatOllama(
        model=settings.OLLAMA_DEFAULT_MODEL,
        temperature=temperature,
        **_ollama_kwargs(settings.OLLAMA_HOST, settings.OLLAMA_API_KEY),
    )


def validate_url(url):
    """Return the URL if it looks valid and uses a supported scheme."""
    if not url or not url.strip():
        raise SummarizerError("Please enter a URL.")
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SummarizerError(
            "Only HTTP and HTTPS URLs are supported.",
            detail=f"Scheme '{parsed.scheme}' is not allowed.",
        )
    if not parsed.netloc:
        raise SummarizerError("The URL does not look valid.")
    return url


def fetch_url_content(url, timeout=30):
    """Fetch and extract readable text from a URL."""
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        logger.warning("Timeout fetching URL %s: %s", url, exc)
        raise SummarizerError(
            "The page took too long to respond. Try a shorter page or try again later.",
            detail=str(exc),
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        logger.warning("Connection error fetching URL %s: %s", url, exc)
        raise SummarizerError(
            "Could not connect to that URL. Please check the address and try again.",
            detail=str(exc),
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.warning("Error fetching URL %s: %s", url, exc)
        raise SummarizerError(
            "We couldn't fetch the page.",
            detail=str(exc),
        ) from exc

    try:
        soup = BeautifulSoup(response.content, "lxml")
        # Remove script/style/nav/footer/header tags to reduce noise.
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
    except Exception as exc:
        logger.exception("Failed to parse HTML from %s", url)
        raise SummarizerError(
            "We couldn't read the content of that page.",
            detail=str(exc),
        ) from exc

    # Collapse excessive whitespace.
    lines = (line.strip() for line in text.splitlines())
    text = "\n".join(line for line in lines if line)

    if not text:
        raise SummarizerError(
            "The page loaded but we couldn't extract any text content. Try another URL."
        )

    return text


def chunk_text(text, chunk_size=8000, chunk_overlap=800):
    """Split text into overlapping chunks for vector search."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_text(text)


def _translate_ollama_error(exc):
    """Convert an Ollama ResponseError into a user-facing SummarizerError."""
    status = getattr(exc, "status_code", None)
    if status == 401:
        return SummarizerError(
            "Ollama rejected the API key (401 Unauthorized). "
            "Check that OLLAMA_HOST is set to the API endpoint (e.g. https://api.ollama.com) "
            "and that your OLLAMA_API_KEY is valid.",
            detail=str(exc),
        )
    if status == 403:
        return SummarizerError(
            "Ollama denied the request (403 Forbidden). "
            "Verify your API key has permission to use the selected model.",
            detail=str(exc),
        )
    if status == 404:
        return SummarizerError(
            "The requested Ollama model was not found (404). "
            "Check that the model name in your .env is available on your Ollama host.",
            detail=str(exc),
        )
    return SummarizerError(
        "Ollama returned an error while creating the search index.",
        detail=str(exc),
    )


def build_vector_store(text_chunks):
    """Build an in-memory FAISS index from text chunks."""
    if not text_chunks:
        raise SummarizerError("No text content available to build a search index.")
    try:
        embeddings = _get_embeddings()
        return FAISS.from_texts(text_chunks, embedding=embeddings)
    except ResponseError as exc:
        raise _translate_ollama_error(exc) from exc
    except Exception as exc:
        logger.exception("Failed to build FAISS vector store")
        raise SummarizerError(
            "Could not create the search index. Make sure the Ollama embedding model is available.",
            detail=str(exc),
        ) from exc


def answer_with_rag(question, vector_store):
    """Run retrieval-augmented generation over the vector store."""
    if not question or not question.strip():
        raise SummarizerError("Please enter a question.")

    prompt = ChatPromptTemplate.from_template(
        """Answer the user's question using only the context provided below.
Be detailed and include relevant details. If the context does not contain enough information,
respond exactly with "Answer is not available in the provided context."

Context:
{context}

Question: {input}

Answer:"""
    )

    try:
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        combine_docs_chain = create_stuff_documents_chain(_get_llm(), prompt)
        rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
        result = rag_chain.invoke({"input": question})
        return result.get("answer", "").strip()
    except ResponseError as exc:
        raise _translate_ollama_error(exc) from exc
    except Exception as exc:
        logger.exception("RAG chain failed for question: %s", question)
        raise SummarizerError(
            "The AI model failed to generate an answer. Please check that Ollama is running and the model is pulled.",
            detail=str(exc),
        ) from exc


def summarize_text(text, max_input_length=12000):
    """Generate a concise summary of the provided text using Ollama."""
    if not text:
        raise SummarizerError("No text available to summarize.")

    text = text[:max_input_length]
    prompt = ChatPromptTemplate.from_template(
        "Summarize the following text concisely, preserving the key points:\n\n{text}\n\nSummary:"
    )
    try:
        chain = prompt | _get_llm()
        result = chain.invoke({"text": text})
        return result.content.strip() if hasattr(result, "content") else str(result).strip()
    except ResponseError as exc:
        raise _translate_ollama_error(exc) from exc
    except Exception as exc:
        logger.exception("Summarization failed")
        raise SummarizerError(
            "Could not generate a summary. Please check that Ollama is running.",
            detail=str(exc),
        ) from exc


def translate_text(text, target_language, max_input_length=8000):
    """Translate text into the target language using an Ollama model."""
    target_language = (target_language or "").strip().lower()
    if target_language in ("english", "en", ""):
        return text

    if target_language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES.keys())
        raise SummarizerError(
            f"'{target_language}' is not a supported language. Supported: {supported}."
        )

    text = text[:max_input_length]
    language_name = SUPPORTED_LANGUAGES[target_language]
    prompt = ChatPromptTemplate.from_template(
        "Translate the following text into {language}. "
        "Return only the translation, with no extra explanation:\n\n{text}\n\nTranslation:"
    )
    try:
        chain = prompt | _get_llm()
        result = chain.invoke({"language": language_name, "text": text})
        return result.content.strip() if hasattr(result, "content") else str(result).strip()
    except ResponseError as exc:
        raise _translate_ollama_error(exc) from exc
    except Exception as exc:
        logger.exception("Translation to %s failed", language_name)
        raise SummarizerError(
            f"Could not translate the answer into {language_name}.",
            detail=str(exc),
        ) from exc


def process_url_question(url, question, language):
    """End-to-end pipeline: fetch, chunk, answer/summarize, translate."""
    url = validate_url(url)
    if not question or not question.strip():
        raise SummarizerError("Please enter a question.")

    content = fetch_url_content(url)
    chunks = chunk_text(content)
    vector_store = build_vector_store(chunks)

    answer = answer_with_rag(question, vector_store)
    summary = ""

    if "answer is not available" in answer.lower():
        # The model couldn't answer from the retrieved chunks, so summarize the whole page.
        answer = summarize_text(content)

    translated = translate_text(answer, language)
    return {
        "answer": answer,
        "summary": summary,
        "translated": translated if translated != answer else "",
        "language": language,
        "language_name": SUPPORTED_LANGUAGES.get(language, language.title()),
    }
