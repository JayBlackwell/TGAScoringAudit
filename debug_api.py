#!/usr/bin/env python3
"""Debug script to test Golf Genius API endpoints."""

import sys
import json
from tga_scoring_audit.config import Config
from tga_scoring_audit.api.golf_genius import GolfGeniusAPI

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_api.py <api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Setup config and API
    config = Config()
    config.set_api_key(api_key)
    api = GolfGeniusAPI(config)
    
    try:
        print("Testing API connection...")
        if not api.test_connection():
            print("❌ API connection failed")
            return
        print("✅ API connection successful")
        
        print("\n--- Testing Seasons ---")
        seasons = api.get_seasons()
        print(f"Found {len(seasons)} seasons:")
        for i, season in enumerate(seasons[:3]):  # Show first 3
            print(f"  {i+1}. {season.get('name', 'No name')} (ID: {season.get('id', 'No ID')})")
        
        if not seasons:
            print("No seasons found - can't test events")
            return
            
        # Use first season for testing
        season_id = seasons[0].get('id')
        print(f"\n--- Testing Events for Season {season_id} ---")
        
        # Test single page first
        print("Testing single page of events...")
        events_response = api.get_events(season_id, page=1)
        print(f"Response type: {type(events_response)}")
        print(f"Response keys: {list(events_response.keys()) if isinstance(events_response, dict) else 'Not a dict'}")
        
        events = events_response.get('events', [])
        print(f"Events in first page: {len(events)}")
        
        if events:
            print("First event:")
            print(f"  Name: {events[0].get('name', 'No name')}")
            print(f"  ID: {events[0].get('id', 'No ID')}")
        
        # Test get_all_events
        print("\n--- Testing get_all_events ---")
        all_events = api.get_all_events(season_id)
        print(f"Total events found: {len(all_events)}")
        
        # Check pagination info
        if len(events) > 0 and len(all_events) != len(events):
            print(f"Pagination working: first page had {len(events)}, total is {len(all_events)}")
        elif len(events) == len(all_events):
            print("Either only one page, or pagination not working")
            
        # Test second page to see if there is one
        print("\nTesting page 2...")
        try:
            page2_response = api.get_events(season_id, page=2)
            page2_events = page2_response.get('events', [])
            print(f"Events in page 2: {len(page2_events)}")
        except Exception as e:
            print(f"Page 2 error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        api.close()

if __name__ == "__main__":
    main()