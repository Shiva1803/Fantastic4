"""
Unit tests for data models.

Tests basic functionality of all data model classes including
validation, serialization, and deserialization.
"""

import pytest
from datetime import datetime
from backend.models.data_models import (
    StyleProfile,
    Message,
    EscalationResult,
    ConversationSession,
    ConversationSummary
)


class TestStyleProfile:
    """Tests for StyleProfile data model."""
    
    def test_valid_style_profile(self):
        """Test creating a valid StyleProfile."""
        profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.8,
            common_emojis=["😂", "👍", "🔥"],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=["lol", "haha", "for sure"],
            formality_level=0.2,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        assert profile.sentence_length == "short"
        assert profile.emoji_frequency == 0.8
        assert len(profile.common_emojis) == 3
    
    def test_invalid_emoji_frequency(self):
        """Test that invalid emoji_frequency raises ValueError."""
        with pytest.raises(ValueError, match="emoji_frequency must be between 0 and 1"):
            StyleProfile(
                sentence_length="short",
                emoji_frequency=1.5,
                common_emojis=[],
                punctuation_style="minimal",
                tone="casual",
                common_phrases=[],
                formality_level=0.5,
                analysis_timestamp="2024-01-01T00:00:00Z"
            )
    
    def test_invalid_formality_level(self):
        """Test that invalid formality_level raises ValueError."""
        with pytest.raises(ValueError, match="formality_level must be between 0 and 1"):
            StyleProfile(
                sentence_length="short",
                emoji_frequency=0.5,
                common_emojis=[],
                punctuation_style="minimal",
                tone="casual",
                common_phrases=[],
                formality_level=-0.1,
                analysis_timestamp="2024-01-01T00:00:00Z"
            )
    
    def test_to_dict(self):
        """Test StyleProfile serialization to dict."""
        profile = StyleProfile(
            sentence_length="medium",
            emoji_frequency=0.5,
            common_emojis=["😊"],
            punctuation_style="standard",
            tone="mixed",
            common_phrases=["thanks"],
            formality_level=0.5,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        data = profile.to_dict()
        assert isinstance(data, dict)
        assert data['sentenceLength'] == "medium"
        assert data['emojiFrequency'] == 0.5
    
    def test_from_dict(self):
        """Test StyleProfile deserialization from dict."""
        data = {
            'sentence_length': 'long',
            'emoji_frequency': 0.1,
            'common_emojis': [],
            'punctuation_style': 'heavy',
            'tone': 'formal',
            'common_phrases': ['indeed', 'certainly'],
            'formality_level': 0.9,
            'analysis_timestamp': '2024-01-01T00:00:00Z'
        }
        profile = StyleProfile.from_dict(data)
        assert profile.sentence_length == 'long'
        assert profile.formality_level == 0.9


class TestMessage:
    """Tests for Message data model."""
    
    def test_valid_message(self):
        """Test creating a valid Message."""
        msg = Message(
            id="msg-123",
            sender="user",
            text="Hello there!",
            timestamp="2024-01-01T12:00:00Z",
            is_ai_generated=False
        )
        assert msg.id == "msg-123"
        assert msg.sender == "user"
        assert msg.text == "Hello there!"
    
    def test_invalid_sender(self):
        """Test that invalid sender raises ValueError."""
        with pytest.raises(ValueError, match="sender must be"):
            Message(
                id="msg-123",
                sender="invalid",
                text="Hello",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            )
    
    def test_empty_text(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            Message(
                id="msg-123",
                sender="user",
                text="   ",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            )
    
    def test_to_dict(self):
        """Test Message serialization to dict."""
        msg = Message(
            id="msg-456",
            sender="ai",
            text="Sure thing!",
            timestamp="2024-01-01T12:01:00Z",
            is_ai_generated=True
        )
        data = msg.to_dict()
        assert data['id'] == "msg-456"
        assert data['isAiGenerated'] is True
    
    def test_from_dict(self):
        """Test Message deserialization from dict."""
        data = {
            'id': 'msg-789',
            'sender': 'friend',
            'text': 'How are you?',
            'timestamp': '2024-01-01T12:02:00Z',
            'is_ai_generated': False
        }
        msg = Message.from_dict(data)
        assert msg.sender == 'friend'
        assert msg.is_ai_generated is False


class TestEscalationResult:
    """Tests for EscalationResult data model."""
    
    def test_no_escalation(self):
        """Test creating EscalationResult with no escalation."""
        result = EscalationResult(
            detected=False,
            confidence_score=85.0
        )
        assert result.detected is False
        assert result.confidence_score == 85.0
        assert result.reason is None
    
    def test_escalation_detected(self):
        """Test creating EscalationResult with escalation."""
        result = EscalationResult(
            detected=True,
            confidence_score=45.0,
            reason="Serious topic detected",
            category="serious_question"
        )
        assert result.detected is True
        assert result.reason == "Serious topic detected"
        assert result.category == "serious_question"
    
    def test_invalid_confidence_score(self):
        """Test that invalid confidence_score raises ValueError."""
        with pytest.raises(ValueError, match="confidence_score must be between 0 and 100"):
            EscalationResult(
                detected=False,
                confidence_score=150.0
            )
    
    def test_detected_without_reason(self):
        """Test that detected=True without reason raises ValueError."""
        with pytest.raises(ValueError, match="reason is required when detected is True"):
            EscalationResult(
                detected=True,
                confidence_score=50.0
            )
    
    def test_to_dict(self):
        """Test EscalationResult serialization to dict."""
        result = EscalationResult(
            detected=True,
            confidence_score=60.0,
            reason="Emotional content",
            category="emotional_distress"
        )
        data = result.to_dict()
        assert data['detected'] is True
        assert data['category'] == "emotional_distress"


class TestConversationSession:
    """Tests for ConversationSession data model."""
    
    def test_valid_session(self):
        """Test creating a valid ConversationSession."""
        profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.5,
            common_emojis=[],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=[],
            formality_level=0.3,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        msg = Message(
            id="msg-1",
            sender="user",
            text="Hi",
            timestamp="2024-01-01T12:00:00Z",
            is_ai_generated=False
        )
        session = ConversationSession(
            session_id="session-123",
            messages=[msg],
            style_profile=profile,
            start_time="2024-01-01T12:00:00Z"
        )
        assert session.session_id == "session-123"
        assert len(session.messages) == 1
        assert session.escalation_count == 0
    
    def test_to_dict_and_from_dict(self):
        """Test ConversationSession serialization round-trip."""
        profile = StyleProfile(
            sentence_length="medium",
            emoji_frequency=0.7,
            common_emojis=["😊"],
            punctuation_style="standard",
            tone="casual",
            common_phrases=["cool"],
            formality_level=0.4,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        msg = Message(
            id="msg-2",
            sender="ai",
            text="Sure!",
            timestamp="2024-01-01T12:01:00Z",
            is_ai_generated=True
        )
        session = ConversationSession(
            session_id="session-456",
            messages=[msg],
            style_profile=profile,
            start_time="2024-01-01T12:00:00Z",
            escalation_count=1
        )
        
        # Serialize and deserialize
        data = session.to_dict()
        restored = ConversationSession.from_dict(data)
        
        assert restored.session_id == session.session_id
        assert len(restored.messages) == 1
        assert restored.escalation_count == 1


class TestConversationSummary:
    """Tests for ConversationSummary data model."""
    
    def test_valid_summary(self):
        """Test creating a valid ConversationSummary."""
        msg1 = Message(
            id="msg-1",
            sender="friend",
            text="Want to grab lunch?",
            timestamp="2024-01-01T12:00:00Z",
            is_ai_generated=False
        )
        msg2 = Message(
            id="msg-2",
            sender="ai",
            text="Sure! 12:30?",
            timestamp="2024-01-01T12:01:00Z",
            is_ai_generated=True
        )
        
        summary = ConversationSummary(
            session_id="session-789",
            transcript=[msg1, msg2],
            commitments=["Lunch at 12:30"],
            action_items=["Confirm restaurant"],
            key_topics=["lunch plans"],
            ai_message_count=1,
            human_message_count=1,
            duration=300
        )
        
        assert summary.session_id == "session-789"
        assert len(summary.transcript) == 2
        assert summary.ai_message_count == 1
        assert summary.duration == 300
    
    def test_invalid_counts(self):
        """Test that negative counts raise ValueError."""
        with pytest.raises(ValueError, match="ai_message_count cannot be negative"):
            ConversationSummary(
                session_id="session-999",
                transcript=[],
                commitments=[],
                action_items=[],
                key_topics=[],
                ai_message_count=-1,
                human_message_count=0
            )
    
    def test_to_dict(self):
        """Test ConversationSummary serialization to dict."""
        msg = Message(
            id="msg-3",
            sender="user",
            text="Thanks!",
            timestamp="2024-01-01T12:02:00Z",
            is_ai_generated=False
        )
        summary = ConversationSummary(
            session_id="session-111",
            transcript=[msg],
            commitments=[],
            action_items=[],
            key_topics=["gratitude"],
            ai_message_count=0,
            human_message_count=1
        )
        data = summary.to_dict()
        assert data['sessionId'] == "session-111"
        assert len(data['transcript']) == 1
        assert data['keyTopics'] == ["gratitude"]
