"""
Property-based tests for CacheManager service using Hypothesis.

These tests verify universal properties that should hold for all valid inputs,
particularly focusing on cache storage and retrieval round-trips.

Property 2: Style Profile Caching Round-Trip
Validates: Requirements 1.3, 9.5, 10.1
"""

from hypothesis import given, strategies as st
from backend.services.cache_manager import CacheManager
from backend.models.data_models import StyleProfile, ConversationSession, Message


# Import strategies from data models property tests
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
def user_id_strategy(draw):
    """Generate random valid user IDs."""
    # Generate non-empty, non-whitespace-only strings
    user_id = draw(st.text(min_size=1, max_size=50))
    while not user_id.strip():
        user_id = draw(st.text(min_size=1, max_size=50))
    return user_id


@st.composite
def session_id_strategy(draw):
    """Generate random valid session IDs."""
    # Generate non-empty, non-whitespace-only strings
    session_id = draw(st.text(min_size=1, max_size=50))
    while not session_id.strip():
        session_id = draw(st.text(min_size=1, max_size=50))
    return session_id


# Property Tests

@given(user_id_strategy(), style_profile_strategy())
def test_style_profile_cache_round_trip(user_id, profile):
    """
    Property 2: Style Profile Caching Round-Trip
    
    For any StyleProfile, storing it in the cache and then retrieving it
    should return an equivalent StyleProfile with all fields preserved.
    
    Validates: Requirements 1.3, 9.5, 10.1
    """
    cache = CacheManager()
    
    # Store profile in cache
    cache.set_style_profile(user_id, profile)
    
    # Retrieve profile from cache
    retrieved = cache.get_style_profile(user_id)
    
    # Verify profile was retrieved
    assert retrieved is not None
    
    # Verify all fields are preserved
    assert retrieved.sentence_length == profile.sentence_length
    assert retrieved.emoji_frequency == profile.emoji_frequency
    assert retrieved.common_emojis == profile.common_emojis
    assert retrieved.punctuation_style == profile.punctuation_style
    assert retrieved.tone == profile.tone
    assert retrieved.common_phrases == profile.common_phrases
    assert retrieved.formality_level == profile.formality_level
    assert retrieved.analysis_timestamp == profile.analysis_timestamp


@given(session_id_strategy(), conversation_session_strategy())
def test_conversation_session_cache_round_trip(session_id, session):
    """
    Property: Conversation Session Caching Round-Trip
    
    For any ConversationSession, storing it in the cache and then retrieving it
    should return an equivalent ConversationSession with all fields preserved.
    
    Validates: Requirements 10.2
    """
    cache = CacheManager()
    
    # Store session in cache
    cache.set_session(session_id, session)
    
    # Retrieve session from cache
    retrieved = cache.get_session(session_id)
    
    # Verify session was retrieved
    assert retrieved is not None
    
    # Verify all fields are preserved
    assert retrieved.session_id == session.session_id
    assert len(retrieved.messages) == len(session.messages)
    assert retrieved.start_time == session.start_time
    assert retrieved.end_time == session.end_time
    assert retrieved.escalation_count == session.escalation_count
    
    # Verify messages are preserved
    for original_msg, retrieved_msg in zip(session.messages, retrieved.messages):
        assert retrieved_msg.id == original_msg.id
        assert retrieved_msg.sender == original_msg.sender
        assert retrieved_msg.text == original_msg.text
        assert retrieved_msg.is_ai_generated == original_msg.is_ai_generated
    
    # Verify style profile is preserved
    assert retrieved.style_profile.sentence_length == session.style_profile.sentence_length
    assert retrieved.style_profile.emoji_frequency == session.style_profile.emoji_frequency
    assert retrieved.style_profile.tone == session.style_profile.tone


