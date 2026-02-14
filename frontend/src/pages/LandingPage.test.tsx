/**
 * Unit tests for LandingPage component.
 * 
 * Tests navigation behavior and content display with x402-inspired design.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import LandingPage from './LandingPage';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('LandingPage', () => {
  it('renders the landing page with hero content', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    // Check for main heading in nav
    expect(screen.getByText('Conversation Autopilot')).toBeInTheDocument();
    
    // Check for hero description
    expect(screen.getByText(/Your AI-powered texting assistant/i)).toBeInTheDocument();
    
    // Check for CTA buttons (there are multiple)
    const buttons = screen.getAllByRole('button', { name: /Train Your AI/i });
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('displays feature cards with new design', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    // Check for new feature headings
    expect(screen.getByText('Zero Setup')).toBeInTheDocument();
    expect(screen.getByText('Instant Training')).toBeInTheDocument();
    expect(screen.getByText('Smart Escalation')).toBeInTheDocument();
  });

  it('navigates to /train when clicking "Train Your AI" button', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    // Find and click the first button (hero section)
    const buttons = screen.getAllByRole('button', { name: /Train Your AI/i });
    await user.click(buttons[0]);

    // Verify navigation was called with correct path
    expect(mockNavigate).toHaveBeenCalledWith('/train');
  });

  it('displays comparison section', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    // Check for comparison section headings
    expect(screen.getByText('Old way vs New way')).toBeInTheDocument();
    expect(screen.getByText('Manual Texting')).toBeInTheDocument();
    expect(screen.getByText('With Autopilot')).toBeInTheDocument();
  });
});
