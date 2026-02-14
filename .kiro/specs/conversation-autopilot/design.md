# Design Document: Conversation Autopilot

## Overview

Conversation Autopilot is a web application that learns a user's texting style and generates responses matching their communication patterns. The system consists of a React/TypeScript frontend for user interaction and a Flask backend that orchestrates Groq or OpenRouter API calls for AI capabilities.

The architecture follows a client-server model where the frontend handles UI state and user interactions, while the backend manages API integration, caching, and business logic. The system is designed for a 3-hour MVP build time with focus on core functionality over advanced features.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Vite + React)         │
│  ┌─────────┬─────────┬──────┬─────────┐│
│  │ Landing │  Train  │ Demo │ Summary ││
│  └─────────┴─────────┴──────┴─────────┘│
└──────────────────┬──────────────────────┘
                   │ HTTP/JSON
┌──────────────────▼──────────────────────┐
│         Backend (Flask)                  │
│  ┌──────────────────────────────────┐   │
│  │   API Routes                      │   │
│  │   /api/train                      │   │
│  │   /api/respond                    │   │
│  │   /api/summarize                  │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   Business Logic Layer            │   │
│  │   - StyleAnalyzer                 │   │
│  │   - ResponseGenerator             │   │
│  │   - EscalationDetector            │   │
│  │   - ConversationSummarizer        │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │   Cache Layer (in-memory)         │   │
│  └──────────────────────────────────┘   │
└──────────────────┬──────────────────────┘
                   │ API Calls
┌──────────────────▼──────────────────────┐
│      Groq or OpenRouter API             │
└─────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: Vite, React 18, TypeScript, Tailwind CSS
- **Backend**: Flask 3.x, Python 3.10+
- **AI**: Groq API or OpenRouter API (user choice for free/cheaper alternative)
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Fetch API (frontend), requests library (backend)

## Components and Interfaces

### Frontend Components

#### 1. LandingPage
- **Purpose**: Entry point with project introduction and CTA
- **State**: None
- **Props**: None
- **Navigation**: Routes to TrainPage on button click

#### 2. TrainPage
- **Purpose**: Accepts training data and displays style profile
- **State**: 
  - `trainingText: string` - User input text
  - `styleProfile: StyleProfile | null` - Analysis results
  - `isLoading: boolean` - Loading state
  - `error: string | null` - Error messages
- **Props**: None
- **API Calls**: POST /api/train
- **Navigation**: Routes to DemoPage after successful training

#### 3. DemoPage
- **Purpose**: Live conversation simulation with autopilot controls
- **State**:
  - `messages: Message[]` - Conversation history
  - `currentInput: string` - Friend's message input
  - `autopilotEnabled: boolean` - Autopilot toggle state
  - `isGenerating: boolean` - Response generation state
  - `escalation: EscalationWarning | null` - Current escalation
  - `sessionId: string` - Unique session identifier
- **Props**: 
  - `styleProfile: StyleProfile` - Passed from TrainPage
- **API Calls**: POST /api/respond
- **Navigation**: Routes to SummaryPage on session end

#### 4. SummaryPage
- **Purpose**: Displays conversation summary with highlights
- **State**:
  - `summary: ConversationSummary | null` - Summary data
  - `isLoading: boolean` - Loading state
- **Props**:
  - `sessionId: string` - Session to summarize
- **API Calls**: POST /api/summarize
- **Navigation**: Routes back to Landing or Demo

### Backend Components

#### 1. StyleAnalyzer
```python
class StyleAnalyzer:
    def analyze(self, training_data: List[str]) -> StyleProfile:
        """
        Analyzes training data to extract texting patterns.
        
        Args:
            training_data: List of past text messages
            
        Returns:
            StyleProfile containing extracted patterns
            
        Raises:
            ValueError: If training_data has fewer than 10 messages
        """
```

**Responsibilities**:
- Validate training data quantity
- Call Groq or OpenRouter API with style analysis prompt
- Parse API response into StyleProfile structure
- Handle API errors and retries

#### 2. ResponseGenerator
```python
class ResponseGenerator:
    def generate(self, 
                 style_profile: StyleProfile, 
                 conversation_history: List[Message],
                 incoming_message: str) -> str:
        """
        Generates a response matching the user's style.
        
        Args:
            style_profile: User's texting patterns
            conversation_history: Previous messages in session
            incoming_message: Friend's latest message
            
        Returns:
            Generated response text
        """
```

