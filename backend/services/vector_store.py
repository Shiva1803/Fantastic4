"""
VectorStore service using FAISS for similarity search.

Stores embeddings mapped to item IDs and supports
filtered search by space_id.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple


class VectorStore:
    """
    In-memory FAISS-backed vector store.
    
    Maintains a flat L2 index and a mapping from
    internal FAISS indices to item metadata.
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize the vector store.
        
        Args:
            dimension: Embedding dimension (384 for MiniLM)
        """
        import faiss
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        
        # Maps internal FAISS index position → metadata
        self._id_map: List[Dict] = []  # [{item_id, space_id}, ...]
        # Maps item_id → FAISS index position
        self._item_to_idx: Dict[str, int] = {}
    
    def add_embedding(self, item_id: str, embedding: np.ndarray, space_id: str) -> None:
        """
        Add an embedding to the store.
        
        Args:
            item_id: Unique item identifier
            embedding: numpy array of shape (dimension,)
            space_id: Space the item belongs to
        """
        # Remove existing if present (update case)
        if item_id in self._item_to_idx:
            self.delete_embedding(item_id)
        
        embedding = embedding.astype(np.float32).reshape(1, -1)
        idx = self.index.ntotal
        self.index.add(embedding)
        
        self._id_map.append({
            'item_id': item_id,
            'space_id': space_id
        })
        self._item_to_idx[item_id] = idx
    
    def search(self, query_embedding: np.ndarray, space_id: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar items within a space.
        
        Args:
            query_embedding: Query vector
            space_id: Filter results to this space
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'item_id', 'score', 'space_id'
        """
        if self.index.ntotal == 0:
            return []
        
        query = query_embedding.astype(np.float32).reshape(1, -1)
        
        # Search more than top_k to account for space filtering
        search_k = min(self.index.ntotal, top_k * 10)
        distances, indices = self.index.search(query, search_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            if idx >= len(self._id_map):
                continue
            
            meta = self._id_map[idx]
            if meta['space_id'] != space_id:
                continue
            
            # Convert L2 distance to similarity score (0-1 range)
            score = 1.0 / (1.0 + float(dist))
            
            results.append({
                'item_id': meta['item_id'],
                'space_id': meta['space_id'],
                'score': round(score, 4)
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def delete_embedding(self, item_id: str) -> bool:
        """
        Mark an embedding as deleted.
        
        Note: FAISS IndexFlatL2 doesn't support true deletion.
        We mark the entry as deleted in our metadata map.
        The vector remains in the FAISS index but won't be
        returned in searches.
        
        Args:
            item_id: Item to delete
            
        Returns:
            True if found and deleted, False if not found
        """
        if item_id not in self._item_to_idx:
            return False
        
        idx = self._item_to_idx[item_id]
        # Mark as deleted by clearing space_id
        self._id_map[idx] = {'item_id': None, 'space_id': None}
        del self._item_to_idx[item_id]
        return True
    
    @property
    def total_vectors(self) -> int:
        """Total number of active vectors."""
        return len(self._item_to_idx)
