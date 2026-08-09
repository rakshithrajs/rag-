"""Cross-encoder reranker for retrieved chunks."""

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L2-v2"
DEFAULT_TOP_N = 5


class Reranker:
    """Lazy-loaded wrapper around a HuggingFace cross-encoder.

    Uses MiniLM (~×60 MB) to stay within tight memory budgets.
    Falls back to distance ranking if the model fails to load or score.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self._model_name = model_name
        self._tokenizer = None
        self._model = None
        self._lock = threading.Lock()
        self._load_failed = False

    def _ensure_model(self) -> None:
        if self._model is not None or self._load_failed:
            return
        with self._lock:
            if self._model is not None or self._load_failed:
                return
            try:
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
                self._model = AutoModelForSequenceClassification.from_pretrained(self._model_name)
                self._model.eval()
                logger.info("Loaded reranker model %s", self._model_name)
            except Exception:
                logger.exception(
                    "Failed to load reranker model %s", self._model_name
                )
                self._load_failed = True

    def rerank(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        top_n: int = DEFAULT_TOP_N,
    ) -> list[dict[str, Any]]:
        if not chunks:
            return []

        self._ensure_model()
        if self._model is None or self._tokenizer is None:
            logger.warning(
                "Reranker unavailable; falling back to distance ranking"
            )
            return sorted(chunks, key=lambda c: c.get("distance", 1.0))[:top_n]

        pairs = [(query, c["text"]) for c in chunks]
        try:
            import torch

            queries, passages = zip(*pairs)
            features = self._tokenizer(
                list(queries),
                list(passages),
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            with torch.no_grad():
                logits = self._model(**features).logits.squeeze(-1).tolist()
            if isinstance(logits, float):
                scores: list[float] = [logits]
            else:
                scores = [float(s) for s in logits]
        except Exception:
            logger.exception(
                "Reranker scoring failed; falling back to distance ranking"
            )
            return sorted(chunks, key=lambda c: c.get("distance", 1.0))[:top_n]

        ranked = sorted(
            zip(chunks, scores), key=lambda pair: pair[1], reverse=True
        )
        out: list[dict[str, Any]] = []
        for chunk, score in ranked[:top_n]:
            chunk["rerank_score"] = score
            out.append(chunk)
        return out
