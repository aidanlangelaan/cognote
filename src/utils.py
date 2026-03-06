import re
from datetime import datetime


def slugify(title: str, max_length: int = 50) -> str:
    """Convert a meeting title to a filesystem-safe slug.

    Example: "Weekly Sync!" -> "weekly-sync"
    """
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length]


def session_folder_name(start: datetime, title: str, max_slug_length: int = 50) -> str:
    """Build the session folder name from start time and title.

    Example: "2026-03-06_14-05_weekly-sync"
    """
    timestamp = start.strftime("%Y-%m-%d_%H-%M")
    slug = slugify(title, max_length=max_slug_length)
    return f"{timestamp}_{slug}"


def format_timestamp(seconds: float) -> str:
    """Format a float number of seconds as HH:MM:SS for use in the transcript.

    Example: 65.3 -> "00:01:05"
    """
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_dutch_date(dt: datetime) -> str:
    """Format a datetime as a Dutch-style date string: DD-MM-YYYY."""
    return dt.strftime("%d-%m-%Y")


def format_dutch_time(dt: datetime) -> str:
    """Format a datetime as HH:MM."""
    return dt.strftime("%H:%M")
