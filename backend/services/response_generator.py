"""
ResponseGenerator service for generating responses matching user's texting style.

This module generates contextually appropriate responses that match the user's
communication patterns including tone, emoji usage, and sentence structure.
"""

import os
import json
import time
from typing import List
from openai import OpenAI
from groq import Groq
from backend.models.data_models import StyleProfile, Message


class ResponseGenerator:
    """
    Generates responses matching a user's texting style.
    
    This class uses Groq or OpenRouter API to generate responses that
    match the user's communication patterns while being contextually
    appropriate for the conversation.
    
    Attributes:
        client: OpenAI-compatible client for API calls
        api_provider: Which API provider is being used ("groq" or "openrouter")
        max_retries: Maximum number of retry attempts for failed API calls
    """
    
    def __init__(self, api_key: str = None, api_provider: str = "openai"):
        """
        Initialize ResponseGenerator with API credentials.
        
        Args:
            api_key: API key for OpenAI or Groq (defaults to env variable)
            api_provider: Which API to use - "openai" or "groq"
            
        Raises:
            ValueError: If no API key is provided and none found in environment
        """
        self.api_provider = api_provider.lower()
        self.max_retries = 3
        
        # Get API key from parameter or environment
        if api_key is None:
            if self.api_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif self.api_provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
            else:
                api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
            raise ValueError(f"No API key provided for {self.api_provider}")
        
        # Initialize client
        if self.api_provider == "openai":
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
        elif self.api_provider == "groq":
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Only OpenAI and Groq providers are supported")
    
    def generate(
        self,
        style_profile: StyleProfile,
        conversation_history: List[Message],
        incoming_message: str
    ) -> str:
        """
        Generate a response matching the user's style.
        
        Args:
            style_profile: User's texting patterns
            conversation_history: Previous messages in the conversation
            incoming_message: The message to respond to
            
        Returns:
            Generated response text matching the user's style
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If API call fails after all retries
            
        Example:
            >>> generator = ResponseGenerator()
            >>> profile = StyleProfile(...)
            >>> history = [Message(...), Message(...)]
            >>> response = generator.generate(profile, history, "hey what's up?")
            >>> print(response)
            'not much! hbu 😂'
        """
        # Validate inputs
        if not incoming_message or not incoming_message.strip():
            raise ValueError("incoming_message cannot be empty")
        
        # Construct prompt for response generation
        prompt = self._build_response_prompt(
            style_profile,
            conversation_history,
            incoming_message
        )
        
        # Call API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                # Clean up the response
                cleaned_response = self._clean_response(response)
                return cleaned_response
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Failed to generate response after {self.max_retries} attempts: {str(e)}"
                    )
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        raise RuntimeError("Unexpected error in generate method")
    
    def _build_response_prompt(
        self,
        style_profile: StyleProfile,
        conversation_history: List[Message],
        incoming_message: str
    ) -> str:
        """
        Build the prompt for response generation.
        
        Args:
            style_profile: User's texting patterns
            conversation_history: Previous messages
            incoming_message: Message to respond to
            
        Returns:
            Formatted prompt string
        """
        # Format conversation history (last 10 messages for context)
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                sender_label = "You" if msg.sender == "user" else "Friend"
                history_text += f"{sender_label}: {msg.text}\n"
        
        # Build style description
        style_desc = self._format_style_description(style_profile)
        
        prompt = f"""You are texting AS this person. Mimic their exact style.

{style_desc}

Conversation so far:
{history_text if history_text else "(No previous messages)"}

New message from friend: "{incoming_message}"

Respond EXACTLY as this person would. Match their emoji usage, sentence length, tone, and quirks. Be natural and conversational. Return ONLY the response text, nothing else."""
        
        return prompt
    
    def _format_style_description(self, profile: StyleProfile) -> str:
        """
        Format style profile into a readable description.
        
        Args:
            profile: StyleProfile to format
            
        Returns:
            Formatted style description
        """
        emoji_desc = "frequently" if profile.emoji_frequency > 0.5 else \
                     "occasionally" if profile.emoji_frequency > 0.2 else "rarely"
        
        common_emojis_str = ", ".join(profile.common_emojis[:3]) if profile.common_emojis else "none"
        common_phrases_str = ", ".join([f'"{p}"' for p in profile.common_phrases[:5]]) if profile.common_phrases else "none"
        
        style_desc = f"""Style Profile:
- Sentence length: {profile.sentence_length}
- Uses emojis {emoji_desc} (common ones: {common_emojis_str})
- Punctuation: {profile.punctuation_style}
- Tone: {profile.tone}
- Formality: {"very casual" if profile.formality_level < 0.3 else "casual" if profile.formality_level < 0.7 else "formal"}
- Common phrases: {common_phrases_str}"""
        
        return style_desc
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to Groq or OpenRouter.
        
        Args:
            prompt: The response generation prompt
            
        Returns:
            API response text
            
        Raises:
            Exception: If API call fails
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are mimicking someone's texting style. Respond naturally and briefly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Higher temperature for more natural variation
            max_tokens=200  # Keep responses concise like texts
        )
        
        return response.choices[0].message.content
    
    def _clean_response(self, response: str) -> str:
        """
        Clean up the API response.
        
        Args:
            response: Raw API response
            
        Returns:
            Cleaned response text
        """
        # Remove any quotes that might wrap the response
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        if response.startswith("'") and response.endswith("'"):
            response = response[1:-1]
        
        # Remove any "You:" or similar prefixes
        prefixes = ["You:", "Response:", "Me:", "User:"]
        for prefix in prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        return response.strip()
