"""Main TGA Scoring Audit application."""

import sys
import csv
from typing import List, Optional, Dict
from datetime import datetime

from .config import Config
from .api.golf_genius import GolfGeniusAPI
from .api import AuthenticationError
from .models.season import Season
from .models.event import Event
from .models.round import Round
from .analysis.scoring import ScoringAnalyzer
from .utils.date_helpers import (
    validate_date_range,
    is_date_in_range,
    format_date_for_display,
    get_date_input_prompt,
)
from .utils.validators import validate_selection_index, validate_list_not_empty


class TGAScoringAudit:
    """Main application class for TGA Scoring Audit."""

    def __init__(self) -> None:
        self.config = Config()
        self.api: Optional[GolfGeniusAPI] = None
        self.analyzer = ScoringAnalyzer()

    def run(self) -> None:
        """Run the main application workflow."""
        print("=== TGA Scoring Audit ===")
        print("Automated Golf Genius scoring issue detection\n")

        try:
            # Step 1: Setup and authentication
            self._setup_api_connection()

            # Step 2: Season selection
            selected_season = self._select_season()
            print(f"Selected season: {selected_season}\n")

            # Step 3: Event discovery
            print("Fetching events for selected season...")
            events = self._fetch_events(selected_season.id)
            print(f"Found {len(events)} events\n")

            # Step 4: Round collection
            print("Collecting rounds from all events...")
            rounds = self._collect_rounds(events)
            print(f"Found {len(rounds)} total rounds\n")

            # Step 5: Date range filtering
            start_date, end_date = self._get_date_range()
            filtered_rounds = self._filter_rounds_by_date(rounds, start_date, end_date)
            print(f"Filtered to {len(filtered_rounds)} rounds in date range\n")

            if not filtered_rounds:
                print("No rounds found in the specified date range.")
                return

            # Step 6: Scoring analysis
            print("Analyzing scoring data...")
            flagged_rounds = self._analyze_scoring(filtered_rounds)

            # Step 7: Results output
            self._output_results(flagged_rounds)

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        finally:
            if self.api:
                self.api.close()

    def _setup_api_connection(self) -> None:
        """Setup and test API connection."""
        # Get API key from user
        api_key = input("Enter your Golf Genius API key: ").strip()

        if not api_key:
            raise ValueError("API key is required")

        # Configure and test connection
        self.config.set_api_key(api_key)
        self.api = GolfGeniusAPI(self.config)

        print("Testing API connection...")
        if not self.api.test_connection():
            raise AuthenticationError(
                "Failed to connect to Golf Genius API. Please check your API key."
            )

        print("✓ Successfully connected to Golf Genius API\n")

    def _select_season(self) -> Season:
        """Allow user to select a season."""
        if not self.api:
            raise RuntimeError("API not initialized")

        print("Fetching available seasons...")
        seasons_data = self.api.get_seasons()
        validate_list_not_empty(seasons_data, "seasons")

        seasons = [Season.from_api_response(data) for data in seasons_data]

        # Display seasons for selection
        print("\nAvailable seasons:")
        for i, season in enumerate(seasons, 1):
            print(f"{i}. {season}")

        # Get user selection
        while True:
            try:
                selection = input(f"\nSelect a season (1-{len(seasons)}): ").strip()
                index = validate_selection_index(selection, len(seasons))
                return seasons[index]
            except ValueError as e:
                print(f"Invalid selection: {e}")
                continue

    def _fetch_events(self, season_id: str) -> List[Event]:
        """Fetch all events for the selected season."""
        if not self.api:
            raise RuntimeError("API not initialized")

        events_data = self.api.get_all_events(season_id)
        return [Event.from_api_response(data) for data in events_data]

    def _collect_rounds(self, events: List[Event]) -> List[Round]:
        """Collect all rounds from all events."""
        if not self.api:
            raise RuntimeError("API not initialized")

        all_rounds = []
        total_events = len(events)

        for i, event in enumerate(events, 1):
            print(f"Processing event {i}/{total_events}: {event.name}")

            try:
                rounds_data = self.api.get_rounds(event.id)
                rounds = [
                    Round.from_api_response(data, event.id) for data in rounds_data
                ]
                all_rounds.extend(rounds)

            except Exception as e:
                print(f"  Warning: Failed to fetch rounds for event {event.name}: {e}")
                continue

        return all_rounds

    def _get_date_range(self) -> tuple[datetime, datetime]:
        """Get date range from user input."""
        print("Enter date range for analysis:")

        while True:
            try:
                start_input = input(f"Start {get_date_input_prompt()}").strip()
                end_input = input(f"End {get_date_input_prompt()}").strip()

                start_date, end_date = validate_date_range(start_input, end_input)

                print(
                    f"Date range: {format_date_for_display(start_date)} to {format_date_for_display(end_date)}\n"
                )
                return start_date, end_date

            except ValueError as e:
                print(f"Invalid date range: {e}")
                continue

    def _filter_rounds_by_date(
        self, rounds: List[Round], start_date: datetime, end_date: datetime
    ) -> List[Round]:
        """Filter rounds to those within the specified date range."""
        filtered = []
        for round_obj in rounds:
            if is_date_in_range(round_obj.date, start_date, end_date):
                filtered.append(round_obj)
        return filtered

    def _analyze_scoring(self, rounds: List[Round]) -> List[Round]:
        """Analyze scoring for each round and flag incomplete ones."""
        if not self.api:
            raise RuntimeError("API not initialized")

        flagged_rounds = []
        total_rounds = len(rounds)

        for i, round_obj in enumerate(rounds, 1):
            print(f"Analyzing round {i}/{total_rounds}: {round_obj.name}")

            try:
                # Fetch tee sheet data
                tee_sheet_data = self.api.get_tee_sheet(
                    round_obj.event_id, round_obj.id
                )

                # Analyze scoring
                is_flagged, reason = self.analyzer.analyze_round_scoring(tee_sheet_data)

                if is_flagged:
                    round_obj.flag(reason)
                    flagged_rounds.append(round_obj)
                    print(f"  → FLAGGED: {reason}")
                else:
                    print(f"  → OK: {reason}")

            except Exception as e:
                # Flag rounds where we can't get scoring data
                round_obj.flag(f"Unable to retrieve scoring data: {str(e)}")
                flagged_rounds.append(round_obj)
                print(f"  → FLAGGED: Unable to analyze - {e}")
                continue

        return flagged_rounds

    def _output_results(self, flagged_rounds: List[Round]) -> None:
        """Output the final results to console and CSV file."""
        print("\n=== ANALYSIS COMPLETE ===")
        print(f"Found {len(flagged_rounds)} rounds with potential scoring issues:\n")

        if not flagged_rounds:
            print("No scoring issues detected!")
            return

        # Generate CSV filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"tga_scoring_audit_{timestamp}.csv"

        # Write results to CSV file
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Event ID', 'Round ID', 'Date', 'Round Name', 'Issue', 'Scorecard URL'])
                
                # Write data rows
                for round_obj in flagged_rounds:
                    date_str = format_date_for_display(round_obj.date)
                    scorecard_url = f"https://www.golfgenius.com/leagues/{round_obj.event_id}/rounds/{round_obj.id}/scorecards"
                    writer.writerow([
                        round_obj.event_id,
                        round_obj.id,
                        date_str,
                        round_obj.name,
                        round_obj.flag_reason,
                        scorecard_url
                    ])
            
            print(f"✓ Results exported to: {csv_filename}")
            
        except Exception as e:
            print(f"Warning: Failed to write CSV file: {e}")

        # Also display results on console
        print("\nFLAGGED ROUNDS:")
        print("=" * 80)
        print(
            f"{'Event ID':<12} {'Round ID':<12} {'Date':<12} {'Round Name':<20} {'Issue'}"
        )
        print("=" * 80)

        for round_obj in flagged_rounds:
            date_str = format_date_for_display(round_obj.date)
            print(
                f"{round_obj.event_id:<12} {round_obj.id:<12} {date_str:<12} {round_obj.name[:20]:<20} {round_obj.flag_reason}"
            )

        print("=" * 80)
        print(f"\nTotal flagged rounds: {len(flagged_rounds)}")
        print(f"Results saved to: {csv_filename}")
        print("\nThese rounds should be reviewed for scoring completeness.")


def main() -> None:
    """Entry point for the application."""
    app = TGAScoringAudit()
    app.run()


if __name__ == "__main__":
    main()
