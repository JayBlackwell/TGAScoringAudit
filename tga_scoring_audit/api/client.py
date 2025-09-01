"""Base API client with comprehensive error handling and retry logic."""

import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config import Config


class APIError(Exception):
    """Base exception for API-related errors."""

    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""

    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    pass


class ValidationError(APIError):
    """Raised when data validation fails."""

    pass


class APIClient:
    """Base API client with error handling and retry logic."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Configure session with retry strategy."""
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Note: timeout is set per request, not on session

    def _make_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Make HTTP request with error handling."""
        try:
            # Apply rate limiting
            time.sleep(self.config.rate_limit_delay)

            response = self.session.request(
                method, url, timeout=self.config.request_timeout, **kwargs
            )

            # Handle specific HTTP status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code >= 400:
                raise APIError(f"HTTP {response.status_code}: {response.text}")

            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            raise APIError(
                f"Request timeout after {self.config.request_timeout} seconds"
            )
        except requests.exceptions.ConnectionError:
            raise APIError("Connection error - check internet connection")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request and return JSON response."""
        response = self._make_request("GET", url, params=params)

        try:
            data: Dict[str, Any] = response.json()
            return data
        except ValueError:
            # Provide more detailed error information
            content_preview = response.text[:200] if response.text else "(empty response)"
            raise APIError(f"Invalid JSON response from API. Content: {content_preview}")

    def validate_response(
        self, data: Dict[str, Any], required_fields: list[str]
    ) -> None:
        """Validate API response has required fields."""
        if not isinstance(data, dict):
            raise ValidationError("Response is not a dictionary")

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    def close(self) -> None:
        """Close the session."""
        self.session.close()
