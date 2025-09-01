# TGA Scoring Audit - Web Interface

A user-friendly web interface for the TGA Scoring Audit tool that allows your team to easily identify scoring issues in Golf Genius leagues without needing command line access.

## Quick Start

### Option 1: Simple Startup
```bash
# Navigate to the project directory
cd /path/to/TGAScoringAudit

# Activate virtual environment
source venv/bin/activate

# Run the web interface
python run_web.py
```

### Option 2: Using Flask directly
```bash
# Navigate to the project directory
cd /path/to/TGAScoringAudit

# Activate virtual environment
source venv/bin/activate

# Run Flask app
python app.py
```

## Accessing the Interface

Once started, the web interface will be available at:
- **Local access**: http://localhost:5000
- **Team access**: http://[your-computer-ip]:5000

To find your computer's IP address:
```bash
# On Linux/Mac
hostname -I

# On Windows
ipconfig
```

## How to Use

### 1. Enter API Key
- Navigate to the web interface
- Enter your Golf Genius API key
- The system will test the connection automatically

### 2. Select Season
- Choose from the available seasons in your Golf Genius account
- Click on a season card to select it

### 3. Set Date Range
- Use the date pickers or quick preset buttons
- Choose the time period you want to analyze

### 4. Run Analysis
- Click "Start Analysis" to begin
- Watch the progress bar as the system processes your data
- The analysis runs automatically in the background

### 5. Review Results
- View flagged rounds in an organized table
- Click "View Scorecard" to go directly to problematic rounds in Golf Genius
- Download results as CSV for further analysis

## Features

✅ **No Command Line Required** - Pure point-and-click interface
✅ **Real-time Progress** - Visual progress indicators during analysis
✅ **Team Sharing** - Multiple people can access the same interface
✅ **CSV Export** - Download results for reporting
✅ **Direct Links** - Click to go straight to problem scorecards
✅ **Session Management** - Keep your work as you navigate
✅ **Responsive Design** - Works on desktop and mobile devices

## Requirements

- Valid Golf Genius API key
- Python environment with dependencies installed (see requirements.txt)
- Web browser (Chrome, Firefox, Safari, Edge)

## Troubleshooting

### Can't Connect to Golf Genius
- Verify your API key is correct
- Check your internet connection
- Ensure your organization has API access enabled

### Web Interface Won't Load
- Check that the Flask server is running
- Verify the port (5000) is not blocked by firewall
- Try accessing via localhost first: http://localhost:5000

### Analysis Fails
- Verify you have access to the selected season
- Check that the date range contains actual rounds
- Ensure your API key has sufficient permissions

## Security Notes

- API keys are stored temporarily in browser sessions only
- No permanent storage of credentials
- Session data is cleared when you close the browser
- Use "Start Over" button to clear all data

## For Development

To run in development mode with auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your Golf Genius API access
3. Contact your system administrator for network/firewall issues