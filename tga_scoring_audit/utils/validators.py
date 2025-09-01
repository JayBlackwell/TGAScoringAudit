"""Validation utility functions."""

from typing import List, Dict, Any


def validate_non_empty_string(value: Any, field_name: str) -> str:
    """Validate that a value is a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def validate_selection_index(selection: str, max_index: int) -> int:
    """Validate user selection index input."""
    try:
        index = int(selection.strip())
        if index < 1 or index > max_index:
            raise ValueError(f"Selection must be between 1 and {max_index}")
        return index - 1  # Convert to 0-based index
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Selection must be a number")
        raise


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format (basic checks)."""
    if not isinstance(api_key, str):
        return False

    api_key = api_key.strip()

    # Basic validation: non-empty, reasonable length
    if len(api_key) < 10:
        return False

    # Check for obviously invalid characters (spaces, special chars that shouldn't be in API keys)
    if " " in api_key or "\n" in api_key or "\t" in api_key:
        return False

    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that dictionary contains all required fields."""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


def validate_list_not_empty(data: List[Any], item_name: str) -> None:
    """Validate that a list is not empty."""
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"No {item_name} found")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    # Remove or replace characters that are invalid in filenames
    invalid_chars = '<>:"/\\|?*'
    sanitized = filename

    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "output"

    return sanitized
