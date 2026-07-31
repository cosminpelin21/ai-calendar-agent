/
├── .env                # Chei API, ID-uri (ex: Google Client ID)
├── requirements.txt    # Dependențele proiectului
├── credentials.json    # Fișierul de la Google Cloud Console (OAuth 2.0)
├── src/
│   ├── __init__.py
│   ├── main.py         # Interfața Streamlit (punctul de intrare)
│   ├── config.py       # Configurări: încărcare .env, setări model
│   ├── models.py       # Definirea structurilor de date (Pydantic schemas)
│   ├── calendar_utils.py # Logica de autentificare Google API (OAuth flow)
│   ├── agent.py        # Crearea agentului LangChain și a logicii de reasoning
│   └── tools/          # Folderul pentru tool-urile agentului
│       ├── __init__.py
│       └── google_calendar.py # Implementarea tool-urilor (Add, List, Update events)