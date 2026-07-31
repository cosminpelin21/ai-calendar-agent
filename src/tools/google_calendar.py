import datetime
from langchain.tools import tool
import re
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
            return "You have no upcoming events scheduled."

        event_summaries = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event["summary"]
            event_summaries.append(f"ID: {event['id']} - '{summary}' on {start}")

        return "\n".join(event_summaries)

    except Exception as e:
        return f"An error occurred while accessing the calendar: {e}"

def _get_timezone_from_iso(iso_time_str: str, default_timezone: str = 'Europe/Bucharest') -> str:
    """
    Helper function to extract timezone from ISO 8601 string or use a default.
    A full date parsing library would be more robust for complex cases.
    """
    # Check for 'Z' (UTC) or timezone offset (+HH:MM, -HH:MM)
    if iso_time_str.endswith('Z'):
        return 'UTC'
    match = re.search(r'([+-]\d{2}:\d{2})$', iso_time_str)
    if match:
        return None # Google Calendar API can often infer timezone from offset in dateTime string
    return default_timezone

@tool
def add_calendar_event(summary: str, start_time: str, end_time: str, description: str = "", location: str = "", timezone: str = 'Europe/Bucharest') -> str:
    """
    Adds a new event to the user's Google Calendar.

    `start_time` and `end_time` must be provided in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ' for UTC or 'YYYY-MM-DDTHH:MM:SS-HH:MM' for a specific timezone).
    Example: '2024-07-15T10:00:00-07:00' for July 15, 2024, 10:00 AM Pacific Daylight Time.

    Args:
        summary (str): The title of the event.
        start_time (str): The start time of the event in ISO 8601 format.
        end_time (str): The end time of the event in ISO 8601 format.
        description (str, optional): A detailed description of the event. Defaults to "".
        location (str, optional): The physical location of the event. Defaults to "".
        timezone (str, optional): The IANA timezone string for the event (e.g., 'America/New_York', 'Europe/Bucharest').
                                  Defaults to 'Europe/Bucharest'. If start_time/end_time include a timezone offset,
                                  this parameter might be overridden or ignored by Google Calendar API.

    Returns:
        str: A confirmation message with the event details or an error message.
    """
    try:
        service = get_calendar_service()

        start_tz = _get_timezone_from_iso(start_time, timezone)
        end_tz = _get_timezone_from_iso(end_time, timezone)

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24 * 60}, {'method': 'popup', 'minutes': 10}]},
        }

        if start_tz:
            event['start']['timeZone'] = start_tz
        if end_tz:
            event['end']['timeZone'] = end_tz
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating event: {e}"

@tool
def update_calendar_event(event_id: str, summary: str = None, start_time: str = None, end_time: str = None, description: str = None, location: str = None, timezone: str = 'Europe/Bucharest') -> str:
    """
    Updates an existing event in the user's Google Calendar.

    `start_time` and `end_time` must be provided in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SSZ' for UTC or 'YYYY-MM-DDTHH:MM:SS-HH:MM' for a specific timezone).
    Example: '2024-07-15T10:00:00-07:00' for July 15, 2024, 10:00 AM Pacific Daylight Time.

    Args:
        event_id (str): The ID of the event to update. This can be obtained from `list_calendar_events`.
        summary (str, optional): The new title of the event.
        start_time (str, optional): The new start time of the event in ISO 8601 format.
        end_time (str, optional): The new end time of the event in ISO 8601 format.
        description (str, optional): A new detailed description of the event.
        location (str, optional): The new physical location of the event.
        timezone (str, optional): The IANA timezone string for the event (e.g., 'America/New_York', 'Europe/Bucharest').
                                  Defaults to 'Europe/Bucharest'. If start_time/end_time include a timezone offset,
                                  this parameter might be overridden or ignored by Google Calendar API.

    Returns:
        str: A confirmation message with the updated event details or an error message.
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute() # Fetch existing event

        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if start_time:
            event['start'] = {'dateTime': start_time}
            start_tz = _get_timezone_from_iso(start_time, timezone)
            if start_tz:
                event['start']['timeZone'] = start_tz
        if end_time:
            event['end'] = {'dateTime': end_time}
            end_tz = _get_timezone_from_iso(end_time, timezone)
            if end_tz:
                event['end']['timeZone'] = end_tz

        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return f"Event updated: {updated_event.get('htmlLink')}"
    except Exception as e:
        return f"Error updating event: {e}"

@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Deletes an event from the user's Google Calendar.

    Args:
        event_id (str): The ID of the event to delete. This can be obtained from `list_calendar_events`.

    Returns:
        str: A confirmation message or an error message.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Event with ID '{event_id}' deleted successfully."
    except Exception as e:
        return f"Error deleting event: {e}"
