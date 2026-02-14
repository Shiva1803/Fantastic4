# Implementation Plan: Conversation Autopilot

## Overview

This implementation plan breaks down the Conversation Autopilot system into discrete coding tasks. The approach follows an incremental build strategy: backend API foundation → frontend pages → integration → testing. Each task builds on previous work to ensure no orphaned code.

Tech stack: Vite + React + TypeScript + Tailwind CSS (frontend), Flask + Python (backend), Groq or OpenRouter API.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create backend Flask project with virtual environment
  - Create frontend Vite + React + TypeScript project with Tailwind CSS
  - Install dependencies: Flask, requests, openai SDK (backend); React, React Router, TypeScript, Tailwind (frontend)
  - Set up environment variables for Groq or OpenRouter API key
  - Create basic folder structure: backend/api, backend/services, frontend/src/pages, frontend/src/components
  - _Requirements: All (foundation)_

- [x] 2. Implement backend data models and types
  - [x] 2.1 Create Python data models
    - Define StyleProfile, Message, EscalationResult, ConversationSession, ConversationSummary as dataclasses
    - Add validation methods for required fields
    - Implement to_dict() and from_dict() methods for JSON serialization
    - _Requirements: 1.1, 1.2, 4.3, 5.1_
  
  - [x] 2.2 Write property test for data model serialization
    - **Property 2: Style Profile Caching Round-Trip**
    - **Validates: Requirements 1.3, 9.5, 10.1**
    - Test that for any StyleProfile, serializing to dict then deserializing produces equivalent object

- [x] 3. Implement CacheManager service
  - [x] 3.1 Create in-memory cache for style profiles and sessions
    - Implement get_style_profile() and set_style_profile() methods
    - Implement get_session() and set_session() methods
    - Use Python dict with user_id/session_id as keys
    - _Requirements: 1.3, 10.1, 10.2_
  
  - [x] 3.2 Write property test for cache round-trip
    - **Property 2: Style Profile Caching Round-Trip**
    - **Validates: Requirements 1.3, 9.5, 10.1**
    - Test that storing and retrieving preserves all StyleProfile fields

- [x] 4. Implement StyleAnalyzer service
  - [x] 4.1 Create StyleAnalyzer class with analyze() method
    - Validate training data has at least 10 messages
    - Construct Groq or OpenRouter API prompt for style analysis
    - Call Groq or OpenRouter API with training data
    - Parse API response into StyleProfile object
    - Handle API errors with retry logic (3 attempts, exponential backoff)
    - _Requirements: 1.1, 1.2, 1.4, 8.4_
  
  - [x] 4.2 Write property test for pattern extraction
    - **Property 1: Pattern Extraction Completeness**
    - **Validates: Requirements 1.1, 1.2**
    - Test that for any valid training data, all StyleProfile fields are populated
  
  - [x] 4.3 Write property test for insufficient data rejection
    - **Property 4: Insufficient Training Data Rejection**
    - **Validates: Requirements 1.4, 7.3**
    - Test that training data with < 10 messages is rejected with error

- [x] 5. Implement ResponseGenerator service
  - [x] 5.1 Create ResponseGenerator class with generate() method
    - Accept StyleProfile, conversation history, and incoming message
    - Construct Groq or OpenRouter API prompt with style constraints
    - Call Groq or OpenRouter API for response generation
    - Apply style patterns from profile (emoji, tone, sentence length)
    - Return generated response text
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  
  - [x] 5.2 Write property test for style profile application
    - **Property 5: Style Profile Application**
    - **Validates: Requirements 2.1, 2.4, 2.5**
    - Test that responses match profile patterns (emojis, tone, sentence length)

- [x] 6. Implement EscalationDetector service
  - [x] 6.1 Create EscalationDetector class with detect() method
    - Accept message and conversation history
    - Call Groq or OpenRouter API to analyze for escalation triggers
    - Identify serious questions, emotional distress, unfamiliar topics, scheduling, sensitive info
    - Calculate confidence score (0-100)
    - Return EscalationResult with detected flag, score, reason, category
    - _Requirements: 4.1, 4.3, 4.4_
  
  - [x] 6.2 Write property test for confidence score bounds
    - **Property 12: Confidence Score Bounds**
    - **Validates: Requirements 4.3**
    - Test that for any message, confidence score is between 0 and 100
  
  - [x] 6.3 Write property test for low confidence escalation
    - **Property 13: Low Confidence Triggers Escalation**
    - **Validates: Requirements 4.4**
    - Test that confidence < 70 triggers escalation detection

