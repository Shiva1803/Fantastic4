/**
 * Tests for DemoPage component.
 * 
 * Validates autopilot behavior, escalation detection, and conversation flow.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import DemoPage from './DemoPage';
import * as apiClient from '../api/client';
import type { StyleProfile, RespondResponse } from '../types';

// Mock the API client module
vi.mock('../api/client');

// Mock the utils module
vi.mock('../api/utils', () => ({
  generateSessionId: vi.fn(() => 'test-session-id'),
  createMessage: vi.fn((sender, text) => ({
    id: `msg-${Date.now()}`,
    sender,
    text,
    timestamp: new Date().toISOString(),
    isAiGenerated: sender === 'ai',
  })),
}));

const mockStyleProfile: StyleProfile = {
  sentenceLength: 'short',
  emojiFrequency: 0.5,
  commonEmojis: ['😊', '👍'],
  punctuationStyle: 'minimal',
  tone: 'casual',
  commonPhrases: ['hey', 'cool'],
  formalityLevel: 0.3,
  analysisTimestamp: new Date().toISOString(),
};

describe('DemoPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('redirects to /train if no style profile is provided', () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/demo']}>
        <DemoPage />
      </MemoryRouter>
    );
    
    // Component should render nothing and redirect
    expect(container.firstChild).toBeNull();
  });

  it('renders conversation interface with autopilot toggle', () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    expect(screen.getByText('Conversation Demo')).toBeInTheDocument();
    expect(screen.getByLabelText('Autopilot')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Type a message as the Friend/)).toBeInTheDocument();
    expect(screen.getByText('End Session')).toBeInTheDocument();
  });

  it('generates automatic response when autopilot is enabled', async () => {
    const user = userEvent.setup();
    
    const mockResponse: RespondResponse = {
      response: 'Hey! How are you?',
      escalation: {
        detected: false,
        confidenceScore: 85,
        reason: null,
        category: null,
      },
    };
    
    vi.mocked(apiClient.generateResponse).mockResolvedValue(mockResponse);
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Type and send a message
    await user.type(input, 'Hi there!');
    await user.click(sendButton);
    
    // Wait for friend message to appear
    await waitFor(() => {
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });
    
    // Wait for AI response to appear
    await waitFor(() => {
      expect(screen.getByText('Hey! How are you?')).toBeInTheDocument();
    });
    
    // Verify API was called
    expect(apiClient.generateResponse).toHaveBeenCalledWith(
      expect.objectContaining({
        autopilotEnabled: true,
        incomingMessage: 'Hi there!',
      })
    );
  });

  it('does not generate automatic response when autopilot is disabled', async () => {
    const user = userEvent.setup();
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    // Disable autopilot
    const autopilotToggle = screen.getByLabelText('Autopilot');
    await user.click(autopilotToggle);
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Type and send a message
    await user.type(input, 'Hi there!');
    await user.click(sendButton);
    
    // Wait for friend message to appear
    await waitFor(() => {
      expect(screen.getByText('Hi there!')).toBeInTheDocument();
    });
    
    // Verify API was NOT called
    expect(apiClient.generateResponse).not.toHaveBeenCalled();
    
    // Verify status message
    expect(screen.getByText(/Autopilot disabled/)).toBeInTheDocument();
  });

  it('displays escalation banner and pauses autopilot when escalation is detected', async () => {
    const user = userEvent.setup();
    
    const mockResponse: RespondResponse = {
      response: null,
      escalation: {
        detected: true,
        confidenceScore: 45,
        reason: 'Serious question detected requiring personal attention',
        category: 'serious_question',
      },
    };
    
    vi.mocked(apiClient.generateResponse).mockResolvedValue(mockResponse);
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Type and send a message
    await user.type(input, 'Can you help me with something important?');
    await user.click(sendButton);
    
    // Wait for escalation banner to appear
    await waitFor(() => {
      expect(screen.getByText('Human Attention Needed')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Serious question detected/)).toBeInTheDocument();
    expect(screen.getByText(/Confidence: 45%/)).toBeInTheDocument();
    expect(screen.getByText('Acknowledge')).toBeInTheDocument();
    expect(screen.getByText('Take Over')).toBeInTheDocument();
    
    // Verify autopilot status message
    expect(screen.getByText(/Autopilot paused/)).toBeInTheDocument();
  });

  it('allows user to acknowledge escalation and continue', async () => {
    const user = userEvent.setup();
    
    const mockResponse: RespondResponse = {
      response: null,
      escalation: {
        detected: true,
        confidenceScore: 50,
        reason: 'Emotional distress detected',
        category: 'emotional_distress',
      },
    };
    
    vi.mocked(apiClient.generateResponse).mockResolvedValue(mockResponse);
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Trigger escalation
    await user.type(input, 'I am really upset');
    await user.click(sendButton);
    
    // Wait for escalation banner
    await waitFor(() => {
      expect(screen.getByText('Human Attention Needed')).toBeInTheDocument();
    });
    
    // Acknowledge escalation
    const acknowledgeButton = screen.getByText('Acknowledge');
    await user.click(acknowledgeButton);
    
    // Banner should disappear
    await waitFor(() => {
      expect(screen.queryByText('Human Attention Needed')).not.toBeInTheDocument();
    });
  });

  it('shows loading indicator while generating response', async () => {
    const user = userEvent.setup();
    
    // Create a promise that we can control
    let resolveResponse: (value: RespondResponse) => void;
    const responsePromise = new Promise<RespondResponse>((resolve) => {
      resolveResponse = resolve;
    });
    
    vi.mocked(apiClient.generateResponse).mockReturnValue(responsePromise);
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Send message
    await user.type(input, 'Hello');
    await user.click(sendButton);
    
    // Loading indicator should appear
    await waitFor(() => {
      expect(screen.getByText('Generating response...')).toBeInTheDocument();
    });
    
    // Resolve the promise
    resolveResponse!({
      response: 'Hi!',
      escalation: {
        detected: false,
        confidenceScore: 90,
        reason: null,
        category: null,
      },
    });
    
    // Loading indicator should disappear
    await waitFor(() => {
      expect(screen.queryByText('Generating response...')).not.toBeInTheDocument();
    });
  });

  it('displays error message when API call fails', async () => {
    const user = userEvent.setup();
    
    const error = new Error('API error');
    error.name = 'ApiClientError';
    vi.mocked(apiClient.generateResponse).mockRejectedValue(error);
    
    render(
      <MemoryRouter initialEntries={[{ pathname: '/demo', state: { styleProfile: mockStyleProfile } }]}>
        <DemoPage />
      </MemoryRouter>
    );
    
    const input = screen.getByPlaceholderText(/Type a message as the Friend/);
    const sendButton = screen.getByText('Send');
    
    // Send message
    await user.type(input, 'Hello');
    await user.click(sendButton);
    
    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/Failed to generate response/)).toBeInTheDocument();
    });
  });
});
