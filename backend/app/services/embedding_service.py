"""Embedding service for semantic text analysis using Hugging Face."""

import asyncio
import hashlib
import logging
from typing import Optional

import httpx
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Hugging Face models."""

    def __init__(self):
        """Initialize embedding service."""
        self.api_key = settings.huggingface_api_key
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.max_retries = 3
        self.timeout = 30.0

        if not self.api_key:
            logger.warning(
                "Hugging Face API key not configured. Embeddings will not be available."
            )

    async def embed_text(self, text: str) -> Optional[list[float]]:
        """
        Generate embedding vector for text using Hugging Face API.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        if not self.api_key:
            logger.error("Cannot generate embeddings without API key")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        # Clean and truncate text (model has token limit)
        text = text.strip()[:1000]

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": text}

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.api_url, headers=headers, json=payload
                    )

                    if response.status_code == 200:
                        embedding = response.json()

                        # Handle different response formats
                        if isinstance(embedding, list) and len(embedding) > 0:
                            if isinstance(embedding[0], list):
                                # Format: [[embedding]]
                                return embedding[0]
                            elif isinstance(embedding[0], (int, float)):
                                # Format: [embedding]
                                return embedding

                        logger.error(f"Unexpected embedding format: {type(embedding)}")
                        return None

                    elif response.status_code == 503:
                        # Model is loading, wait and retry
                        wait_time = 2**attempt
                        logger.info(
                            f"Model loading, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        logger.error(
                            f"Hugging Face API error: {response.status_code} - {response.text}"
                        )
                        return None

            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                return None

            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                return None

        logger.error("Max retries exceeded for embedding generation")
        return None

    async def embed_texts(self, texts: list[str]) -> list[Optional[list[float]]]:
        """
        Generate embeddings for multiple texts in parallel.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        tasks = [self.embed_text(text) for text in texts]
        return await asyncio.gather(*tasks)

    def cosine_similarity(
        self, vec1: list[float], vec2: list[float]
    ) -> Optional[float]:
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
