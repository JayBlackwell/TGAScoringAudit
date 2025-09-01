"""Unit tests for utility functions."""

import pytest
from datetime import datetime

from tga_scoring_audit.utils.date_helpers import (
    parse_date,
    validate_date_range,
    is_date_in_range,
    format_date_for_display,
    get_date_input_prompt,
)
from tga_scoring_audit.utils.validators import (
    validate_non_empty_string,
    validate_selection_index,
    validate_api_key_format,
    validate_required_fields,
    validate_list_not_empty,
    sanitize_filename,
)


class TestDateHelpers:
    """Test date helper functions."""

    def test_parse_date_iso_format(self) -> None:
        """Test parsing ISO format date."""
        result = parse_date("2023-06-15")
        assert result is not None
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15

    def test_parse_date_us_format(self) -> None:
        """Test parsing US format date."""
        result = parse_date("06/15/2023")
        assert result is not None
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15

    def test_parse_date_invalid(self) -> None:
        """Test parsing invalid date."""
        result = parse_date("invalid-date")
        assert result is None

    def test_parse_date_empty(self) -> None:
        """Test parsing empty date."""
        result = parse_date("")
        assert result is None

    def test_validate_date_range_valid(self) -> None:
        """Test valid date range."""
        start, end = validate_date_range("2023-06-01", "2023-06-30")
        assert start.year == 2023
        assert start.month == 6
        assert start.day == 1
        assert end.day == 30

    def test_validate_date_range_invalid_start(self) -> None:
        """Test date range with invalid start date."""
        with pytest.raises(ValueError, match="Invalid start date"):
            validate_date_range("invalid", "2023-06-30")

    def test_validate_date_range_start_after_end(self) -> None:
        """Test date range where start is after end."""
        with pytest.raises(ValueError, match="Start date must be before end date"):
            validate_date_range("2023-06-30", "2023-06-01")

    def test_is_date_in_range_true(self) -> None:
        """Test date is in range."""
        start = datetime(2023, 6, 1)
        end = datetime(2023, 6, 30)
        check = datetime(2023, 6, 15)
        assert is_date_in_range(check, start, end) is True

    def test_is_date_in_range_false(self) -> None:
        """Test date is not in range."""
        start = datetime(2023, 6, 1)
        end = datetime(2023, 6, 30)
        check = datetime(2023, 7, 15)
        assert is_date_in_range(check, start, end) is False

    def test_is_date_in_range_none(self) -> None:
        """Test date in range with None date."""
        start = datetime(2023, 6, 1)
        end = datetime(2023, 6, 30)
        assert is_date_in_range(None, start, end) is False

    def test_format_date_for_display(self) -> None:
        """Test date formatting for display."""
        dt = datetime(2023, 6, 15)
        result = format_date_for_display(dt)
        assert result == "2023-06-15"

    def test_format_date_for_display_none(self) -> None:
        """Test date formatting for display with None."""
        result = format_date_for_display(None)
        assert result == "No Date"

    def test_get_date_input_prompt(self) -> None:
        """Test date input prompt."""
        prompt = get_date_input_prompt()
        assert "date" in prompt.lower()
        assert "YYYY-MM-DD" in prompt


class TestValidators:
    """Test validator functions."""

    def test_validate_non_empty_string_valid(self) -> None:
        """Test valid non-empty string."""
        result = validate_non_empty_string("test", "field")
        assert result == "test"

    def test_validate_non_empty_string_strips_whitespace(self) -> None:
        """Test string validation strips whitespace."""
        result = validate_non_empty_string("  test  ", "field")
        assert result == "test"

    def test_validate_non_empty_string_empty(self) -> None:
        """Test empty string validation."""
        with pytest.raises(ValueError, match="field must be a non-empty string"):
            validate_non_empty_string("", "field")

    def test_validate_non_empty_string_whitespace_only(self) -> None:
        """Test whitespace-only string validation."""
        with pytest.raises(ValueError, match="field must be a non-empty string"):
            validate_non_empty_string("   ", "field")

    def test_validate_selection_index_valid(self) -> None:
        """Test valid selection index."""
        result = validate_selection_index("3", 5)
        assert result == 2  # 0-based index

    def test_validate_selection_index_out_of_range(self) -> None:
        """Test selection index out of range."""
        with pytest.raises(ValueError, match="Selection must be between 1 and 5"):
            validate_selection_index("6", 5)

    def test_validate_selection_index_not_number(self) -> None:
        """Test selection index not a number."""
        with pytest.raises(ValueError, match="Selection must be a number"):
            validate_selection_index("abc", 5)

    def test_validate_api_key_format_valid(self) -> None:
        """Test valid API key format."""
        assert validate_api_key_format("test_api_key_123456") is True

    def test_validate_api_key_format_too_short(self) -> None:
        """Test API key too short."""
        assert validate_api_key_format("short") is False

    def test_validate_api_key_format_has_spaces(self) -> None:
        """Test API key with spaces."""
        assert validate_api_key_format("key with spaces") is False

    def test_validate_required_fields_valid(self) -> None:
        """Test valid required fields."""
        data = {"id": "123", "name": "test"}
        validate_required_fields(data, ["id", "name"])  # Should not raise

    def test_validate_required_fields_missing(self) -> None:
        """Test missing required fields."""
        data = {"id": "123"}
        with pytest.raises(ValueError, match="Missing required fields: name"):
            validate_required_fields(data, ["id", "name"])

    def test_validate_list_not_empty_valid(self) -> None:
        """Test valid non-empty list."""
        validate_list_not_empty([1, 2, 3], "items")  # Should not raise

    def test_validate_list_not_empty_empty(self) -> None:
        """Test empty list."""
        with pytest.raises(ValueError, match="No items found"):
            validate_list_not_empty([], "items")

    def test_sanitize_filename_valid(self) -> None:
        """Test filename sanitization with valid name."""
        result = sanitize_filename("test_file.txt")
        assert result == "test_file.txt"

    def test_sanitize_filename_invalid_chars(self) -> None:
        """Test filename sanitization with invalid characters."""
        result = sanitize_filename("test<>file?.txt")
        assert result == "test__file_.txt"

    def test_sanitize_filename_empty(self) -> None:
        """Test filename sanitization with empty string."""
        result = sanitize_filename("")
        assert result == "output"
