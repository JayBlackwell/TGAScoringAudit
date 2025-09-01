"""Round data model."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Round:
    """Represents a golf round."""

    id: str
    event_id: str
    name: str
    date: Optional[datetime] = None
    is_flagged: bool = False
    flag_reason: str = ""

    @classmethod
    def from_api_response(cls, data: Dict[str, Any], event_id: str) -> "Round":
        """Create Round from API response data."""
        round_date = None

        # Try to parse date from multiple possible fields
        for date_field in ["date", "round_date", "start_date", "tee_time"]:
            if date_field in data and data[date_field]:
                try:
                    date_str = str(data[date_field])
                    # Handle various date formats
                    if "T" in date_str or "+" in date_str or "Z" in date_str:
                        round_date = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Try parsing as date only
                        round_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    break
                except (ValueError, AttributeError):
                    continue

        return cls(
            id=str(data.get("id", "")),
            event_id=event_id,
            name=str(data.get("name", data.get("round_name", "Round"))),
            date=round_date,
            is_flagged=False,
            flag_reason="",
        )

    def flag(self, reason: str) -> None:
        """Flag this round with a reason."""
        self.is_flagged = True
        self.flag_reason = reason

    def unflag(self) -> None:
        """Remove flag from this round."""
        self.is_flagged = False
        self.flag_reason = ""

    def __str__(self) -> str:
        """String representation for user display."""
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "No Date"
        flag_str = " [FLAGGED]" if self.is_flagged else ""
        return f"{self.name} ({date_str}){flag_str}"