**Responsibilities**:
- Construct prompt with style profile and context
- Call Groq or OpenRouter API for response generation
- Apply style constraints (emoji, tone, length)
- Enforce 2-second timeout

#### 3. EscalationDetector
```python
class EscalationDetector:
    def detect(self, 
               message: str, 
               conversation_history: List[Message]) -> EscalationResult:
        """
        Detects if message requires human intervention.
        
        Args:
            message: Incoming message to analyze
            conversation_history: Context from session
            
        Returns:
            EscalationResult with confidence score and reason
        """
```

**Responsibilities**:
- Identify serious questions, emotional distress, unfamiliar topics
- Detect scheduling conflicts and sensitive information requests
- Calculate confidence score (0-100)
- Return escalation reason when score < 70

#### 4. ConversationSummarizer
```python
class ConversationSummarizer:
    def summarize(self, 
                  messages: List[Message],
                  style_profile: StyleProfile) -> ConversationSummary:
        """
        Generates summary of autopilot session.
        
        Args:
            messages: Full conversation transcript
            style_profile: User's style for context
            
        Returns:
            ConversationSummary with highlights and action items
        """
```

**Responsibilities**:
- Extract commitments and plans made
- Identify action items
- Categorize key topics discussed
- Mark AI vs human messages

#### 5. CacheManager
```python
class CacheManager:
    def get_style_profile(self, user_id: str) -> Optional[StyleProfile]:
        """Retrieves cached style profile."""
        
    def set_style_profile(self, user_id: str, profile: StyleProfile):
        """Stores style profile in cache."""
        
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieves conversation session."""
        
    def set_session(self, session_id: str, session: ConversationSession):
        """Stores conversation session."""
```

**Responsibilities**:
- In-memory caching of style profiles
- Session storage during active conversations
- Cache invalidation on retrain

### API Endpoints

#### POST /api/train
```typescript
Request: {
  trainingData: string[]  // 10-50 messages
}

Response: {
  styleProfile: {
    sentenceLength: "short" | "medium" | "long"
    emojiFrequency: number  // 0-1 scale
    commonEmojis: string[]
    punctuationStyle: string
    tone: "casual" | "formal" | "mixed"
    commonPhrases: string[]
    formalityLevel: number  // 0-1 scale
  }
}

Errors:
  400: Insufficient training data (< 10 messages)
  500: API error or processing failure
```

#### POST /api/respond
```typescript
Request: {
  sessionId: string
  styleProfile: StyleProfile
  conversationHistory: Message[]
  incomingMessage: string
  autopilotEnabled: boolean
}

Response: {
  response: string
  escalation: {
    detected: boolean
    reason?: string
    confidenceScore: number
  }
}

Errors:
  500: API error or generation failure
```

#### POST /api/summarize
```typescript
Request: {
  sessionId: string
  messages: Message[]
}

Response: {
  summary: {
    transcript: Message[]
    commitments: string[]
    actionItems: string[]
    keyTopics: string[]
    aiMessageCount: number
    humanMessageCount: number
  }
}

Errors:
  404: Session not found
  500: API error or summarization failure
```

## Data Models

### StyleProfile
```typescript
interface StyleProfile {
  sentenceLength: "short" | "medium" | "long"
  emojiFrequency: number  // 0-1, where 1 = emoji in every message
  commonEmojis: string[]  // Top 5 most used emojis
  punctuationStyle: string  // Description: "minimal", "heavy", "standard"
  tone: "casual" | "formal" | "mixed"
  commonPhrases: string[]  // Frequently used expressions
  formalityLevel: number  // 0-1, where 0 = very casual, 1 = very formal
  analysisTimestamp: string  // ISO 8601 timestamp
}
```

### Message
```typescript
interface Message {
  id: string
  sender: "user" | "friend" | "ai"
  text: string
  timestamp: string  // ISO 8601
  isAiGenerated: boolean
}
```

### EscalationResult
```typescript
interface EscalationResult {
  detected: boolean
  confidenceScore: number  // 0-100
  reason?: string  // Present when detected = true
  category?: "serious_question" | "emotional_distress" | 
             "unfamiliar_topic" | "scheduling" | "sensitive_info"
}
```

### ConversationSession
```typescript
interface ConversationSession {
  sessionId: string
  messages: Message[]
  styleProfile: StyleProfile
  startTime: string
  endTime?: string
  escalationCount: number
}
```

