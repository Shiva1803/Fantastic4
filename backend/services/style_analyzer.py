"""
StyleAnalyzer service for extracting texting style patterns from training data.

This module analyzes past text conversations to extract patterns including
sentence length, emoji usage, punctuation style, tone, and formality level.
"""

import os
import json
import time
from typing import List
from datetime import datetime, timezone
from groq import Groq
from openai import OpenAI
from backend.models.data_models import StyleProfile


class StyleAnalyzer:
    """
    Analyzes training data to extract user's texting style patterns.
    
    This class uses Groq or OpenRouter API to analyze past text messages
    and extract patterns that define a user's unique texting style.
    
    Attributes:
        client: OpenAI-compatible client for API calls
        api_provider: Which API provider is being used ("groq" or "openrouter")
        max_retries: Maximum number of retry attempts for failed API calls
    """
    
    def __init__(self, api_key: str = None, api_provider: str = "openai"):
        """
        Initialize StyleAnalyzer with API credentials.
        
        Args:
            api_key: API key for OpenAI or Groq (defaults to env variable)
            api_provider: Which API to use - "openai" or "groq"
            
        Raises:
            ValueError: If no API key is provided and none found in environment
        """
        print(f"[DEBUG] StyleAnalyzer.__init__ called with api_provider={api_provider}")
        
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
        
        print(f"[DEBUG] API key found: {api_key[:20]}...")
        
        # Initialize client
        if self.api_provider == "openai":
            print(f"[DEBUG] Initializing OpenAI client...")
            try:
                self.client = OpenAI(api_key=api_key)
                print(f"[DEBUG] OpenAI client initialized successfully")
            except Exception as e:
                print(f"[DEBUG] Error initializing OpenAI client: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise
            self.model = "gpt-4o-mini"
        elif self.api_provider == "groq":
            print(f"[DEBUG] Initializing Groq client...")
            try:
                self.client = Groq(api_key=api_key)
                print(f"[DEBUG] Groq client initialized successfully")
            except Exception as e:
                print(f"[DEBUG] Error initializing Groq client: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise
            self.model = "llama-3.3-70b-versatile"
        else:  # openrouter
            print(f"[DEBUG] OpenRouter not supported")
            raise ValueError("Only OpenAI and Groq providers are supported")
            self.model = "meta-llama/llama-3.1-70b-instruct"
    
    def analyze(self, training_data: List[str]) -> StyleProfile:
        """
        Analyze training data to extract texting style patterns.
        
        Args:
            training_data: List of past text messages (minimum 10 required)
            
        Returns:
            StyleProfile containing extracted patterns
            
        Raises:
            ValueError: If training_data has fewer than 10 messages
            RuntimeError: If API call fails after all retries
            
        Example:
            >>> analyzer = StyleAnalyzer()
            >>> messages = ["hey!", "lol yeah", "sounds good 😂", ...]
            >>> profile = analyzer.analyze(messages)
            >>> print(profile.tone)
            'casual'
        """
        # Validate training data
        if len(training_data) < 10:
            raise ValueError(
                f"Insufficient training data: {len(training_data)} messages provided, "
                f"minimum 10 required"
            )
        
        # Construct prompt for style analysis
        prompt = self._build_analysis_prompt(training_data)
        
        # Call API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                profile = self._parse_response(response)
                return profile
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"Failed to analyze style after {self.max_retries} attempts: {str(e)}"
                    )
                # Exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        raise RuntimeError("Unexpected error in analyze method")
    
    def _build_analysis_prompt(self, training_data: List[str]) -> str:
        """
        Build the prompt for style analysis.
        
        Args:
            training_data: List of text messages
            
        Returns:
            Formatted prompt string
        """
        messages_text = "\n".join([f"- {msg}" for msg in training_data[:50]])
        
        prompt = f"""You are analyzing someone's texting style. Based on these messages:

{messages_text}

Analyze the texting patterns and return ONLY valid JSON with this exact structure:
{{
  "sentence_length": "short" | "medium" | "long",
  "emoji_frequency": <number between 0 and 1>,
  "common_emojis": [<list of frequently used emojis>],
  "punctuation_style": "minimal" | "standard" | "heavy",
  "tone": "casual" | "formal" | "mixed",
  "common_phrases": [<list of frequently used phrases>],
  "formality_level": <number between 0 and 1>
}}

Guidelines:
- sentence_length: "short" if avg < 10 words, "medium" if 10-20, "long" if > 20
- emoji_frequency: ratio of messages containing emojis (0 = none, 1 = every message)
- common_emojis: top 3-5 most used emojis
- punctuation_style: "minimal" if rarely uses periods/commas, "standard" if normal, "heavy" if excessive
- tone: "casual" if informal/relaxed, "formal" if professional, "mixed" if varies
- common_phrases: 3-5 frequently used expressions (e.g., "lol", "for sure", "tbh")
- formality_level: 0 = very casual, 1 = very formal

Return ONLY the JSON object, no additional text."""
        
        return prompt
    
    def _call_api(self, prompt: str) -> str:
        """
        Make API call to Groq or OpenRouter.
        
        Args:
            prompt: The analysis prompt
            
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
                    "content": "You are a texting style analysis expert. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _parse_response(self, response: str) -> StyleProfile:
        """
        Parse API response into StyleProfile.
        
        Args:
            response: JSON string from API
            
        Returns:
            StyleProfile object
            
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
            required_fields = [
                "sentence_length", "emoji_frequency", "common_emojis",
                "punctuation_style", "tone", "common_phrases", "formality_level"
            ]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create StyleProfile with current timestamp
            profile = StyleProfile(
                sentence_length=data["sentence_length"],
                emoji_frequency=float(data["emoji_frequency"]),
                common_emojis=data["common_emojis"],
                punctuation_style=data["punctuation_style"],
                tone=data["tone"],
                common_phrases=data["common_phrases"],
                formality_level=float(data["formality_level"]),
                analysis_timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            return profile
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
