"""Production settings."""

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

# Additional production-only settings (HTTPS, caching, etc.) go here.
