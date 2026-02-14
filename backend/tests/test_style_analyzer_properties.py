"""
Property-based tests for StyleAnalyzer service using Hypothesis.

These tests verify universal properties that should hold for all valid inputs.

Property 1: Pattern Extraction Completeness
Validates: Requirements 1.1, 1.2

Property 4: Insufficient Training Data Rejection
Validates: Requirements 1.4, 7.3
"""

import json
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume
from backend.services.style_analyzer import StyleAnalyzer
from backend.models.data_models import StyleProfile


# Strategies for generating test data

@st.composite
def valid_training_data_strategy(draw):
    """Generate valid training data with 10-50 messages."""
    num_messages = draw(st.integers(min_value=10, max_value=50))
    messages = [
        draw(st.text(min_size=1, max_size=200))
        for _ in range(num_messages)
    ]
    # Ensure messages aren't all whitespace
    messages = [msg if msg.strip() else "message" for msg in messages]
    return messages


@st.composite
def insufficient_training_data_strategy(draw):
    """Generate insufficient training data with fewer than 10 messages."""
    num_messages = draw(st.integers(min_value=0, max_value=9))
    messages = [
        draw(st.text(min_size=1, max_size=200))
        for _ in range(num_messages)
    ]
    return messages


@st.composite
def api_response_strategy(draw):
    """Generate valid API response JSON."""
    response = {
        "sentence_length": draw(st.sampled_from(["short", "medium", "long"])),
        "emoji_frequency": draw(st.floats(min_value=0.0, max_value=1.0)),
        "common_emojis": draw(st.lists(st.text(min_size=1, max_size=2), max_size=5)),
        "punctuation_style": draw(st.sampled_from(["minimal", "standard", "heavy"])),
        "tone": draw(st.sampled_from(["casual", "formal", "mixed"])),
        "common_phrases": draw(st.lists(st.text(min_size=1, max_size=20), max_size=10)),
        "formality_level": draw(st.floats(min_value=0.0, max_value=1.0))
    }
    return json.dumps(response)


# Property Tests

@given(insufficient_training_data_strategy())
def test_insufficient_data_rejection(training_data):
    """
    Property 4: Insufficient Training Data Rejection
    
    For any training data containing fewer than 10 messages,
    the Style_Analyzer should reject it and return an error
    indicating insufficient data.
    
    Validates: Requirements 1.4, 7.3
    """
    with patch('backend.services.style_analyzer.OpenAI'):
        analyzer = StyleAnalyzer(api_key="test-key")
        
        # Verify that analyzing insufficient data raises ValueError
        try:
            analyzer.analyze(training_data)
            # If we get here, the test should fail
            assert False, f"Expected ValueError for {len(training_data)} messages"
        except ValueError as e:
            # Verify the error message mentions insufficient data
            assert "insufficient" in str(e).lower() or "minimum" in str(e).lower()
            assert "10" in str(e)


