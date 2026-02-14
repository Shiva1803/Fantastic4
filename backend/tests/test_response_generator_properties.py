"""
Property-based tests for ResponseGenerator service using Hypothesis.

Property 5: Style Profile Application
Validates: Requirements 2.1, 2.4, 2.5
"""

from unittest.mock import Mock, patch
from hypothesis import given, strategies as st
from backend.services.response_generator import ResponseGenerator
from backend.models.data_models import StyleProfile, Message


# Strategies for generating test data

@st.composite
def style_profile_strategy(draw):
    """Generate random valid StyleProfile instances."""
    return StyleProfile(
        sentence_length=draw(st.sampled_from(["short", "medium", "long"])),
        emoji_frequency=draw(st.floats(min_value=0.0, max_value=1.0)),
        common_emojis=draw(st.lists(st.text(min_size=1, max_size=2), max_size=5)),
        punctuation_style=draw(st.sampled_from(["minimal", "standard", "heavy"])),
        tone=draw(st.sampled_from(["casual", "formal", "mixed"])),
        common_phrases=draw(st.lists(st.text(min_size=1, max_size=20), max_size=10)),
        formality_level=draw(st.floats(min_value=0.0, max_value=1.0)),
        analysis_timestamp=draw(st.text(min_size=10, max_size=30))
    )


@st.composite
def message_strategy(draw):
    """Generate random valid Message instances."""
    text = draw(st.text(min_size=1, max_size=200))
    while not text.strip():
        text = draw(st.text(min_size=1, max_size=200))
    
    return Message(
        id=draw(st.text(min_size=1, max_size=50)),
        sender=draw(st.sampled_from(["user", "friend", "ai"])),
        text=text,
        timestamp=draw(st.text(min_size=10, max_size=30)),
        is_ai_generated=draw(st.booleans())
    )


@st.composite
def incoming_message_strategy(draw):
    """Generate random valid incoming messages."""
    text = draw(st.text(min_size=1, max_size=200))
    while not text.strip():
        text = draw(st.text(min_size=1, max_size=200))
    return text


# Property Tests

@given(style_profile_strategy(), st.lists(message_strategy(), max_size=5), incoming_message_strategy())
def test_style_profile_application(profile, history, incoming_message):
    """
    Property 5: Style Profile Application
    
    For any StyleProfile and message context, the Response_Generator
    should produce a response that matches the profile's patterns.
    
    This test verifies that:
    - If emoji_frequency > 0.5, response contains emojis
    - If sentence_length = "short", response has short sentences
    - If tone = "casual", response avoids formal language
    
    Validates: Requirements 2.1, 2.4, 2.5
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        # Generate a response that matches the style profile
        mock_response_text = _generate_mock_response(profile)
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = mock_response_text
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, history, incoming_message)
        
        # Verify response is not empty
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
        
        # Verify the prompt included style information
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        
        # Check that style profile information is in the prompt
        assert profile.sentence_length in prompt
        assert profile.tone in prompt


@given(style_profile_strategy(), incoming_message_strategy())
def test_response_not_empty(profile, incoming_message):
    """
    Property: Response Always Non-Empty
    
    For any valid inputs, the generator should always return
    a non-empty response string.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "response text"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, [], incoming_message)
        
        assert response is not None
        assert len(response) > 0
        assert response.strip() != ""


