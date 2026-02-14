"""
Property-based tests for data models using Hypothesis.

These tests verify universal properties that should hold for all valid inputs,
particularly focusing on serialization/deserialization round-trips.

Property 2: Style Profile Caching Round-Trip
Validates: Requirements 1.3, 9.5, 10.1
"""

from hypothesis import given, strategies as st
from backend.models.data_models import (
    StyleProfile,
    Message,
    EscalationResult,
    ConversationSession,
    ConversationSummary
)


# Custom strategies for generating valid test data

@st.composite
def style_profile_strategy(draw):
    """Generate random valid StyleProfile instances."""
    return StyleProfile(
        sentence_length=draw(st.sampled_from(["short", "medium", "long"])),
        emoji_frequency=draw(st.floats(min_value=0.0, max_value=1.0)),
        common_emojis=draw(st.lists(st.text(min_size=1, max_size=2), max_size=10)),
        punctuation_style=draw(st.sampled_from(["minimal", "standard", "heavy"])),
        tone=draw(st.sampled_from(["casual", "formal", "mixed"])),
        common_phrases=draw(st.lists(st.text(min_size=1, max_size=20), max_size=10)),
        formality_level=draw(st.floats(min_value=0.0, max_value=1.0)),
        analysis_timestamp=draw(st.text(min_size=10, max_size=30))
    )


@st.composite
def message_strategy(draw):
    """Generate random valid Message instances."""
    # Generate text that's not just whitespace
    text = draw(st.text(min_size=1, max_size=500))
    while not text.strip():
        text = draw(st.text(min_size=1, max_size=500))
    
    return Message(
        id=draw(st.text(min_size=1, max_size=50)),
        sender=draw(st.sampled_from(["user", "friend", "ai"])),
        text=text,
        timestamp=draw(st.text(min_size=10, max_size=30)),
        is_ai_generated=draw(st.booleans())
    )


@st.composite
def escalation_result_strategy(draw):
    """Generate random valid EscalationResult instances."""
    detected = draw(st.booleans())
    confidence_score = draw(st.floats(min_value=0.0, max_value=100.0))
    
    if detected:
        reason = draw(st.text(min_size=1, max_size=200))
        category = draw(st.sampled_from([
            "serious_question",
            "emotional_distress",
            "unfamiliar_topic",
            "scheduling",
            "sensitive_info"
        ]))
    else:
        reason = None
        category = None
    
    return EscalationResult(
        detected=detected,
        confidence_score=confidence_score,
        reason=reason,
        category=category
    )


@st.composite
def conversation_session_strategy(draw):
    """Generate random valid ConversationSession instances."""
    return ConversationSession(
        session_id=draw(st.text(min_size=1, max_size=50)),
        messages=draw(st.lists(message_strategy(), max_size=20)),
        style_profile=draw(style_profile_strategy()),
        start_time=draw(st.text(min_size=10, max_size=30)),
        end_time=draw(st.one_of(st.none(), st.text(min_size=10, max_size=30))),
        escalation_count=draw(st.integers(min_value=0, max_value=100))
    )


@st.composite
def conversation_summary_strategy(draw):
    """Generate random valid ConversationSummary instances."""
    return ConversationSummary(
        session_id=draw(st.text(min_size=1, max_size=50)),
        transcript=draw(st.lists(message_strategy(), max_size=20)),
        commitments=draw(st.lists(st.text(min_size=1, max_size=100), max_size=10)),
        action_items=draw(st.lists(st.text(min_size=1, max_size=100), max_size=10)),
        key_topics=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10)),
        ai_message_count=draw(st.integers(min_value=0, max_value=100)),
        human_message_count=draw(st.integers(min_value=0, max_value=100)),
        escalation_count=draw(st.integers(min_value=0, max_value=100)),
        duration=draw(st.integers(min_value=0, max_value=86400))
    )


# Property Tests

@given(style_profile_strategy())
def test_style_profile_serialization_round_trip(profile):
    """
    Property 2: Style Profile Caching Round-Trip
    
    For any StyleProfile, serializing to dict then deserializing
    should produce an equivalent StyleProfile with all fields preserved.
    
    Validates: Requirements 1.3, 9.5, 10.1
    """
    # Serialize to dict
    data = profile.to_dict()
    
    # Deserialize back to StyleProfile
    restored = StyleProfile.from_dict(data)
    
    # Verify all fields are preserved
    assert restored.sentence_length == profile.sentence_length
    assert restored.emoji_frequency == profile.emoji_frequency
    assert restored.common_emojis == profile.common_emojis
    assert restored.punctuation_style == profile.punctuation_style
    assert restored.tone == profile.tone
    assert restored.common_phrases == profile.common_phrases
    assert restored.formality_level == profile.formality_level
    assert restored.analysis_timestamp == profile.analysis_timestamp


