"""Scoring analysis engine for detecting incomplete rounds."""

from typing import List, Dict, Any, Tuple


class ScoringAnalyzer:
    """Analyzes golf scoring data to identify potential issues."""

    def analyze_round_scoring(
        self, tee_sheet_data: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Analyze if a round has incomplete scoring on front/back 9.

        Args:
            tee_sheet_data: List of pairing groups with player data

        Returns:
            Tuple of (is_flagged, reason)

        Based on PRP specification:
        - We need to know when at least one score has been entered on holes 1-9
        - And at least one score has been entered on holes 10-18
        - Flag if only one side has scores (incomplete round)
        """
        if not tee_sheet_data:
            return True, "No tee sheet data available"

        total_front_9_scores = 0
        total_back_9_scores = 0
        total_players = 0

        try:
            for item in tee_sheet_data:
                if not isinstance(item, dict):
                    continue

                # Extract pairing_group from the wrapper if present
                if "pairing_group" in item:
                    pairing_group = item["pairing_group"]
                else:
                    pairing_group = item

                # Handle different possible structures
                players = self._extract_players(pairing_group)

                for player in players:
                    if not isinstance(player, dict):
                        continue

                    total_players += 1
                    scores = self._extract_scores(player)

                    if len(scores) >= 18:
                        front_9_scores = scores[0:9]
                        back_9_scores = scores[9:18]

                        # Check if front 9 has at least one valid score
                        if self._has_valid_scores(front_9_scores):
                            total_front_9_scores += 1

                        # Check if back 9 has at least one valid score
                        if self._has_valid_scores(back_9_scores):
                            total_back_9_scores += 1

        except Exception as e:
            return True, f"Error analyzing scores: {str(e)}"

        # Analysis logic
        if total_players == 0:
            return False, "No players found in tee sheet"

        # Flag if we have scores for BOTH sides of the course (complete rounds)
        has_front_9_scores = total_front_9_scores > 0
        has_back_9_scores = total_back_9_scores > 0

        if has_front_9_scores and has_back_9_scores:
            return (
                True,
                f"Complete scoring detected: F9={total_front_9_scores}, B9={total_back_9_scores} players",
            )

        # Don't flag incomplete rounds
        if has_front_9_scores and not has_back_9_scores:
            return (
                False,
                f"Only front 9 scores found ({total_front_9_scores}/{total_players} players)",
            )

        if has_back_9_scores and not has_front_9_scores:
            return (
                False,
                f"Only back 9 scores found ({total_back_9_scores}/{total_players} players)",
            )

        if not has_front_9_scores and not has_back_9_scores:
            return False, "No scores found on either front or back 9"

        # Should not reach here, but just in case
        return False, "Unexpected scoring state"

    def _extract_players(self, pairing_group: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract players list from pairing group, handling different structures."""
        # Try different possible keys for players data
        for key in ["players", "player", "pairing", "members"]:
            if key in pairing_group:
                players_data = pairing_group[key]
                if isinstance(players_data, list):
                    return players_data
                elif isinstance(players_data, dict):
                    return [players_data]

        # If pairing_group itself looks like a player, return it
        if "name" in pairing_group or "scores" in pairing_group:
            return [pairing_group]

        return []

    def _extract_scores(self, player: Dict[str, Any]) -> List[Any]:
        """Extract scores from player data, handling different structures."""
        # Try different possible keys for scores
        for key in ["score_array", "scores", "score", "holes", "hole_scores"]:
            if key in player:
                scores_data = player[key]
                if isinstance(scores_data, list):
                    return scores_data

        return []

    def _has_valid_scores(self, scores: List[Any]) -> bool:
        """Check if score list has at least one valid (non-null, non-empty) score."""
        for score in scores:
            # Skip empty objects, None, empty strings, and zero
            if score is None or score == "" or score == 0 or score == {}:
                continue
                
            # Skip empty dictionaries or objects
            if isinstance(score, dict) and not score:
                continue
                
            # Additional validation: score should be a reasonable golf score
            try:
                score_int = int(score)
                if 1 <= score_int <= 15:  # Reasonable golf score range
                    return True
            except (ValueError, TypeError):
                # If it's not a number but also not None/empty, might be valid
                if str(score).strip() and str(score) != "{}":
                    return True

        return False

    def get_detailed_analysis(
        self, tee_sheet_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get detailed analysis of the round scoring."""
        if not tee_sheet_data:
            return {
                "total_players": 0,
                "front_9_players": 0,
                "back_9_players": 0,
                "complete_players": 0,
                "incomplete_players": 0,
                "is_flagged": True,
                "flag_reason": "No tee sheet data available",
            }

        total_players = 0
        front_9_players = 0
        back_9_players = 0
        complete_players = 0

        try:
            for item in tee_sheet_data:
                if not isinstance(item, dict):
                    continue

                # Extract pairing_group from the wrapper if present
                if "pairing_group" in item:
                    pairing_group = item["pairing_group"]
                else:
                    pairing_group = item

                players = self._extract_players(pairing_group)

                for player in players:
                    if not isinstance(player, dict):
                        continue

                    total_players += 1
                    scores = self._extract_scores(player)

                    if len(scores) >= 18:
                        front_9_scores = scores[0:9]
                        back_9_scores = scores[9:18]

                        has_front_9 = self._has_valid_scores(front_9_scores)
                        has_back_9 = self._has_valid_scores(back_9_scores)

                        if has_front_9:
                            front_9_players += 1
                        if has_back_9:
                            back_9_players += 1
                        if has_front_9 and has_back_9:
                            complete_players += 1

        except Exception as e:
            return {
                "total_players": 0,
                "front_9_players": 0,
                "back_9_players": 0,
                "complete_players": 0,
                "incomplete_players": 0,
                "is_flagged": True,
                "flag_reason": f"Error analyzing scores: {str(e)}",
            }

        incomplete_players = total_players - complete_players
        is_flagged, flag_reason = self.analyze_round_scoring(tee_sheet_data)

        return {
            "total_players": total_players,
            "front_9_players": front_9_players,
            "back_9_players": back_9_players,
            "complete_players": complete_players,
            "incomplete_players": incomplete_players,
            "is_flagged": is_flagged,
            "flag_reason": flag_reason,
        }
