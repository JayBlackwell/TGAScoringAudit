"""Event data model."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Event:
    """Represents a golf event/league."""

    id: str
    name: str
    season_id: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: str = ""

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Event":
        """Create Event from API response data."""
        start_date = None
        end_date = None

        # Try to parse dates if provided
        if "start_date" in data and data["start_date"]:
            try:
                start_date = datetime.fromisoformat(
                    str(data["start_date"]).replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        if "end_date" in data and data["end_date"]:
            try:
                end_date = datetime.fromisoformat(
                    str(data["end_date"]).replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            season_id=str(data.get("season_id", "")),
            start_date=start_date,
            end_date=end_date,
            description=str(data.get("description", "")),
        )

    def __str__(self) -> str:
        """String representation for user display."""
        return self.name
