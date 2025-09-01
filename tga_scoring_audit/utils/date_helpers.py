"""Date utility functions."""

from datetime import datetime
from typing import Optional, Tuple
from dateutil import parser


def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string into datetime object, handling various formats."""
    if not date_string or not date_string.strip():
        return None

    try:
        # Use dateutil parser for flexible date parsing
        parsed_date: datetime = parser.parse(date_string.strip())
        return parsed_date
    except (ValueError, parser.ParserError):
        # Try common formats manually
        for fmt in [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
        ]:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue

    return None


def validate_date_range(start_date: str, end_date: str) -> Tuple[datetime, datetime]:
    """Validate and parse date range inputs."""
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    if start_dt is None:
        raise ValueError(f"Invalid start date format: {start_date}")
    if end_dt is None:
        raise ValueError(f"Invalid end date format: {end_date}")

    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")

    return start_dt, end_dt


def is_date_in_range(
    check_date: Optional[datetime], start_date: datetime, end_date: datetime
) -> bool:
    """Check if a date falls within the specified range."""
    if check_date is None:
        return False
    return start_date <= check_date <= end_date


def format_date_for_display(dt: Optional[datetime]) -> str:
    """Format datetime for user display."""
    if dt is None:
        return "No Date"
    return dt.strftime("%Y-%m-%d")


def get_date_input_prompt() -> str:
    """Get user-friendly prompt for date input."""
    return "Enter date (YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format): "