@given(message_strategy())
def test_message_serialization_round_trip(message):
    """
    Property: Message Serialization Round-Trip
    
    For any Message, serializing to dict then deserializing
    should produce an equivalent Message with all fields preserved.
    """
    # Serialize to dict
    data = message.to_dict()
    
    # Deserialize back to Message
    restored = Message.from_dict(data)
    
    # Verify all fields are preserved
    assert restored.id == message.id
    assert restored.sender == message.sender
    assert restored.text == message.text
    assert restored.timestamp == message.timestamp
    assert restored.is_ai_generated == message.is_ai_generated


@given(escalation_result_strategy())
def test_escalation_result_serialization_round_trip(result):
    """
    Property: EscalationResult Serialization Round-Trip
    
    For any EscalationResult, serializing to dict then deserializing
    should produce an equivalent EscalationResult with all fields preserved.
    """
    # Serialize to dict
    data = result.to_dict()
    
    # Deserialize back to EscalationResult
    restored = EscalationResult.from_dict(data)
    
    # Verify all fields are preserved
    assert restored.detected == result.detected
    assert restored.confidence_score == result.confidence_score
    assert restored.reason == result.reason
    assert restored.category == result.category


@given(conversation_session_strategy())
def test_conversation_session_serialization_round_trip(session):
    """
    Property 3: Session Persistence Round-Trip
    
    For any ConversationSession, storing it then retrieving it
    should return an equivalent session with all messages and metadata preserved.
    
    Validates: Requirements 10.2
    """
    # Serialize to dict
    data = session.to_dict()
    
    # Deserialize back to ConversationSession
    restored = ConversationSession.from_dict(data)
    
    # Verify all fields are preserved
    assert restored.session_id == session.session_id
    assert len(restored.messages) == len(session.messages)
    assert restored.start_time == session.start_time
    assert restored.end_time == session.end_time
    assert restored.escalation_count == session.escalation_count
    
    # Verify messages are preserved
    for original_msg, restored_msg in zip(session.messages, restored.messages):
        assert restored_msg.id == original_msg.id
        assert restored_msg.sender == original_msg.sender
        assert restored_msg.text == original_msg.text
        assert restored_msg.is_ai_generated == original_msg.is_ai_generated
    
    # Verify style profile is preserved
    assert restored.style_profile.sentence_length == session.style_profile.sentence_length
    assert restored.style_profile.emoji_frequency == session.style_profile.emoji_frequency
    assert restored.style_profile.tone == session.style_profile.tone


@given(conversation_summary_strategy())
def test_conversation_summary_serialization_round_trip(summary):
    """
    Property: ConversationSummary Serialization Round-Trip
    
    For any ConversationSummary, serializing to dict then deserializing
    should produce an equivalent ConversationSummary with all fields preserved.
    """
    # Serialize to dict
    data = summary.to_dict()
    
    # Deserialize back to ConversationSummary
    restored = ConversationSummary.from_dict(data)
    
    # Verify all fields are preserved
    assert restored.session_id == summary.session_id
    assert len(restored.transcript) == len(summary.transcript)
    assert restored.commitments == summary.commitments
    assert restored.action_items == summary.action_items
    assert restored.key_topics == summary.key_topics
    assert restored.ai_message_count == summary.ai_message_count
    assert restored.human_message_count == summary.human_message_count
    assert restored.escalation_count == summary.escalation_count
    assert restored.duration == summary.duration
    
    # Verify transcript messages are preserved
    for original_msg, restored_msg in zip(summary.transcript, restored.transcript):
        assert restored_msg.id == original_msg.id
        assert restored_msg.sender == original_msg.sender
        assert restored_msg.text == original_msg.text


@given(style_profile_strategy())
def test_style_profile_to_dict_returns_dict(profile):
    """
    Property: to_dict() always returns a dictionary.
    
    For any StyleProfile, calling to_dict() should return a dict type.
    """
    result = profile.to_dict()
    assert isinstance(result, dict)


@given(style_profile_strategy())
def test_style_profile_dict_contains_all_fields(profile):
    """
    Property: Serialized dict contains all required fields.
    
    For any StyleProfile, the serialized dict should contain all fields (in camelCase for frontend).
    """
    data = profile.to_dict()
    required_fields = [
        'sentenceLength',
        'emojiFrequency',
        'commonEmojis',
        'punctuationStyle',
        'tone',
        'commonPhrases',
        'formalityLevel',
        'analysisTimestamp'
    ]
    for field in required_fields:
        assert field in data


@given(message_strategy())
def test_message_dict_contains_all_fields(message):
    """
    Property: Serialized Message dict contains all required fields.
    
    For any Message, the serialized dict should contain all fields (in camelCase for frontend).
    """
    data = message.to_dict()
    required_fields = ['id', 'sender', 'text', 'timestamp', 'isAiGenerated']
    for field in required_fields:
        assert field in data
