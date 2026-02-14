/**
 * TypeScript types and interfaces for Conversation Autopilot.
 * 
 * These types match the backend data models and use camelCase naming
 * for consistency with JavaScript/TypeScript conventions.
 */

// Re-export type guards
export * from './guards';

/**
 * User's texting style profile extracted from training data.
 */
export interface StyleProfile {
  sentenceLength: 'short' | 'medium' | 'long';
  emojiFrequency: number; // 0-1
  commonEmojis: string[];
  punctuationStyle: string;
  tone: 'casual' | 'formal' | 'mixed';
  commonPhrases: string[];
  formalityLevel: number; // 0-1
  analysisTimestamp: string; // ISO 8601
}

/**
 * A single message in a conversation.
 */
export interface Message {
  id: string;
  sender: 'user' | 'friend' | 'ai';
  text: string;
  timestamp: string; // ISO 8601
  isAiGenerated: boolean;
}

/**
 * Result of escalation detection analysis.
 */
export interface EscalationResult {
  detected: boolean;
  confidenceScore: number; // 0-100
  reason: string | null;
  category: 'serious_question' | 'emotional_distress' | 'unfamiliar_topic' | 'scheduling' | 'sensitive_info' | null;
}

/**
 * An active conversation session.
 */
export interface ConversationSession {
  sessionId: string;
  messages: Message[];
  styleProfile: StyleProfile;
  startTime: string; // ISO 8601
  endTime: string | null;
  escalationCount: number;
}

/**
 * Summary of a completed conversation session.
 */
export interface ConversationSummary {
  sessionId: string;
  transcript: Message[];
  commitments: string[];
  actionItems: string[];
  keyTopics: string[];
  aiMessageCount: number;
  humanMessageCount: number;
  escalationCount: number;
  duration: number; // seconds
}

/**
 * API error response structure.
 */
export interface ApiError {
  error: string;
  details?: string;
  provided?: number;
  required?: number;
}

/**
 * Request body for POST /api/train
 */
export interface TrainRequest {
  trainingData: string[];
  userId?: string;
}

/**
 * Response body for POST /api/train
 */
export interface TrainResponse {
  styleProfile: StyleProfile;
  userId: string;
}

/**
 * Request body for POST /api/respond
 */
export interface RespondRequest {
  sessionId: string;
  styleProfile: StyleProfile;
  conversationHistory: Message[];
  incomingMessage: string;
  autopilotEnabled: boolean;
}

/**
 * Response body for POST /api/respond
 */
export interface RespondResponse {
  response: string | null;
  escalation: EscalationResult;
}

/**
 * Request body for POST /api/summarize
 */
export interface SummarizeRequest {
  sessionId: string;
  messages: Message[];
  styleProfile: StyleProfile;
}

/**
 * Response body for POST /api/summarize
 */
export interface SummarizeResponse {
  summary: ConversationSummary;
}

/**
 * A conversation space for organizing content.
 */
export interface Space {
  id: string;
  userId: string;
  name: string;
  description: string | null;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
  itemCount: number;
}