@given(user_id_strategy(), style_profile_strategy())
def test_profile_overwrite_preserves_latest(user_id, profile1):
    """
    Property: Profile Overwrite Preserves Latest
    
    For any user_id, storing multiple profiles should preserve only the latest one.
    """
    cache = CacheManager()
    
    # Create a second different profile
    profile2 = StyleProfile(
        sentence_length="long" if profile1.sentence_length != "long" else "short",
        emoji_frequency=0.5,
        common_emojis=["🎉"],
        punctuation_style="heavy",
        tone="formal" if profile1.tone != "formal" else "casual",
        common_phrases=["indeed"],
        formality_level=0.9,
        analysis_timestamp="2024-12-31T23:59:59Z"
    )
    
    # Store first profile
    cache.set_style_profile(user_id, profile1)
    
    # Store second profile (overwrite)
    cache.set_style_profile(user_id, profile2)
    
    # Retrieve profile
    retrieved = cache.get_style_profile(user_id)
    
    # Verify it's the second profile
    assert retrieved.sentence_length == profile2.sentence_length
    assert retrieved.tone == profile2.tone
    assert retrieved.formality_level == profile2.formality_level


@given(user_id_strategy(), style_profile_strategy())
def test_profile_delete_removes_from_cache(user_id, profile):
    """
    Property: Profile Delete Removes from Cache
    
    For any cached profile, deleting it should make it unavailable for retrieval.
    """
    cache = CacheManager()
    
    # Store profile
    cache.set_style_profile(user_id, profile)
    
    # Verify it's stored
    assert cache.get_style_profile(user_id) is not None
    
    # Delete profile
    result = cache.delete_style_profile(user_id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify profile is no longer retrievable
    assert cache.get_style_profile(user_id) is None


@given(session_id_strategy(), conversation_session_strategy())
def test_session_delete_removes_from_cache(session_id, session):
    """
    Property: Session Delete Removes from Cache
    
    For any cached session, deleting it should make it unavailable for retrieval.
    """
    cache = CacheManager()
    
    # Store session
    cache.set_session(session_id, session)
    
    # Verify it's stored
    assert cache.get_session(session_id) is not None
    
    # Delete session
    result = cache.delete_session(session_id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify session is no longer retrievable
    assert cache.get_session(session_id) is None


@given(st.lists(st.tuples(user_id_strategy(), style_profile_strategy()), min_size=1, max_size=10, unique_by=lambda x: x[0]))
def test_multiple_profiles_independent(profiles_data):
    """
    Property: Multiple Profiles are Independent
    
    For any set of unique user_id/profile pairs, storing them should keep them independent.
    Retrieving one should not affect others.
    """
    cache = CacheManager()
    
    # Store all profiles
    for user_id, profile in profiles_data:
        cache.set_style_profile(user_id, profile)
    
    # Verify all profiles can be retrieved independently
    for user_id, original_profile in profiles_data:
        retrieved = cache.get_style_profile(user_id)
        assert retrieved is not None
        assert retrieved.sentence_length == original_profile.sentence_length
        assert retrieved.tone == original_profile.tone


@given(st.lists(st.tuples(session_id_strategy(), conversation_session_strategy()), min_size=1, max_size=10, unique_by=lambda x: x[0]))
def test_multiple_sessions_independent(sessions_data):
    """
    Property: Multiple Sessions are Independent
    
    For any set of unique session_id/session pairs, storing them should keep them independent.
    Retrieving one should not affect others.
    """
    cache = CacheManager()
    
    # Store all sessions
    for session_id, session in sessions_data:
        cache.set_session(session_id, session)
    
    # Verify all sessions can be retrieved independently
    for session_id, original_session in sessions_data:
        retrieved = cache.get_session(session_id)
        assert retrieved is not None
        assert retrieved.session_id == original_session.session_id
        assert len(retrieved.messages) == len(original_session.messages)


@given(user_id_strategy(), style_profile_strategy())
def test_cache_count_accuracy(user_id, profile):
    """
    Property: Cache Count is Accurate
    
    For any cache operations, the count should accurately reflect the number of items.
    """
    cache = CacheManager()
    
    # Initially empty
    assert cache.get_profile_count() == 0
    
    # After adding one
    cache.set_style_profile(user_id, profile)
    assert cache.get_profile_count() == 1
    
    # After deleting
    cache.delete_style_profile(user_id)
    assert cache.get_profile_count() == 0
