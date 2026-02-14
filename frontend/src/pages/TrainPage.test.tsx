/**
 * Unit tests for TrainPage component.
 * 
 * Tests training data validation, API integration, and navigation.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import TrainPage from './TrainPage';
import * as apiClient from '../api/client';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock API client
vi.mock('../api/client', () => ({
  trainStyle: vi.fn(),
  ApiClientError: class ApiClientError extends Error {
    constructor(message: string, public statusCode: number) {
      super(message);
      this.name = 'ApiClientError';
    }
  },
}));

describe('TrainPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the training page with form', () => {
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    // Check for heading (there are multiple, use getAllByText)
    const headings = screen.getAllByText('Train Your AI');
    expect(headings.length).toBeGreaterThan(0);
    expect(screen.getByLabelText(/Your Messages/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Analyze My Style/i })).toBeInTheDocument();
  });

  it('shows message count as user types', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const textarea = screen.getByLabelText(/Your Messages/i);
    
    // Initially 0 messages (text is split across elements)
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('messages entered')).toBeInTheDocument();
    
    // Type some messages
    await user.type(textarea, 'hey\nhow are you\ngood thanks');
    
    // Should show 3 messages
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('shows error when submitting with insufficient data (< 10 messages)', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const textarea = screen.getByLabelText(/Your Messages/i);
    const submitButton = screen.getByRole('button', { name: /Analyze My Style/i });
    
    // Enter only 3 messages
    await user.type(textarea, 'hey\nhow are you\ngood thanks');
    await user.click(submitButton);
    
    // Should show error
    await waitFor(() => {
      expect(screen.getByText(/Insufficient training data/i)).toBeInTheDocument();
    });
  });

  it('calls API and displays style profile on successful training', async () => {
    const user = userEvent.setup();
    
    const mockStyleProfile = {
      sentenceLength: 'short' as const,
      emojiFrequency: 0.8,
      commonEmojis: ['😊', '👍'],
      punctuationStyle: 'minimal',
      tone: 'casual' as const,
      commonPhrases: ['hey', 'cool'],
      formalityLevel: 0.2,
      analysisTimestamp: '2024-01-01T00:00:00Z',
    };
    
    vi.mocked(apiClient.trainStyle).mockResolvedValue({
      styleProfile: mockStyleProfile,
      userId: 'test-user',
    });
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const textarea = screen.getByLabelText(/Your Messages/i);
    const submitButton = screen.getByRole('button', { name: /Analyze My Style/i });
    
    // Enter 10 messages
    const messages = Array.from({ length: 10 }, (_, i) => `message ${i + 1}`).join('\n');
    await user.type(textarea, messages);
    await user.click(submitButton);
    
    // Wait for API call and profile display
    await waitFor(() => {
      expect(screen.getByText('Your Texting Style Profile')).toBeInTheDocument();
    });
    
    // Check profile details are displayed
    expect(screen.getByText('short')).toBeInTheDocument();
    expect(screen.getByText('casual')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument(); // emoji frequency
    expect(screen.getByText('20%')).toBeInTheDocument(); // formality level
  });

  it('displays error message when API call fails', async () => {
    const user = userEvent.setup();
    
    vi.mocked(apiClient.trainStyle).mockRejectedValue(
      new apiClient.ApiClientError('API Error', 500)
    );
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const textarea = screen.getByLabelText(/Your Messages/i);
    const submitButton = screen.getByRole('button', { name: /Analyze My Style/i });
    
    // Enter 10 messages
    const messages = Array.from({ length: 10 }, (_, i) => `message ${i + 1}`).join('\n');
    await user.type(textarea, messages);
    await user.click(submitButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('navigates to /demo when clicking Continue button', async () => {
    const user = userEvent.setup();
    
    const mockStyleProfile = {
      sentenceLength: 'medium' as const,
      emojiFrequency: 0.5,
      commonEmojis: [],
      punctuationStyle: 'standard',
      tone: 'casual' as const,
      commonPhrases: [],
      formalityLevel: 0.5,
      analysisTimestamp: '2024-01-01T00:00:00Z',
    };
    
    vi.mocked(apiClient.trainStyle).mockResolvedValue({
      styleProfile: mockStyleProfile,
      userId: 'test-user',
    });
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const textarea = screen.getByLabelText(/Your Messages/i);
    const submitButton = screen.getByRole('button', { name: /Analyze My Style/i });
    
    // Enter and submit training data
    const messages = Array.from({ length: 10 }, (_, i) => `message ${i + 1}`).join('\n');
    await user.type(textarea, messages);
    await user.click(submitButton);
    
    // Wait for profile to appear
    await waitFor(() => {
      expect(screen.getByText('Your Texting Style Profile')).toBeInTheDocument();
    });
    
    // Click Continue button
    const continueButton = screen.getByRole('button', { name: /Continue to Demo/i });
    await user.click(continueButton);
    
    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/demo', {
      state: { styleProfile: mockStyleProfile },
    });
  });

  it('allows file upload to populate textarea', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const fileInput = screen.getByLabelText(/Or upload a text file/i);
    const textarea = screen.getByLabelText(/Your Messages/i) as HTMLTextAreaElement;
    
    // Create a mock file
    const fileContent = 'message 1\nmessage 2\nmessage 3';
    const file = new File([fileContent], 'messages.txt', { type: 'text/plain' });
    
    // Upload file
    await user.upload(fileInput, file);
    
    // Wait for file to be read and textarea to be populated
    await waitFor(() => {
      expect(textarea.value).toBe(fileContent);
    });
  });

  it('navigates back to home when clicking back button', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <TrainPage />
      </BrowserRouter>
    );

    const backButton = screen.getByText(/Back to Home/i);
    await user.click(backButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
});
