"""Unit tests for data models."""

from datetime import datetime

from tga_scoring_audit.models.season import Season
from tga_scoring_audit.models.event import Event
from tga_scoring_audit.models.round import Round


class TestSeason:
    """Test Season model."""

    def test_create_season_basic(self) -> None:
        """Test basic season creation."""
        season = Season(id="123", name="Test Season")
        assert season.id == "123"
        assert season.name == "Test Season"
        assert season.year == ""

    def test_from_api_response(self) -> None:
        """Test creating season from API response."""
        api_data = {
            "id": 456,
            "name": "2023 League",
            "year": "2023",
            "description": "Test description",
        }
        season = Season.from_api_response(api_data)
        assert season.id == "456"
        assert season.name == "2023 League"
        assert season.year == "2023"
        assert season.description == "Test description"

    def test_str_with_year(self) -> None:
        """Test string representation with year."""
        season = Season(id="123", name="Test Season", year="2023")
        assert str(season) == "Test Season (2023)"

    def test_str_without_year(self) -> None:
        """Test string representation without year."""
        season = Season(id="123", name="Test Season")
        assert str(season) == "Test Season"


class TestEvent:
    """Test Event model."""

    def test_create_event_basic(self) -> None:
        """Test basic event creation."""
        event = Event(id="123", name="Test Event")
        assert event.id == "123"
        assert event.name == "Test Event"
        assert event.season_id == ""

    def test_from_api_response_with_dates(self) -> None:
        """Test creating event from API response with dates."""
        api_data = {
            "id": 789,
            "name": "Test Tournament",
            "season_id": "456",
            "start_date": "2023-06-01T09:00:00Z",
            "end_date": "2023-06-30T18:00:00Z",
        }
        event = Event.from_api_response(api_data)
        assert event.id == "789"
        assert event.name == "Test Tournament"
        assert event.season_id == "456"
        assert event.start_date is not None
        assert event.end_date is not None

    def test_from_api_response_invalid_dates(self) -> None:
        """Test creating event with invalid date formats."""
        api_data = {
            "id": 789,
            "name": "Test Tournament",
            "start_date": "invalid-date",
            "end_date": "also-invalid",
        }
        event = Event.from_api_response(api_data)
        assert event.start_date is None
        assert event.end_date is None


class TestRound:
    """Test Round model."""

    def test_create_round_basic(self) -> None:
        """Test basic round creation."""
        round_obj = Round(id="123", event_id="456", name="Round 1")
        assert round_obj.id == "123"
        assert round_obj.event_id == "456"
        assert round_obj.name == "Round 1"
        assert round_obj.is_flagged is False

    def test_from_api_response_with_date(self) -> None:
        """Test creating round from API response with date."""
        api_data = {"id": 789, "name": "Round 2", "date": "2023-06-15T10:00:00Z"}
        round_obj = Round.from_api_response(api_data, "456")
        assert round_obj.id == "789"
        assert round_obj.event_id == "456"
        assert round_obj.name == "Round 2"
        assert round_obj.date is not None

    def test_from_api_response_date_only(self) -> None:
        """Test creating round with date-only format."""
        api_data = {"id": 789, "name": "Round 3", "date": "2023-06-15"}
        round_obj = Round.from_api_response(api_data, "456")
        assert round_obj.date is not None
        assert round_obj.date.year == 2023
        assert round_obj.date.month == 6
        assert round_obj.date.day == 15

    def test_flag_round(self) -> None:
        """Test flagging a round."""
        round_obj = Round(id="123", event_id="456", name="Round 1")
        round_obj.flag("Incomplete scoring")
        assert round_obj.is_flagged is True
        assert round_obj.flag_reason == "Incomplete scoring"

    def test_unflag_round(self) -> None:
        """Test unflagging a round."""
        round_obj = Round(id="123", event_id="456", name="Round 1")
        round_obj.flag("Test reason")
        round_obj.unflag()
        assert round_obj.is_flagged is False
        assert round_obj.flag_reason == ""

    def test_str_with_date_and_flag(self) -> None:
        """Test string representation with date and flag."""
        round_obj = Round(id="123", event_id="456", name="Round 1")
        round_obj.date = datetime(2023, 6, 15)
        round_obj.flag("Test issue")
        assert str(round_obj) == "Round 1 (2023-06-15) [FLAGGED]"

    def test_str_no_date(self) -> None:
        """Test string representation without date."""
        round_obj = Round(id="123", event_id="456", name="Round 1")
        assert str(round_obj) == "Round 1 (No Date)"
