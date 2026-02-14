/**
 * Type guards for runtime type checking.
 * 
 * These functions validate that data received from the API
 * matches the expected TypeScript types.
 */

import type {
  StyleProfile,
  Message,
  EscalationResult,
  ConversationSummary,
} from './index';

/**
 * Type guard for StyleProfile.
 */
export function isStyleProfile(value: unknown): value is StyleProfile {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const profile = value as Partial<StyleProfile>;
  
  return (
    typeof profile.sentenceLength === 'string' &&
    ['short', 'medium', 'long'].includes(profile.sentenceLength) &&
    typeof profile.emojiFrequency === 'number' &&
    profile.emojiFrequency >= 0 &&
    profile.emojiFrequency <= 1 &&
    Array.isArray(profile.commonEmojis) &&
    typeof profile.punctuationStyle === 'string' &&
    typeof profile.tone === 'string' &&
    ['casual', 'formal', 'mixed'].includes(profile.tone) &&
    Array.isArray(profile.commonPhrases) &&
    typeof profile.formalityLevel === 'number' &&
    profile.formalityLevel >= 0 &&
    profile.formalityLevel <= 1 &&
    typeof profile.analysisTimestamp === 'string'
  );
}

/**
 * Type guard for Message.
 */
export function isMessage(value: unknown): value is Message {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const message = value as Partial<Message>;
  
  return (
    typeof message.id === 'string' &&
    typeof message.sender === 'string' &&
    ['user', 'friend', 'ai'].includes(message.sender) &&
    typeof message.text === 'string' &&
    message.text.trim().length > 0 &&
    typeof message.timestamp === 'string' &&
    typeof message.isAiGenerated === 'boolean'
  );
}

/**
 * Type guard for EscalationResult.
 */
export function isEscalationResult(value: unknown): value is EscalationResult {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const result = value as Partial<EscalationResult>;
  
  return (
    typeof result.detected === 'boolean' &&
    typeof result.confidenceScore === 'number' &&
    result.confidenceScore >= 0 &&
    result.confidenceScore <= 100 &&
    (result.reason === null || typeof result.reason === 'string') &&
    (result.category === null || typeof result.category === 'string')
  );
}

/**
 * Type guard for ConversationSummary.
 */
export function isConversationSummary(value: unknown): value is ConversationSummary {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const summary = value as Partial<ConversationSummary>;
  
  return (
    typeof summary.sessionId === 'string' &&
    Array.isArray(summary.transcript) &&
    summary.transcript.every(isMessage) &&
    Array.isArray(summary.commitments) &&
    summary.commitments.every((c) => typeof c === 'string') &&
    Array.isArray(summary.actionItems) &&
    summary.actionItems.every((a) => typeof a === 'string') &&
    Array.isArray(summary.keyTopics) &&
    summary.keyTopics.every((t) => typeof t === 'string') &&
    typeof summary.aiMessageCount === 'number' &&
    typeof summary.humanMessageCount === 'number' &&
    typeof summary.escalationCount === 'number' &&
    typeof summary.duration === 'number'
  );
}

/**
 * Validates and parses a StyleProfile from unknown data.
 * 
 * @throws Error if validation fails
 */
export function validateStyleProfile(data: unknown): StyleProfile {
  if (!isStyleProfile(data)) {
    throw new Error('Invalid StyleProfile data');
  }
  return data;
}

/**
 * Validates and parses a Message from unknown data.
 * 
 * @throws Error if validation fails
 */
export function validateMessage(data: unknown): Message {
  if (!isMessage(data)) {
    throw new Error('Invalid Message data');
  }
  return data;
}

/**
 * Validates and parses an EscalationResult from unknown data.
 * 
 * @throws Error if validation fails
 */
export function validateEscalationResult(data: unknown): EscalationResult {
  if (!isEscalationResult(data)) {
    throw new Error('Invalid EscalationResult data');
  }
  return data;
}

/**
 * Validates and parses a ConversationSummary from unknown data.
 * 
 * @throws Error if validation fails
 */
export function validateConversationSummary(data: unknown): ConversationSummary {
  if (!isConversationSummary(data)) {
    throw new Error('Invalid ConversationSummary data');
  }
  return data;
}
