"""Tests for catcher_blocking module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.catcher_blocking import catcher_blocking, catcher_blocking_range

SAMPLE_CSV = (
    "player_id,player_name,team_name,start_year,end_year,pitches,"
    "catcher_blocking_runs,blocks_above_average,n_pbwp,x_pbwp\n"
    '663728,"Realmuto, J.T.",Phillies,2024,2024,12000,5.2,15,30,42.5\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestCatcherBlocking:
    @patch("savant_extras.catcher_blocking.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_blocking(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.catcher_blocking.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_blocking(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.catcher_blocking.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert catcher_blocking(2024).empty


class TestCatcherBlockingRange:
    @patch("savant_extras.catcher_blocking.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_blocking_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.catcher_blocking.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_blocking_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.catcher_blocking.time.sleep")
    @patch("savant_extras.catcher_blocking.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_blocking_range(2022, 2024)
        assert mock_sleep.call_count == 2