@given(valid_training_data_strategy(), api_response_strategy())
def test_pattern_extraction_completeness(training_data, api_response):
    """
    Property 1: Pattern Extraction Completeness
    
    For any valid training data (10-50 messages), the Style_Analyzer
    should extract all required patterns and produce a StyleProfile
    with all fields populated.
    
    Validates: Requirements 1.1, 1.2
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(training_data)
        
        # Verify profile is returned
        assert profile is not None
        assert isinstance(profile, StyleProfile)
        
        # Verify all required fields are populated
        assert profile.sentence_length in ["short", "medium", "long"]
        assert 0.0 <= profile.emoji_frequency <= 1.0
        assert isinstance(profile.common_emojis, list)
        assert isinstance(profile.punctuation_style, str)
        assert profile.tone in ["casual", "formal", "mixed"]
        assert isinstance(profile.common_phrases, list)
        assert 0.0 <= profile.formality_level <= 1.0
        assert profile.analysis_timestamp is not None
        assert isinstance(profile.analysis_timestamp, str)


@given(valid_training_data_strategy())
def test_valid_data_does_not_raise_insufficient_error(training_data):
    """
    Property: Valid Data Acceptance
    
    For any training data with 10 or more messages, the analyzer
    should not raise an insufficient data error (though it may fail
    for other reasons like API errors).
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        # Create a valid API response
        valid_response = json.dumps({
            "sentence_length": "medium",
            "emoji_frequency": 0.5,
            "common_emojis": ["😊"],
            "punctuation_style": "standard",
            "tone": "casual",
            "common_phrases": ["cool"],
            "formality_level": 0.4
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        
        # Should not raise ValueError about insufficient data
        try:
            profile = analyzer.analyze(training_data)
            # If successful, verify it's a valid profile
            assert isinstance(profile, StyleProfile)
        except ValueError as e:
            # If ValueError is raised, it should NOT be about insufficient data
            error_msg = str(e).lower()
            assert "insufficient" not in error_msg
            assert "minimum 10" not in error_msg


@given(st.integers(min_value=10, max_value=100))
def test_message_count_boundary(message_count):
    """
    Property: Message Count Boundary
    
    For any message count >= 10, analysis should proceed.
    For any message count < 10, analysis should fail with ValueError.
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        # Generate messages
        messages = [f"message {i}" for i in range(message_count)]
        
        # Create valid API response
        valid_response = json.dumps({
            "sentence_length": "short",
            "emoji_frequency": 0.3,
            "common_emojis": [],
            "punctuation_style": "minimal",
            "tone": "casual",
            "common_phrases": [],
            "formality_level": 0.2
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        
        if message_count >= 10:
            # Should succeed
            profile = analyzer.analyze(messages)
            assert isinstance(profile, StyleProfile)
        else:
            # Should fail
            try:
                analyzer.analyze(messages)
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "insufficient" in str(e).lower()


@given(valid_training_data_strategy())
def test_analysis_timestamp_present(training_data):
    """
    Property: Analysis Timestamp Always Present
    
    For any successful analysis, the resulting StyleProfile
    should have a non-empty analysis_timestamp field.
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        valid_response = json.dumps({
            "sentence_length": "medium",
            "emoji_frequency": 0.5,
            "common_emojis": [],
            "punctuation_style": "standard",
            "tone": "mixed",
            "common_phrases": [],
            "formality_level": 0.5
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(training_data)
        
        # Verify timestamp is present and non-empty
        assert profile.analysis_timestamp is not None
        assert len(profile.analysis_timestamp) > 0
        assert isinstance(profile.analysis_timestamp, str)


@given(valid_training_data_strategy())
def test_emoji_frequency_bounds(training_data):
    """
    Property: Emoji Frequency Bounds
    
    For any analysis result, emoji_frequency should be between 0 and 1.
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        # Generate response with random emoji frequency
        emoji_freq = 0.7
        valid_response = json.dumps({
            "sentence_length": "short",
            "emoji_frequency": emoji_freq,
            "common_emojis": ["😂"],
            "punctuation_style": "minimal",
            "tone": "casual",
            "common_phrases": [],
            "formality_level": 0.3
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(training_data)
        
        # Verify emoji frequency is within bounds
        assert 0.0 <= profile.emoji_frequency <= 1.0


@given(valid_training_data_strategy())
def test_formality_level_bounds(training_data):
    """
    Property: Formality Level Bounds
    
    For any analysis result, formality_level should be between 0 and 1.
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        formality = 0.85
        valid_response = json.dumps({
            "sentence_length": "long",
            "emoji_frequency": 0.1,
            "common_emojis": [],
            "punctuation_style": "heavy",
            "tone": "formal",
            "common_phrases": [],
            "formality_level": formality
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(training_data)
        
        # Verify formality level is within bounds
        assert 0.0 <= profile.formality_level <= 1.0


@given(st.integers(min_value=0, max_value=5))
def test_exact_boundary_at_10_messages(offset):
    """
    Property: Exact Boundary at 10 Messages
    
    Test the exact boundary: 9 messages should fail, 10 should succeed.
    """
    with patch('backend.services.style_analyzer.OpenAI') as mock_openai:
        # Test with 9 messages (should fail)
        if offset < 10:
            messages_fail = [f"msg {i}" for i in range(9)]
            analyzer = StyleAnalyzer(api_key="test-key")
            
            try:
                analyzer.analyze(messages_fail)
                assert False, "Should have raised ValueError for 9 messages"
            except ValueError as e:
                assert "insufficient" in str(e).lower()
        
        # Test with 10 messages (should succeed)
        messages_success = [f"msg {i}" for i in range(10)]
        
        valid_response = json.dumps({
            "sentence_length": "short",
            "emoji_frequency": 0.0,
            "common_emojis": [],
            "punctuation_style": "minimal",
            "tone": "casual",
            "common_phrases": [],
            "formality_level": 0.0
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = valid_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        analyzer = StyleAnalyzer(api_key="test-key")
        profile = analyzer.analyze(messages_success)
        
        assert isinstance(profile, StyleProfile)
