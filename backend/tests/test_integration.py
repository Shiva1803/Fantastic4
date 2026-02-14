"""
Integration tests to verify all backend services work together.

These tests ensure that the complete backend pipeline functions correctly.
"""

import pytest
from unittest.mock import Mock, patch
import json
from backend.services.style_analyzer import StyleAnalyzer
from backend.services.response_generator import ResponseGenerator
from backend.services.escalation_detector import EscalationDetector
from backend.services.conversation_summarizer import ConversationSummarizer
from backend.services.cache_manager import CacheManager
from backend.models.data_models import Message


class TestBackendIntegration:
    """Integration tests for backend services."""
    
    @patch('backend.services.style_analyzer.OpenAI')
    @patch('backend.services.response_generator.OpenAI')
    @patch('backend.services.escalation_detector.OpenAI')
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_complete_conversation_flow(
        self,
        mock_summarizer_openai,
        mock_escalation_openai,
        mock_response_openai,
        mock_analyzer_openai
    ):
        """
        Test complete flow: analyze style → generate responses → detect escalation → summarize.
        
        This simulates a full user journey through the system.
        """
        # Setup mock responses for StyleAnalyzer
        style_response = json.dumps({
            "sentence_length": "medium",
            "emoji_frequency": 0.5,
            "common_emojis": ["😊", "👍"],
            "punctuation_style": "standard",
            "tone": "casual",
            "common_phrases": ["hey", "cool"],
            "formality_level": 0.3
        })
        
        mock_analyzer_response = Mock()
        mock_analyzer_response.choices = [Mock()]
        mock_analyzer_response.choices[0].message.content = style_response
        
        mock_analyzer_client = Mock()
        mock_analyzer_client.chat.completions.create.return_value = mock_analyzer_response
        mock_analyzer_openai.return_value = mock_analyzer_client
        
        # Setup mock responses for ResponseGenerator
        mock_response_response = Mock()
        mock_response_response.choices = [Mock()]
        mock_response_response.choices[0].message.content = "Sure, sounds good! 😊"
        
        mock_response_client = Mock()
        mock_response_client.chat.completions.create.return_value = mock_response_response
        mock_response_openai.return_value = mock_response_client
        
        # Setup mock responses for EscalationDetector
        escalation_response = json.dumps({
            "needs_human": False,
            "reason": "Casual conversation",
            "urgency": "low",
            "confidence": 85,
            "category": None
        })
        
        mock_escalation_response = Mock()
        mock_escalation_response.choices = [Mock()]
        mock_escalation_response.choices[0].message.content = escalation_response
        
        mock_escalation_client = Mock()
        mock_escalation_client.chat.completions.create.return_value = mock_escalation_response
        mock_escalation_openai.return_value = mock_escalation_client
        
        # Setup mock responses for ConversationSummarizer
        summary_response = json.dumps({
            "commitments": ["Lunch tomorrow"],
            "action_items": ["Confirm time"],
            "key_topics": ["Lunch plans"]
        })
        
        mock_summarizer_response = Mock()
        mock_summarizer_response.choices = [Mock()]
        mock_summarizer_response.choices[0].message.content = summary_response
        
        mock_summarizer_client = Mock()
        mock_summarizer_client.chat.completions.create.return_value = mock_summarizer_response
        mock_summarizer_openai.return_value = mock_summarizer_client
        
        # Initialize all services
        cache = CacheManager()
        analyzer = StyleAnalyzer(api_key="test-key")
        generator = ResponseGenerator(api_key="test-key")
        detector = EscalationDetector(api_key="test-key")
        summarizer = ConversationSummarizer(api_key="test-key")
        
        # Step 1: Analyze style from training data
        training_data = [
            "hey how are you",
            "good thanks!",
            "wanna hang out?",
            "sure sounds good",
            "cool see you later",
            "bye!",
            "talk soon",
            "yeah definitely",
            "catch you later",
            "peace out"
        ]
        
        style_profile = analyzer.analyze(training_data)
        assert style_profile is not None
        assert style_profile.tone == "casual"
        
        # Step 2: Cache the style profile
        cache.set_style_profile("user-123", style_profile)
        cached_profile = cache.get_style_profile("user-123")
        assert cached_profile is not None
        assert cached_profile.tone == style_profile.tone
        
        # Step 3: Simulate a conversation
        messages = []
        
        # Friend sends message
        friend_msg = Message(
            id="msg-1",
            sender="friend",
            text="Want to grab lunch tomorrow?",
            timestamp="2024-01-01T12:00:00Z",
            is_ai_generated=False
        )
        messages.append(friend_msg)
        
        # Step 4: Check for escalation
        escalation_result = detector.detect(friend_msg.text, messages)
        assert escalation_result.detected is False
        assert escalation_result.confidence_score == 85
        
        # Step 5: Generate response
        response_text = generator.generate(
            style_profile,
            messages,
            friend_msg.text
        )
        assert response_text is not None
        assert len(response_text) > 0
        
        # Add AI response to messages
        ai_msg = Message(
            id="msg-2",
            sender="user",
            text=response_text,
            timestamp="2024-01-01T12:01:00Z",
            is_ai_generated=True
        )
        messages.append(ai_msg)
        
        # Step 6: Summarize conversation
        summary = summarizer.summarize(messages, style_profile, "session-123")
        assert summary is not None
        assert len(summary.transcript) == 2
        assert summary.ai_message_count == 1
        assert summary.human_message_count == 1
        assert len(summary.commitments) > 0
        
    def test_cache_manager_isolation(self):
        """Test that CacheManager properly isolates different users and sessions."""
        cache = CacheManager()
        
        # Create mock profiles for different users
        from backend.models.data_models import StyleProfile
        
        profile1 = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.8,
            common_emojis=["😊"],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=["hey"],
            formality_level=0.2,
            analysis_timestamp="2024-01-01T12:00:00Z"
        )
        
        profile2 = StyleProfile(
            sentence_length="long",
            emoji_frequency=0.1,
            common_emojis=["👍"],
            punctuation_style="heavy",
            tone="formal",
            common_phrases=["greetings"],
            formality_level=0.9,
            analysis_timestamp="2024-01-01T12:00:00Z"
        )
        
        # Store profiles for different users
        cache.set_style_profile("user-1", profile1)
        cache.set_style_profile("user-2", profile2)
        
        # Verify isolation
        retrieved1 = cache.get_style_profile("user-1")
        retrieved2 = cache.get_style_profile("user-2")
        
        assert retrieved1.tone == "casual"
        assert retrieved2.tone == "formal"
        assert retrieved1.formality_level != retrieved2.formality_level
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_style_analyzer_with_cache(self, mock_openai):
        """Test that StyleAnalyzer results can be cached and retrieved."""
        style_response = json.dumps({
            "sentence_length": "medium",
            "emoji_frequency": 0.5,
            "common_emojis": ["😊"],
            "punctuation_style": "standard",
            "tone": "casual",
            "common_phrases": ["hey"],
            "formality_level": 0.3
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = style_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        cache = CacheManager()
        analyzer = StyleAnalyzer(api_key="test-key")
        
        training_data = ["msg" + str(i) for i in range(10)]
        
        # Analyze and cache
        profile = analyzer.analyze(training_data)
        cache.set_style_profile("user-123", profile)
        
        # Retrieve from cache
        cached = cache.get_style_profile("user-123")
        
        assert cached.tone == profile.tone
        assert cached.emoji_frequency == profile.emoji_frequency