### ConversationSummary
```typescript
interface ConversationSummary {
  sessionId: string
  transcript: Message[]
  commitments: string[]  // Plans, promises, info shared
  actionItems: string[]  // Things to do
  keyTopics: string[]  // Main discussion themes
  aiMessageCount: number
  humanMessageCount: number
  escalationCount: number
  duration: number  // seconds
}
```

## Error Handling

### Frontend Error Handling
- Display user-friendly error messages for all API failures
- Show loading states during async operations
- Validate input before API calls (minimum message count)
- Provide retry options for transient failures
- Clear error states on successful operations

### Backend Error Handling
- Implement retry logic with exponential backoff for Groq/OpenRouter API (3 attempts)
- Return structured error responses with HTTP status codes
- Log all errors for debugging
- Handle rate limiting gracefully with 429 responses
- Validate all inputs before processing

### API Integration Error Handling
- Catch network errors and timeout exceptions
- Handle malformed API responses
- Implement circuit breaker pattern for repeated failures
- Provide fallback messages when generation fails
- Track API usage to avoid quota exhaustion

## Testing Strategy

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage.

### Unit Testing Approach
- Test specific examples and edge cases
- Focus on integration points between components
- Validate error conditions and boundary cases
- Test UI component rendering and state management
- Mock Claude API responses for deterministic tests

### Property-Based Testing Approach
- Verify universal properties across randomized inputs
- Test with minimum 100 iterations per property
- Generate varied training data, messages, and profiles
- Validate invariants that must hold for all inputs
- Each property test references its design document property

### Testing Tools
- **Frontend**: Vitest, React Testing Library
- **Backend**: pytest, hypothesis (for property-based tests)
- **API Mocking**: MSW (Mock Service Worker) for frontend, responses library for backend

### Test Coverage Goals
- Unit test coverage: 80%+ for business logic
- Property test coverage: All correctness properties implemented
- Integration tests: All API endpoints
- E2E tests: Critical user flows (train → demo → summary)

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, several redundancies were identified:
- Requirements 2.3 and 3.3 both test autopilot automatic response generation (combined into Property 3)
- Requirements 5.1 and 5.6 both test summary completeness (combined into Property 13)
- Requirements 1.3, 9.5, and 10.1 all test style profile caching (combined into Property 2)
- Requirements 1.4 and 7.3 both test minimum message validation (combined into Property 4)

The following properties represent the unique, non-redundant correctness guarantees:

### Style Analysis Properties

Property 1: Pattern Extraction Completeness
*For any* valid training data (10-50 messages), the Style_Analyzer should extract all required patterns and produce a StyleProfile with all fields populated (sentenceLength, emojiFrequency, commonEmojis, punctuationStyle, tone, commonPhrases, formalityLevel, analysisTimestamp).
**Validates: Requirements 1.1, 1.2**

Property 2: Style Profile Caching Round-Trip
*For any* StyleProfile, storing it in the cache and then retrieving it should return an equivalent StyleProfile with all fields preserved.
**Validates: Requirements 1.3, 9.5, 10.1**

Property 3: Session Persistence Round-Trip
*For any* ConversationSession, storing it then retrieving it after application reload should return an equivalent session with all messages and metadata preserved.
**Validates: Requirements 10.2**

Property 4: Insufficient Training Data Rejection
*For any* training data containing fewer than 10 messages, the Style_Analyzer should reject it and return an error indicating insufficient data.
**Validates: Requirements 1.4, 7.3**

### Response Generation Properties

Property 5: Style Profile Application
*For any* StyleProfile and message context, the Response_Generator should produce a response that matches the profile's patterns: if emojiFrequency > 0.5 then response contains emojis, if sentenceLength = "short" then response has short sentences, if tone = "casual" then response avoids formal language.
**Validates: Requirements 2.1, 2.4, 2.5**

Property 6: Autopilot Response Generation
*For any* incoming Friend message when autopilot is enabled, the Response_Generator should automatically create and add a response to the conversation history.
**Validates: Requirements 2.3, 3.3**

Property 7: Autopilot Disabled No Generation
*For any* incoming Friend message when autopilot is disabled, the System should not automatically generate or add a response to the conversation history.
**Validates: Requirements 3.2**

### Autopilot Control Properties

Property 8: Autopilot Toggle State Transition
*For any* autopilot state (enabled or disabled), toggling should flip the state to its opposite (enabled → disabled, disabled → enabled).
**Validates: Requirements 3.1**

