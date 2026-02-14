"""
Unit tests for EscalationDetector service.

Tests escalation detection functionality with mocked API responses.
"""

import pytest
import json
from unittest.mock import Mock, patch
from backend.services.escalation_detector import EscalationDetector
from backend.models.data_models import Message, EscalationResult


class TestEscalationDetector:
    """Tests for EscalationDetector service."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.sample_history = [
            Message(
                id="msg-1",
                sender="friend",
                text="hey what's up?",
                timestamp="2024-01-01T12:00:00Z",
                is_ai_generated=False
            )
        ]
        
        self.escalation_response = json.dumps({
            "needs_human": True,
            "reason": "Serious health concern detected",
            "urgency": "high",
            "confidence": 95,
            "category": "serious_question"
        })
        
        self.no_escalation_response = json.dumps({
            "needs_human": False,
            "reason": "Casual conversation, AI can handle",
            "urgency": "low",
            "confidence": 85,
            "category": None
        })
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_initialization(self, mock_openai):
        """Test EscalationDetector initialization."""
        detector = EscalationDetector(api_key="test-key")
        assert detector.api_provider == "groq"
        assert detector.max_retries == 3
    
    def test_initialization_without_api_key(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="No API key provided"):
                EscalationDetector()
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_escalation(self, mock_openai):
        """Test detecting a message that needs escalation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.escalation_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("your mom is in the hospital?", self.sample_history)
        
        assert isinstance(result, EscalationResult)
        assert result.detected is True
        assert result.confidence_score == 95
        assert "health" in result.reason.lower()
        assert result.category == "serious_question"
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_no_escalation(self, mock_openai):
        """Test detecting a message that doesn't need escalation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.no_escalation_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("wanna grab lunch?", self.sample_history)
        
        assert result.detected is False
        assert result.confidence_score == 85
        assert result.category is None
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_with_empty_message(self, mock_openai):
        """Test that empty message raises ValueError."""
        detector = EscalationDetector(api_key="test-key")
        
        with pytest.raises(ValueError, match="message cannot be empty"):
            detector.detect("", self.sample_history)
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_low_confidence_triggers_escalation(self, mock_openai):
        """Test that confidence < 70 triggers escalation."""
        low_confidence_response = json.dumps({
            "needs_human": False,
            "reason": "Uncertain about context",
            "urgency": "medium",
            "confidence": 65,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = low_confidence_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("ambiguous message", self.sample_history)
        
        # Should be escalated due to low confidence
        assert result.detected is True
        assert result.confidence_score == 65
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_confidence_score_bounds(self, mock_openai):
        """Test that confidence scores are bounded to 0-100."""
        out_of_bounds_response = json.dumps({
            "needs_human": False,
            "reason": "Test",
            "urgency": "low",
            "confidence": 150,  # Out of bounds
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = out_of_bounds_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("test message", self.sample_history)
        
        # Should be clamped to 100
        assert 0 <= result.confidence_score <= 100
    
    @patch('backend.services.escalation_detector.OpenAI')
    @patch('backend.services.escalation_detector.time.sleep')
    def test_detect_retry_logic(self, mock_sleep, mock_openai):
        """Test that API failures trigger retry."""
        mock_response_success = Mock()
        mock_response_success.choices = [Mock()]
        mock_response_success.choices[0].message.content = self.no_escalation_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response_success
        ]
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("test", self.sample_history)
        
        assert mock_client.chat.completions.create.call_count == 2
        assert result.detected is False
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_with_markdown_json(self, mock_openai):
        """Test parsing response with markdown code blocks."""
        response_with_markdown = f"```json\n{self.escalation_response}\n```"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = response_with_markdown
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("serious message", self.sample_history)
        
        assert result.detected is True
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_build_detection_prompt(self, mock_openai):
        """Test that detection prompt is built correctly."""
        detector = EscalationDetector(api_key="test-key")
        prompt = detector._build_detection_prompt("test message", self.sample_history)
        
        assert "test message" in prompt
        assert "needs_human" in prompt
        assert "confidence" in prompt
        assert "hey what's up?" in prompt  # from history
    
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_with_empty_history(self, mock_openai):
        """Test detection with no conversation history."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = self.no_escalation_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("hello", [])
        
        assert isinstance(result, EscalationResult)
