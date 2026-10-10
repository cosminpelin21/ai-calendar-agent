import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.google_calendar import (
    find_free_slots,
    list_calendar_events,
    add_calendar_event,
    update_calendar_event,
    delete_calendar_event,
)
from config import OLLAMA_MODEL

TZ = ZoneInfo("Europe/Bucharest")

tools = [
    list_calendar_events,
    add_calendar_event,
    update_calendar_event,
    delete_calendar_event,
    find_free_slots,
]

SYSTEM_PROMPT_TEMPLATE = """You are a calendar assistant. You manage the user's Google Calendar using the provided tools. Always reply in English.

# CONTEXT
- Now: {now} ({weekday}), timezone {timezone}.
- Resolve relative dates ("tomorrow", "Monday", "next week") from this date only. A bare weekday means the next upcoming one.
- Tools take dates as YYYY-MM-DD and times as HH:MM (24h).

# HOW TO WORK
1. Use the conversation history. Short follow-ups ("tomorrow", "at 17:15", "that one") continue the task in progress. Never reply with a generic "what would you like to do?".
2. Never guess. If something required is missing (especially a start time), ask ONE short question about exactly that and call no tool. Times in these instructions are not the user's times.
3. Adding is always creating a NEW event. Never replace, move or delete existing events unless the user explicitly asks. Existing events are only relevant for update/delete requests and for finding free time.
4. To update or delete an event, call the tool with the event's title (and event_date if known). The tool finds the event itself: never ask the user for an ID. If a tool says several events match, ask the user which one. Never invent events, dates or times. Confirm before deleting multiple events.
5. For any question about free or available time, ALWAYS call find_free_slots and report its result as is. Never compute free time yourself.
6. For updates, pass only the fields the user wants to change. The tools preserve everything else.
7. If a tool returns ERROR, fix the problem or ask the user. Never retry with guessed values and never pretend it succeeded.
8. After a successful action, confirm in one short sentence (what, date, time). Never mention tool names or IDs.

# EXAMPLE
User: "Schedule a meeting with Ioana tomorrow called 'homework plan'"
-> No time given: call no tool. Reply: "At what time should I schedule 'homework plan' with Ioana tomorrow?"
"""

def build_system_prompt() -> str:
    now = datetime.datetime.now(TZ)
    tomorrow = now + datetime.timedelta(days=1)
    offset = now.strftime("%z")  
    offset = f"{offset[:3]}:{offset[3:]}" 

    return SYSTEM_PROMPT_TEMPLATE.format(
        now=now.strftime("%Y-%m-%d %H:%M"),
        weekday=now.strftime("%A"),
        timezone="Europe/Bucharest",
        utc_offset=offset,
        example_today=now.strftime("%Y-%m-%d"),
        example_tomorrow=tomorrow.strftime("%Y-%m-%d"),
    )


def create_agent_executor():
    """Creates the agent. Call it on every new message so the date is always current."""
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        temperature=0,
        num_ctx=8192,
    )
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=build_system_prompt(),
    )