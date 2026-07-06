import datetime
from langchain.tools import tool
from typing import List

from calendar_utils import get_calendar_service

@tool
def list_calendar_events(max_results: int = 10) -> List[str]:
    """
    Use this tool to list upcoming events from the calendar.
    Returns a list of the next 'max_results' events.
    """
    try:
        service = get_calendar_service()

        # Get the current date and time in UTC format
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC

        print("Getting the upcoming events...")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return ["You have no upcoming events scheduled."]

        event_summaries = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event["summary"]
            event_summaries.append(f"- '{summary}' on {start}")

        return event_summaries

    except Exception as e:
        return [f"An error occurred while accessing the calendar: {e}"]