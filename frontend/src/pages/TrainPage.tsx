/**
 * Training page for Conversation Autopilot.
 * 
 * x402.org-inspired LIGHT MODE design with technical, developer-tool aesthetic.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { trainStyle, ApiClientError } from '../api/client';
import { parseTrainingData, validateTrainingData } from '../api/utils';
import type { StyleProfile } from '../types';

export default function TrainPage() {
  const navigate = useNavigate();
  
  const [trainingText, setTrainingText] = useState('');
  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setStyleProfile(null);

    // Parse and validate training data
    const trainingData = parseTrainingData(trainingText);
    const validation = validateTrainingData(trainingData);
    
    if (!validation.valid) {
      setError(validation.error || 'Invalid training data');
      return;
    }

    // Call API to train
    setIsLoading(true);
    try {
      const response = await trainStyle(trainingData);
      setStyleProfile(response.styleProfile);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = () => {
    if (styleProfile) {
      navigate('/demo', { state: { styleProfile } });
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setTrainingText(text);
    };
    reader.readAsText(file);
  };

  return (
    <div className="min-h-screen bg-x402-white">
      {/* Navigation */}
      <nav className="border-b border-x402-border bg-x402-white">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="text-x402-text-primary hover:text-x402-accent transition-all text-sm font-medium"
            >
              ← Back to Home
            </button>
            <h1 className="text-xl font-bold text-x402-text-primary">Train Your AI</h1>
            <div className="w-24"></div> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h2 className="text-display text-x402-text-primary mb-4">
            Train Your AI
          </h2>
          <p className="text-lg text-x402-text-secondary">
            Paste at least 10 of your messages to train the AI on your texting style
          </p>
        </div>

        {/* Training Form */}
        {!styleProfile && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="card">
              <label htmlFor="training-text" className="block text-sm font-medium text-x402-text-primary mb-3">
                Your Messages <span className="text-x402-text-secondary">(one per line)</span>
              </label>
              <textarea
                id="training-text"
                value={trainingText}
                onChange={(e) => setTrainingText(e.target.value)}
                placeholder="hey how are you&#10;good thanks!&#10;wanna hang out?&#10;sure sounds good&#10;..."
                className="input w-full h-64 font-mono text-sm resize-none bg-x402-code-bg"
                disabled={isLoading}
              />
              <div className="mt-3 flex items-center justify-between">
                <p className="text-sm text-x402-text-secondary">
                  <span className="text-x402-accent font-mono font-bold">{parseTrainingData(trainingText).length}</span> messages entered
                </p>
                <p className="text-sm text-x402-text-secondary">
                  minimum <span className="text-x402-text-primary font-mono font-bold">10</span> required
                </p>
              </div>
            </div>

            {/* File Upload (Optional) */}
            <div className="card">
              <label htmlFor="file-upload" className="block text-sm font-medium text-x402-text-primary mb-3">
                Or upload a text file <span className="text-x402-text-secondary">(optional)</span>
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="block w-full text-sm text-x402-text-secondary
                  file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border file:border-x402-border
                  file:text-sm file:font-medium file:bg-x402-white file:text-x402-text-primary
                  hover:file:bg-x402-light-gray file:transition-colors"
                disabled={isLoading}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="card border-red-500 bg-red-50">
                <p className="text-sm text-red-600 mb-3">{error}</p>
                <button
                  type="button"
                  onClick={handleSubmit}
                  className="text-sm text-red-600 hover:text-red-700 font-medium underline"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Analyzing...
                </span>
              ) : (
                'Analyze My Style'
              )}
            </button>
          </form>
        )}

        {/* Style Profile Results */}
        {styleProfile && (
          <div className="space-y-6 animate-fade-in">
            <div className="card">
              <h2 className="text-2xl font-bold text-x402-text-primary mb-6">
                Your Texting Style Profile
              </h2>
              
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div className="stat-card bg-x402-light-gray">
                  <p className="stat-label">Sentence Length</p>
                  <p className="stat-value text-x402-accent capitalize">
                    {styleProfile.sentenceLength}
                  </p>
                </div>
                
                <div className="stat-card bg-x402-light-gray">
                  <p className="stat-label">Tone</p>
                  <p className="stat-value text-x402-accent capitalize">
                    {styleProfile.tone}
                  </p>
                </div>
                
                <div className="stat-card bg-x402-light-gray">
                  <p className="stat-label">Emoji Frequency</p>
                  <p className="stat-value text-x402-accent">
                    {(styleProfile.emojiFrequency * 100).toFixed(0)}%
                  </p>
                </div>
                
                <div className="stat-card bg-x402-light-gray">
                  <p className="stat-label">Formality Level</p>
                  <p className="stat-value text-x402-accent">
                    {(styleProfile.formalityLevel * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {styleProfile.commonEmojis.length > 0 && (
                <div className="mb-6 pb-6 border-b border-x402-border">
                  <p className="stat-label mb-3">Common Emojis</p>
                  <div className="flex flex-wrap gap-3">
                    {styleProfile.commonEmojis.map((emoji, index) => (
                      <span key={index} className="text-3xl">
                        {emoji}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {styleProfile.commonPhrases.length > 0 && (
                <div>
                  <p className="stat-label mb-3">Common Phrases</p>
                  <div className="flex flex-wrap gap-2">
                    {styleProfile.commonPhrases.slice(0, 10).map((phrase, index) => (
                      <span
                        key={index}
                        className="px-3 py-1.5 bg-x402-code-bg border border-x402-border text-x402-text-primary text-sm font-mono rounded-lg"
                      >
                        {phrase}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleContinue}
              className="btn-primary w-full"
            >
              Continue to Demo →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
