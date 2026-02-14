"""
EscalationDetector service for identifying when conversations need human intervention.

This module analyzes incoming messages to detect serious topics, emotional distress,
unfamiliar subjects, scheduling conflicts, and sensitive information requests.
"""

import os
import json
import time
from typing import List
from openai import OpenAI
from groq import Groq
from backend.models.data_models import Message, EscalationResult


class EscalationDetector:
    """
    Detects when conversations require human intervention.
    
    This class uses Groq or OpenRouter API to analyze messages and determine
    if they contain topics that should be handled by a human rather than AI.
    
    Attributes:
        client: OpenAI-compatible client for API calls
        api_provider: Which API provider is being used ("groq" or "openrouter")
        max_retries: Maximum number of retry attempts for failed API calls
    """
    
    def __init__(self, api_key: str = None, api_provider: str = "openai"):
        """
        Initialize EscalationDetector with API credentials.
        
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
    
    def detect(
        self,
        message: str,
        conversation_history: List[Message]
    ) -> EscalationResult:
        """
        Detect if a message requires human intervention.
        
        Args:
            message: Incoming message to analyze
            conversation_history: Context from the conversation
            
        Returns:
            EscalationResult with detection status, confidence score, and reason
            
        Raises:
            ValueError: If message is empty
            RuntimeError: If API call fails after all retries
            
        Example:
            >>> detector = EscalationDetector()
            >>> history = [Message(...), Message(...)]
            >>> result = detector.detect("your mom is in the hospital?", history)
            >>> print(result.detected)
            True
            >>> print(result.reason)
            'Serious health concern detected'
        """
        # Validate input
        if not message or not message.strip():
            raise ValueError("message cannot be empty")
        
        # Construct prompt for escalation detection
        prompt = self._build_detection_prompt(message, conversation_history)
        
        # Call API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                result = self._parse_response(response)
                return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Failed to detect escalation after {self.max_retries} attempts: {str(e)}"
                    )
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        raise RuntimeError("Unexpected error in detect method")
    
    def _build_detection_prompt(
        self,
        message: str,
        conversation_history: List[Message]
    ) -> str:
        """
        Build the prompt for escalation detection.
        
        Args:
            message: Message to analyze
            conversation_history: Recent conversation context
            
        Returns:
            Formatted prompt string
        """
        # Format conversation history (last 5 messages for context)
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-5:]
            for msg in recent_history:
                sender_label = "User" if msg.sender == "user" else "Friend"
                history_text += f"{sender_label}: {msg.text}\n"
        
        prompt = f"""Analyze if this message needs the real human to respond.

Context from conversation:
{history_text if history_text else "(No previous context)"}

New message from friend: "{message}"

Determine if this message requires human intervention. Return ONLY valid JSON:
{{
  "needs_human": true/false,
  "reason": "why it needs human OR why AI can handle it",
  "urgency": "low/medium/high",
  "confidence": 0-100,
  "category": "serious_question" | "emotional_distress" | "unfamiliar_topic" | "scheduling" | "sensitive_info" | null
}}

Escalate (needs_human=true) if:
- Serious questions about health, safety, legal matters, or emergencies
- Emotional distress, grief, mental health concerns
- Unfamiliar topics the AI hasn't seen in training
- Complex scheduling that requires checking calendar
- Requests for sensitive personal information (passwords, SSN, etc.)

Set confidence < 70 if uncertain. Higher urgency for emergencies."""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to Groq or OpenRouter.
        
        Args:
            prompt: The detection prompt
            
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
                    "content": "You are an escalation detection expert. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for more consistent detection
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> EscalationResult:
        """
        Parse API response into EscalationResult.
        
        Args:
            response: JSON string from API
            
        Returns:
            EscalationResult object
            
        Raises:
            ValueError: If response is not valid JSON or missing required fields
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
            
            # Validate required fields
            if "needs_human" not in data:
                raise ValueError("Missing required field: needs_human")
            if "confidence" not in data:
                raise ValueError("Missing required field: confidence")
            
            # Extract fields
            detected = bool(data["needs_human"])
            confidence_score = float(data["confidence"])
            reason = data.get("reason")
            category = data.get("category")
            
            # Validate confidence score bounds
            if not 0 <= confidence_score <= 100:
                confidence_score = max(0, min(100, confidence_score))
            
            # If confidence < 70, escalate
            if confidence_score < 70:
                detected = True
                if not reason:
                    reason = "Low confidence in handling this message"
            
            # Create EscalationResult
            result = EscalationResult(
                detected=detected,
                confidence_score=confidence_score,
                reason=reason,
                category=category
            )
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
