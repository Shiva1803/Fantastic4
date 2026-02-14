"""
Unit tests for ConversationSummarizer service.

Tests conversation summarization functionality with mocked API responses.
"""

import pytest
import json
from unittest.mock import Mock, patch
from backend.services.conversation_summarizer import ConversationSummarizer
from backend.models.data_models import Message, StyleProfile, ConversationSummary


class TestConversationSummarizer:
    """Tests for ConversationSummarizer service."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.sample_profile = StyleProfile(
            sentence_length="medium",
            emoji_frequency=0.5,
            common_emojis=["😊", "👍"],
            punctuation_style="standard",
            tone="casual",
            common_phrases=["hey", "cool"],
            formality_level=0.3,
            analysis_timestamp="2024-01-01T12:00:00Z"
        )
        
        self.sample_messages = [
            Message(
                id="msg-1",
                sender="friend",
                text="Hey, want to grab lunch tomorrow at 3pm?",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            ),
            Message(
                id="msg-2",
                sender="user",
                text="Sure! I'll meet you at the cafe",
                timestamp="2024-01-01T12:01:00Z",
                is_ai_generated=True
            ),
            Message(
                id="msg-3",
                sender="friend",
                text="Great! Can you bring that book I lent you?",
                timestamp="2024-01-01T12:02:00Z",
                is_ai_generated=False
            )
        ]
        
        self.summary_response = json.dumps({
            "commitments": ["Lunch at 3pm tomorrow", "Meet at the cafe", "Bring borrowed book"],
            "action_items": ["Bring book to lunch"],
            "key_topics": ["Lunch plans", "Borrowed book"]
        })
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_initialization(self, mock_openai):
        """Test ConversationSummarizer initialization."""
        summarizer = ConversationSummarizer(api_key="test-key")
        assert summarizer.api_provider == "groq"
        assert summarizer.max_retries == 3
    
    def test_initialization_without_api_key(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No API key provided"):
                ConversationSummarizer()
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_summarize_success(self, mock_openai):
        """Test successful conversation summarization."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(
            self.sample_messages,
            self.sample_profile,
            "session-123"
        )
        
        assert isinstance(summary, ConversationSummary)
        assert summary.session_id == "session-123"
        assert len(summary.transcript) == 3
        assert len(summary.commitments) == 3
        assert len(summary.action_items) == 1
        assert len(summary.key_topics) == 2
        assert summary.ai_message_count == 1
        assert summary.human_message_count == 2
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_summarize_with_empty_messages(self, mock_openai):
        """Test that empty messages list raises ValueError."""
        summarizer = ConversationSummarizer(api_key="test-key")
        
        with pytest.raises(ValueError, match="messages list cannot be empty"):
            summarizer.summarize([], self.sample_profile, "session-123")
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_message_count_accuracy(self, mock_openai):
        """Test that AI and human message counts are accurate."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        messages = [
            Message("1", "friend", "hi", "2024-01-01T12:00:00Z", False),
            Message("2", "user", "hey", "2024-01-01T12:01:00Z", True),
            Message("3", "friend", "how are you", "2024-01-01T12:02:00Z", False),
            Message("4", "user", "good", "2024-01-01T12:03:00Z", True),
            Message("5", "user", "actually let me respond", "2024-01-01T12:04:00Z", False),
        ]
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, self.sample_profile, "session-123")
        
        assert summary.ai_message_count == 2
        assert summary.human_message_count == 3
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_escalation_count(self, mock_openai):
        """Test that escalation count is calculated correctly."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Conversation with one escalation (user takes over after AI)
        messages = [
            Message("1", "friend", "hi", "2024-01-01T12:00:00Z", False),
            Message("2", "user", "hey", "2024-01-01T12:01:00Z", True),  # AI response
            Message("3", "friend", "serious question", "2024-01-01T12:02:00Z", False),
            Message("4", "user", "let me handle this", "2024-01-01T12:03:00Z", False),  # Escalation!
        ]
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, self.sample_profile, "session-123")
        
        assert summary.escalation_count == 1
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_duration_calculation(self, mock_openai):
        """Test that conversation duration is calculated correctly."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        messages = [
            Message("1", "friend", "hi", "2024-01-01T12:00:00Z", False),
            Message("2", "user", "hey", "2024-01-01T12:05:00Z", True),  # 5 minutes later
        ]
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, self.sample_profile, "session-123")
        
        assert summary.duration == 300  # 5 minutes = 300 seconds
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_empty_summary_fields(self, mock_openai):
        """Test handling of empty summary fields."""
        empty_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = empty_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(
            self.sample_messages,
            self.sample_profile,
            "session-123"
        )
        
        assert summary.commitments == []
        assert summary.action_items == []
        assert summary.key_topics == []
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_parse_response_with_markdown(self, mock_openai):
        """Test parsing response with markdown code blocks."""
        response_with_markdown = f"```json\n{self.summary_response}\n```"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = response_with_markdown
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(
            self.sample_messages,
            self.sample_profile,
            "session-123"
        )
        
        assert len(summary.commitments) > 0
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    @patch('backend.services.conversation_summarizer.time.sleep')
    def test_retry_logic(self, mock_sleep, mock_openai):
        """Test that API failures trigger retry."""
        mock_response_success = Mock()
        mock_response_success.choices = [Mock()]
        mock_response_success.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response_success
        ]
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(
            self.sample_messages,
            self.sample_profile,
            "session-123"
        )
        
        assert mock_client.chat.completions.create.call_count == 2
        assert isinstance(summary, ConversationSummary)
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    @patch('backend.services.conversation_summarizer.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_openai):
        """Test that max retries raises RuntimeError."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Failed to generate summary"):
            summarizer.summarize(
                self.sample_messages,
                self.sample_profile,
                "session-123"
            )
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_build_summary_prompt(self, mock_openai):
        """Test that summary prompt is built correctly."""
        summarizer = ConversationSummarizer(api_key="test-key")
        prompt = summarizer._build_summary_prompt(
            self.sample_messages,
            self.sample_profile
        )
        
        assert "Conversation Transcript:" in prompt
        assert "commitments" in prompt
        assert "action_items" in prompt
        assert "key_topics" in prompt
        assert self.sample_messages[0].text in prompt
    
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_transcript_preservation(self, mock_openai):
        """Test that all messages are preserved in transcript."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.summary_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(
            self.sample_messages,
            self.sample_profile,
            "session-123"
        )
        
        # All messages should be in transcript
        assert len(summary.transcript) == len(self.sample_messages)
        for i, msg in enumerate(summary.transcript):
            assert msg.id == self.sample_messages[i].id
            assert msg.text == self.sample_messages[i].text
            assert msg.is_ai_generated == self.sample_messages[i].is_ai_generated
