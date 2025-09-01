"""Season data model."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Season:
    """Represents a golf season."""

    id: str
    name: str
    year: str = ""
    description: str = ""

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Season":
        """Create Season from API response data."""
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            year=str(data.get("year", "")),
            description=str(data.get("description", "")),
        )

    def __str__(self) -> str:
        """String representation for user display."""
        if self.year:
            return f"{self.name} ({self.year})"
        return self.name
