# API Client Usage

This directory contains the API client for the Conversation Autopilot backend.

## Quick Start

```typescript
import { trainStyle, generateResponse, summarizeConversation } from './api';
import { generateSessionId, createMessage, parseTrainingData } from './api/utils';

// 1. Train the AI with your texting style
const trainingText = `
  hey how are you
  good thanks!
  wanna hang out?
  sure sounds good
  cool see you later
  bye!
  talk soon
  yeah definitely
  catch you later
  peace out
`;

const trainingData = parseTrainingData(trainingText);
const { styleProfile } = await trainStyle(trainingData, 'user-123');

// 2. Generate responses in a conversation
const sessionId = generateSessionId();
const conversationHistory = [];

const friendMessage = createMessage('friend', 'Want to grab lunch?');
conversationHistory.push(friendMessage);

const { response, escalation } = await generateResponse({
  sessionId,
  styleProfile,
  conversationHistory,
  incomingMessage: friendMessage.text,
  autopilotEnabled: true,
});

if (response && !escalation.detected) {
  const aiMessage = createMessage('ai', response, true);
  conversationHistory.push(aiMessage);
}

// 3. Summarize the conversation
const { summary } = await summarizeConversation({
  sessionId,
  messages: conversationHistory,
  styleProfile,
});

console.log('Commitments:', summary.commitments);
console.log('Action Items:', summary.actionItems);
```

## Error Handling

```typescript
import { trainStyle, ApiClientError } from './api';

try {
  const result = await trainStyle(['not', 'enough', 'messages']);
} catch (error) {
  if (error instanceof ApiClientError) {
    console.error(`API Error (${error.statusCode}):`, error.message);
    if (error.details) {
      console.error('Details:', error.details);
    }
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Type Guards

Use type guards to validate data at runtime:

```typescript
import { isStyleProfile, validateStyleProfile } from '../types';

// Check if data is valid
if (isStyleProfile(data)) {
  // TypeScript knows data is StyleProfile here
  console.log(data.tone);
}

// Or throw an error if invalid
const profile = validateStyleProfile(data);
```

## Environment Configuration

Set the API URL via environment variable:

```bash
# .env.local
VITE_API_URL=http://localhost:5000
```

If not set, defaults to `http://localhost:5000`.