Property 9: Takeover Disables Autopilot Temporarily
*For any* conversation state where autopilot is enabled, activating takeover should disable automatic response generation for the current message only.
**Validates: Requirements 3.5**

Property 10: Autopilot State Restoration After Manual Message
*For any* conversation where autopilot was enabled, then takeover was used to send a manual message, the autopilot state should return to enabled after the manual message is sent.
**Validates: Requirements 3.6**

### Escalation Detection Properties

Property 11: Escalation Trigger Detection
*For any* message containing escalation triggers (serious questions, emotional distress signals, unfamiliar topics, scheduling conflicts, sensitive information requests), the Escalation_Detector should flag it with detected=true and provide a specific reason.
**Validates: Requirements 4.1**

Property 12: Confidence Score Bounds
*For any* message analyzed by the Escalation_Detector, the confidence score should be between 0 and 100 inclusive.
**Validates: Requirements 4.3**

Property 13: Low Confidence Triggers Escalation
*For any* message with a confidence score below 70, the Escalation_Detector should set detected=true and flag the message for human review.
**Validates: Requirements 4.4**

Property 14: Escalation Banner Display
*For any* EscalationResult where detected=true, the UI should display an Escalation_Banner containing both the confidence score and the escalation reason.
**Validates: Requirements 4.2, 4.5**

Property 15: Escalation Pauses Autopilot
*For any* conversation where an escalation is detected, the System should not generate automatic responses until the user acknowledges the escalation warning.
**Validates: Requirements 4.6**

### Conversation Summary Properties

Property 16: Summary Completeness
*For any* ConversationSession, the generated ConversationSummary should include all messages from the session in the transcript field.
**Validates: Requirements 5.1, 5.6**

Property 17: Message Attribution Preservation
*For any* message in a ConversationSummary transcript, the isAiGenerated field should correctly indicate whether the message was AI-generated or human-written.
**Validates: Requirements 5.2**

Property 18: Commitment Extraction
*For any* conversation containing explicit commitments (plans, promises, information shared), the ConversationSummary should identify and list them in the commitments field.
**Validates: Requirements 5.3**

Property 19: Action Item Extraction
*For any* conversation containing action items (tasks to do, follow-ups needed), the ConversationSummary should identify and list them in the actionItems field.
**Validates: Requirements 5.4**

Property 20: Topic Extraction
*For any* conversation, the ConversationSummary should extract and list the key topics discussed in the keyTopics field.
**Validates: Requirements 5.5**

### Navigation Properties

Property 21: Training Navigation Flow
*For any* successful training completion, the System should navigate from the Train page to the Demo page.
**Validates: Requirements 6.4**

Property 22: Session End Navigation Flow
*For any* ConversationSession that ends, the System should navigate from the Demo page to the Summary page.
**Validates: Requirements 6.5**

Property 23: Train Button Navigation
*For any* click on the "Train Your AI" button on the Landing page, the System should navigate to the Train page.
**Validates: Requirements 6.3**

### Data Validation Properties

Property 24: Invalid Format Error Display
*For any* training data submission with invalid format, the System should display an error message explaining the expected format.
**Validates: Requirements 7.4**

Property 25: Format Parsing Support
*For any* training data in a supported format (plain text with message separators), the System should successfully parse it into a list of individual messages.
**Validates: Requirements 7.5**

### API Integration Properties

Property 26: API Retry Logic
*For any* API call that fails, the System should retry up to 3 times with exponential backoff before returning an error.
**Validates: Requirements 8.4**

Property 27: Retry Exhaustion Error Display
*For any* API operation where all 3 retry attempts fail, the System should display a user-friendly error message to the user.
**Validates: Requirements 8.5**

Property 28: Rate Limit Handling
*For any* API rate limit response (429 status), the System should queue the request for later execution rather than failing immediately.
**Validates: Requirements 8.6**

### UI Feedback Properties

Property 29: Loading Indicator Display
*For any* operation that takes longer than 500 milliseconds, the System should display a loading indicator until the operation completes.
**Validates: Requirements 9.4**

### Session Management Properties

Property 30: Conversation History Maintenance
*For any* message added during a ConversationSession, that message should appear in the session's conversation history.
**Validates: Requirements 10.4**

Property 31: History Cleanup After Summary
*For any* ConversationSession that ends, after the ConversationSummary is generated, the System should clear the conversation history for that session.
**Validates: Requirements 10.5**
