/**
 * Demo page for Conversation Autopilot.
 * 
 * x402.org-inspired LIGHT MODE chat interface with technical, developer-tool aesthetic.
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { generateResponse, ApiClientError } from '../api/client';
import { generateSessionId, createMessage } from '../api/utils';
import type { StyleProfile, Message, EscalationResult } from '../types';

export default function DemoPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Get style profile from navigation state
  const styleProfile = location.state?.styleProfile as StyleProfile | undefined;
  
  // State management
  const [sessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [autopilotEnabled, setAutopilotEnabled] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [escalation, setEscalation] = useState<EscalationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);

  // Redirect if no style profile
  useEffect(() => {
    if (!styleProfile) {
      navigate('/train');
    }
  }, [styleProfile, navigate]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentInput.trim() || !styleProfile) return;
    
    setError(null);
    
    // Add friend's message to conversation
    const friendMessage = createMessage('friend', currentInput.trim());
    const updatedMessages = [...messages, friendMessage];
    setMessages(updatedMessages);
    setCurrentInput('');

    // If autopilot is enabled and no unacknowledged escalation, generate response
    if (autopilotEnabled && !escalation) {
      await generateAIResponse(updatedMessages, friendMessage.text);
    }
  };

  const generateAIResponse = async (conversationHistory: Message[], incomingMessage: string) => {
    if (!styleProfile) return;
    
    setIsGenerating(true);
    
    try {
      const response = await generateResponse({
        sessionId,
        styleProfile,
        conversationHistory,
        incomingMessage,
        autopilotEnabled: true,
      });

      // Check for escalation
      if (response.escalation.detected) {
        setEscalation(response.escalation);
        setAutopilotEnabled(false); // Pause autopilot
      }

      // Add AI response if generated
      if (response.response) {
        const aiMessage = createMessage('ai', response.response);
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
        setLastFailedMessage(incomingMessage);
      } else {
        setError('Failed to generate response. Please try again.');
        setLastFailedMessage(incomingMessage);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRetryGeneration = async () => {
    if (lastFailedMessage) {
      setError(null);
      await generateAIResponse(messages, lastFailedMessage);
    }
  };

  const handleTakeover = () => {
    // Takeover allows manual input - autopilot will resume after sending
    setEscalation(null);
  };

  const handleAcknowledgeEscalation = () => {
    setEscalation(null);
    // User can choose to re-enable autopilot or continue manually
  };

  const handleEndSession = () => {
    navigate('/summary', { 
      state: { 
        sessionId, 
        messages,
        styleProfile 
      } 
    });
  };

  if (!styleProfile) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-x402-white flex flex-col">
      {/* Header */}
      <div className="border-b border-x402-border bg-x402-light-gray">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-x402-text-primary mb-1">
                Conversation Demo
              </h1>
              <p className="text-sm text-x402-text-secondary font-mono">
                Session: {sessionId.slice(0, 8)}...
              </p>
            </div>
            
            {/* Autopilot Toggle */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <span className="text-sm font-medium text-x402-text-primary">
                  Autopilot
                </span>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={autopilotEnabled}
                    onChange={(e) => setAutopilotEnabled(e.target.checked)}
                    className="sr-only peer"
                    disabled={isGenerating}
                  />
                  <div className="w-11 h-6 bg-x402-border rounded-full peer 
                    peer-checked:bg-x402-accent peer-disabled:opacity-50
                    peer-focus-visible:ring-2 peer-focus-visible:ring-x402-accent peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-x402-white
                    transition-colors">
                    <div className="absolute top-0.5 left-0.5 bg-white w-5 h-5 rounded-full transition-transform
                      peer-checked:translate-x-5"></div>
                  </div>
                </div>
              </label>
              
              <button
                onClick={handleEndSession}
                className="btn-secondary text-sm"
              >
                End Session
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Escalation Banner */}
      {escalation && (
        <div className="border-b border-x402-amber bg-amber-50 fade-in">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-x402-amber" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="font-semibold text-x402-amber">
                    Human Attention Needed
                  </span>
                  <span className="text-sm text-x402-amber font-mono">
                    Confidence: {escalation.confidenceScore}%
                  </span>
                </div>
                <p className="text-sm text-x402-text-secondary">
                  {escalation.reason}
                </p>
              </div>
              <button
                onClick={handleAcknowledgeEscalation}
                className="px-4 py-2 bg-x402-amber text-white text-sm font-medium rounded-lg hover:bg-opacity-90 transition-all w-full sm:w-auto"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="border-b border-red-500 bg-red-50 fade-in">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
              <p className="text-sm text-red-600 flex-1">{error}</p>
              {lastFailedMessage && (
                <button
                  onClick={handleRetryGeneration}
                  disabled={isGenerating}
                  className="px-4 py-2 bg-red-500 hover:bg-red-600 disabled:bg-x402-text-secondary text-white text-sm font-medium rounded-lg transition-colors w-full sm:w-auto"
                >
                  Retry
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Conversation Area */}
      <div className="flex-1 overflow-y-auto px-6 py-8 bg-x402-light-gray">
        <div className="max-w-7xl mx-auto">
          {messages.length === 0 && (
            <div className="text-center py-20">
              <p className="text-x402-text-secondary text-lg mb-2">
                Start a conversation by typing a message as the Friend
              </p>
              <p className="text-x402-text-secondary text-sm">
                The AI will respond automatically when autopilot is enabled
              </p>
            </div>
          )}
          
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex fade-in ${message.sender === 'friend' ? 'justify-start' : 'justify-end'}`}
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
            
            {isGenerating && (
              <div className="flex justify-end animate-fade-in">
                <div className="max-w-xl px-4 py-3 rounded-lg bg-x402-accent text-white">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-sm font-mono">Generating response...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-x402-border bg-white">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <form onSubmit={handleSendMessage} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder="Type a message as the Friend..."
              className="input flex-1"
              disabled={isGenerating}
            />
            
            <div className="flex gap-3">
              {escalation && (
                <button
                  type="button"
                  onClick={handleTakeover}
                  className="px-6 py-2 bg-x402-amber text-white font-medium rounded-lg hover:bg-opacity-90 transition-all flex-1 sm:flex-none"
                >
                  Take Over
                </button>
              )}
              
              <button
                type="submit"
                disabled={isGenerating || !currentInput.trim()}
                className="btn-primary flex-1 sm:flex-none"
              >
                Send
              </button>
            </div>
          </form>
          
          <p className="text-xs text-x402-text-secondary mt-3 font-mono">
            {autopilotEnabled && !escalation
              ? '● Autopilot active - AI will respond automatically'
              : escalation
              ? '⚠ Autopilot paused - acknowledge escalation or take over'
              : '○ Autopilot disabled - responses will not be generated'}
          </p>
        </div>
      </div>
    </div>
  );
}
