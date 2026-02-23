"""Tests for catcher_throwing module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.catcher_throwing import catcher_throwing, catcher_throwing_range

SAMPLE_CSV = (
    "player_id,player_name,team_name,start_year,end_year,sb_attempts,"
    "catcher_stealing_runs,caught_stealing_above_average,n_cs,rate_cs,"
    "est_cs_pct,pop_time,exchange_time,arm_strength\n"
    '663728,"Realmuto, J.T.",Phillies,2024,2024,80,3.1,5,20,0.25,0.30,1.92,0.72,82.5\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestCatcherThrowing:
    @patch("savant_extras.catcher_throwing.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_throwing(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.catcher_throwing.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_throwing(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.catcher_throwing.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert catcher_throwing(2024).empty


class TestCatcherThrowingRange:
    @patch("savant_extras.catcher_throwing.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_throwing_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.catcher_throwing.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_throwing_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.catcher_throwing.time.sleep")
    @patch("savant_extras.catcher_throwing.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_throwing_range(2022, 2024)
        assert mock_sleep.call_count == 2
