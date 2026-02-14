/**
 * Utility functions for API interactions.
 */

import type { Message } from '../types';

/**
 * Generate a unique session ID.
 */
export function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Generate a unique message ID.
 */
export function generateMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Create a new message object.
 */
export function createMessage(
  sender: 'user' | 'friend' | 'ai',
  text: string,
  isAiGenerated: boolean = false
): Message {
  return {
    id: generateMessageId(),
    sender,
    text,
    timestamp: new Date().toISOString(),
    isAiGenerated,
  };
}

/**
 * Format a timestamp for display.
 */
export function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Format duration in seconds to human-readable string.
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return remainingMinutes > 0
    ? `${hours}h ${remainingMinutes}m`
    : `${hours}h`;
}

/**
 * Validate training data before sending to API.
 */
export function validateTrainingData(data: string[]): {
  valid: boolean;
  error?: string;
} {
  if (!Array.isArray(data)) {
    return { valid: false, error: 'Training data must be an array' };
  }
  
  if (data.length < 10) {
    return {
      valid: false,
      error: `Insufficient training data. Please provide at least 10 messages. (${data.length}/10)`,
    };
  }
  
  const emptyMessages = data.filter((msg) => !msg.trim());
  if (emptyMessages.length > 0) {
    return {
      valid: false,
      error: 'Training data contains empty messages',
    };
  }
  
  return { valid: true };
}

/**
 * Parse training data from text input.
 * Splits by newlines and filters out empty lines.
 */
export function parseTrainingData(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}
