"""
Unit tests for CacheManager service.

Tests basic caching functionality including storing, retrieving,
and deleting style profiles and conversation sessions.
"""

import pytest
from backend.services.cache_manager import CacheManager
from backend.models.data_models import StyleProfile, ConversationSession, Message


class TestCacheManager:
    """Tests for CacheManager service."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.cache = CacheManager()
        self.sample_profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.8,
            common_emojis=["😂", "👍"],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=["lol", "haha"],
            formality_level=0.2,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        self.sample_message = Message(
            id="msg-1",
            sender="user",
            text="Hello",
            timestamp="2024-01-01T12:00:00Z",
            is_ai_generated=False
        )
        self.sample_session = ConversationSession(
            session_id="session-123",
            messages=[self.sample_message],
            style_profile=self.sample_profile,
            start_time="2024-01-01T12:00:00Z"
        )
    
    def test_get_nonexistent_profile(self):
        """Test retrieving a profile that doesn't exist returns None."""
        result = self.cache.get_style_profile("nonexistent")
        assert result is None
    
    def test_set_and_get_profile(self):
        """Test storing and retrieving a style profile."""
        self.cache.set_style_profile("user123", self.sample_profile)
        retrieved = self.cache.get_style_profile("user123")
        
        assert retrieved is not None
        assert retrieved.sentence_length == "short"
        assert retrieved.emoji_frequency == 0.8
        assert retrieved.tone == "casual"
    
    def test_set_profile_with_empty_user_id(self):
        """Test that setting profile with empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            self.cache.set_style_profile("", self.sample_profile)
    
    def test_set_profile_with_none(self):
        """Test that setting None profile raises ValueError."""
        with pytest.raises(ValueError, match="profile cannot be None"):
            self.cache.set_style_profile("user123", None)
    
    def test_overwrite_existing_profile(self):
        """Test that setting a profile twice overwrites the first one."""
        profile1 = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.5,
            common_emojis=[],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=[],
            formality_level=0.3,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        profile2 = StyleProfile(
            sentence_length="long",
            emoji_frequency=0.9,
            common_emojis=["🎉"],
            punctuation_style="heavy",
            tone="formal",
            common_phrases=["indeed"],
            formality_level=0.8,
            analysis_timestamp="2024-01-02T00:00:00Z"
        )
        
        self.cache.set_style_profile("user123", profile1)
        self.cache.set_style_profile("user123", profile2)
        
        retrieved = self.cache.get_style_profile("user123")
        assert retrieved.sentence_length == "long"
        assert retrieved.emoji_frequency == 0.9
    
    def test_get_nonexistent_session(self):
        """Test retrieving a session that doesn't exist returns None."""
        result = self.cache.get_session("nonexistent")
        assert result is None
    
    def test_set_and_get_session(self):
        """Test storing and retrieving a conversation session."""
        self.cache.set_session("session-123", self.sample_session)
        retrieved = self.cache.get_session("session-123")
        
        assert retrieved is not None
        assert retrieved.session_id == "session-123"
        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].text == "Hello"
    
    def test_set_session_with_empty_session_id(self):
        """Test that setting session with empty session_id raises ValueError."""
        with pytest.raises(ValueError, match="session_id cannot be empty"):
            self.cache.set_session("", self.sample_session)
    
    def test_set_session_with_none(self):
        """Test that setting None session raises ValueError."""
        with pytest.raises(ValueError, match="session cannot be None"):
            self.cache.set_session("session-123", None)
    
    def test_delete_existing_profile(self):
        """Test deleting an existing profile returns True."""
        self.cache.set_style_profile("user123", self.sample_profile)
        result = self.cache.delete_style_profile("user123")
        
        assert result is True
        assert self.cache.get_style_profile("user123") is None
    
    def test_delete_nonexistent_profile(self):
        """Test deleting a nonexistent profile returns False."""
        result = self.cache.delete_style_profile("nonexistent")
        assert result is False
    
    def test_delete_existing_session(self):
        """Test deleting an existing session returns True."""
        self.cache.set_session("session-123", self.sample_session)
        result = self.cache.delete_session("session-123")
        
        assert result is True
        assert self.cache.get_session("session-123") is None
    
    def test_delete_nonexistent_session(self):
        """Test deleting a nonexistent session returns False."""
        result = self.cache.delete_session("nonexistent")
        assert result is False
    
    def test_clear_all_profiles(self):
        """Test clearing all profiles."""
        self.cache.set_style_profile("user1", self.sample_profile)
        self.cache.set_style_profile("user2", self.sample_profile)
        
        self.cache.clear_all_profiles()
        
        assert self.cache.get_style_profile("user1") is None
        assert self.cache.get_style_profile("user2") is None
        assert self.cache.get_profile_count() == 0
    
    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        self.cache.set_session("session1", self.sample_session)
        self.cache.set_session("session2", self.sample_session)
        
        self.cache.clear_all_sessions()
        
        assert self.cache.get_session("session1") is None
        assert self.cache.get_session("session2") is None
        assert self.cache.get_session_count() == 0
    
    def test_get_profile_count(self):
        """Test getting the count of cached profiles."""
        assert self.cache.get_profile_count() == 0
        
        self.cache.set_style_profile("user1", self.sample_profile)
        assert self.cache.get_profile_count() == 1
        
        self.cache.set_style_profile("user2", self.sample_profile)
        assert self.cache.get_profile_count() == 2
        
        self.cache.delete_style_profile("user1")
        assert self.cache.get_profile_count() == 1
    
    def test_get_session_count(self):
        """Test getting the count of cached sessions."""
        assert self.cache.get_session_count() == 0
        
        self.cache.set_session("session1", self.sample_session)
        assert self.cache.get_session_count() == 1
        
        self.cache.set_session("session2", self.sample_session)
        assert self.cache.get_session_count() == 2
        
        self.cache.delete_session("session1")
        assert self.cache.get_session_count() == 1
    
    def test_multiple_users_and_sessions(self):
        """Test managing multiple users and sessions simultaneously."""
        profile1 = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.5,
            common_emojis=[],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=[],
            formality_level=0.3,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        profile2 = StyleProfile(
            sentence_length="long",
            emoji_frequency=0.1,
            common_emojis=[],
            punctuation_style="heavy",
            tone="formal",
            common_phrases=[],
            formality_level=0.9,
            analysis_timestamp="2024-01-02T00:00:00Z"
        )
        
        # Store multiple profiles
        self.cache.set_style_profile("user1", profile1)
        self.cache.set_style_profile("user2", profile2)
        
        # Store multiple sessions
        self.cache.set_session("session1", self.sample_session)
        self.cache.set_session("session2", self.sample_session)
        
        # Verify all are stored correctly
        assert self.cache.get_profile_count() == 2
        assert self.cache.get_session_count() == 2
        
        # Verify correct retrieval
        retrieved1 = self.cache.get_style_profile("user1")
        retrieved2 = self.cache.get_style_profile("user2")
        
        assert retrieved1.sentence_length == "short"
        assert retrieved2.sentence_length == "long"
