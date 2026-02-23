"""Tests for timer_infractions module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.timer_infractions import timer_infractions, timer_infractions_range

SAMPLE_CSV = (
    "entity_id,entity_name,year,pitches,all_violations,"
    "pitcher_timer,batter_timer,batter_timeout,catcher_timer,defensive_shift\n"
    '543037,"Cole, Gerrit",2024,3200,5,3,1,0,1,0\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestTimerInfractions:
    @patch("savant_extras.timer_infractions.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = timer_infractions(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.timer_infractions.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        timer_infractions(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.timer_infractions.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert timer_infractions(2024).empty


class TestTimerInfractionsRange:
    @patch("savant_extras.timer_infractions.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = timer_infractions_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.timer_infractions.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        timer_infractions_range(2023, 2024)
        assert mock_get.call_count == 2

    @patch("savant_extras.timer_infractions.time.sleep")
    @patch("savant_extras.timer_infractions.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        timer_infractions_range(2023, 2024)
        assert mock_sleep.call_count == 1
