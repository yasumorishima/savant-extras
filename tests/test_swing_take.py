"""Tests for swing_take module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras.swing_take import swing_take, swing_take_range

SAMPLE_CSV = (
    "year,\"last_name, first_name\",player_id,team_id,pa,pitches,"
    "runs_all,runs_heart,runs_shadow,runs_chase,runs_waste\n"
    '2024,"Soto, Juan",665742,147,700,2800,15.2,8.1,3.5,2.8,0.8\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestSwingTake:
    @patch("savant_extras.swing_take.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = swing_take(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.swing_take.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        swing_take(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.swing_take.requests.get")
    def test_player_type_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        swing_take(2024, player_type="pitcher")
        url = mock_get.call_args[0][0]
        assert "type=pitcher" in url

    def test_invalid_player_type(self):
        with pytest.raises(ValueError):
            swing_take(2024, player_type="team")

    @patch("savant_extras.swing_take.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert swing_take(2024).empty


class TestSwingTakeRange:
    @patch("savant_extras.swing_take.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = swing_take_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.swing_take.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        swing_take_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.swing_take.time.sleep")
    @patch("savant_extras.swing_take.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        swing_take_range(2022, 2024)
        assert mock_sleep.call_count == 2
