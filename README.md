# TGA Scoring Audit

Automated Golf Genius API integration for identifying scoring issues across golf leagues.

## Overview

This tool analyzes golf scoring data from Golf Genius to identify rounds with incomplete scoring (missing front 9 or back 9 scores). It helps golf league administrators quickly identify rounds that may need attention.

## Features

- **Automated API Integration**: Seamlessly connects to Golf Genius API v2
- **Season Selection**: Interactive season selection from available options
- **Date Range Filtering**: Filter rounds by specific date ranges
- **Scoring Analysis**: Identifies incomplete scoring patterns (front 9 vs back 9)
- **Detailed Reporting**: Clear output with flagged rounds and reasons

## Prerequisites

- Python 3.12+
- Golf Genius API key (contact Golf Genius Support for access)
- Internet connection for API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TGAScoringAudit
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### Environment Variable (Optional)

You can set your API key as an environment variable:
```bash
export GOLF_GENIUS_API_KEY="your_api_key_here"
python main.py
```

### Interactive Workflow

1. **API Key Entry**: Enter your Golf Genius API key when prompted
2. **Season Selection**: Choose from available seasons
3. **Date Range**: Specify start and end dates for analysis
4. **Analysis**: The tool will process all rounds in the date range
5. **Results**: View flagged rounds with details about scoring issues

### Example Output

```
=== TGA Scoring Audit ===
Automated Golf Genius scoring issue detection

Enter your Golf Genius API key: ****
Testing API connection...
✓ Successfully connected to Golf Genius API

Fetching available seasons...
Available seasons:
1. 2023 Summer League (2023)
2. 2023 Fall League (2023)
3. 2024 Spring League (2024)

Select a season (1-3): 3
Selected season: 2024 Spring League (2024)

Fetching events for selected season...
Found 15 events

Collecting rounds from all events...
Found 120 total rounds

Enter date range for analysis:
Start Enter date (YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format): 2024-03-01
End Enter date (YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format): 2024-03-31
Date range: 2024-03-01 to 2024-03-31

Filtered to 25 rounds in date range

Analyzing scoring data...
Analyzing round 1/25: Round 1
  → OK: Complete scoring: F9=4, B9=4 players
Analyzing round 2/25: Round 2
  → FLAGGED: Only front 9 scores found (3/4 players)
...

=== ANALYSIS COMPLETE ===
Found 3 rounds with potential scoring issues:

FLAGGED ROUNDS:
================================================================================
Event ID     Round ID     Date         Round Name           Issue
================================================================================
12345        67890        2024-03-15   Round 2              Only front 9 scores found (3/4 players)
12345        67891        2024-03-20   Round 3              Only back 9 scores found (2/4 players)
12346        67892        2024-03-25   Round 1              No scores found on either front or back 9
================================================================================

Total flagged rounds: 3

These rounds should be reviewed for scoring completeness.
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run unit tests
pytest tga_scoring_audit/tests/unit/ -v

# Run tests with coverage
pytest tga_scoring_audit/tests/unit/ -v --cov=tga_scoring_audit --cov-report=html
```

### Code Quality

```bash
# Linting and formatting
ruff check --fix .
ruff format .

# Type checking
mypy tga_scoring_audit --strict

# Security scanning
bandit -r tga_scoring_audit -ll
```

### Project Structure

```
tga_scoring_audit/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── api/
│   ├── client.py          # Base API client
│   └── golf_genius.py     # Golf Genius API implementation
├── models/
│   ├── season.py          # Season data model
│   ├── event.py           # Event data model
│   └── round.py           # Round data model
├── analysis/
│   └── scoring.py         # Scoring analysis logic
├── utils/
│   ├── date_helpers.py    # Date utility functions
│   └── validators.py      # Input validation
└── tests/
    └── unit/              # Unit tests
```

## API Documentation

The application uses Golf Genius API v2 with the following endpoints:

- `GET /api_v2/{api_key}/seasons` - Retrieve available seasons
- `GET /api_v2/{api_key}/events` - Retrieve events for a season
- `GET /api_v2/{api_key}/events/{event_id}/rounds` - Retrieve rounds for an event
- `GET /api_v2/{api_key}/events/{event_id}/rounds/{round_id}/tee_sheet` - Retrieve scoring data

## Troubleshooting

### Common Issues

1. **Authentication Error**: Verify your API key is correct and active
2. **Connection Issues**: Check internet connection and Golf Genius API status
3. **No Seasons Found**: Ensure your API key has access to seasons
4. **Date Format Errors**: Use YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY formats

### Getting Help

1. Check the error message for specific details
2. Verify your Golf Genius API key with their support team
3. Ensure you have the required permissions for API access

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass and code quality checks pass
6. Submit a pull request

## Support

For issues with:
- **Golf Genius API access**: Contact Golf Genius Support
- **Application bugs**: Create an issue in this repository
- **Feature requests**: Create an issue with detailed requirements