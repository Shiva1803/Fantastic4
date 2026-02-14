/**
 * API client for Conversation Autopilot backend.
 * 
 * Provides type-safe functions for calling backend endpoints.
 */

import type {
  TrainRequest,
  TrainResponse,
  RespondRequest,
  RespondResponse,
  SummarizeRequest,
  SummarizeResponse,
  ApiError,
} from '../types';

// Base API URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Custom error class for API errors.
 */
export class ApiClientError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: string
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

/**
 * Helper function to handle API responses.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData: ApiError = await response.json().catch(() => ({
      error: 'Unknown error occurred',
    }));
    
    throw new ApiClientError(
      errorData.error,
      response.status,
      errorData.details
    );
  }
  
  return response.json();
}

/**
 * Train the AI with user's texting style.
 * 
 * @param trainingData - Array of at least 10 message strings
 * @param userId - Optional user identifier
 * @returns Style profile and user ID
 * @throws ApiClientError if request fails or validation errors occur
 */
export async function trainStyle(
  trainingData: string[],
  userId?: string
): Promise<TrainResponse> {
  const requestBody: TrainRequest = {
    trainingData,
    userId,
  };
  
  const response = await fetch(`${API_BASE_URL}/api/train`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  
  return handleResponse<TrainResponse>(response);
}

/**
 * Generate a response to an incoming message.
 * 
 * @param request - Request containing session info, style profile, and message
 * @returns Generated response and escalation detection result
 * @throws ApiClientError if request fails
 */
export async function generateResponse(
  request: RespondRequest
): Promise<RespondResponse> {
  const response = await fetch(`${API_BASE_URL}/api/respond`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  return handleResponse<RespondResponse>(response);
}

/**
 * Generate a summary of a conversation session.
 * 
 * @param request - Request containing session ID, messages, and style profile
 * @returns Conversation summary with commitments, action items, and topics
 * @throws ApiClientError if request fails
 */
export async function summarizeConversation(
  request: SummarizeRequest
): Promise<SummarizeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  return handleResponse<SummarizeResponse>(response);
}

/**
 * Check if the backend is healthy and reachable.
 * 
 * @returns True if backend is healthy, false otherwise
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}
