import datetime
import re
from zoneinfo import ZoneInfo

from langchain.tools import tool

from calendar_utils import get_calendar_service

TIMEZONE = "Europe/Bucharest"
TZ = ZoneInfo(TIMEZONE)

USER_CONTEXT = {"text": ""}

TIME_PATTERN = re.compile(
    r"\b\d{1,2}[:.]\d{2}\b"
    r"|\b(?:at|to|la|ora|de la|from)\s+\d{1,2}\b"
    r"|\b\d{1,2}\s?(?:am|pm)\b",
    re.IGNORECASE,
)


# ---------- helpers ----------

def _user_gave_time() -> bool:
    return bool(TIME_PATTERN.search(USER_CONTEXT["text"]))


def _parse_date(value: str) -> datetime.date:
    return datetime.datetime.strptime(value.strip(), "%Y-%m-%d").date()


def _parse_time(value: str) -> datetime.time:
    return datetime.datetime.strptime(value.strip(), "%H:%M").time()


def _event_dt(info: dict):
    """Google start/end dict -> aware datetime in local TZ (None for all-day events)."""
    raw = info.get("dateTime")
    if not raw:
        return None
    return datetime.datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(TZ)


def _tz_payload(dt: datetime.datetime) -> dict:
    return {"dateTime": dt.isoformat(timespec="seconds"), "timeZone": TIMEZONE}


def _describe(ev: dict) -> str:
    title = ev.get("summary", "No title")
    s, e = _event_dt(ev["start"]), _event_dt(ev["end"])
    if s is None:
        return f"'{title}' on {ev['start'].get('date')} (all day)"
    return f"'{title}' on {s:%Y-%m-%d} {s:%H:%M}-{e:%H:%M}"


def _resolve_event(title: str, event_date: str = "", days_ahead: int = 30):
    """
    Find a single event by title (and optionally by the day it is on).
    Returns (event, None) on success or (None, error_message) otherwise.
    """
    if not title or not title.strip():
        return None, "ERROR: event_title is missing. Ask the user which event they mean."

    service = get_calendar_service()
    today_start = datetime.datetime.combine(
        datetime.datetime.now(TZ).date(), datetime.time.min, tzinfo=TZ
    )
    if event_date:
        start = datetime.datetime.combine(_parse_date(event_date), datetime.time.min, tzinfo=TZ)
        end = start + datetime.timedelta(days=1)
    else:
        start = today_start
        end = start + datetime.timedelta(days=days_ahead)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = result.get("items", [])

    q = title.strip().lower()
    matches = [e for e in items if e.get("summary", "").strip().lower() == q]
    if not matches:  # fall back to partial match
        matches = [e for e in items if q in e.get("summary", "").lower()]

    if not matches:
        return None, f"ERROR: no event matching '{title}' was found. Tell the user and ask for the correct title or date."
    if len(matches) > 1:
        options = "; ".join(_describe(e) for e in matches)
        return None, (
            f"ERROR: several events match '{title}': {options}. "
            "Ask the user which one (by date or time), then call the tool again with event_date."
        )
    return matches[0], None


# ---------- tools ----------

@tool
def list_calendar_events(date_from: str = "", date_to: str = "", max_results: int = 20) -> str:
    """
    Lists calendar events with their dates and times.

    Args:
        date_from: First day to include, YYYY-MM-DD. If empty, starts from now.
        date_to: Last day to include, YYYY-MM-DD. If empty and date_from is set,
            only date_from is listed. If both are empty, lists the next 7 days.
        max_results: Maximum number of events (default 20).

    To inspect a specific day, set date_from to that day.
    """
    try:
        if date_from:
            first_day = _parse_date(date_from)
            last_day = _parse_date(date_to) if date_to else first_day
            start_dt = datetime.datetime.combine(first_day, datetime.time.min, tzinfo=TZ)
        else:
            start_dt = datetime.datetime.now(TZ)
            last_day = (
                _parse_date(date_to)
                if date_to
                else (start_dt + datetime.timedelta(days=7)).date()
            )

        end_dt = datetime.datetime.combine(
            last_day + datetime.timedelta(days=1), datetime.time.min, tzinfo=TZ
        )

        service = get_calendar_service()
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = result.get("items", [])
        if not events:
            return "No events found in this period."
        return "\n".join(_describe(ev) for ev in events)

    except ValueError:
        return "ERROR: dates must be in YYYY-MM-DD format."
    except Exception as e:
        return f"An error occurred while accessing the calendar: {e}"


@tool
def find_free_slots(
    date: str,
    duration_minutes: int = 60,
    day_start: str = "08:00",
    day_end: str = "20:00",
) -> str:
    """
    Finds free time slots on a given day. Use this when the user asks when they
    are free or available, or asks for a good time for a meeting.

    Args:
        date: Day to check, YYYY-MM-DD ("tomorrow" = tomorrow's date).
        duration_minutes: Minimum length of a free slot (default 60).
        day_start: Start of the considered day, HH:MM (default 08:00).
        day_end: End of the considered day, HH:MM (default 20:00).
    """
    try:
        day = _parse_date(date)
        window_start = datetime.datetime.combine(day, _parse_time(day_start), tzinfo=TZ)
        window_end = datetime.datetime.combine(day, _parse_time(day_end), tzinfo=TZ)

        service = get_calendar_service()
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=window_start.isoformat(),
                timeMax=window_end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        busy = []
        for ev in result.get("items", []):
            s, e = _event_dt(ev["start"]), _event_dt(ev["end"])
            if s is None:  # all-day events are ignored
                continue
            busy.append((max(s, window_start), min(e, window_end)))

        free, cursor = [], window_start
        for s, e in sorted(busy):
            if s - cursor >= datetime.timedelta(minutes=duration_minutes):
                free.append((cursor, s))
            cursor = max(cursor, e)
        if window_end - cursor >= datetime.timedelta(minutes=duration_minutes):
            free.append((cursor, window_end))

        if not free:
            return f"No free slots of {duration_minutes} min on {day} between {day_start} and {day_end}."
        slots = ", ".join(f"{a:%H:%M}-{b:%H:%M}" for a, b in free)
        return f"Free slots on {day}: {slots}. Report exactly these slots to the user."

    except ValueError:
        return "ERROR: date must be YYYY-MM-DD and times must be HH:MM."
    except Exception as e:
        return f"An error occurred while accessing the calendar: {e}"


