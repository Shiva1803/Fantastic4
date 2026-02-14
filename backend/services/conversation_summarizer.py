"""
ConversationSummarizer service for generating conversation summaries.

This module analyzes conversation transcripts to extract commitments, action items,
and key topics discussed during an autopilot session.
"""

import os
import json
import time
from typing import List
from openai import OpenAI
from groq import Groq
from backend.models.data_models import Message, StyleProfile, ConversationSummary


class ConversationSummarizer:
    """
    Generates summaries of conversation sessions.
    
    This class uses Groq or OpenRouter API to analyze conversation transcripts
    and extract key information like commitments, action items, and topics.
    
    Attributes:
        client: OpenAI-compatible client for API calls
        api_provider: Which API provider is being used ("groq" or "openrouter")
        max_retries: Maximum number of retry attempts for failed API calls
    """
    
    def __init__(self, api_key: str = None, api_provider: str = "openai"):
        """
        Initialize ConversationSummarizer with API credentials.
        
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
    
    def summarize(
        self,
        messages: List[Message],
        style_profile: StyleProfile,
        session_id: str = "unknown"
    ) -> ConversationSummary:
        """
        Generate a summary of a conversation session.
        
        Args:
            messages: Full conversation transcript
            style_profile: User's texting style for context
            session_id: Unique identifier for the session
            
        Returns:
            ConversationSummary with commitments, action items, and key topics
            
        Raises:
            ValueError: If messages list is empty
            RuntimeError: If API call fails after all retries
            
        Example:
            >>> summarizer = ConversationSummarizer()
            >>> messages = [Message(...), Message(...)]
            >>> profile = StyleProfile(...)
            >>> summary = summarizer.summarize(messages, profile, "session-123")
            >>> print(summary.commitments)
            ['Meeting at 3pm tomorrow', 'Will send the document']
        """
        # Validate input
        if not messages:
            raise ValueError("messages list cannot be empty")
        
        # Count AI vs human messages
        ai_message_count = sum(1 for msg in messages if msg.is_ai_generated)
        human_message_count = len(messages) - ai_message_count
        
        # Count escalations (messages from user after AI was supposed to respond)
        escalation_count = self._count_escalations(messages)
        
        # Calculate duration (if timestamps are available)
        duration = self._calculate_duration(messages)
        
        # Build prompt for summarization
        prompt = self._build_summary_prompt(messages, style_profile)
        
        # Call API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                summary_data = self._parse_response(response)
                
                # Build ConversationSummary object
                summary = ConversationSummary(
                    session_id=session_id,
                    transcript=messages,
                    commitments=summary_data.get("commitments", []),
                    action_items=summary_data.get("action_items", []),
                    key_topics=summary_data.get("key_topics", []),
                    ai_message_count=ai_message_count,
                    human_message_count=human_message_count,
                    escalation_count=escalation_count,
                    duration=duration
                )
                
                return summary
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Failed to generate summary after {self.max_retries} attempts: {str(e)}"
                    )
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        raise RuntimeError("Unexpected error in summarize method")
    
    def _count_escalations(self, messages: List[Message]) -> int:
        """
        Count the number of escalations in the conversation.
        
        An escalation is when the user takes over from the AI.
        This is detected by finding user messages that are not AI-generated
        following AI-generated user messages (with possible friend messages in between).
        
        Args:
            messages: Conversation transcript
            
        Returns:
            Number of escalations detected
        """
        escalation_count = 0
        last_user_was_ai = False
        
        for msg in messages:
            if msg.sender == "user":
                # If we see a human-written user message after an AI-generated user message
                if not msg.is_ai_generated and last_user_was_ai:
                    escalation_count += 1
                
                # Track if this user message was AI-generated
                last_user_was_ai = msg.is_ai_generated
        
        return escalation_count
    
    def _calculate_duration(self, messages: List[Message]) -> int:
        """
        Calculate conversation duration in seconds.
        
        Args:
            messages: Conversation transcript with timestamps
            
        Returns:
            Duration in seconds (0 if timestamps unavailable)
        """
        if len(messages) < 2:
            return 0
        
        try:
            from datetime import datetime
            
            first_time = datetime.fromisoformat(messages[0].timestamp.replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(messages[-1].timestamp.replace('Z', '+00:00'))
            
            duration = (last_time - first_time).total_seconds()
            return int(duration)
        except Exception:
            # If timestamp parsing fails, return 0
            return 0
    
    def _build_summary_prompt(
        self,
        messages: List[Message],
        style_profile: StyleProfile
    ) -> str:
        """
        Build the prompt for conversation summarization.
        
        Args:
            messages: Conversation transcript
            style_profile: User's texting style
            
        Returns:
            Formatted prompt string
        """
        # Format conversation transcript
        transcript_text = ""
        for msg in messages:
            sender_label = "User" if msg.sender == "user" else "Friend" if msg.sender == "friend" else "AI"
            ai_marker = " [AI]" if msg.is_ai_generated else ""
            transcript_text += f"{sender_label}{ai_marker}: {msg.text}\n"
        
        prompt = f"""Analyze this conversation and extract key information.

Conversation Transcript:
{transcript_text}

User's Communication Style:
- Tone: {style_profile.tone}
- Formality: {style_profile.formality_level:.1f}/1.0
- Sentence Length: {style_profile.sentence_length}

Extract the following information and return ONLY valid JSON:
{{
  "commitments": ["list of plans, promises, or information shared"],
  "action_items": ["list of tasks to do or follow-ups needed"],
  "key_topics": ["list of main discussion themes"]
}}

Guidelines:
- Commitments: Plans made, promises given, information shared (e.g., "Meeting at 3pm", "Will send document")
- Action Items: Things that need to be done (e.g., "Call dentist", "Review proposal")
- Key Topics: Main subjects discussed (e.g., "Weekend plans", "Work project", "Health concerns")
- Return empty arrays if none found
- Be concise and specific"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to Groq or OpenRouter.
        
        Args:
            prompt: The summarization prompt
            
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
                    "content": "You are a conversation analysis expert. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for consistent extraction
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> dict:
        """
        Parse API response into summary data.
        
        Args:
            response: JSON string from API
            
        Returns:
            Dictionary with commitments, action_items, and key_topics
            
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Extract JSON from response (in case there's extra text)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            # Ensure all required fields exist (use empty lists as defaults)
            result = {
                "commitments": data.get("commitments", []),
                "action_items": data.get("action_items", []),
                "key_topics": data.get("key_topics", [])
            }
            
            # Validate that fields are lists
            for key in result:
                if not isinstance(result[key], list):
                    result[key] = []
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
