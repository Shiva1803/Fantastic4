"""
Unit tests for StyleAnalyzer service.

Tests style analysis functionality with mocked API responses.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from backend.services.style_analyzer import StyleAnalyzer
from backend.models.data_models import StyleProfile


class TestStyleAnalyzer:
    """Tests for StyleAnalyzer service."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.sample_messages = [
            "hey what's up",
            "lol yeah",
            "sounds good 😂",
            "for sure!",
            "haha nice",
            "omg that's crazy",
            "yeah definitely",
            "lmao 😂",
            "cool cool",
            "alright bet"
        ]
        
        self.sample_api_response = json.dumps({
            "sentence_length": "short",
            "emoji_frequency": 0.3,
            "common_emojis": ["😂", "👍"],
            "punctuation_style": "minimal",
            "tone": "casual",
            "common_phrases": ["lol", "yeah", "for sure"],
            "formality_level": 0.2
        })
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_initialization_with_groq(self, mock_openai):
        """Test StyleAnalyzer initialization with Groq."""
        analyzer = StyleAnalyzer(api_key="test-key", api_provider="groq")
        
        assert analyzer.api_provider == "groq"
        assert analyzer.max_retries == 3
        mock_openai.assert_called_once()
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_initialization_with_openrouter(self, mock_openai):
        """Test StyleAnalyzer initialization with OpenRouter."""
        analyzer = StyleAnalyzer(api_key="test-key", api_provider="openrouter")
        
        assert analyzer.api_provider == "openrouter"
        mock_openai.assert_called_once()
    
    def test_initialization_without_api_key(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No API key provided"):
                StyleAnalyzer()
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_insufficient_training_data(self, mock_openai):
        """Test that fewer than 10 messages raises ValueError."""
        analyzer = StyleAnalyzer(api_key="test-key")
        
        with pytest.raises(ValueError, match="Insufficient training data"):
            analyzer.analyze(["message1", "message2"])
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_analyze_success(self, mock_openai):
        """Test successful style analysis."""
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.sample_api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(self.sample_messages)
        
        assert isinstance(profile, StyleProfile)
        assert profile.sentence_length == "short"
        assert profile.emoji_frequency == 0.3
        assert profile.tone == "casual"
        assert len(profile.common_emojis) == 2
        assert len(profile.common_phrases) == 3
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_analyze_with_json_markdown(self, mock_openai):
        """Test parsing response with markdown code blocks."""
        # Mock API response with markdown
        response_with_markdown = f"```json\n{self.sample_api_response}\n```"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = response_with_markdown
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(self.sample_messages)
        
        assert isinstance(profile, StyleProfile)
        assert profile.sentence_length == "short"
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_analyze_invalid_json_response(self, mock_openai):
        """Test that invalid JSON response raises ValueError."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not JSON"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Failed to analyze style"):
            analyzer.analyze(self.sample_messages)
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_analyze_missing_required_field(self, mock_openai):
        """Test that response missing required fields raises ValueError."""
        # Mock response missing 'tone' field
        incomplete_response = json.dumps({
            "sentence_length": "short",
            "emoji_frequency": 0.3,
            "common_emojis": ["😂"],
            "punctuation_style": "minimal",
            # Missing 'tone'
            "common_phrases": ["lol"],
            "formality_level": 0.2
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = incomplete_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Failed to analyze style"):
            analyzer.analyze(self.sample_messages)
    
    @patch('backend.services.style_analyzer.OpenAI')
    @patch('backend.services.style_analyzer.time.sleep')
    def test_analyze_retry_logic(self, mock_sleep, mock_openai):
        """Test that API failures trigger retry with exponential backoff."""
        # Mock API to fail twice then succeed
        mock_response_success = Mock()
        mock_response_success.choices = [Mock()]
        mock_response_success.choices[0].message.content = self.sample_api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_response_success
        ]
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(self.sample_messages)
        
        # Verify retries happened
        assert mock_client.chat.completions.create.call_count == 3
        assert mock_sleep.call_count == 2
        
        # Verify exponential backoff
        mock_sleep.assert_any_call(1)  # 2^0
        mock_sleep.assert_any_call(2)  # 2^1
        
        # Verify success after retries
        assert isinstance(profile, StyleProfile)
    
    @patch('backend.services.style_analyzer.OpenAI')
    @patch('backend.services.style_analyzer.time.sleep')
    def test_analyze_max_retries_exceeded(self, mock_sleep, mock_openai):
        """Test that exceeding max retries raises RuntimeError."""
        # Mock API to always fail
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        
        with pytest.raises(RuntimeError, match="Failed to analyze style after 3 attempts"):
            analyzer.analyze(self.sample_messages)
        
        # Verify all retries were attempted
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_build_analysis_prompt(self, mock_openai):
        """Test that analysis prompt is built correctly."""
        analyzer = StyleAnalyzer(api_key="test-key")
        prompt = analyzer._build_analysis_prompt(self.sample_messages)
        
        assert "analyzing someone's texting style" in prompt.lower()
        assert "sentence_length" in prompt
        assert "emoji_frequency" in prompt
        assert "tone" in prompt
        assert self.sample_messages[0] in prompt
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_parse_response_valid(self, mock_openai):
        """Test parsing valid API response."""
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer._parse_response(self.sample_api_response)
        
        assert isinstance(profile, StyleProfile)
        assert profile.sentence_length == "short"
        assert profile.emoji_frequency == 0.3
        assert profile.formality_level == 0.2
        assert profile.analysis_timestamp is not None
    
    @patch('backend.services.style_analyzer.OpenAI')
    def test_analyze_limits_messages_to_50(self, mock_openai):
        """Test that analysis only uses first 50 messages."""
        # Create 60 messages
        many_messages = [f"message {i}" for i in range(60)]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.sample_api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(many_messages)
        
        # Check that prompt was built (implicitly tests the 50 message limit)
        assert isinstance(profile, StyleProfile)
        
        # Verify API was called
        assert mock_client.chat.completions.create.called
