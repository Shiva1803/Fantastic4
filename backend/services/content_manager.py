"""
ContentManager service for managing space content.

This module handles creating, retrieving, and deleting content items (messages/files)
within spaces. Integrates with EmbeddingGenerator and VectorStore for vector search.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict
from backend.models.data_models import SpaceItem
from backend.services.file_storage import FileStorage
from backend.services.embedding_generator import EmbeddingGenerator
from backend.services.vector_store import VectorStore
from backend.services.file_processor import FileProcessor
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage


class ContentManager:
    """
    Manages storage and operations for SpaceItems.
    Generates embeddings on save and supports vector search.
    """
    
    def __init__(self):
        """Initialize item storage, file service, and vector search components."""
        self._items: Dict[str, SpaceItem] = {}
        self.file_storage = FileStorage()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.file_processor = FileProcessor()
        
    def save_message(self, space_id: str, content: str, notes: Optional[str] = None) -> SpaceItem:
        """
        Save a text message to a space.
        Generates an embedding and stores it in the vector store.
        """
        item_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        item = SpaceItem(
            id=item_id,
            space_id=space_id,
            type="message",
            content=content,
            notes=notes,
            metadata={},
            created_at=now
        )
        
        self._items[item_id] = item
        
        # Generate and store embedding
        try:
            text_for_embedding = content
            if notes:
                text_for_embedding += f" | Notes: {notes}"
            embedding = self.embedding_generator.generate_embedding(text_for_embedding)
            self.vector_store.add_embedding(item_id, embedding, space_id)
        except Exception as e:
            print(f"[ContentManager] Warning: failed to generate embedding for message {item_id}: {e}")
        
        return item
        
    def save_file(self, space_id: str, file: WerkzeugFileStorage, notes: Optional[str] = None) -> SpaceItem:
        """
        Save a file to a space.
        Extracts text, generates embedding, and stores in vector store.
        """
        # Save physical file
        filename, file_path, size = self.file_storage.save_file(file)
        
        item_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Extract text from file for embedding
        extracted_text = ""
        try:
            extracted_text = self.file_processor.extract_text(file_path)
        except Exception as e:
            print(f"[ContentManager] Warning: failed to extract text from {file_path}: {e}")
        
        # Create item record
        item = SpaceItem(
            id=item_id,
            space_id=space_id,
            type="file",
            content=filename,
            notes=notes,
            metadata={
                "original_name": file.filename,
                "size_bytes": size,
                "mime_type": file.mimetype,
                "path": file_path,
                "extracted_text": extracted_text[:5000] if extracted_text else ""  # Cap at 5k chars
            },
            created_at=now
        )
        
        self._items[item_id] = item
        
        # Generate and store embedding from extracted text
        try:
            text_for_embedding = extracted_text or file.filename or ""
            if notes:
                text_for_embedding += f" | Notes: {notes}"
            if text_for_embedding.strip():
                embedding = self.embedding_generator.generate_embedding(text_for_embedding)
                self.vector_store.add_embedding(item_id, embedding, space_id)
        except Exception as e:
            print(f"[ContentManager] Warning: failed to generate embedding for file {item_id}: {e}")
        
        return item
    
    def get_items(self, space_id: str) -> List[SpaceItem]:
        """Get all items in a space, sorted by creation date (newest first)."""
        items = [
            item for item in self._items.values() 
            if item.space_id == space_id
        ]
        return sorted(items, key=lambda x: x.created_at, reverse=True)
    
    def search_items(self, space_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for items in a space using semantic similarity.
        
        Args:
            space_id: Space to search within
            query: Search query text
            top_k: Number of results
            
        Returns:
            List of dicts with item data and relevance score
        """
        query_embedding = self.embedding_generator.generate_embedding(query)
        search_results = self.vector_store.search(query_embedding, space_id, top_k)
        
        results = []
        for result in search_results:
            item = self._items.get(result['item_id'])
            if item:
                item_dict = item.to_dict()
                item_dict['score'] = result['score']
                results.append(item_dict)
        
        return results
        
    def delete_item(self, item_id: str) -> bool:
        """Delete an item and its embedding."""
        item = self._items.get(item_id)
        if not item:
            return False
            
        # Delete embedding from vector store
        self.vector_store.delete_embedding(item_id)
            
        # If it's a file, delete physical file too
        if item.type == "file":
            self.file_storage.delete_file(item.content)
            
        del self._items[item_id]
        return True
