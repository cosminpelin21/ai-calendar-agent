```markdown
# 📅 AI Calendar Agent

An intelligent AI agent powered by LLMs that interacts with **Google Calendar** to manage events, check availability, and automate calendar tasks using natural language.

---

## 📋 Features

* 🗓️ **Manage Events**: Create, update, delete, and list events in Google Calendar.
* 🔍 **Check Availability**: Search free/busy slots across your schedule.
* 💬 **Natural Language Interface**: Interact with your calendar using conversational prompts.
* 🔐 **Secure OAuth 2.0 Auth**: Safe integration using official Google API credentials.

---

## 🛠️ Project Structure

```text
ai-calendar-agent/
├── src/
│   ├── tools/
│   │   └── google_calendar.py  # Google Calendar API tools & integrations
│   ├── agent.py                 # Core AI agent logic
│   ├── calendar_utils.py        # Date formatting & utility functions
│   ├── config.py               # Config & environment variables loader
│   ├── main.py                 # Application entry point
│   └── models.py               # Data models & Pydantic schemas
├── .env                        # Environment variables & API keys (private)
├── credentials.json            # Google OAuth 2.0 credentials (private)
├── token.json                  # OAuth session token (auto-generated, private)
├── requirements.txt            # Python dependencies
└── README.md

```

---

## 🚀 Getting Started

### 1. Prerequisites

* Python 3.10 or higher installed.
* A Google Cloud account with the **Google Calendar API** enabled.

---

### 2. Clone Repository & Setup Environment

```bash
# Clone the repository
git clone [https://github.com/cosminpelin21/ai-calendar-agent.git](https://github.com/cosminpelin21/ai-calendar-agent.git)
cd ai-calendar-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS / Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```

---

### 3. Setup Credentials & Environment Variables

1. **Google OAuth Credentials:**
* Open the [Google Cloud Console](https://console.cloud.google.com/).
* Enable the **Google Calendar API**.
* Create an **OAuth 2.0 Client ID** credential (Application type: *Desktop app*).
* Download the credentials JSON file and save it as **`credentials.json`** in the root directory of the project.


2. **Environment Variables (`.env`):**
* Create a `.env` file in the root directory and add your API keys:



```env
GEMINI_API_KEY=your_api_key_here

```

---

## 💻 Running the Application

To start the AI Calendar Agent, run:

```bash
python -m src.main

```

> **Note:** On the first execution, a browser window will pop up asking for permission to access your Google Calendar. Once granted, a `token.json` file will be generated automatically to persist your authentication session.

---
