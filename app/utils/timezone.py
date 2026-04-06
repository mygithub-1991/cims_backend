"""
IST (Indian Standard Time) Timezone Utilities

This module provides timezone-aware datetime functions for IST (UTC+05:30).
All datetime operations in the application should use these functions to ensure
consistent timezone handling.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# IST is UTC + 5 hours 30 minutes
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    """
    Get current datetime in IST timezone.

    Returns:
        datetime: Current time in IST with timezone info

    Example:
        >>> from app.utils.timezone import now_ist
        >>> current_time = now_ist()
        >>> print(current_time)  # 2026-04-06 23:30:00+05:30
    """
    return datetime.now(IST)


def utc_to_ist(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to IST.

    Args:
        utc_dt: Datetime in UTC timezone

    Returns:
        datetime: Datetime converted to IST

    Example:
        >>> utc_time = datetime(2026, 4, 6, 18, 0, 0, tzinfo=timezone.utc)
        >>> ist_time = utc_to_ist(utc_time)
        >>> print(ist_time)  # 2026-04-06 23:30:00+05:30
    """
    if utc_dt.tzinfo is None:
        # Assume naive datetime is UTC
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(IST)


def ist_to_utc(ist_dt: datetime) -> datetime:
    """
    Convert IST datetime to UTC.

    Args:
        ist_dt: Datetime in IST timezone

    Returns:
        datetime: Datetime converted to UTC

    Example:
        >>> ist_time = datetime(2026, 4, 6, 23, 30, 0, tzinfo=IST)
        >>> utc_time = ist_to_utc(ist_time)
        >>> print(utc_time)  # 2026-04-06 18:00:00+00:00
    """
    if ist_dt.tzinfo is None:
        # Assume naive datetime is IST
        ist_dt = ist_dt.replace(tzinfo=IST)
    return ist_dt.astimezone(timezone.utc)


def timestamp_to_ist_datetime(ts: Optional[int]) -> Optional[datetime]:
    """
    Convert Unix timestamp (milliseconds) to IST datetime.

    Android sends timestamps in milliseconds since Unix epoch (UTC-based).
    This function converts them to IST datetime for database storage.

    Args:
        ts: Unix timestamp in milliseconds (from Android)

    Returns:
        datetime: Datetime in IST timezone, or None if input is None

    Example:
        >>> # Android sends: 1704067200000 (2024-01-01 00:00:00 UTC)
        >>> ist_dt = timestamp_to_ist_datetime(1704067200000)
        >>> print(ist_dt)  # 2024-01-01 05:30:00+05:30 (IST)
    """
    if ts is None:
        return None
    # Convert milliseconds to seconds, create UTC datetime, then convert to IST
    utc_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return utc_dt.astimezone(IST)


def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[int]:
    """
    Convert datetime to Unix timestamp (milliseconds) for API response.

    Converts IST (or any timezone-aware) datetime to Unix timestamp in milliseconds.
    This is sent to Android app which expects milliseconds since epoch.

    Args:
        dt: Datetime with timezone info (typically IST)

    Returns:
        int: Unix timestamp in milliseconds, or None if input is None

    Example:
        >>> ist_dt = datetime(2024, 1, 1, 5, 30, 0, tzinfo=IST)
        >>> timestamp = datetime_to_timestamp(ist_dt)
        >>> print(timestamp)  # 1704067200000
    """
    if dt is None:
        return None
    # Handle naive datetimes by assuming IST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    return int(dt.timestamp() * 1000)


def format_ist(dt: datetime, format_str: str = "%d-%m-%Y %I:%M %p IST") -> str:
    """
    Format datetime in IST for display.

    Args:
        dt: Datetime to format
        format_str: Python strftime format string

    Returns:
        str: Formatted datetime string

    Example:
        >>> dt = now_ist()
        >>> formatted = format_ist(dt)
        >>> print(formatted)  # "06-04-2026 11:30 PM IST"
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST)
    ist_dt = dt.astimezone(IST)
    return ist_dt.strftime(format_str)


def get_ist_date_start(date_dt: datetime) -> datetime:
    """
    Get start of day (00:00:00) in IST for a given datetime.

    Args:
        date_dt: Any datetime

    Returns:
        datetime: Start of that day in IST (00:00:00+05:30)

    Example:
        >>> dt = now_ist()
        >>> start = get_ist_date_start(dt)
        >>> print(start)  # 2026-04-06 00:00:00+05:30
    """
    ist_dt = date_dt.astimezone(IST) if date_dt.tzinfo else date_dt.replace(tzinfo=IST)
    return ist_dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_ist_date_end(date_dt: datetime) -> datetime:
    """
    Get end of day (23:59:59.999999) in IST for a given datetime.

    Args:
        date_dt: Any datetime

    Returns:
        datetime: End of that day in IST (23:59:59.999999+05:30)

    Example:
        >>> dt = now_ist()
        >>> end = get_ist_date_end(dt)
        >>> print(end)  # 2026-04-06 23:59:59.999999+05:30
    """
    ist_dt = date_dt.astimezone(IST) if date_dt.tzinfo else date_dt.replace(tzinfo=IST)
    return ist_dt.replace(hour=23, minute=59, second=59, microsecond=999999)


# Legacy compatibility - will be deprecated
def timestamp_to_datetime(ts: Optional[int]) -> Optional[datetime]:
    """
    DEPRECATED: Use timestamp_to_ist_datetime() instead.

    Kept for backward compatibility during migration.
    """
    return timestamp_to_ist_datetime(ts)
