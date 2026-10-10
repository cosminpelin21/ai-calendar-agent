# 📅 AI Calendar Agent

A conversational AI agent that manages your **Google Calendar** using natural language. Tell it what to schedule, move or delete, and it does it for you.

> 🚧 **Status: work in progress.** This is my first AI agent project and it is still under active development. It works for the basic flows, but it has bugs. Expect rough edges.

> 🤖 **Built with AI assistance.** I used AI tools throughout this project: for design decisions, writing and refactoring code, and debugging.

---

## ✨ Features

- 🗓️ **Manage events**: create, update, delete and list events in Google Calendar.
- 🔍 **Check availability**: ask "when am I free tomorrow?" and get the free time slots of a day.
- 💬 **Natural language**: "move the dentist to 16:00", "add gym tomorrow at 18:30 for 45 minutes".
- 🧠 **Conversation memory**: follow-ups like "at 17:15" or "move it to 12:30" continue the task in progress.
- 🏠 **Runs locally**: uses a local LLM through [Ollama](https://ollama.com/), so your prompts stay on your machine.
- 🔐 **Google OAuth 2.0**: official API credentials, stored locally.

---

## 🧱 Tech Stack

| Part | Tool |
|---|---|
| LLM | Llama 3.1 via Ollama (configurable) |
| Agent framework | LangChain (`create_agent`) + `langchain-ollama` |
| UI | Streamlit chat interface |
| Calendar | Google Calendar API |
| Language | Python 3.10+ |

---

## 🧠 How It Works

The agent has five tools:

| Tool | What it does |
|---|---|
| `list_calendar_events` | Lists events for a day or a date range |
| `find_free_slots` | Calculates free time slots on a given day |
| `add_calendar_event` | Creates a new event |
| `update_calendar_event` | Changes the title, date, time or duration of an event |
| `delete_calendar_event` | Deletes an event |

Design notes (lessons learned so far):

- **Small local models make mistakes**, so critical logic lives in code, not in the prompt. For example, the tools compute end times, preserve the original date when only the time changes, and calculate free slots.
- **Guards in code**: `add_calendar_event` refuses to run if the user never wrote a start time, so the agent asks instead of inventing one.
- **Events are found by title**, not by ID. The tools look the event up themselves and ask the user when several events match.
- The system prompt is rebuilt on every message so "today" and "tomorrow" are always correct.

---

## 📁 Project Structure

```text
ai-calendar-agent/
├── src/
│   ├── tools/
│   │   └── google_calendar.py   # Google Calendar tools used by the agent
│   ├── agent.py                 # Agent setup and system prompt
│   ├── calendar_utils.py        # Google API auth & service helper
│   ├── config.py                # Config & environment variables loader
│   ├── main.py                  # Streamlit app (entry point)
│   └── models.py                # Data models & Pydantic schemas
├── .env                         # Environment variables (private)
├── credentials.json             # Google OAuth 2.0 credentials (private)
├── token.json                   # OAuth session token (auto-generated, private)
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com/) installed and running
- A Google Cloud account with the **Google Calendar API** enabled

### 2. Clone and install

```bash
git clone https://github.com/cosminpelin21/ai-calendar-agent.git
cd ai-calendar-agent

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Download a model

```bash
ollama pull llama3.1
```

Llama 3.1 8B works but is not the most reliable at tool calling. If you have enough VRAM, `qwen2.5:14b` is noticeably more stable.

### 4. Google credentials

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and enable the **Google Calendar API**.
2. Create an **OAuth 2.0 Client ID** (application type: *Desktop app*).
3. Download the JSON file and save it as `credentials.json` in the project root.

### 5. Environment variables

Create a `.env` file in the project root (adjust the names to match your `config.py`):

```env
OLLAMA_MODEL=llama3.1
```

---

## 💻 Running the App

```bash
streamlit run src/main.py
```

On the first run a browser window opens asking for permission to access your Google Calendar. After you accept, a `token.json` file is created and reused for later sessions.


---

## 🐛 Known Issues

This is an early version. Known problems:

- **Invented or missing details**: the model sometimes guesses a start time or misreads a follow-up, especially on long conversations. Guards in code catch the most common cases, but not all.
- **Tool calls printed as text**: Llama 3.1 sometimes writes a tool call as JSON in the chat instead of executing it. A fallback in `main.py` runs it, but it is a workaround.
- **Time check is approximate**: the "did the user give a time?" guard looks for a time in the last 3 user messages, not specifically for the event being created.
- **No overlap warning**: adding an event at a busy time does not warn about the conflict.
- **Hardcoded timezone**: `Europe/Bucharest`.
- **Destructive actions**: the agent can delete real events from your calendar. Test with a separate calendar if you can.


---

## 🤝 Contributing

Issues and suggestions are welcome, especially from people who have built agents before. This is a learning project, so feedback on the design is appreciated.

---
