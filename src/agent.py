import datetime
from langchain_ollama import ChatOllama  
from langchain.agents import create_agent 
from tools.google_calendar import list_calendar_events, add_calendar_event, update_calendar_event, delete_calendar_event  
from config import OLLAMA_MODEL  

tools = [list_calendar_events, add_calendar_event, update_calendar_event, delete_calendar_event]  

system_prompt_template = """You are a precise AI assistant for calendar management.  
Speak in flawless, grammatically correct English or romanian.  
CRITICAL RULE: You only have access to the tools listed in your configuration. Never suggest, invent, or mention function names like 'adaugare_eveniment' or 'afisare_calendar' to the user. If a tool doesn't exist, simply tell the user what you can or cannot do in plain text. You can list existing events, add new events, update existing events, and delete events from the calendar.""" 

def create_agent_executor():          
    """Creates and returns the agent executor."""          
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0)

    # Injectăm data curentă pentru ca modelul să știe când e "mâine", "luni", etc.
    current_time_info = f"\nCurrent Date and Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    full_system_prompt = system_prompt_template + current_time_info

    agent_executor = create_agent(
        model=llm,
        tools=tools,
        system_prompt=full_system_prompt
    )                
    return agent_executor