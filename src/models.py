from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    """Enum for task priority."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CalendarEvent(BaseModel):
    """Structure of a calendar event."""
    summary: str = Field(description="The title of the event")
    description: Optional[str] = Field(None, description="The description or details of the event")
    start_time: datetime = Field(description="Start date and time (datetime object)")
    end_time: datetime = Field(description="End date and time (datetime object)")
    location: Optional[str] = Field(None, description="The location of the event")

class Task(BaseModel):
    """Structure of a task to be scheduled."""
    title: str = Field(description="The name of the task")
    duration_minutes: int = Field(default=30, description="Estimated duration in minutes")
    deadline: Optional[datetime] = Field(None, description="The deadline by which it must be done")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority: high, medium, low")
