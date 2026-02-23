"""Tests for baserunning module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.baserunning import baserunning, baserunning_range

SAMPLE_CSV = (
    "player_id,entity_name,team_name,start_year,end_year,"
    "runner_runs_tot,runner_runs_XB,runner_runs_SBX\n"
    '665742,"Soto, Juan",Yankees,2024,2024,2.5,1.8,0.7\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestBaserunning:
    @patch("savant_extras.baserunning.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = baserunning(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.baserunning.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        baserunning(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.baserunning.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert baserunning(2024).empty


class TestBaserunningRange:
    @patch("savant_extras.baserunning.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = baserunning_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.baserunning.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        baserunning_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.baserunning.time.sleep")
    @patch("savant_extras.baserunning.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        baserunning_range(2022, 2024)
        assert mock_sleep.call_count == 2