@tool
def add_calendar_event(
    summary: str,
    date: str,
    start_time: str,
    duration_minutes: int = 60,
    description: str = "",
    location: str = "",
) -> str:
    """
    Adds a NEW event to the user's Google Calendar.

    Args:
        summary: Event title.
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM 24h format. It MUST be a time the user
            explicitly stated. If the user did not state a time, DO NOT call this
            tool: ask the user for the time instead.
        duration_minutes: Duration in minutes (default 60).
        description: Optional description.
        location: Optional location.
    """
    if not _user_gave_time():
        return (
            "ERROR: the user has not specified a start time. Do not guess. "
            "Ask the user at what time the event should start."
        )

    try:
        day = _parse_date(date)
        t = _parse_time(start_time)
    except ValueError:
        return "ERROR: date must be YYYY-MM-DD and start_time must be HH:MM (24h)."

    start = datetime.datetime.combine(day, t)
    end = start + datetime.timedelta(minutes=duration_minutes)

    try:
        service = get_calendar_service()
        event = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": _tz_payload(start),
            "end": _tz_payload(end),
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 10}],
            },
        }
        service.events().insert(calendarId="primary", body=event).execute()
        return f"Event '{summary}' created for {start:%Y-%m-%d %H:%M}-{end:%H:%M}."
    except Exception as e:
        return f"Error creating event: {e}"


@tool
def update_calendar_event(
    event_title: str,
    event_date: str = "",
    new_title: str = None,
    new_date: str = None,
    new_start_time: str = None,
    duration_minutes: int = None,
    description: str = None,
    location: str = None,
) -> str:
    """
    Updates an existing event. The event is found automatically by its title:
    never ask the user for an ID. Only the fields you provide are changed;
    everything else (date, time, duration) is preserved automatically.

    Args:
        event_title: Title of the event to change, as the user said it.
        event_date: Day the event is CURRENTLY on, YYYY-MM-DD. Only needed if several
            events share the title.
        new_title: New title. Provide ONLY if the user wants to rename the event.
        new_date: New date YYYY-MM-DD. Provide ONLY if the user asked to change the day.
        new_start_time: New start time HH:MM (24h). Provide ONLY if the user asked to
            change the time. The duration is kept unless duration_minutes is given.
        duration_minutes: New duration in minutes. Provide ONLY if the user asked to change it.
        description: New description.
        location: New location.
    """
    try:
        event, error = _resolve_event(event_title, event_date)
        if error:
            return error

        body = {}
        if new_title:
            body["summary"] = new_title
        if description is not None:
            body["description"] = description
        if location is not None:
            body["location"] = location

        if new_date or new_start_time or duration_minutes:
            if new_start_time and not _user_gave_time():
                return (
                    "ERROR: the user has not specified a new time. Do not guess. "
                    "Ask the user for the exact time."
                )

            old_start, old_end = _event_dt(event["start"]), _event_dt(event["end"])
            if old_start is None:
                return "ERROR: this is an all-day event; changing its time is not supported."

            day = _parse_date(new_date) if new_date else old_start.date()
            t = _parse_time(new_start_time) if new_start_time else old_start.time()
            duration = (
                datetime.timedelta(minutes=duration_minutes)
                if duration_minutes
                else old_end - old_start
            )

            new_start = datetime.datetime.combine(day, t)
            body["start"] = _tz_payload(new_start)
            body["end"] = _tz_payload(new_start + duration)

        if not body:
            return "ERROR: no changes were provided."

        service = get_calendar_service()
        updated = (
            service.events()
            .patch(calendarId="primary", eventId=event["id"], body=body)
            .execute()
        )
        s, e = _event_dt(updated["start"]), _event_dt(updated["end"])
        return f"Event '{updated.get('summary')}' updated: {s:%Y-%m-%d %H:%M}-{e:%H:%M}."

    except ValueError:
        return "ERROR: dates must be YYYY-MM-DD and times must be HH:MM (24h)."
    except Exception as e:
        return f"Error updating event: {e}"


@tool
def delete_calendar_event(event_title: str, event_date: str = "") -> str:
    """
    Deletes an event from the user's Google Calendar. The event is found
    automatically by its title: never ask the user for an ID.

    Args:
        event_title: Title of the event to delete, as the user said it.
        event_date: Day the event is on, YYYY-MM-DD. Only needed if several
            events share the title.
    """
    try:
        event, error = _resolve_event(event_title, event_date)
        if error:
            return error
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event["id"]).execute()
        return f"Event '{event.get('summary', 'No title')}' deleted successfully."
    except ValueError:
        return "ERROR: event_date must be YYYY-MM-DD."
    except Exception as e:
        return f"Error deleting event: {e}"