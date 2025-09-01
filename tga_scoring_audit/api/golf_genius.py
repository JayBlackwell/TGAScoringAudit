"""Golf Genius API specific implementation."""

from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from .client import APIClient, AuthenticationError, ValidationError
from ..config import Config


class GolfGeniusAPI:
    """Golf Genius API client implementation."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = APIClient(config)
        self._validate_setup()

    def _validate_setup(self) -> None:
        """Validate that API key is available and formatted correctly."""
        try:
            api_key = self.config.get_api_key()
            if not self.config.validate_api_key(api_key):
                raise AuthenticationError("API key format is invalid")
        except ValueError as e:
            raise AuthenticationError(str(e))

    def _build_url(self, endpoint: str) -> str:
        """Build full URL with API key embedded in path."""
        api_key = self.config.get_api_key()
        # URL format from documentation: https://www.golfgenius.com/api_v2/{api_key}/{endpoint}
        url = urljoin(f"{self.config.base_url}/", f"{api_key}/{endpoint}")
        return url

    def get_seasons(self) -> List[Dict[str, Any]]:
        """Fetch all available seasons."""
        url = self._build_url("seasons")
        
        try:
            response = self.client.get(url)

            # Validate response structure and extract season data
            if isinstance(response, list):
                # Response format: [{"season": {"id": "...", "name": "..."}}, ...]
                seasons = []
                for item in response:
                    if isinstance(item, dict) and "season" in item:
                        seasons.append(item["season"])
                    else:
                        seasons.append(item)
            elif isinstance(response, dict) and "seasons" in response:
                seasons = response["seasons"]
            else:
                raise ValidationError("Unexpected seasons response format")

            # Validate each season has required fields
            for season in seasons:
                if not isinstance(season, dict):
                    continue
                self.client.validate_response(season, ["id", "name"])

            seasons_list: List[Dict[str, Any]] = seasons
            return seasons_list

        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(f"Failed to fetch seasons: {str(e)}")

    def get_events(
        self,
        season_id: str,
        page: int = 1,
        category_id: Optional[str] = None,
        directory_id: Optional[str] = None,
        archived: bool = False,
    ) -> Dict[str, Any]:
        """Fetch events for a specific season."""
        params = {"page": str(page), "season": season_id}

        if category_id:
            params["category"] = category_id
        if directory_id:
            params["directory"] = directory_id
        if archived:
            params["archived"] = "true"

        url = self._build_url("events")

        try:
            response = self.client.get(url, params=params)

            # Handle different response formats
            if isinstance(response, list):
                # API returns events as array of objects with "event" key
                events = []
                for item in response:
                    if isinstance(item, dict) and "event" in item:
                        events.append(item["event"])
                    elif isinstance(item, dict):
                        # Fallback: treat the item itself as event data
                        events.append(item)
                result = {"events": events}
            elif isinstance(response, dict):
                # API returns events wrapped in an object
                result = response
                # Ensure events key exists
                if "events" not in result:
                    result["events"] = []
            else:
                # Unexpected format
                result = {"events": []}

            # Validate each event has required fields
            for event in result.get("events", []):
                if isinstance(event, dict):
                    self.client.validate_response(event, ["id", "name"])

            return result

        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(f"Failed to fetch events: {str(e)}")

    def get_all_events(self, season_id: str) -> List[Dict[str, Any]]:
        """Fetch all events for a season, handling pagination."""
        all_events = []
        page = 1

        while True:
            try:
                response = self.get_events(season_id, page=page)
                events = response.get("events", [])

                # Debug: Print page info
                print(f"  Page {page}: {len(events)} events")

                # If no events in this page, we're done
                if not events:
                    break

                all_events.extend(events)
                page += 1

                # Safety check to prevent infinite loops
                if page > 1000:
                    print("  Warning: Stopped at page 1000 to prevent infinite loop")
                    break

            except ValidationError as e:
                # If we can't fetch a page, stop pagination
                print(f"  Warning: Failed to fetch page {page}: {e}")
                break
            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break

        print(f"  Total events collected: {len(all_events)}")
        return all_events

    def get_rounds(self, event_id: str) -> List[Dict[str, Any]]:
        """Fetch all rounds for a specific event."""
        url = self._build_url(f"events/{event_id}/rounds")

        try:
            response = self.client.get(url)

            # Handle different response formats
            if isinstance(response, list):
                # API returns rounds as array of objects with "round" key
                rounds = []
                for item in response:
                    if isinstance(item, dict) and "round" in item:
                        rounds.append(item["round"])
                    elif isinstance(item, dict):
                        # Fallback: treat the item itself as round data
                        rounds.append(item)
            elif isinstance(response, dict) and "rounds" in response:
                rounds = response["rounds"]
            else:
                rounds = []

            # Validate each round has required fields
            for round_data in rounds:
                if isinstance(round_data, dict):
                    self.client.validate_response(round_data, ["id"])

            rounds_list: List[Dict[str, Any]] = rounds
            return rounds_list

        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(
                f"Failed to fetch rounds for event {event_id}: {str(e)}"
            )

    def get_tee_sheet(
        self, event_id: str, round_id: str, include_all_custom_fields: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch tee sheet data for a specific round."""
        params = {}
        if include_all_custom_fields:
            params["include_all_custom_fields"] = "true"

        url = self._build_url(f"events/{event_id}/rounds/{round_id}/tee_sheet")

        try:
            response = self.client.get(url, params=params)

            # Handle different response formats
            if isinstance(response, list):
                tee_sheet = response
            elif isinstance(response, dict):
                # Look for common keys that might contain the data
                for key in ["tee_sheet", "pairing_groups", "data", "groups"]:
                    if key in response and isinstance(response[key], list):
                        tee_sheet = response[key]
                        break
                else:
                    # If no list found, wrap the dict in a list
                    tee_sheet = [response] if response else []
            else:
                tee_sheet = []

            tee_sheet_list: List[Dict[str, Any]] = tee_sheet
            return tee_sheet_list

        except Exception as e:
            if isinstance(e, (AuthenticationError, ValidationError)):
                raise
            raise ValidationError(
                f"Failed to fetch tee sheet for round {round_id}: {str(e)}"
            )

    def test_connection(self) -> bool:
        """Test API connection by fetching seasons."""
        try:
            seasons = self.get_seasons()
            return isinstance(seasons, list)
        except Exception:
            return False

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
