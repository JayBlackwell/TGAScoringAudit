"""Unit tests for scoring analysis."""

from tga_scoring_audit.analysis.scoring import ScoringAnalyzer


class TestScoringAnalyzer:
    """Test scoring analysis functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.analyzer = ScoringAnalyzer()

    def test_analyze_empty_data(self) -> None:
        """Test analysis with empty tee sheet data."""
        is_flagged, reason = self.analyzer.analyze_round_scoring([])
        assert is_flagged is True
        assert "No tee sheet data available" in reason

    def test_analyze_complete_scores(self) -> None:
        """Test analysis with complete front and back 9 scores."""
        tee_sheet_data = [
            {
                "players": [
                        {
                            "name": "Test Player",
                            "scores": [
                                4,
                                5,
                                3,
                                4,
                                5,
                                4,
                                4,
                                3,
                                5,
                                4,
                                4,
                                5,
                                3,
                                4,
                                4,
                                5,
                                4,
                                3,
                            ],
                        }
                ]
            }
        ]

        is_flagged, reason = self.analyzer.analyze_round_scoring(tee_sheet_data)
        assert is_flagged is False
        assert "Complete scoring" in reason

    def test_analyze_front_9_only(self) -> None:
        """Test analysis with only front 9 scores."""
        tee_sheet_data = [
            {
                "players": [
                        {
                            "name": "Test Player",
                            "scores": [
                                4,
                                5,
                                3,
                                4,
                                5,
                                4,
                                4,
                                3,
                                5,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                            ],
                        }
                ]
            }
        ]

        is_flagged, reason = self.analyzer.analyze_round_scoring(tee_sheet_data)
        assert is_flagged is True
        assert "Only front 9 scores found" in reason

    def test_analyze_back_9_only(self) -> None:
        """Test analysis with only back 9 scores."""
        tee_sheet_data = [
            {
                "players": [
                        {
                            "name": "Test Player",
                            "scores": [
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                4,
                                4,
                                5,
                                3,
                                4,
                                4,
                                5,
                                4,
                                3,
                            ],
                        }
                ]
            }
        ]

        is_flagged, reason = self.analyzer.analyze_round_scoring(tee_sheet_data)
        assert is_flagged is True
        assert "Only back 9 scores found" in reason

    def test_analyze_no_scores(self) -> None:
        """Test analysis with no valid scores."""
        tee_sheet_data = [
            {
                "players": [{"name": "Test Player", "scores": [None] * 18}]
            }
        ]

        is_flagged, reason = self.analyzer.analyze_round_scoring(tee_sheet_data)
        assert is_flagged is True
        assert "No scores found" in reason

    def test_has_valid_scores_with_valid_data(self) -> None:
        """Test has_valid_scores with valid score data."""
        scores = [4, 5, 3, None, 6]
        assert self.analyzer._has_valid_scores(scores) is True

    def test_has_valid_scores_with_no_valid_data(self) -> None:
        """Test has_valid_scores with no valid score data."""
        scores = [None, "", 0, None]
        assert self.analyzer._has_valid_scores(scores) is False

    def test_has_valid_scores_empty_list(self) -> None:
        """Test has_valid_scores with empty list."""
        assert self.analyzer._has_valid_scores([]) is False

    def test_extract_players_standard_format(self) -> None:
        """Test player extraction with standard format."""
        pairing_group = {"players": [{"name": "Player 1"}, {"name": "Player 2"}]}
        players = self.analyzer._extract_players(pairing_group)
        assert len(players) == 2
        assert players[0]["name"] == "Player 1"

    def test_extract_players_alternative_formats(self) -> None:
        """Test player extraction with alternative formats."""
        # Test with 'player' key (singular)
        pairing_group = {"player": {"name": "Single Player"}}
        players = self.analyzer._extract_players(pairing_group)
        assert len(players) == 1
        assert players[0]["name"] == "Single Player"

    def test_extract_scores_standard_format(self) -> None:
        """Test score extraction with standard format."""
        player = {"scores": [4, 5, 3, 4, 5]}
        scores = self.analyzer._extract_scores(player)
        assert scores == [4, 5, 3, 4, 5]

    def test_extract_scores_no_scores(self) -> None:
        """Test score extraction when no scores present."""
        player = {"name": "Test Player"}
        scores = self.analyzer._extract_scores(player)
        assert scores == []

    def test_get_detailed_analysis(self) -> None:
        """Test detailed analysis functionality."""
        tee_sheet_data = [
            {
                "players": [
                        {
                            "name": "Complete Player",
                            "scores": [
                                4,
                                5,
                                3,
                                4,
                                5,
                                4,
                                4,
                                3,
                                5,
                                4,
                                4,
                                5,
                                3,
                                4,
                                4,
                                5,
                                4,
                                3,
                            ],
                        },
                        {
                            "name": "Front 9 Only",
                            "scores": [
                                4,
                                5,
                                3,
                                4,
                                5,
                                4,
                                4,
                                3,
                                5,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                            ],
                        },
                ]
            }
        ]

        analysis = self.analyzer.get_detailed_analysis(tee_sheet_data)
        assert analysis["total_players"] == 2
        assert analysis["complete_players"] == 1
        assert analysis["incomplete_players"] == 1
        assert analysis["front_9_players"] == 2
        assert analysis["back_9_players"] == 1
