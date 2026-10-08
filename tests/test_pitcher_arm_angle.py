"""Tests for pitcher_arm_angle module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.pitcher_arm_angle import pitcher_arm_angle, pitcher_arm_angle_range

SAMPLE_CSV = (
    "pitcher,pitcher_name,pitch_hand,n_pitches,team_id,"
    "ball_angle,relative_release_ball_x,release_ball_z,"
    "relative_shoulder_x,shoulder_z\n"
    "543037,\"Cole, Gerrit\",R,3200,147,45.2,1.5,5.8,0.8,5.2\n"
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestPitcherArmAngle:
    @patch("requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitcher_arm_angle(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitcher_arm_angle(2024)
        url = mock_get.call_args[0][0]
        assert "season=2024" in url
        assert "year=" not in url

    @patch("requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert pitcher_arm_angle(2024).empty


class TestPitcherArmAngleRange:
    @patch("requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitcher_arm_angle_range(2023, 2024)
        assert "year" in df.columns

    @patch("requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitcher_arm_angle_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("time.sleep")
    @patch("requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitcher_arm_angle_range(2022, 2024)
        assert mock_sleep.call_count == 2