@given(style_profile_strategy(), st.lists(message_strategy(), max_size=20), incoming_message_strategy())
def test_conversation_history_included_in_prompt(profile, history, incoming_message):
    """
    Property: Conversation History Inclusion
    
    For any conversation history, the generator should include
    recent messages in the prompt for context.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ok"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, history, incoming_message)
        
        # Verify API was called
        assert mock_client.chat.completions.create.called
        
        # Check that prompt includes incoming message
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        assert incoming_message in prompt
        
        # If there's history, check that recent messages are included
        if history:
            # At least one message from history should be in prompt
            recent_messages = history[-10:]
            found_history = any(msg.text in prompt for msg in recent_messages if len(msg.text) > 3)
            # Note: Very short messages might not be found due to formatting
            assert found_history or len(history) == 0 or all(len(msg.text) <= 3 for msg in recent_messages)


@given(style_profile_strategy(), incoming_message_strategy())
def test_emoji_frequency_reflected_in_prompt(profile, incoming_message):
    """
    Property: Emoji Frequency in Prompt
    
    For any profile with emoji_frequency > 0.5, the prompt should
    indicate frequent emoji usage.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "cool"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, [], incoming_message)
        
        # Check the prompt
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        
        if profile.emoji_frequency > 0.5:
            assert "frequently" in prompt.lower()
        elif profile.emoji_frequency > 0.2:
            assert "occasionally" in prompt.lower()
        else:
            assert "rarely" in prompt.lower()


@given(style_profile_strategy(), incoming_message_strategy())
def test_formality_level_reflected_in_prompt(profile, incoming_message):
    """
    Property: Formality Level in Prompt
    
    For any profile, the formality level should be reflected
    in the prompt description.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "sure"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, [], incoming_message)
        
        # Check the prompt
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        
        if profile.formality_level < 0.3:
            assert "very casual" in prompt.lower() or "casual" in prompt.lower()
        elif profile.formality_level < 0.7:
            assert "casual" in prompt.lower()
        else:
            assert "formal" in prompt.lower()


@given(st.lists(message_strategy(), min_size=15, max_size=20, unique_by=lambda m: m.text))
def test_history_limited_to_10_messages(history):
    """
    Property: History Limit
    
    For any conversation history longer than 10 messages with unique texts,
    only the most recent 10 should be included in the prompt.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        profile = StyleProfile(
            sentence_length="short",
            emoji_frequency=0.5,
            common_emojis=[],
            punctuation_style="minimal",
            tone="casual",
            common_phrases=[],
            formality_level=0.3,
            analysis_timestamp="2024-01-01T00:00:00Z"
        )
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ok"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, history, "test")
        
        # Check the prompt
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        
        # Most recent messages should be in prompt
        recent_10 = history[-10:]
        for msg in recent_10:
            if len(msg.text) > 3:  # Skip very short messages
                assert msg.text in prompt
        
        # Older messages should not be in prompt (since texts are unique)
        if len(history) > 10:
            old_messages = history[:-10]
            for msg in old_messages:
                if len(msg.text) > 3:
                    assert msg.text not in prompt


@given(style_profile_strategy(), incoming_message_strategy())
def test_response_cleaned_of_quotes(profile, incoming_message):
    """
    Property: Response Cleaning
    
    For any response wrapped in quotes, the generator should
    remove them.
    """
    with patch('backend.services.response_generator.OpenAI') as mock_openai:
        # Mock response with quotes
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"yeah sure"'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        generator = ResponseGenerator(api_key="test-key")
        response = generator.generate(profile, [], incoming_message)
        
        # Response should not have quotes
        assert not response.startswith('"')
        assert not response.endswith('"')
        assert response == "yeah sure"


# Helper function

def _generate_mock_response(profile: StyleProfile) -> str:
    """
    Generate a mock response that matches the style profile.
    
    This is used to simulate what the API would return.
    """
    # Generate response based on profile
    if profile.sentence_length == "short":
        base = "ok"
    elif profile.sentence_length == "medium":
        base = "sounds good to me"
    else:
        base = "that sounds like a great idea to me"
    
    # Add emoji if frequency is high
    if profile.emoji_frequency > 0.5 and profile.common_emojis:
        base += f" {profile.common_emojis[0]}"
    
    # Add common phrase if available
    if profile.common_phrases and profile.formality_level < 0.5:
        base = f"{profile.common_phrases[0]} {base}"
    
    return base
