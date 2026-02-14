"""
Property-based tests for EscalationDetector service.

These tests validate universal properties that should hold for all inputs.
"""

import pytest
import json
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume
from backend.services.escalation_detector import EscalationDetector
from backend.models.data_models import Message


# Strategy for generating valid messages
message_strategy = st.text(min_size=1, max_size=500).filter(lambda x: x.strip())

# Strategy for generating conversation history
def message_list_strategy():
    """Generate a list of Message objects."""
    return st.lists(
        st.builds(
            Message,
            id=st.text(min_size=1, max_size=20),
            sender=st.sampled_from(["user", "friend"]),
            text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
            timestamp=st.just("2024-01-01T12:00:00Z"),
            is_ai_generated=st.booleans()
        ),
        max_size=10
    )


class TestEscalationDetectorProperties:
    """Property-based tests for EscalationDetector."""
    
    @given(
        message=message_strategy,
        confidence=st.floats(min_value=-100, max_value=200)
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_property_12_confidence_score_bounds(self, mock_openai, message, confidence):
        """
        Property 12: Confidence Score Bounds
        
        For any message analyzed by the Escalation_Detector, the confidence 
        score should be between 0 and 100 inclusive.
        
        **Validates: Requirements 4.3**
        """
        # Create mock response with potentially out-of-bounds confidence
        api_response = json.dumps({
            "needs_human": False,
            "reason": "Test reason",
            "urgency": "low",
            "confidence": confidence,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect(message, [])
        
        # Property: Confidence score must be bounded to 0-100
        assert 0 <= result.confidence_score <= 100, \
            f"Confidence score {result.confidence_score} is outside bounds [0, 100]"
    
    @given(
        message=message_strategy,
        confidence=st.floats(min_value=0, max_value=69.9)
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_property_13_low_confidence_triggers_escalation(
        self, 
        mock_openai, 
        message, 
        confidence
    ):
        """
        Property 13: Low Confidence Triggers Escalation
        
        For any message with a confidence score below 70, the Escalation_Detector 
        should set detected=true and flag the message for human review.
        
        **Validates: Requirements 4.4**
        """
        # Create mock response with low confidence
        api_response = json.dumps({
            "needs_human": False,  # Even if API says no escalation
            "reason": "Uncertain about context",
            "urgency": "medium",
            "confidence": confidence,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect(message, [])
        
        # Property: Low confidence (< 70) must trigger escalation
        assert result.detected is True, \
            f"Low confidence ({confidence}) should trigger escalation, but detected={result.detected}"
        assert result.confidence_score == confidence
    
    @given(
        message=message_strategy,
        confidence=st.floats(min_value=70, max_value=100)
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_high_confidence_respects_api_decision(
        self, 
        mock_openai, 
        message, 
        confidence
    ):
        """
        Test that high confidence (>= 70) respects the API's escalation decision.
        
        This is the complement to Property 13 - when confidence is high enough,
        the system should trust the API's judgment.
        """
        # Create mock response with high confidence and no escalation
        api_response = json.dumps({
            "needs_human": False,
            "reason": "AI can handle this",
            "urgency": "low",
            "confidence": confidence,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect(message, [])
        
        # With high confidence, should respect API decision (no escalation)
        assert result.detected is False, \
            f"High confidence ({confidence}) with needs_human=False should not escalate"
        assert result.confidence_score == confidence
    
    @given(
        message=message_strategy,
        needs_human=st.booleans(),
        confidence=st.floats(min_value=70, max_value=100)
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_escalation_result_structure(
        self, 
        mock_openai, 
        message, 
        needs_human,
        confidence
    ):
        """
        Test that EscalationResult always has valid structure.
        
        Validates that the result object is properly formed regardless of input.
        """
        api_response = json.dumps({
            "needs_human": needs_human,
            "reason": "Test reason",
            "urgency": "medium",
            "confidence": confidence,
            "category": "serious_question" if needs_human else None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect(message, [])
        
        # Validate result structure
        assert hasattr(result, 'detected')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'reason')
        assert hasattr(result, 'category')
        assert isinstance(result.detected, bool)
        assert isinstance(result.confidence_score, (int, float))
        assert 0 <= result.confidence_score <= 100
    
    @given(
        message=message_strategy,
        history=message_list_strategy()
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_detect_with_various_history_lengths(
        self, 
        mock_openai, 
        message, 
        history
    ):
        """
        Test that detection works with conversation histories of any length.
        
        Validates that the detector handles empty, short, and long histories.
        """
        api_response = json.dumps({
            "needs_human": False,
            "reason": "Test",
            "urgency": "low",
            "confidence": 85,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect(message, history)
        
        # Should successfully detect regardless of history length
        assert isinstance(result.detected, bool)
        assert 0 <= result.confidence_score <= 100
    
    @given(
        confidence=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @patch('backend.services.escalation_detector.OpenAI')
    def test_confidence_clamping_edge_cases(self, mock_openai, confidence):
        """
        Test that extreme confidence values are properly clamped.
        
        Validates that any confidence value, no matter how extreme, 
        gets bounded to [0, 100].
        """
        api_response = json.dumps({
            "needs_human": False,
            "reason": "Test",
            "urgency": "low",
            "confidence": confidence,
            "category": None
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        detector = EscalationDetector(api_key="test-key")
        result = detector.detect("test message", [])
        
        # Confidence must be clamped to valid range
        assert 0 <= result.confidence_score <= 100
        
        # Verify clamping behavior
        if confidence < 0:
            assert result.confidence_score == 0
        elif confidence > 100:
            assert result.confidence_score == 100
        else:
            assert result.confidence_score == confidence
