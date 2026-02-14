"""
Property-based tests for ConversationSummarizer service.

These tests validate universal properties that should hold for all inputs.
"""

import pytest
import json
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st
from backend.services.conversation_summarizer import ConversationSummarizer
from backend.models.data_models import Message, StyleProfile


# Strategy for generating valid messages
def message_strategy():
    """Generate a Message object."""
    return st.builds(
        Message,
        id=st.text(min_size=1, max_size=20),
        sender=st.sampled_from(["user", "friend"]),
        text=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        timestamp=st.just("2024-01-01T12:00:00Z"),
        is_ai_generated=st.booleans()
    )


# Strategy for generating message lists
def message_list_strategy():
    """Generate a non-empty list of Message objects."""
    return st.lists(
        message_strategy(),
        min_size=1,
        max_size=20
    )


# Strategy for generating StyleProfile
def style_profile_strategy():
    """Generate a StyleProfile object."""
    return st.builds(
        StyleProfile,
        sentence_length=st.sampled_from(["short", "medium", "long"]),
        emoji_frequency=st.floats(min_value=0.0, max_value=1.0),
        common_emojis=st.lists(st.text(min_size=1, max_size=2), max_size=5),
        punctuation_style=st.sampled_from(["minimal", "standard", "heavy"]),
        tone=st.sampled_from(["casual", "formal", "mixed"]),
        common_phrases=st.lists(st.text(min_size=1, max_size=20), max_size=5),
        formality_level=st.floats(min_value=0.0, max_value=1.0),
        analysis_timestamp=st.just("2024-01-01T12:00:00Z")
    )


class TestConversationSummarizerProperties:
    """Property-based tests for ConversationSummarizer."""
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_property_16_summary_completeness(self, mock_openai, messages, profile):
        """
        Property 16: Summary Completeness
        
        For any ConversationSession, the generated ConversationSummary should 
        include all messages from the session in the transcript field.
        
        **Validates: Requirements 5.1, 5.6**
        """
        # Mock API response
        api_response = json.dumps({
            "commitments": ["Test commitment"],
            "action_items": ["Test action"],
            "key_topics": ["Test topic"]
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Property: All messages must be in transcript
        assert len(summary.transcript) == len(messages), \
            f"Summary transcript has {len(summary.transcript)} messages, expected {len(messages)}"
        
        # Verify each message is preserved
        for i, msg in enumerate(messages):
            assert summary.transcript[i].id == msg.id
            assert summary.transcript[i].text == msg.text
            assert summary.transcript[i].sender == msg.sender
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_property_17_message_attribution_preservation(
        self, 
        mock_openai, 
        messages, 
        profile
    ):
        """
        Property 17: Message Attribution Preservation
        
        For any message in a ConversationSummary transcript, the isAiGenerated 
        field should correctly indicate whether the message was AI-generated 
        or human-written.
        
        **Validates: Requirements 5.2**
        """
        api_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Property: AI attribution must be preserved for all messages
        for i, msg in enumerate(messages):
            assert summary.transcript[i].is_ai_generated == msg.is_ai_generated, \
                f"Message {i} attribution mismatch: expected {msg.is_ai_generated}, got {summary.transcript[i].is_ai_generated}"
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_message_count_accuracy(self, mock_openai, messages, profile):
        """
        Test that AI and human message counts are always accurate.
        
        Validates that the counts match the actual message attribution.
        """
        api_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Count actual AI and human messages
        expected_ai_count = sum(1 for msg in messages if msg.is_ai_generated)
        expected_human_count = len(messages) - expected_ai_count
        
        # Property: Counts must match actual message attribution
        assert summary.ai_message_count == expected_ai_count, \
            f"AI count mismatch: expected {expected_ai_count}, got {summary.ai_message_count}"
        assert summary.human_message_count == expected_human_count, \
            f"Human count mismatch: expected {expected_human_count}, got {summary.human_message_count}"
        assert summary.ai_message_count + summary.human_message_count == len(messages)
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_summary_structure_validity(self, mock_openai, messages, profile):
        """
        Test that summary always has valid structure.
        
        Validates that all required fields are present and have correct types.
        """
        api_response = json.dumps({
            "commitments": ["commitment 1"],
            "action_items": ["action 1"],
            "key_topics": ["topic 1"]
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Validate structure
        assert hasattr(summary, 'session_id')
        assert hasattr(summary, 'transcript')
        assert hasattr(summary, 'commitments')
        assert hasattr(summary, 'action_items')
        assert hasattr(summary, 'key_topics')
        assert hasattr(summary, 'ai_message_count')
        assert hasattr(summary, 'human_message_count')
        assert hasattr(summary, 'escalation_count')
        assert hasattr(summary, 'duration')
        
        # Validate types
        assert isinstance(summary.commitments, list)
        assert isinstance(summary.action_items, list)
        assert isinstance(summary.key_topics, list)
        assert isinstance(summary.ai_message_count, int)
        assert isinstance(summary.human_message_count, int)
        assert isinstance(summary.escalation_count, int)
        assert isinstance(summary.duration, int)
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_empty_summary_fields_are_lists(self, mock_openai, messages, profile):
        """
        Test that empty summary fields are empty lists, not None.
        
        Validates that missing data is represented consistently.
        """
        # API returns empty arrays
        api_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Property: Empty fields should be empty lists, not None
        assert summary.commitments == []
        assert summary.action_items == []
        assert summary.key_topics == []
        assert isinstance(summary.commitments, list)
        assert isinstance(summary.action_items, list)
        assert isinstance(summary.key_topics, list)
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_escalation_count_non_negative(self, mock_openai, messages, profile):
        """
        Test that escalation count is always non-negative.
        
        Validates that the count is a valid non-negative integer.
        """
        api_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Property: Escalation count must be non-negative
        assert summary.escalation_count >= 0, \
            f"Escalation count cannot be negative: {summary.escalation_count}"
    
    @given(
        messages=message_list_strategy(),
        profile=style_profile_strategy()
    )
    @patch('backend.services.conversation_summarizer.OpenAI')
    def test_duration_non_negative(self, mock_openai, messages, profile):
        """
        Test that duration is always non-negative.
        
        Validates that the duration is a valid non-negative integer.
        """
        api_response = json.dumps({
            "commitments": [],
            "action_items": [],
            "key_topics": []
        })
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = api_response
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(api_key="test-key")
        summary = summarizer.summarize(messages, profile, "test-session")
        
        # Property: Duration must be non-negative
        assert summary.duration >= 0, \
            f"Duration cannot be negative: {summary.duration}"
