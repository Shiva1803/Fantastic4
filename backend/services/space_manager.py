"""
SpaceManager service for managing conversation spaces.

This module provides functionality to create, read, update, and delete
spaces, persisting them in memory for the session.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict
from backend.models.data_models import Space


class SpaceManager:
    """
    Manages in-memory storage and operations for Spaces.
    
    Attributes:
        _spaces: Dictionary storing Space objects by space_id
    """
    
    def __init__(self):
        """Initialize empty space storage."""
        self._spaces: Dict[str, Space] = {}
        
    def create_space(self, user_id: str, name: str, description: Optional[str] = None) -> Space:
        """
        Create a new space.
        
        Args:
            user_id: ID of the user creating the space
            name: Name of the space
            description: Optional description
            
        Returns:
            The created Space object
            
        Raises:
            ValueError: If validation fails
        """
        # Validation is handled by the Space data model __post_init__
        # but we need to generate the ID and timestamps first
        
        space_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        space = Space(
            id=space_id,
            user_id=user_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            item_count=0
        )
        
        self._spaces[space_id] = space
        return space
    
    def get_spaces(self, user_id: str) -> List[Space]:
        """
        Get all spaces for a specific user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of Space objects
        """
        return [
            space for space in self._spaces.values() 
            if space.user_id == user_id
        ]
    
    def get_space(self, space_id: str) -> Optional[Space]:
        """
        Get a specific space by ID.
        
        Args:
            space_id: The space ID
            
        Returns:
            Space object if found, None otherwise
        """
        return self._spaces.get(space_id)
    
    def update_space(self, space_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Space]:
        """
        Update an existing space.
        
        Args:
            space_id: The space ID
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            Updated Space object if found, None otherwise
        """
        space = self._spaces.get(space_id)
        if not space:
            return None
            
        if name is not None:
            space.name = name
        if description is not None:
            space.description = description
            
        space.updated_at = datetime.now().isoformat()
        
        # Re-validate by re-initializing or checking constraints?
        # Data class __post_init__ only runs on init.
        # We should probably add validation here or reuse logic.
        if len(space.name) > 50:
            raise ValueError("name must be 50 characters or less")
        if space.description and len(space.description) > 500:
            raise ValueError("description must be 500 characters or less")
            
        return space
    
    def delete_space(self, space_id: str) -> bool:
        """
        Delete a space.
        
        Args:
            space_id: The space ID
            
        Returns:
            True if deleted, False if not found
        """
        if space_id in self._spaces:
            del self._spaces[space_id]
            return True
        return False
