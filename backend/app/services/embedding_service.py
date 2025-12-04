"""Embedding service for semantic text analysis using local sentence-transformers."""

import asyncio
import hashlib
import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using local sentence-transformers models."""

    def __init__(self):
        """Initialize embedding service with local model."""
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model: Optional[SentenceTransformer] = None
        self.max_retries = 3

        # Initialize the model
        try:
            logger.info(f"Loading local sentence-transformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers model: {str(e)}")
            self.model = None

    async def embed_text(self, text: str) -> list[float] | None:
        """
        Generate embedding vector for text using local sentence-transformers model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        if not self.model:
            logger.error("Cannot generate embeddings - model not loaded")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        # Clean and truncate text (model has token limit)
        text = text.strip()[:1000]

        try:
            # Generate embedding using local model
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self.model.encode,
                text
            )

            # Convert numpy array to list
            if isinstance(embedding, np.ndarray):
                return embedding.tolist()
            elif isinstance(embedding, list):
                return embedding
            else:
                logger.error(f"Unexpected embedding format: {type(embedding)}")
                return None

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    async def embed_texts(self, texts: list[str]) -> list[list[float] | None]:
        """
        Generate embeddings for multiple texts in parallel.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        if not self.model:
            logger.error("Cannot generate embeddings - model not loaded")
            return [None] * len(texts)

        try:
            # Clean and truncate all texts
            cleaned_texts = [text.strip()[:1000] for text in texts if text and text.strip()]

            if not cleaned_texts:
                logger.warning("No valid texts provided for embedding")
                return [None] * len(texts)

            # Generate embeddings using local model (batch processing)
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                cleaned_texts
            )

            # Convert numpy arrays to lists
            if isinstance(embeddings, np.ndarray):
                return [emb.tolist() for emb in embeddings]
            elif isinstance(embeddings, list):
                return embeddings
            else:
                logger.error(f"Unexpected embeddings format: {type(embeddings)}")
                return [None] * len(texts)

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return [None] * len(texts)

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float | None:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Similarity score between 0 and 1, or None if invalid input
        """
        if not vec1 or not vec2:
            return None

        if len(vec1) != len(vec2):
            logger.error(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
            return None

        try:
            # Convert to numpy arrays for efficient computation
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)

            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0

            similarity = dot_product / (norm_v1 * norm_v2)

            # Clip to [0, 1] range (cosine is [-1, 1], but we want similarity)
            similarity = (similarity + 1) / 2

            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return None

    def text_hash(self, text: str) -> str:
        """
        Generate a hash for text (useful for caching).

        Args:
            text: Text to hash

        Returns:
            MD5 hash of the text
        """
        return hashlib.md5(text.encode()).hexdigest()

    async def semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1 (0 if embedding fails)
        """
        embeddings = await self.embed_texts([text1, text2])

        if embeddings[0] is None or embeddings[1] is None:
            logger.warning("Failed to generate embeddings for similarity comparison")
            return 0.0

        similarity = self.cosine_similarity(embeddings[0], embeddings[1])

        return similarity if similarity is not None else 0.0

    @property
    def api_key(self) -> bool:
        """
        Compatibility property for code that checks if embedding service is available.
        Returns True if model is loaded, False otherwise.
        """
        return self.model is not None
