/**
 * Landing page for Conversation Autopilot.
 * 
 * x402.org-inspired LIGHT MODE design with minimal, clean aesthetic.
 */

import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function LandingPage() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/spaces');
  };

  useEffect(() => {
    // Smooth scroll animations
    const ctx = gsap.context(() => {
      // Hero fade in
      gsap.from('.hero-content', {
        opacity: 0,
        y: 40,
        duration: 1,
        ease: 'power3.out',
      });

      // Stats section
      gsap.from('.stat-item', {
        scrollTrigger: {
          trigger: '.stats-section',
          start: 'top 80%',
        },
        opacity: 0,
        y: 30,
        stagger: 0.1,
        duration: 0.8,
        ease: 'power2.out',
      });

      // Feature cards
      gsap.from('.feature-card', {
        scrollTrigger: {
          trigger: '.features-section',
          start: 'top 70%',
        },
        opacity: 0,
        y: 40,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power2.out',
      });

      // Comparison cards
      gsap.from('.comparison-card', {
        scrollTrigger: {
          trigger: '.comparison-section',
          start: 'top 70%',
        },
        opacity: 0,
        x: (index) => (index === 0 ? -40 : 40),
        stagger: 0.2,
        duration: 0.8,
        ease: 'power2.out',
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <div className="min-h-screen bg-x402-white">
      {/* Navigation */}
      <nav className="bg-black border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-white">con.ai</h1>
            <div className="flex items-center gap-6">
              <button
                onClick={() => navigate('/spaces')}
                className="text-white hover:text-gray-300 transition-all text-sm font-medium"
              >
                Spaces
              </button>
              <button
                onClick={handleGetStarted}
                className="bg-white text-black px-4 py-1.5 rounded-lg hover:bg-gray-200 transition-all text-sm font-medium"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with iPhone mockup */}
      <section className="max-w-7xl mx-auto px-6 py-12 md:py-16">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          {/* Left: Hero Content */}
          <div className="hero-content">
            <h2 className="text-5xl md:text-6xl text-x402-text-primary mb-4 leading-tight font-bold">
              AI that remembers your conversations
            </h2>
            <p className="text-lg text-x402-text-secondary mb-6 leading-relaxed">
              Save messages and files to organized spaces. Ask questions and get instant answers from your conversation history.
            </p>
            <button
              onClick={handleGetStarted}
              className="btn-primary text-lg"
            >
              Train Your AI
            </button>
          </div>

          {/* Right: iPhone Mockup with Chat */}
          <div className="relative flex justify-center md:justify-end">
            {/* iPhone Frame */}
            <div className="relative w-[280px] h-[570px] bg-black rounded-[3rem] p-3 shadow-2xl">
              {/* Notch */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-black rounded-b-3xl z-10"></div>

              {/* Screen */}
              <div className="w-full h-full bg-white rounded-[2.5rem] overflow-hidden">
                {/* Status Bar */}
                <div className="bg-x402-light-gray px-6 py-3 flex items-center justify-between text-xs">
                  <span className="font-semibold">9:41</span>
                  <div className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                    </svg>
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M17.778 8.222c-4.296-4.296-11.26-4.296-15.556 0A1 1 0 01.808 6.808c5.076-5.077 13.308-5.077 18.384 0a1 1 0 01-1.414 1.414zM14.95 11.05a7 7 0 00-9.9 0 1 1 0 01-1.414-1.414 9 9 0 0112.728 0 1 1 0 01-1.414 1.414zM12.12 13.88a3 3 0 00-4.242 0 1 1 0 01-1.415-1.415 5 5 0 017.072 0 1 1 0 01-1.415 1.415zM9 16a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clipRule="evenodd" />
                    </svg>
                    <svg className="w-5 h-3" fill="currentColor" viewBox="0 0 24 12">
                      <rect x="0" y="3" width="18" height="6" rx="2" />
                      <rect x="19" y="4" width="3" height="4" rx="1" />
                      <rect x="22" y="5" width="2" height="2" />
                    </svg>
                  </div>
                </div>

                {/* Chat Header */}
                <div className="bg-x402-light-gray px-4 py-3 border-b border-x402-border flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-x402-accent flex items-center justify-center text-white text-sm font-bold">
                    J
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">John</div>
                    <div className="text-xs text-x402-text-secondary">Active now</div>
                  </div>
                </div>

                {/* Chat Messages */}
                <div className="p-4 space-y-3 h-[420px] overflow-y-auto bg-white">
                  {/* Incoming message */}
                  <div className="flex justify-start animate-fade-in">
                    <div className="bg-x402-light-gray rounded-2xl rounded-tl-sm px-4 py-2 max-w-[200px]">
                      <p className="text-sm">Hey! Want to grab coffee later?</p>
                      <span className="text-xs text-x402-text-secondary">10:30 AM</span>
                    </div>
                  </div>

                  {/* Typing indicator (animated) */}
                  <div className="flex justify-end typing-indicator" style={{ animationDelay: '1s' }}>
                    <div className="bg-x402-accent text-white rounded-2xl rounded-tr-sm px-4 py-3 flex items-center gap-1">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms', animationDuration: '1.4s' }}></div>
                        <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '200ms', animationDuration: '1.4s' }}></div>
                        <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '400ms', animationDuration: '1.4s' }}></div>
                      </div>
                    </div>
                  </div>

                  {/* Outgoing message (AI) - fades in after typing */}
                  <div className="flex justify-end message-appear" style={{ animationDelay: '3s' }}>
                    <div className="bg-x402-accent text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[200px]">
                      <p className="text-sm">Sure! How about 3pm at the usual spot?</p>
                      <div className="flex items-center justify-end gap-1 mt-1">
                        <span className="text-xs opacity-70">10:31 AM</span>
                        <span className="text-xs">✓✓</span>
                      </div>
                    </div>
                  </div>

                  {/* Incoming message */}
                  <div className="flex justify-start" style={{ animationDelay: '4s', animation: 'fadeIn 0.5s ease-in forwards', opacity: 0 }}>
                    <div className="bg-x402-light-gray rounded-2xl rounded-tl-sm px-4 py-2 max-w-[200px]">
                      <p className="text-sm">Perfect! See you then</p>
                      <span className="text-xs text-x402-text-secondary">10:32 AM</span>
                    </div>
                  </div>

                  {/* AI Badge */}
                  <div className="flex justify-center" style={{ animationDelay: '4.5s', animation: 'fadeIn 0.5s ease-in forwards', opacity: 0 }}>
                    <div className="bg-x402-code-bg px-3 py-1 rounded-full text-xs text-x402-text-secondary flex items-center gap-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 7H7v6h6V7z" />
                        <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                      </svg>
                      <span>AI responded</span>
                    </div>
                  </div>
                </div>

                {/* Input Bar */}
                <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-x402-border p-3">
                  <div className="flex items-center gap-2 bg-x402-light-gray rounded-full px-4 py-2">
                    <input
                      type="text"
                      placeholder="Message..."
                      className="flex-1 bg-transparent text-sm outline-none"
                      disabled
                    />
                    <svg className="w-5 h-5 text-x402-text-secondary" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .typing-indicator {
          animation: fadeIn 0.5s ease-in forwards;
          opacity: 0;
        }

        .message-appear {
          animation: fadeIn 0.5s ease-in forwards;
          opacity: 0;
        }
      `}</style>

      {/* Divider */}
      <div className="max-w-7xl mx-auto px-6">
        <hr className="border-black" />
      </div>

      {/* How It Works - Visual Learning Demo */}
      <section className="bg-white">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid md:grid-cols-2 gap-20 items-center">
            {/* Left: Visual Demo - Conversation Spaces */}
            <div className="space-y-5">
              <div className="text-xs font-semibold text-x402-text-secondary mb-2 uppercase tracking-wide flex items-center gap-2">
                <span className="w-6 h-6 bg-black rounded-md flex items-center justify-center text-white text-[10px] font-bold">#</span>
                Space: Trip Planning
              </div>

              <div className="space-y-3">
                <div className="bg-x402-light-gray rounded-lg px-4 py-3 flex items-start gap-3">
                  <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center shrink-0">
                    <svg className="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-x402-text-primary">Sarah said she booked the Airbnb for Dec 20-27 in Goa. Total was ₹18,500.</p>
                    <p className="text-xs text-x402-text-secondary mt-1">Saved from WhatsApp</p>
                  </div>
                </div>

                <div className="bg-x402-light-gray rounded-lg px-4 py-3 flex items-start gap-3">
                  <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center shrink-0">
                    <svg className="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-x402-text-primary">flight_tickets.pdf</p>
                    <p className="text-xs text-x402-text-secondary mt-1">Uploaded · 2.3 MB</p>
                  </div>
                </div>

                <div className="bg-x402-light-gray rounded-lg px-4 py-3 flex items-start gap-3">
                  <div className="w-7 h-7 bg-gray-200 rounded-full flex items-center justify-center shrink-0">
                    <svg className="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm text-x402-text-primary">Raj confirmed he'll drive us from the airport. Arrives 2pm.</p>
                    <p className="text-xs text-x402-text-secondary mt-1">Saved from iMessage</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 py-3">
                <div className="flex-1 h-px bg-x402-border"></div>
                <span className="text-xs font-semibold text-x402-text-secondary">ASK ANYTHING</span>
                <div className="flex-1 h-px bg-x402-border"></div>
              </div>

              <div className="bg-black border border-gray-800 rounded-lg px-4 py-3">
                <p className="text-xs font-medium text-gray-300 mb-1">Q: How much was the Airbnb?</p>
                <p className="text-sm text-white">Sarah booked it for ₹18,500 for Dec 20-27 in Goa.</p>
                <p className="text-xs text-gray-400 mt-2">Source: WhatsApp message from Sarah</p>
              </div>
            </div>

            {/* Right: Explanation */}
            <div className="space-y-6">
              <h3 className="text-display text-x402-text-primary font-bold">What is <span className="font-black">con.ai</span>?</h3>
              <p className="text-lg text-x402-text-secondary leading-loose">
                con.ai creates <span className="text-x402-text-primary font-semibold">organized spaces for your conversations</span> - save messages, files, and context from different people or topics.
              </p>
              <p className="text-lg text-x402-text-secondary leading-loose">
                When you need info, just ask: <span className="text-x402-text-primary font-semibold">"What did Sarah say about her trip?"</span> or <span className="text-x402-text-primary font-semibold">"What's the total from last month's invoices?"</span>
              </p>
              <p className="text-lg text-x402-text-secondary leading-loose">
                No more scrolling through endless chat history or searching through files. Your AI <span className="text-x402-text-primary font-semibold">remembers everything</span> for you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="bg-x402-light-gray features-section">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <h3 className="text-display text-x402-text-primary mb-12 font-bold text-center">Perfect for</h3>
          <div className="grid md:grid-cols-3 gap-12">
            {/* Long Messages */}
            <div className="feature-card text-center">
              <svg className="w-12 h-12 mb-4 text-x402-text-primary mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <h4 className="text-xl font-bold text-x402-text-primary mb-3">Long Messages</h4>
              <p className="text-x402-text-secondary">
                Save lengthy texts from friends or partners. Ask "What was the main point?" instead of re-reading.
              </p>
            </div>

            {/* Documents & Files */}
            <div className="feature-card text-center">
              <svg className="w-12 h-12 mb-4 text-x402-text-primary mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h4 className="text-xl font-bold text-x402-text-primary mb-3">Documents & Files</h4>
              <p className="text-x402-text-secondary">
                Store invoices, receipts, contracts. Ask "What's the total?" or "When's the deadline?"
              </p>
            </div>

            {/* Conversation History */}
            <div className="feature-card text-center">
              <svg className="w-12 h-12 mb-4 text-x402-text-primary mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h4 className="text-xl font-bold text-x402-text-primary mb-3">Conversation History</h4>
              <p className="text-x402-text-secondary">
                Never forget plans, promises, or important details. Your AI remembers so you don't have to.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 comparison-section">
        <h3 className="text-display text-x402-text-primary mb-12 font-bold text-center">but how <span className="font-black">Con.AI</span> works</h3>
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Step 1: Save */}
          <div className="relative comparison-card p-[3px] bg-gradient-to-r from-green-500 via-emerald-400 to-green-500 rounded-lg animate-gradient-x">
            <div className="relative card border-0 shadow-lg bg-white">
              <h4 className="text-xl font-bold text-x402-text-primary mb-6">1. Save to Spaces</h4>
              <ul className="space-y-4">
                <li className="flex items-start">
                  <span className="text-x402-accent mr-3 font-bold">→</span>
                  <span className="text-x402-text-primary">Create spaces: "Personal", "Work", "Friends"</span>
                </li>
                <li className="flex items-start">
                  <span className="text-x402-accent mr-3 font-bold">→</span>
                  <span className="text-x402-text-primary">Save messages, files, or entire conversations</span>
                </li>
                <li className="flex items-start">
                  <span className="text-x402-accent mr-3 font-bold">→</span>
                  <span className="text-x402-text-primary">AI indexes everything for instant recall</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Step 2: Ask */}
          <div className="card comparison-card">
            <h4 className="text-xl font-bold text-x402-text-secondary mb-6">2. Ask Questions</h4>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className="text-x402-text-secondary mr-3">?</span>
                <span className="text-x402-text-secondary">"What did Sarah say about her trip?"</span>
              </li>
              <li className="flex items-start">
                <span className="text-x402-text-secondary mr-3">?</span>
                <span className="text-x402-text-secondary">"What's the invoice total from Mike?"</span>
              </li>
              <li className="flex items-start">
                <span className="text-x402-text-secondary mr-3">?</span>
                <span className="text-x402-text-secondary">"When did we agree to meet?"</span>
              </li>
              <li className="flex items-start">
                <span className="text-x402-text-secondary mr-3">?</span>
                <span className="text-x402-text-secondary">"Summarize yesterday's conversation"</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <style>{`
        @keyframes gradient-x {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }

        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 3s ease infinite;
        }
      `}</style>

      {/* CTA Footer */}
      <section className="bg-x402-light-gray relative overflow-hidden">
        {/* Dotted pattern with horizontal fade - contained within section */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="w-full h-full dotted-pattern-large opacity-60" style={{
            maskImage: 'linear-gradient(to right, rgba(0,0,0,0.8), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.8))',
            WebkitMaskImage: 'linear-gradient(to right, rgba(0,0,0,0.8), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.8))'
          }}></div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-20 text-center relative z-10">
          <h3 className="text-display text-x402-text-primary mb-6 italic" style={{ fontFamily: 'Georgia, "Times New Roman", serif' }}>Ready to get started?</h3>
          <p className="text-xl text-x402-text-secondary mb-8">
            It only takes 1 minute to create your space
          </p>
          <button
            onClick={handleGetStarted}
            className="btn-primary text-lg"
          >
            Take me there
          </button>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="bg-white">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <h3 className="text-display text-x402-text-primary mb-12 font-bold">FAQs</h3>

          <div className="space-y-0">
            {/* FAQ Item 1 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">What are "spaces" and how do they work?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                Spaces are organized folders for different contexts - like "Personal", "Work", or "Friends". You save messages, files, or conversations to a space, and the AI indexes everything. Later, you can ask questions and get instant answers from that specific context without scrolling through chat history.
              </div>
            </details>

            {/* FAQ Item 2 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">What types of files can I save?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                You can save text messages, PDFs, images, documents, invoices, receipts, contracts - basically anything you receive in conversations. The AI can read and understand the content, so you can ask questions about it later without having to open and search through files manually.
              </div>
            </details>

            {/* FAQ Item 3 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">How does the AI remember everything?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                When you save content to a space, con.ai processes and indexes it using AI. It understands the context, key information, and relationships between different pieces of content. When you ask a question, it searches through the relevant space and provides accurate answers based on what you've saved.
              </div>
            </details>

            {/* FAQ Item 4 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">What about privacy and data security?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                Your privacy is our priority. Training data is processed securely and used only to create your personalized style profile. We don't store your messages permanently or share them with third parties. You maintain full control over your data and can delete your profile at any time.
              </div>
            </details>

            {/* FAQ Item 5 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">How accurate are the AI-generated responses?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                con.ai achieves high accuracy by analyzing multiple aspects of your communication style including sentence length, tone, formality level, emoji usage, and common phrases. The more training data you provide, the better it understands your unique voice. Most users find the responses indistinguishable from their own writing.
              </div>
            </details>

            {/* FAQ Item 6 */}
            <details className="group border-b border-x402-border">
              <summary className="flex items-center justify-between py-6 cursor-pointer list-none">
                <span className="text-lg font-semibold text-x402-text-primary">What is escalation detection?</span>
                <span className="text-3xl text-x402-text-primary group-open:rotate-45 transition-transform">+</span>
              </summary>
              <div className="pb-6 text-x402-text-secondary leading-relaxed">
                Escalation detection is a smart feature that identifies when a conversation requires your personal attention. It automatically detects serious questions, emotional distress, sensitive topics, or urgent matters and pauses autopilot mode to alert you. This ensures important conversations never slip through the cracks.
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* Footer - EXACT x402.org style */}
      <footer className="bg-black text-white relative overflow-hidden min-h-[400px] flex flex-col">
        {/* MASSIVE background text exactly like x402 - "con.ai" */}
        <div className="absolute inset-0 flex items-center justify-center opacity-[0.08] pointer-events-none select-none overflow-hidden">
          <div
            className="font-bold leading-none tracking-tighter whitespace-nowrap"
            style={{
              fontSize: 'clamp(12rem, 35vw, 32rem)',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontWeight: '900'
            }}
          >
            con.ai
          </div>
        </div>

        {/* Top navigation bar */}
        <div className="border-b border-gray-800 relative z-10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M13.6823 10.6218L20.2391 3H18.6854L12.9921 9.61788L8.44486 3H3.2002L10.0765 13.0074L3.2002 21H4.75404L10.7663 14.0113L15.5685 21H20.8131L13.6819 10.6218H13.6823ZM11.5541 13.0956L10.8574 12.0991L5.31391 4.16971H7.70053L12.1742 10.5689L12.8709 11.5655L18.6861 19.8835H16.2995L11.5541 13.096V13.0956Z" />
                </svg>
              </a>
            </div>
            <p className="text-sm text-gray-400">built by team Diet Coke for Fantastic4</p>
          </div>
        </div>

        {/* Main footer content */}
        <div className="max-w-7xl mx-auto px-6 py-16 relative z-10 flex-1 flex items-end">
          <div className="text-xs text-gray-500 leading-relaxed max-w-4xl">
            While con.ai is an open and neutral standard, this website is maintained by the con.ai team.
            By using this site, you agree to be bound by our{' '}
            <a href="#" className="text-blue-500 hover:text-blue-400 transition-colors">Terms of Service</a>
            {' '}and{' '}
            <a href="#" className="text-blue-500 hover:text-blue-400 transition-colors">Privacy Policy</a>.
          </div>
        </div>
      </footer>
    </div>
  );
}
