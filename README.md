# Conversation Autopilot

> AI that texts like you when you're busy

## Overview

Conversation Autopilot is an AI-powered application that learns your unique texting style and responds to messages on your behalf. By analyzing your past conversations, it captures your communication patterns—from emoji usage to sentence structure—and generates responses that sound authentically like you.

## The Problem

We're constantly interrupted by messages that require immediate responses, even when we're busy. Missing messages can strain relationships, but context-switching to respond breaks our focus and productivity.

## The Solution

Conversation Autopilot acts as your intelligent texting assistant:
- **Learns your style**: Analyzes 15-20 past messages to understand how you communicate
- **Responds authentically**: Generates messages matching your tone, emoji usage, and quirks
- **Knows its limits**: Detects serious topics and flags when you need to respond personally
- **Keeps you informed**: Provides summaries of what was discussed and commitments made

## Key Features

### 1. Style Training
Upload or paste past text conversations, and the AI analyzes your texting patterns:
- Sentence length and structure
- Emoji frequency and preferences
- Punctuation habits
- Common phrases and expressions
- Tone and formality level

### 2. Autopilot Mode
Enable autopilot and watch the AI respond to incoming messages in real-time, matching your communication style perfectly. Toggle it on/off anytime or take over manually when needed.

### 3. Smart Escalation Detection
The AI knows when conversations need your personal attention:
- Serious questions or emotional topics
- Unfamiliar subjects outside your usual conversations
- Scheduling conflicts or commitments
- Sensitive personal information requests

When detected, it pauses and alerts you with a confidence score and reason.

### 4. Conversation Summaries
After each autopilot session, review:
- Full transcript with AI vs human messages marked
- Commitments and plans made
- Action items identified
- Key topics discussed

## How It Works

### User Flow
1. **Train**: Paste 15-20 of your past text messages
2. **Analyze**: AI extracts your texting style profile
3. **Demo**: Enter simulation mode—type as your friend, AI responds as you
4. **Monitor**: AI flags serious topics for your attention
5. **Review**: See summary of what the AI handled

### Technical Architecture

**Frontend**: Vite + React + TypeScript + Tailwind CSS
- Clean, intuitive interface with four main pages
- Real-time conversation simulation
- Visual feedback for escalations and loading states

**Backend**: Flask (Python)
- RESTful API with three core endpoints
- In-memory caching for performance
- Retry logic and error handling

**AI Integration**: Groq or OpenRouter API
- Style analysis and pattern extraction
- Context-aware response generation
- Escalation detection with confidence scoring

## Tech Stack

- **Frontend**: Vite, React 18, TypeScript, Tailwind CSS
- **Backend**: Flask 3.x, Python 3.10+
- **AI**: Groq API or OpenRouter API
- **State Management**: React hooks
- **Testing**: Vitest, pytest, hypothesis (property-based testing)

## Use Cases

### Personal
- Respond to friends while in meetings or focused work
- Maintain conversations during commutes or workouts
- Handle casual check-ins without breaking concentration

### Professional
- Quick responses to colleagues during deep work sessions
- Maintain communication flow across time zones
- Handle routine inquiries while focusing on priorities

## Demo Script

**Perfect for pitch presentations:**

1. "Here are 20 of my actual text messages" [paste them]
2. "Watch—the AI learned I use '😂' frequently and keep messages short"
3. "Now I'm enabling autopilot. I'll pretend to be my friend:"
4. [Type]: "hey u free for lunch tomorrow?"
5. [AI responds]: "yea probably! what time 😂"
6. [Type]: "your mom is in the hospital right?"
7. [AI shows banner]: "⚠️ SERIOUS TOPIC - You should respond to this yourself"
8. "See? It knows when to hand off. Here's the summary of what it handled."

## Wow Factors

- **Indistinguishable responses**: Side-by-side comparison shows judges can't tell AI from human
- **Live demo capability**: Actually demo it live with audience members texting you
- **Personality insights**: Shows you learned quirks like "you use 'lmao' in 47% of messages"
- **Smart escalation**: The moment AI correctly flags a serious message gets applause

## Build Time

Designed for rapid development: **3-hour MVP build time**
- 25 minutes: Project setup and dependencies
- 60 minutes: Backend services and API endpoints
- 110 minutes: Frontend pages and components
- 40 minutes: Testing and polish

## Future Enhancements

- **Multiple profiles**: Different texting styles for different contacts (casual with friends, formal with boss)
- **Calendar integration**: Check availability before making plans
- **Browser extension**: Works with real messaging apps (iMessage, WhatsApp, etc.)
- **Learning mode**: Continuously improves by observing your corrections

## Why This Matters

In a world of constant connectivity, Conversation Autopilot gives you back control over your attention while maintaining your relationships. It's not about replacing human connection—it's about protecting your focus for what matters most while staying present for the people you care about.

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Groq or OpenRouter API key

### Installation

**Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend Setup**
```bash
cd frontend
npm install
```

### Configuration

Create `.env` files:

**Backend** (`backend/.env`):
```
GROQ_API_KEY=your-api-key-here
# OR
OPENROUTER_API_KEY=your-api-key-here
FLASK_ENV=development
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=http://localhost:5000
```

### Running the Application

**Start Backend**
```bash
cd backend
python app.py
```

**Start Frontend**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to use the application.

## Testing

**Backend Tests**
```bash
cd backend
pytest
```

**Frontend Tests**
```bash
cd frontend
npm test
```

## Project Structure

```
conversation-autopilot/
├── backend/
│   ├── api/              # Flask routes
│   ├── services/         # Business logic
│   │   ├── style_analyzer.py
│   │   ├── response_generator.py
│   │   ├── escalation_detector.py
│   │   └── conversation_summarizer.py
│   ├── models/           # Data models
│   ├── tests/            # Backend tests
│   └── app.py            # Flask application
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages
│   │   ├── components/   # Reusable components
│   │   ├── api/          # API client
│   │   └── types/        # TypeScript interfaces
│   └── tests/            # Frontend tests
└── README.md
```

## License

MIT License - feel free to use this project for your hackathon or personal projects!

## Contributing

This is a hackathon project, but contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Acknowledgments

Built with modern web technologies and AI capabilities to solve a real problem we all face: staying connected without sacrificing focus.

---

**Built for hackathons. Designed for real life. Powered by AI.**
