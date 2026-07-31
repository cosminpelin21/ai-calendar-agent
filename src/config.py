import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# AI Model Settings (Ollama)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Google Calendar Settings
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = "token.json"

# Scopes for Google Calendar (permissions)
SCOPES = ['https://www.googleapis.com/auth/calendar']