#!/usr/bin/env python3
"""Simple startup script for the TGA Scoring Audit web interface."""

import os
import sys
from app import app

def main():
    print("=== TGA Scoring Audit Web Interface ===")
    print("Starting web server...")
    print("")
    print("Once started, open your web browser and go to:")
    print("  http://localhost:5000")
    print("")
    print("To stop the server, press Ctrl+C")
    print("")
    print("=" * 50)
    
    try:
        # Run the Flask app
        app.run(
            debug=False,  # Set to False for team use
            host='0.0.0.0',  # Allow access from other machines on network
            port=5000,
            use_reloader=False  # Disable auto-reload for stability
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()