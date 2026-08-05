"""Extract plain text from PDF, TXT, and URL sources."""

import ipaddress
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

logger = logging.getLogger(__name__)


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024
MAX_URL_SIZE_BYTES = 10 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 30

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


class ExtractionError(Exception):
    """Raised when text extraction fails."""


def extract_pdf(file_path: Path) -> str:
    """Extract text from a PDF file."""
    text_parts = []
    try:
        reader = PdfReader(str(file_path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    except Exception as exc:
        logger.error("PDF extraction failed for %s: %s", file_path, exc)
        raise ExtractionError(f"Could not extract PDF text: {exc}") from exc

    return "\n\n".join(text_parts)


def extract_txt(file_path: Path) -> str:
    """Read text from a UTF-8 text file."""
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        logger.error("TXT decoding failed for %s", file_path)
        raise ExtractionError("Text file is not valid UTF-8") from exc
    except Exception as exc:
        logger.error("TXT read failed for %s: %s", file_path, exc)
        raise ExtractionError(f"Could not read text file: {exc}") from exc


def _is_private_url(url: str) -> bool:
    """Return True if the URL points to a private or reserved network."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return True

    if hostname in ("localhost", "127.0.0.1", "::1"):
        return True

    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_reserved or ip.is_loopback
    except ValueError:
        pass

    return False


def _clean_url(url: str) -> str:
    """Validate scheme and reject obviously malicious URLs."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ExtractionError("Only HTTP and HTTPS URLs are allowed")
    if _is_private_url(url):
        raise ExtractionError("URL resolves to a private or internal address")
    return url


def extract_url(url: str) -> str:
    """Fetch a public webpage and extract its main text content."""
    cleaned_url = _clean_url(url)

    try:
        response = requests.get(
            cleaned_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=True,
            headers=_BROWSER_HEADERS,
        )
        response.raise_for_status()
    except requests.exceptions.TooManyRedirects as exc:
        logger.error("Too many redirects fetching %s", cleaned_url)
        raise ExtractionError("URL redirected too many times") from exc
    except requests.exceptions.Timeout as exc:
        logger.error("Timeout fetching URL %s", cleaned_url)
        raise ExtractionError("URL fetch timed out") from exc
    except requests.exceptions.RequestException as exc:
        logger.error("Failed to fetch URL %s: %s", cleaned_url, exc)
        raise ExtractionError(f"Could not fetch URL: {exc}") from exc

    content_length = response.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_URL_SIZE_BYTES:
        raise ExtractionError("URL response is too large")

    if len(response.content) > MAX_URL_SIZE_BYTES:
        raise ExtractionError("URL response is too large")

    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def extract(source_type: str, file_path: Path | None = None, url: str | None = None) -> str:
    """Dispatch extraction based on source type."""
    if source_type == "pdf":
        if not file_path:
            raise ExtractionError("PDF source is missing a file path")
        return extract_pdf(file_path)
    if source_type == "txt":
        if not file_path:
            raise ExtractionError("Text source is missing a file path")
        return extract_txt(file_path)
    if source_type == "url":
        if not url:
            raise ExtractionError("URL source is missing a URL")
        return extract_url(url)
    raise ExtractionError(f"Unsupported source type: {source_type}")
