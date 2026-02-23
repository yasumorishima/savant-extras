"""Tests for home_runs module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.home_runs import home_runs, home_runs_range

SAMPLE_CSV = (
    "player,player_id,team_abbrev,year,type,avg_hr_trot,doubters,"
    "mostly_gone,no_doubters,no_doubter_per,hr_total,xhr,xhr_diff\n"
    '"Judge, Aaron",592450,NYY,2024,adj_xhr,23.89,13,36,30,49.2,61,56.1,4.9\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestHomeRuns:
    @patch("savant_extras.home_runs.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = home_runs(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.home_runs.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        home_runs(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.home_runs.requests.get")
    def test_hr_type_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        home_runs(2024, hr_type="distance")
        url = mock_get.call_args[0][0]
        assert "type=distance" in url

    @patch("savant_extras.home_runs.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert home_runs(2024).empty

    @patch("savant_extras.home_runs.requests.get")
    def test_html_response(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html>")
        assert home_runs(2024).empty


class TestHomeRunsRange:
    @patch("savant_extras.home_runs.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = home_runs_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.home_runs.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        home_runs_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.home_runs.time.sleep")
    @patch("savant_extras.home_runs.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        home_runs_range(2022, 2024)
        assert mock_sleep.call_count == 2
