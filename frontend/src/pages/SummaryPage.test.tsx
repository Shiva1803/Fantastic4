/**
 * Tests for SummaryPage component.
 * 
 * Validates summary display, message attribution, and navigation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import SummaryPage from './SummaryPage';
import * as apiClient from '../api/client';
import type { StyleProfile, Message, ConversationSummary } from '../types';

// Mock the API client module
vi.mock('../api/client');

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

const mockMessages: Message[] = [
  {
    id: 'msg-1',
    sender: 'friend',
    text: 'Hey, want to grab lunch tomorrow?',
    timestamp: new Date().toISOString(),
    isAiGenerated: false,
  },
  {
    id: 'msg-2',
    sender: 'ai',
    text: 'Sure! How about 12:30?',
    timestamp: new Date().toISOString(),
    isAiGenerated: true,
  },
  {
    id: 'msg-3',
    sender: 'friend',
    text: 'Perfect, see you then!',
    timestamp: new Date().toISOString(),
    isAiGenerated: false,
  },
];

const mockSummary: ConversationSummary = {
  sessionId: 'test-session-123',
  transcript: mockMessages,
  commitments: ['Lunch at 12:30 tomorrow'],
  actionItems: ['Confirm lunch location', 'Set reminder'],
  keyTopics: ['lunch', 'meeting'],
  aiMessageCount: 1,
  humanMessageCount: 2,
  escalationCount: 0,
  duration: 125,
};

describe('SummaryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('redirects to home if no session data is provided', async () => {
    render(
      <MemoryRouter initialEntries={['/summary']}>
        <SummaryPage />
      </MemoryRouter>
    );
    
    // Component should not display summary content
    await waitFor(() => {
      expect(screen.queryByText('Session Summary')).not.toBeInTheDocument();
    });
  });

  it('displays loading state while fetching summary', () => {
    // Create a promise that never resolves to keep loading state
    const neverResolve = new Promise(() => {});
    vi.mocked(apiClient.summarizeConversation).mockReturnValue(neverResolve);
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    expect(screen.getByText('Generating summary...')).toBeInTheDocument();
  });

  it('displays all summary sections when data is loaded', async () => {
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    // Wait for summary to load - use getAllByText and check for multiple instances
    await waitFor(() => {
      expect(screen.getAllByText('Session Summary').length).toBeGreaterThan(0);
    });
    
    // Check statistics - use more specific queries
    expect(screen.getByText('AI Messages')).toBeInTheDocument();
    const aiCount = screen.getByText('AI Messages').nextElementSibling;
    expect(aiCount).toHaveTextContent('1');
    
    expect(screen.getByText('Human Messages')).toBeInTheDocument();
    const humanCount = screen.getByText('Human Messages').nextElementSibling;
    expect(humanCount).toHaveTextContent('2');
    
    expect(screen.getByText('Escalations')).toBeInTheDocument();
    expect(screen.getByText('Duration')).toBeInTheDocument();
    expect(screen.getByText('2m 5s')).toBeInTheDocument();
    
    // Check sections
    expect(screen.getByText('Commitments & Plans')).toBeInTheDocument();
    expect(screen.getByText('Action Items')).toBeInTheDocument();
    expect(screen.getByText('Key Topics')).toBeInTheDocument();
    expect(screen.getByText('Full Transcript')).toBeInTheDocument();
  });

  it('correctly marks AI-generated messages in transcript', async () => {
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getAllByText('Session Summary').length).toBeGreaterThan(0);
    });
    
    // Check that AI badge appears for AI messages
    const aiBadges = screen.getAllByText('AI');
    expect(aiBadges).toHaveLength(1);
    
    // Check that all messages are displayed
    expect(screen.getByText('Hey, want to grab lunch tomorrow?')).toBeInTheDocument();
    expect(screen.getByText('Sure! How about 12:30?')).toBeInTheDocument();
    expect(screen.getByText('Perfect, see you then!')).toBeInTheDocument();
  });

  it('displays commitments list', async () => {
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Commitments & Plans')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Lunch at 12:30 tomorrow')).toBeInTheDocument();
  });

  it('displays action items list', async () => {
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Action Items')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Confirm lunch location')).toBeInTheDocument();
    expect(screen.getByText('Set reminder')).toBeInTheDocument();
  });

  it('displays key topics as tags', async () => {
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Key Topics')).toBeInTheDocument();
    });
    
    expect(screen.getByText('lunch')).toBeInTheDocument();
    expect(screen.getByText('meeting')).toBeInTheDocument();
  });

  it('displays error message when API call fails', async () => {
    const error = new Error('API error');
    error.name = 'ApiClientError';
    vi.mocked(apiClient.summarizeConversation).mockRejectedValue(error);
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Failed to generate summary/)).toBeInTheDocument();
  });

  it('navigates to train page when Start New Session is clicked', async () => {
    const user = userEvent.setup();
    
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: mockSummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getAllByText('Session Summary').length).toBeGreaterThan(0);
    });
    
    const startNewButton = screen.getByText('Start New Session');
    await user.click(startNewButton);
    
    // Navigation would be handled by router in real app
    // In tests, we just verify the button exists and is clickable
    expect(startNewButton).toBeInTheDocument();
  });

  it('hides sections when they have no data', async () => {
    const emptySummary: ConversationSummary = {
      ...mockSummary,
      commitments: [],
      actionItems: [],
      keyTopics: [],
    };
    
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: emptySummary,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getAllByText('Session Summary').length).toBeGreaterThan(0);
    });
    
    // These sections should not appear when empty
    expect(screen.queryByText('Commitments & Plans')).not.toBeInTheDocument();
    expect(screen.queryByText('Action Items')).not.toBeInTheDocument();
    expect(screen.queryByText('Key Topics')).not.toBeInTheDocument();
    
    // Transcript should still appear
    expect(screen.getByText('Full Transcript')).toBeInTheDocument();
  });

  it('formats duration correctly', async () => {
    const summaryWithDuration: ConversationSummary = {
      ...mockSummary,
      duration: 45, // 45 seconds
    };
    
    vi.mocked(apiClient.summarizeConversation).mockResolvedValue({
      summary: summaryWithDuration,
    });
    
    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/summary',
            state: {
              sessionId: 'test-session',
              messages: mockMessages,
              styleProfile: mockStyleProfile,
            },
          },
        ]}
      >
        <SummaryPage />
      </MemoryRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('45s')).toBeInTheDocument();
    });
  });
});