- [x] 7. Implement ConversationSummarizer service
  - [x] 7.1 Create ConversationSummarizer class with summarize() method
    - Accept messages list and style profile
    - Call Groq or OpenRouter API to extract commitments, action items, key topics
    - Count AI vs human messages
    - Build ConversationSummary object with all fields
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 7.2 Write property test for summary completeness
    - **Property 16: Summary Completeness**
    - **Validates: Requirements 5.1, 5.6**
    - Test that summary includes all messages from session
  
  - [x] 7.3 Write property test for message attribution
    - **Property 17: Message Attribution Preservation**
    - **Validates: Requirements 5.2**
    - Test that AI vs human message marking is preserved in summary

- [x] 8. Checkpoint - Backend services complete
  - Ensure all backend services are implemented and unit tests pass
  - Verify Groq or OpenRouter API integration works with test API key
  - Ask the user if questions arise

- [x] 9. Implement Flask API endpoints
  - [x] 9.1 Create POST /api/train endpoint
    - Accept trainingData array in request body
    - Validate minimum 10 messages
    - Call StyleAnalyzer.analyze()
    - Cache StyleProfile using CacheManager
    - Return StyleProfile JSON
    - Handle errors with appropriate HTTP status codes (400, 500)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 7.3, 7.4_
  
  - [x] 9.2 Create POST /api/respond endpoint
    - Accept sessionId, styleProfile, conversationHistory, incomingMessage, autopilotEnabled
    - Call EscalationDetector.detect() for incoming message
    - If autopilot enabled and no escalation, call ResponseGenerator.generate()
    - Update session in CacheManager
    - Return response text and escalation result
    - _Requirements: 2.1, 2.3, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4_
  
  - [x] 9.3 Create POST /api/summarize endpoint
    - Accept sessionId and messages array
    - Call ConversationSummarizer.summarize()
    - Return ConversationSummary JSON
    - Clear session from cache after summary generation
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.5_
  
  - [x] 9.4 Write integration tests for API endpoints
    - Test /api/train with valid and invalid data
    - Test /api/respond with autopilot on/off
    - Test /api/summarize with sample session
    - Mock Groq or OpenRouter API responses for deterministic tests

- [x] 10. Implement frontend TypeScript types and interfaces
  - Create TypeScript interfaces matching backend models: StyleProfile, Message, EscalationResult, ConversationSession, ConversationSummary
  - Create API client functions for /api/train, /api/respond, /api/summarize
  - Add error handling and type guards
  - _Requirements: All (frontend foundation)_

- [x] 11. Implement LandingPage component
  - [x] 11.1 Create LandingPage with hero section and CTA
    - Display project title and description
    - Add "Train Your AI" button
    - Implement navigation to /train on button click
    - Style with clean, minimal CSS
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 11.2 Write unit test for landing page navigation
    - Test that clicking "Train Your AI" navigates to /train

- [x] 12. Implement TrainPage component
  - [x] 12.1 Create TrainPage with text input and file upload
    - Add textarea for pasting training data
    - Add file upload input (optional)
    - Add submit button
    - Implement state: trainingText, styleProfile, isLoading, error
    - Call POST /api/train on submit
    - Display loading indicator during API call
    - Display error messages for validation failures
    - Display StyleProfile results in human-readable format
    - Navigate to /demo on successful training
    - _Requirements: 1.1, 1.2, 1.6, 6.4, 7.1, 7.2, 7.4_
  
  - [x] 12.2 Write property test for training data validation
    - **Property 4: Insufficient Training Data Rejection**
    - **Validates: Requirements 1.4, 7.3**
    - Test that submitting < 10 messages shows error
  
  - [x] 12.3 Write unit test for navigation after training
    - **Property 21: Training Navigation Flow**
    - **Validates: Requirements 6.4**
    - Test that successful training navigates to /demo

