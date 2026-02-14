# con.ai 🧠

> **Your second brain for conversations.**
> Never lose a message, file, or context again.

**con.ai** organizes your scattered conversations into intelligent **Spaces**. Forward messages from Telegram, upload files, or paste text, and then **ask questions** to get instant answers based on your data.

![con.ai Demo](https://github.com/user-attachments/assets/placeholder-image-if-you-have-one)

## 🚀 Why con.ai?

We have conversations across WhatsApp, Telegram, Slack, and iMessage. Important details—like the Airbnb code, flight tickets, or project requirements—get buried in the noise.

**con.ai solves this:**
1.  **Create a Space** (e.g., "Trip to Goa", "Q4 Project")
2.  **Dump Context**: Forward messages, upload PDFs/images, paste text.
3.  **Ask Anything**: "What time is our flight?" or "What acts did we book?"

The AI scans your content and gives you an exact answer with sources.

---

## ✨ Key Features

### 🗂️ Organized Spaces
Group related conversations, documents, and notes into dedicated spaces. No more scrolling back 4,000 messages to find one link.

### 🔍 Semantic Search
Search by **meaning**, not just keywords.
- *Query:* "places to eat"
- *Finds:* "We should check out that Italian place using the old recipe..."

### 🤖 RAG Query Engine (Talk to your Data)
Powered by **Llama 3 (via Groq)** and **Vector Search**.
- **User:** "How much do I owe Sarah?"
- **AI:** "You owe Sarah ₹4,500 for the cab and dinner. Source: WhatsApp screenshot from yesterday."

### ✈️ Telegram Integration
A seamless bridge between your chat apps and your second brain.
- **Forward messages** directly to the bot to save them.
- **Send files/photos** to upload them instantly.
- **Ask questions** right from Telegram: `/ask When is the meeting?`

---

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Backend**: Python, Flask
- **AI & RAG**:
    - **LLM**: Llama 3.3 70B (via Groq API)
    - **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
    - **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Integration**: `python-telegram-bot`

---

## ⚡️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/)
- [Telegram Bot Token](https://t.me/botfather) (optional, for bot features)

### 1. Clone & Setup Backend
```bash
git clone https://github.com/Shiva1803/Fantastic4.git
cd Fantastic4/backend

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
GROQ_API_KEY=your_groq_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
FLASK_PORT=5002
```

### 2. Setup Frontend
```bash
cd ../frontend
npm install

# Create .env
echo "VITE_API_URL=http://localhost:5002" > .env
```

### 3. Run It
**Terminal 1 (Backend):**
```bash
cd backend
# Run the API + Telegram Bot
python app.py
# (Or run 'python telegram_bot.py' separately if needed)
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` and start creating spaces!

---

## 🤖 Telegram Bot Commands

Once your bot is running:
- `/start` - Welcome guide
- `/create <name>` - Create a new space
- `/select <name>` - Switch active space
- `/ask <question>` - Ask your space a question
- **Forward any message** - Saves it to your active space

---

## 🤝 Contributing

Built with ❤️ by **Team Diet Coke** for **Fantastic4**.
OPEN SOURCE - MIT LICENSE.
