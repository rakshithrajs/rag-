"""Forms for creating and validating knowledge sources."""

from django import forms
from django.core.exceptions import ValidationError

from apps.sources.models import KnowledgeSource


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024


class KnowledgeSourceForm(forms.ModelForm):
    """Form for uploading a file or submitting a URL."""

    class Meta:
        model = KnowledgeSource
        fields = ["title", "source_type", "file", "url"]

    def clean(self) -> dict:
        cleaned_data = super().clean()
        source_type = cleaned_data.get("source_type")
        file = cleaned_data.get("file")
        url = cleaned_data.get("url")

        if source_type in (KnowledgeSource.SOURCE_TYPE_PDF, KnowledgeSource.SOURCE_TYPE_TXT):
            if not file:
                raise ValidationError("A file is required for PDF and text sources.")
            extension = file.name.lower().split(".")[-1]
            if source_type == KnowledgeSource.SOURCE_TYPE_PDF and extension != "pdf":
                raise ValidationError("PDF sources require a .pdf file.")
            if source_type == KnowledgeSource.SOURCE_TYPE_TXT and extension != "txt":
                raise ValidationError("Text sources require a .txt file.")
            if file.size > MAX_UPLOAD_SIZE_BYTES:
                raise ValidationError("Uploaded file is too large.")

        if source_type == KnowledgeSource.SOURCE_TYPE_URL:
            if not url:
                raise ValidationError("A URL is required for URL sources.")
            if not url.startswith(("http://", "https://")):
                raise ValidationError("URL must use HTTP or HTTPS.")

        return cleaned_data