- [x] 13. Implement DemoPage component
  - [x] 13.1 Create DemoPage with conversation interface
    - Display conversation history (messages list)
    - Add input field for Friend messages
    - Add autopilot toggle switch
    - Add takeover button
    - Implement state: messages, currentInput, autopilotEnabled, isGenerating, escalation, sessionId
    - Generate unique sessionId on mount
    - Call POST /api/respond when Friend message is sent
    - Display AI responses in conversation
    - Show escalation banner when detected
    - Pause autopilot when escalation detected
    - Allow manual message input via takeover
    - Add "End Session" button to navigate to /summary
    - _Requirements: 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.2, 4.5, 4.6, 6.5_
  
  - [x] 13.2 Write property test for autopilot behavior
    - **Property 6: Autopilot Response Generation**
    - **Validates: Requirements 2.3, 3.3**
    - Test that autopilot enabled generates automatic responses
  
  - [x] 13.3 Write property test for autopilot disabled
    - **Property 7: Autopilot Disabled No Generation**
    - **Validates: Requirements 3.2**
    - Test that autopilot disabled prevents automatic responses
  
  - [x] 13.4 Write property test for escalation pauses autopilot
    - **Property 15: Escalation Pauses Autopilot**
    - **Validates: Requirements 4.6**
    - Test that escalation stops automatic responses until acknowledged

- [x] 14. Implement SummaryPage component
  - [x] 14.1 Create SummaryPage with conversation summary display
    - Accept sessionId from route params
    - Call POST /api/summarize on mount
    - Display full transcript with AI/human message markers
    - Highlight commitments section
    - Display action items list
    - Display key topics list
    - Show message counts (AI vs human)
    - Add "Start New Session" button to return to /train
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [x] 14.2 Write unit test for summary display
    - Test that all summary sections are rendered
    - Test that AI/human messages are correctly marked

- [x] 15. Implement React Router and navigation
  - [x] 15.1 Set up React Router with routes
    - Configured routes: /, /train, /demo, /summary
    - Added catch-all route for 404s (redirects to home)
    - _Requirements: 6.1, 6.3_
  
  - [x] 15.2 Implement navigation guards
    - DemoPage checks for styleProfile in location state, redirects if missing
    - SummaryPage checks for required session data, redirects if missing
    - _Requirements: 6.4, 6.5_
  
  - [x] 15.3 Implement state passing between pages
    - StyleProfile passed via route state from TrainPage to DemoPage
    - Session data passed via route state from DemoPage to SummaryPage
    - _Requirements: 6.6_
  
  - [x] 15.4 Routing tests
    - Individual page components have comprehensive routing tests
    - Navigation flows tested in LandingPage, TrainPage, DemoPage, SummaryPage tests
    - _Note: App-level routing tests removed to avoid nested router issues_

- [x] 16. Implement UI feedback and error handling
  - [x] 16.1 Add loading indicators to all async operations
    - Show spinner when API calls take > 500ms
    - Display loading state in buttons during operations
    - TrainPage: "Analyzing..." button text during API call
    - DemoPage: Animated dots with "Generating response..." message
    - SummaryPage: Full-page spinner with "Generating summary..." text
    - _Requirements: 9.4_
  
  - [x] 16.2 Add error handling and retry logic
    - Display user-friendly error messages for API failures ✅
    - Implement retry buttons for transient errors ✅
    - Show specific error messages for validation failures ✅
    - TrainPage: "Try Again" button in error message
    - DemoPage: "Retry" button for failed response generation
    - SummaryPage: "Retry" and "Start New Session" buttons on error
    - _Requirements: 8.5, 7.4_
  
  - [x] 16.3 Verify loading indicators in tests
    - **Validates: Requirements 9.4**
    - TrainPage tests verify "Analyzing..." state
    - DemoPage tests verify "Generating response..." indicator
    - SummaryPage tests verify "Generating summary..." spinner
    - All page tests include loading state verification

- [x] 17. Implement session management and persistence
  - [x] 17.1 Add conversation history tracking
    - Store messages in DemoPage state ✅
    - Update history when messages are sent/received ✅
    - Messages state tracks full conversation history
    - _Requirements: 10.4_
  
  - [x] 17.2 Add session cleanup after summary
    - Clear conversation history after summary generation ✅
    - Reset session state ✅
    - Backend clears session from cache after summary
    - Frontend navigates away, discarding session state
    - _Requirements: 10.5_
  
  - [x] 17.3 Verify history maintenance in tests
    - **Property 30: Conversation History Maintenance**
    - **Validates: Requirements 10.4**
    - DemoPage tests verify messages are added to history
    - Tests confirm conversation flow maintains message order
    - Test that added messages appear in history

