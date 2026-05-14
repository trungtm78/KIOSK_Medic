from functools import lru_cache
from typing import Optional

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_model(model_name: Optional[str] = None) -> SentenceTransformer:
    """
    Load and cache the embedding model.
    Defaults to settings.EMBEDDING_MODEL_NAME.
    """
    name = model_name or settings.EMBEDDING_MODEL_NAME
    return SentenceTransformer(name)
