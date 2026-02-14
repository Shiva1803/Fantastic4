"""
CacheManager service for storing style profiles and conversation sessions.

This module provides in-memory caching functionality to avoid redundant
API calls and maintain session state during active conversations.
"""

from typing import Optional, Dict
from backend.models.data_models import StyleProfile, ConversationSession


class CacheManager:
    """
    Manages in-memory cache for style profiles and conversation sessions.
    
    This class provides a simple dictionary-based cache for storing:
    - User style profiles (keyed by user_id)
    - Active conversation sessions (keyed by session_id)
    
    Attributes:
        _style_profiles: Dictionary storing StyleProfile objects by user_id
        _sessions: Dictionary storing ConversationSession objects by session_id
    """
    
    def __init__(self):
        """Initialize empty cache dictionaries."""
        self._style_profiles: Dict[str, StyleProfile] = {}
        self._sessions: Dict[str, ConversationSession] = {}
    
    def get_style_profile(self, user_id: str) -> Optional[StyleProfile]:
        """
        Retrieve a cached style profile for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            StyleProfile if found in cache, None otherwise
            
        Example:
            >>> cache = CacheManager()
            >>> profile = cache.get_style_profile("user123")
            >>> if profile:
            ...     print(f"Found profile with tone: {profile.tone}")
        """
        return self._style_profiles.get(user_id)
    
    def set_style_profile(self, user_id: str, profile: StyleProfile) -> None:
        """
        Store a style profile in the cache.
        
        Args:
            user_id: Unique identifier for the user
            profile: StyleProfile object to cache
            
        Raises:
            ValueError: If user_id is empty or profile is None
            
        Example:
            >>> cache = CacheManager()
            >>> profile = StyleProfile(...)
            >>> cache.set_style_profile("user123", profile)
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")
        if profile is None:
            raise ValueError("profile cannot be None")
        
        self._style_profiles[user_id] = profile
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Retrieve a cached conversation session.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            ConversationSession if found in cache, None otherwise
            
        Example:
            >>> cache = CacheManager()
            >>> session = cache.get_session("session456")
            >>> if session:
            ...     print(f"Session has {len(session.messages)} messages")
        """
        return self._sessions.get(session_id)
    
    def set_session(self, session_id: str, session: ConversationSession) -> None:
        """
        Store a conversation session in the cache.
        
        Args:
            session_id: Unique identifier for the session
            session: ConversationSession object to cache
            
        Raises:
            ValueError: If session_id is empty or session is None
            
        Example:
            >>> cache = CacheManager()
            >>> session = ConversationSession(...)
            >>> cache.set_session("session456", session)
        """
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")
        if session is None:
            raise ValueError("session cannot be None")
        
        self._sessions[session_id] = session
    
    def delete_style_profile(self, user_id: str) -> bool:
        """
        Remove a style profile from the cache.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if profile was deleted, False if not found
            
        Example:
            >>> cache = CacheManager()
            >>> cache.set_style_profile("user123", profile)
            >>> cache.delete_style_profile("user123")
            True
        """
        if user_id in self._style_profiles:
            del self._style_profiles[user_id]
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Remove a conversation session from the cache.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session was deleted, False if not found
            
        Example:
            >>> cache = CacheManager()
            >>> cache.set_session("session456", session)
            >>> cache.delete_session("session456")
            True
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def clear_all_profiles(self) -> None:
        """
        Clear all cached style profiles.
        
        Useful for testing or when implementing a "clear cache" feature.
        
        Example:
            >>> cache = CacheManager()
            >>> cache.clear_all_profiles()
        """
        self._style_profiles.clear()
    
    def clear_all_sessions(self) -> None:
        """
        Clear all cached conversation sessions.
        
        Useful for testing or cleanup after batch processing.
        
        Example:
            >>> cache = CacheManager()
            >>> cache.clear_all_sessions()
        """
        self._sessions.clear()
    
    def get_profile_count(self) -> int:
        """
        Get the number of cached style profiles.
        
        Returns:
            Number of profiles in cache
            
        Example:
            >>> cache = CacheManager()
            >>> count = cache.get_profile_count()
            >>> print(f"Cache contains {count} profiles")
        """
        return len(self._style_profiles)
    
    def get_session_count(self) -> int:
        """
        Get the number of cached conversation sessions.
        
        Returns:
            Number of sessions in cache
            
        Example:
            >>> cache = CacheManager()
            >>> count = cache.get_session_count()
            >>> print(f"Cache contains {count} active sessions")
        """
        return len(self._sessions)
