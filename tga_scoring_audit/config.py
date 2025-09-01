"""Configuration management for TGA Scoring Audit application."""

import os
from typing import Optional


class Config:
    """Configuration settings for the TGA Scoring Audit application."""

    def __init__(self) -> None:
        self.api_key: Optional[str] = None
        self.base_url: str = "https://www.golfgenius.com/api_v2"
        self.request_timeout: int = 30
        self.max_retries: int = 3
        self.retry_delay: float = 1.0  # seconds
        self.rate_limit_delay: float = 0.5  # seconds between requests

    def set_api_key(self, api_key: str) -> None:
        """Set the Golf Genius API key."""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        self.api_key = api_key.strip()

    def get_api_key(self) -> str:
        """Get the API key, raising an error if not set."""
        if not self.api_key:
            # Try to get from environment variable
            env_key = os.getenv("GOLF_GENIUS_API_KEY")
            if env_key:
                self.api_key = env_key.strip()
            else:
                raise ValueError(
                    "API key not set. Use set_api_key() or set GOLF_GENIUS_API_KEY environment variable."
                )
        return self.api_key

    def validate_api_key(self, api_key: str) -> bool:
        """Basic API key format validation."""
        if not api_key or len(api_key) < 10:
            return False
        return True
