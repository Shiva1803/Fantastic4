"""
EmbeddingGenerator service for generating text embeddings.

Uses sentence-transformers with the all-MiniLM-L6-v2 model
for fast, lightweight 384-dimensional embeddings.
"""

import hashlib
import numpy as np
from typing import List, Optional, Dict


class EmbeddingGenerator:
    """
    Generates embeddings using sentence-transformers.
    
    Lazy-loads the model on first use to avoid slow startup.
    Includes a simple hash-based cache to avoid recomputing
    embeddings for identical text.
    """
    
    EMBEDDING_DIM = 384
    MODEL_NAME = 'all-MiniLM-L6-v2'
    
    def __init__(self):
        self._model = None
        self._cache: Dict[str, np.ndarray] = {}
    
    def _get_model(self):
        """Lazy-load the sentence transformer model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
        return self._model
    
    def _cache_key(self, text: str) -> str:
        """Generate a cache key from text content."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            384-dimensional numpy array
        """
        if not text or not text.strip():
            return np.zeros(self.EMBEDDING_DIM, dtype=np.float32)
        
        key = self._cache_key(text)
        if key in self._cache:
            return self._cache[key]
        
        model = self._get_model()
        embedding = model.encode(text, convert_to_numpy=True).astype(np.float32)
        
        self._cache[key] = embedding
        return embedding
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of 384-dimensional numpy arrays
        """
        if not texts:
            return []
        
        # Separate cached vs uncached
        results: List[Optional[np.ndarray]] = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results[i] = np.zeros(self.EMBEDDING_DIM, dtype=np.float32)
                continue
            key = self._cache_key(text)
            if key in self._cache:
                results[i] = self._cache[key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
        
        # Batch encode uncached
        if uncached_texts:
            model = self._get_model()
            embeddings = model.encode(uncached_texts, convert_to_numpy=True, batch_size=32)
            for idx, emb in zip(uncached_indices, embeddings):
                emb = emb.astype(np.float32)
                self._cache[self._cache_key(texts[idx])] = emb
                results[idx] = emb
        
        return results
