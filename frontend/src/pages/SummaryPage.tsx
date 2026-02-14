/**
 * Summary page for Conversation Autopilot.
 * 
 * x402.org-inspired LIGHT MODE design with technical data visualization aesthetic.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { summarizeConversation, ApiClientError } from '../api/client';
import type { ConversationSummary, Message, StyleProfile } from '../types';

export default function SummaryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get data from navigation state
  const { sessionId, messages, styleProfile } = location.state as {
    sessionId: string;
    messages: Message[];
    styleProfile: StyleProfile;
  } || {};
  
  const [summary, setSummary] = useState<ConversationSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await summarizeConversation({
        sessionId,
        messages,
        styleProfile,
      });
      setSummary(response.summary);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError('Failed to generate summary. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Redirect if no session data
    if (!sessionId || !messages || !styleProfile) {
      navigate('/');
      return;
    }

    fetchSummary();
  }, [sessionId, messages, styleProfile, navigate]);

  const handleStartNewSession = () => {
    navigate('/train');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-x402-white flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-2 border-x402-accent border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-x402-text-secondary font-mono">Generating summary...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-x402-white flex items-center justify-center px-6">
        <div className="max-w-md w-full card">
          <div className="text-center">
            <svg className="mx-auto h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-bold text-x402-text-primary mb-2">Error</h2>
            <p className="text-x402-text-secondary mb-6">{error}</p>
            <div className="flex gap-3">
              <button
                onClick={fetchSummary}
                className="btn-primary flex-1"
              >
                Retry
              </button>
              <button
                onClick={handleStartNewSession}
                className="btn-secondary flex-1"
              >
                Start New Session
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (minutes === 0) {
      return `${remainingSeconds}s`;
    }
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="min-h-screen bg-x402-white">
      {/* Navigation */}
      <nav className="border-b border-x402-border bg-x402-white">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-xl font-bold text-x402-text-primary">Session Summary</h1>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h2 className="text-display text-x402-text-primary mb-3">
            Session Summary
          </h2>
          <p className="text-x402-text-secondary font-mono">
            Session ID: <span className="text-x402-text-primary">{summary.sessionId.slice(0, 8)}...</span>
          </p>
        </div>

        {/* Statistics Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="stat-card bg-x402-light-gray">
            <p className="stat-label">AI Messages</p>
            <p className="stat-value text-x402-accent">{summary.aiMessageCount}</p>
          </div>
          
          <div className="stat-card bg-x402-light-gray">
            <p className="stat-label">Human Messages</p>
            <p className="stat-value text-x402-accent">{summary.humanMessageCount}</p>
          </div>
          
          <div className="stat-card bg-x402-light-gray">
            <p className="stat-label">Escalations</p>
            <p className="stat-value text-x402-amber">{summary.escalationCount}</p>
          </div>
          
          <div className="stat-card bg-x402-light-gray">
            <p className="stat-label">Duration</p>
            <p className="stat-value text-x402-text-primary">{formatDuration(summary.duration)}</p>
          </div>
        </div>

        {/* Commitments */}
        {summary.commitments.length > 0 && (
          <div className="card mb-6">
            <h3 className="text-2xl font-bold text-x402-text-primary mb-6">
              Commitments & Plans
            </h3>
            <ul className="space-y-3">
              {summary.commitments.map((commitment, index) => (
                <li key={index} className="flex items-start">
                  <svg className="w-5 h-5 text-x402-accent mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-x402-text-secondary leading-relaxed">{commitment}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Items */}
        {summary.actionItems.length > 0 && (
          <div className="card mb-6">
            <h3 className="text-2xl font-bold text-x402-text-primary mb-6">
              Action Items
            </h3>
            <ol className="space-y-3">
              {summary.actionItems.map((item, index) => (
                <li key={index} className="flex items-start">
                  <span className="inline-flex items-center justify-center w-6 h-6 rounded-lg bg-x402-accent text-white text-sm font-bold font-mono mr-3 flex-shrink-0">
                    {index + 1}
                  </span>
                  <span className="text-x402-text-secondary leading-relaxed">{item}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Key Topics */}
        {summary.keyTopics.length > 0 && (
          <div className="card mb-6">
            <h3 className="text-2xl font-bold text-x402-text-primary mb-6">
              Key Topics
            </h3>
            <div className="flex flex-wrap gap-3">
              {summary.keyTopics.map((topic, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-x402-code-bg border border-x402-border text-x402-text-primary text-sm font-mono rounded-lg"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Full Transcript */}
        <div className="card mb-12 bg-x402-light-gray">
          <h3 className="text-2xl font-bold text-x402-text-primary mb-6">
            Full Transcript
          </h3>
          <div className="space-y-4">
            {summary.transcript.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'friend' ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-xl px-4 py-3 rounded-lg ${
                    message.sender === 'friend'
                      ? 'bg-white border border-x402-border text-x402-text-primary'
                      : 'bg-x402-accent text-white'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold font-mono">
                      {message.sender === 'friend' ? 'Friend' : 'You'}
                    </span>
                    {message.isAiGenerated && (
                      <span className="text-xs bg-white text-x402-accent px-2 py-0.5 rounded font-mono">
                        AI
                      </span>
                    )}
                    <span className={`text-xs font-mono ${message.sender === 'friend' ? 'text-x402-text-secondary' : 'text-white text-opacity-70'}`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={handleStartNewSession}
            className="btn-primary flex-1"
          >
            Start New Session
          </button>
          <button
            onClick={() => navigate('/')}
            className="btn-secondary flex-1"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
