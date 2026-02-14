"""
Unit tests for ResponseGenerator service.

Tests response generation functionality with mocked API responses.
"""

import pytest
from unittest.mock import Mock, patch
from backend.services.response_generator import ResponseGenerator
from backend.models.data_models import StyleProfile, Message


class TestResponseGenerator:
    """Tests for ResponseGenerator service."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.sample_profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.8,
            common_emojis=["😂", "👍"],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=["lol", "yeah", "for sure"],
            formality_level=0.2,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        
        self.sample_history = [
            Message(
                id="msg-1",
                sender="friend",
                text="hey what's up?",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            ),
            Message(
                id="msg-2",
                sender="user",
                text="not much hbu",
                timestamp="2024-01-01T12:01:00Z",
                is_ai_generated=False
            )
        ]
    
    @patch('backend.services.response_generator.OpenAI')
    def test_initialization_with_groq(self, mock_openai):
        """Test ResponseGenerator initialization with Groq."""
        generator = ResponseGenerator(api_key="test-key", api_provider="groq")
        
        assert generator.api_provider == "groq"
        assert generator.max_retries == 3
        mock_openai.assert_called_once()
    
    @patch('backend.services.response_generator.OpenAI')
    def test_initialization_with_openrouter(self, mock_openai):
        """Test ResponseGenerator initialization with OpenRouter."""
        generator = ResponseGenerator(api_key="test-key", api_provider="openrouter")
        
        assert generator.api_provider == "openrouter"
        mock_openai.assert_called_once()
    
    def test_initialization_without_api_key(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No API key provided"):
                ResponseGenerator()
    
    @patch('backend.services.response_generator.OpenAI')
    def test_generate_success(self, mock_openai):
        """Test successful response generation."""
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "sounds good!"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            self.sample_history,
            "wanna grab lunch?"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert response == "sounds good!"
    
    @patch('backend.services.response_generator.OpenAI')
    def test_generate_with_empty_message(self, mock_openai):
        """Test that empty incoming message raises ValueError."""
        generator = ResponseGenerator(api_key="test-key")
        
        with pytest.raises(ValueError, match="incoming_message cannot be empty"):
            generator.generate(self.sample_profile, self.sample_history, "")
    
    @patch('backend.services.response_generator.OpenAI')
    def test_generate_with_whitespace_message(self, mock_openai):
        """Test that whitespace-only message raises ValueError."""
        generator = ResponseGenerator(api_key="test-key")
        
        with pytest.raises(ValueError, match="incoming_message cannot be empty"):
            generator.generate(self.sample_profile, self.sample_history, "   ")
    
    @patch('backend.services.response_generator.OpenAI')
    def test_generate_with_empty_history(self, mock_openai):
        """Test generation with no conversation history."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "hey!"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            [],
            "hello"
        )
        
        assert response == "hey!"
    
    @patch('backend.services.response_generator.OpenAI')
    def test_clean_response_removes_quotes(self, mock_openai):
        """Test that response cleaning removes surrounding quotes."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"yeah for sure"'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            self.sample_history,
            "you coming?"
        )
        
        assert response == "yeah for sure"
        assert not response.startswith('"')
    
    @patch('backend.services.response_generator.OpenAI')
    def test_clean_response_removes_prefixes(self, mock_openai):
        """Test that response cleaning removes common prefixes."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "You: sounds good"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            self.sample_history,
            "wanna meet at 5?"
        )
        
        assert response == "sounds good"
        assert not response.startswith("You:")
    
    @patch('backend.services.response_generator.OpenAI')
    @patch('backend.services.response_generator.time.sleep')
    def test_generate_retry_logic(self, mock_sleep, mock_openai):
        """Test that API failures trigger retry with exponential backoff."""
        # Mock API to fail twice then succeed
        mock_response_success = Mock()
        mock_response_success.choices = [Mock()]
        mock_response_success.choices[0].message.content = "cool"
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_response_success
        ]
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            self.sample_history,
            "test message"
        )
        
        # Verify retries happened
        assert mock_client.chat.completions.create.call_count == 3
        assert mock_sleep.call_count == 2
        
        # Verify exponential backoff
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1
        
        # Verify success after retries
        assert response == "cool"
    
    @patch('backend.services.response_generator.OpenAI')
    @patch('backend.services.response_generator.time.sleep')
    def test_generate_max_retries_exceeded(self, mock_sleep, mock_openai):
        """Test that exceeding max retries raises RuntimeError."""
        # Mock API to always fail
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Failed to generate response after 3 attempts"):
            generator.generate(
                self.sample_profile,
                self.sample_history,
                "test message"
            )
        
        # Verify all retries were attempted
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('backend.services.response_generator.OpenAI')
    def test_build_response_prompt(self, mock_openai):
        """Test that response prompt is built correctly."""
        generator = ResponseGenerator(api_key="test-key")
        prompt = generator._build_response_prompt(
            self.sample_profile,
            self.sample_history,
            "what's up?"
        )
        
        assert "texting AS this person" in prompt
        assert "short" in prompt  # sentence_length
        assert "casual" in prompt  # tone
        assert "what's up?" in prompt  # incoming message
        assert "hey what's up?" in prompt  # from history
    
    @patch('backend.services.response_generator.OpenAI')
    def test_format_style_description(self, mock_openai):
        """Test style profile formatting."""
        generator = ResponseGenerator(api_key="test-key")
        description = generator._format_style_description(self.sample_profile)
        
        assert "short" in description
        assert "casual" in description
        assert "minimal" in description
        assert "😂" in description or "👍" in description
    
    @patch('backend.services.response_generator.OpenAI')
    def test_generate_with_long_history(self, mock_openai):
        """Test that only last 10 messages are used from history."""
        # Create 15 messages
        long_history = [
            Message(
                id=f"msg-{i}",
                sender="friend" if i % 2 == 0 else "user",
                text=f"message {i}",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            )
            for i in range(15)
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(
            self.sample_profile,
            long_history,
            "test"
        )
        
        # Verify API was called
        assert mock_client.chat.completions.create.called
        
        # Check that prompt was built (implicitly tests the 10 message limit)
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        
        # Should contain recent messages but not all 15
        assert "message 14" in prompt  # Most recent
        assert "message 5" in prompt   # 10th from end
        assert "message 0" not in prompt  # Too old
    
    @patch('backend.services.response_generator.OpenAI')
    def test_emoji_frequency_high(self, mock_openai):
        """Test style description for high emoji frequency."""
        high_emoji_profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.9,
            common_emojis=["😂"],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=[],
            formality_level=0.1,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        
        generator = ResponseGenerator(api_key="test-key")
        description = generator._format_style_description(high_emoji_profile)
        
        assert "frequently" in description.lower()
    
    @patch('backend.services.response_generator.OpenAI')
    def test_emoji_frequency_low(self, mock_openai):
        """Test style description for low emoji frequency."""
        low_emoji_profile = StyleProfile(
            sentence_length="long",
            emoji_frequency=0.1,
            common_emojis=[],
            punctuation_style="heavy",
            tone="formal",
            common_phrases=[],
            formality_level=0.9,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        
        generator = ResponseGenerator(api_key="test-key")
        description = generator._format_style_description(low_emoji_profile)
        
        assert "rarely" in description.lower()
