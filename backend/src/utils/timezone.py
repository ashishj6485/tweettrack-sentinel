"""
Timezone utilities for converting timestamps to IST (Indian Standard Time).
"""
from datetime import datetime
import pytz


# IST timezone
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.utc


def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST.
    
    Args:
        utc_dt: Datetime object in UTC (can be naive or aware)
    
    Returns:
        Datetime object in IST timezone
    """
    # If naive, assume UTC
    if utc_dt.tzinfo is None:
        utc_dt = UTC.localize(utc_dt)
    
    # Convert to IST
    ist_dt = utc_dt.astimezone(IST)
    return ist_dt


def now_ist() -> datetime:
    """Get current datetime in IST."""
    return datetime.now(IST)


def format_ist(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S %Z') -> str:
    """
    Format datetime in IST.
    
    Args:
        dt: Datetime object (will be converted to IST if not already)
        format_str: strftime format string
    
    Returns:
        Formatted datetime string
    """
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime(format_str)


def get_relative_time(dt: datetime) -> str:
    """
    Get human-readable relative time (e.g., '5 minutes ago').
    
    Args:
        dt: Datetime object
    
    Returns:
        Relative time string
    """
    now = datetime.now(UTC)
    
    # Ensure both datetimes are aware
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
