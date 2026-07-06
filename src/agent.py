from langchain_ollama import ChatOllama 
from langchain.agents import create_agent
from tools.google_calendar import list_calendar_events 
from config import OLLAMA_MODEL 

# The tools the agent can use
tools = [list_calendar_events] 

# The new standard system prompt for LangChain v1.0
system_prompt = """You are a precise AI assistant for calendar management. 
Speak in flawless, grammatically correct English or romanian. 
CRITICAL RULE: You only have access to the tools listed in your configuration. Never suggest, invent, or mention function names like 'adaugare_eveniment' or 'afisare_calendar' to the user. If a tool doesn't exist, simply tell the user what you can or cannot do in plain text."""

def create_agent_executor():     
    """Creates and returns the agent executor."""     
    # Initialize the local Ollama model (Make sure you pulled llama3.1)
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)          
    
    # Create the modern LangChain agent
    agent_executor = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    ) 
         
    return agent_executor