- [x] 18. Redesign UI with x402.org-inspired aesthetic
  - [x] 18.1 Implement design system and global styles
    - **Design Philosophy**: Clean, modern, technical aesthetic inspired by x402.org
    - Create custom Tailwind config with x402-inspired color palette:
      - Background: Deep black (#000000) or very dark gray (#0a0a0a)
      - Primary text: Pure white (#ffffff) for maximum contrast
      - Accent color: Bright cyan/blue (#00d4ff or similar) for CTAs and highlights
      - Secondary text: Light gray (#a0a0a0) for descriptions
      - Borders: Subtle gray (#1a1a1a) for cards and dividers
    - Typography:
      - Use system fonts or modern sans-serif (Inter, SF Pro, or similar)
      - Large, bold headings with generous spacing
      - Clean, readable body text with proper line-height
    - Spacing: Generous whitespace, breathing room between sections
    - _Inspiration: x402.org's dark theme, high contrast, technical feel_
  
  - [x] 18.2 Redesign LandingPage with hero section
    - **Hero Section** (inspired by x402.org top section):
      - Large, bold headline: "Conversation Autopilot" with subtitle
      - Concise value proposition (1-2 sentences max)
      - Prominent CTA button with cyan accent color
      - Clean navigation bar at top (minimal, text-only links)
    - **Stats Section** (inspired by x402.org metrics):
      - Display key metrics in grid layout (e.g., "Messages Analyzed", "AI Responses Generated", "Accuracy Rate")
      - Large numbers with small labels
      - Use subtle borders/cards for each stat
    - **"What is it?" Section** (inspired by x402.org explanation):
      - Clear, concise explanation of what Conversation Autopilot does
      - Use short paragraphs with bold key phrases
      - Technical but accessible language
    - **Features Grid** (inspired by x402.org "Zero X" section):
      - 2-3 column grid of key features
      - Each feature: Icon/emoji + bold title + 1-line description
      - Examples: "Zero Setup", "Instant Training", "Smart Escalation"
    - **Comparison Section** (inspired by x402.org "old way vs new way"):
      - Two-column comparison: "Manual Texting" vs "With Autopilot"
      - Step-by-step breakdown showing time/effort savings
      - Use numbered lists with clear visual separation
    - **CTA Footer**: "Get Started" button leading to training
    - _Remove generic purple theme, use dark background with cyan accents_
  
  - [x] 18.3 Redesign TrainPage with technical aesthetic
    - Dark background with subtle card for training input
    - Monospace font for textarea (code-like feel)
    - Cyan accent for "Analyze" button
    - Style profile results as clean data cards:
      - Each metric in its own bordered card
      - Large values with small labels
      - Grid layout for metrics
    - Progress indicator: Minimal, modern (thin line or dots)
    - Remove colorful backgrounds, use subtle borders instead
    - _Make it feel like a developer tool, not a consumer app_
  
  - [x] 18.4 Redesign DemoPage with chat interface
    - **Layout**: Full-height chat interface with dark theme
    - **Header**: Minimal top bar with session info and controls
      - Session ID in monospace font
      - Autopilot toggle: Modern switch with cyan active state
      - "End Session" button: Subtle, secondary style
    - **Messages**:
      - Friend messages: Left-aligned, dark gray bubble (#1a1a1a)
      - AI messages: Right-aligned, cyan-tinted bubble (#003344 or similar)
      - Timestamps: Small, gray, subtle
      - Remove rounded corners or use minimal rounding (2-4px)
      - Generous spacing between messages
    - **Escalation Banner**:
      - Full-width banner at top (below header)
      - Yellow/amber accent for warning (#fbbf24)
      - Bold text with confidence score
      - "Acknowledge" button with clear action
    - **Input Area**:
      - Fixed bottom bar with dark background
      - Clean input field with subtle border
      - "Send" button with cyan accent
      - Status text below input (small, gray)
    - _Inspiration: Technical chat interfaces, developer tools_
  
  - [x] 18.5 Redesign SummaryPage with data visualization
    - **Header**: Large "Session Summary" title
    - **Metrics Row**: Key stats in grid (AI messages, Human messages, Duration)
    - **Transcript Section**:
      - Clean list of messages with clear AI/Human labels
      - Monospace font for message IDs
      - Subtle borders between messages
    - **Highlights Sections**:
      - Commitments: Bulleted list with cyan bullets
      - Action Items: Numbered list with checkboxes
      - Key Topics: Tag-style pills with dark background
    - **Footer**: "Start New Session" button (cyan accent)
    - Use cards with subtle borders, not colored backgrounds
    - _Make it feel like a technical report, not a social media feed_
  
  - [x] 18.6 Add micro-interactions and polish
    - Button hover states: Subtle brightness increase, no dramatic color changes
    - Focus states: Cyan outline for accessibility
    - Loading states: Minimal spinners or skeleton screens (dark theme)
    - Transitions: Fast (150-200ms), subtle
    - Smooth scrolling for chat messages
    - Fade-in animations for new messages (subtle)
    - _Keep animations minimal and purposeful, not flashy_
  
  - [x] 18.7 Ensure responsive design
    - Mobile: Stack layouts vertically, maintain dark theme
    - Tablet: Optimize grid layouts for medium screens
    - Desktop: Full-width layouts with max-width containers
    - Test on various screen sizes
    - Ensure touch targets are large enough on mobile
    - _Maintain aesthetic consistency across all breakpoints_

- [x] 19. Final integration and testing
  - [x] 19.1 Wire all components together
    - Test complete user flow: Landing → Train → Demo → Summary
    - Verify all API integrations work end-to-end
    - Test autopilot toggle and takeover functionality
    - Test escalation detection and banner display
    - _Requirements: All_
  
  - [x] 19.2 Write end-to-end tests
    - Test complete user journey from training to summary
    - Test error scenarios and recovery
    - Test autopilot and escalation flows
  
  - [x] 19.3 Cross-browser and accessibility testing
    - Test in Chrome, Firefox, Safari
    - Verify keyboard navigation works
    - Check color contrast ratios (WCAG AA minimum)
    - Test with screen readers

- [x] 20. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify all API endpoints work correctly
  - Test with real Groq or OpenRouter API key
  - Verify design consistency across all pages
  - Ask the user if questions arise

## Design Notes

### x402.org-Inspired Aesthetic

The frontend design is heavily inspired by x402.org's clean, technical aesthetic:

**Color Palette**:
- Background: Deep black (#000000) or very dark gray (#0a0a0a)
- Text: Pure white (#ffffff) for headings, light gray (#a0a0a0) for body
- Accent: Bright cyan/blue (#00d4ff) for CTAs, links, and highlights
- Borders: Subtle gray (#1a1a1a) for cards and separators
- Warning: Amber (#fbbf24) for escalation banners

**Typography**:
- System fonts or modern sans-serif (Inter, SF Pro Display)
- Large, bold headings (32-48px)
- Generous line-height (1.6-1.8) for readability
- Monospace for technical elements (session IDs, code)

**Layout Principles**:
- Generous whitespace and breathing room
- High contrast for accessibility
- Minimal borders and shadows
- Clean, geometric shapes
- Grid-based layouts for metrics and features

**Component Style**:
- Buttons: Solid cyan with white text, subtle hover states
- Cards: Dark background with subtle borders, no shadows
- Inputs: Dark with light borders, cyan focus states
- Messages: Minimal bubbles with subtle backgrounds
- Stats: Large numbers with small labels in grid layout

**Inspiration Elements from x402.org**:
1. Hero section with bold headline and single CTA
2. Metrics grid with large numbers
3. "What is it?" explanation section
4. Feature grid with icons and short descriptions
5. Comparison table (old way vs new way)
6. Technical, developer-focused aesthetic
7. Minimal navigation
8. High information density without clutter

## Notes

- All tasks are required for comprehensive testing and production-ready code
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- The implementation follows an incremental approach: backend → frontend → integration
- All code should be production-ready with proper error handling
- Design should feel technical and modern, not generic or consumer-focused
