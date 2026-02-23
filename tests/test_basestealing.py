"""Tests for basestealing module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.basestealing import basestealing, basestealing_range

SAMPLE_CSV = (
    "player_id,player_name,team_name,start_year,end_year,"
    "key_target_base,runs_stolen_on_running_act,n_init,rate_sbx,n_sb,n_cs\n"
    '665742,"Soto, Juan",Yankees,2024,2024,2B,1.2,30,0.83,25,5\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestBasestealing:
    @patch("savant_extras.basestealing.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = basestealing(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.basestealing.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        basestealing(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.basestealing.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert basestealing(2024).empty


class TestBasestealingRange:
    @patch("savant_extras.basestealing.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = basestealing_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.basestealing.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        basestealing_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.basestealing.time.sleep")
    @patch("savant_extras.basestealing.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        basestealing_range(2022, 2024)
        assert mock_sleep.call_count == 2
