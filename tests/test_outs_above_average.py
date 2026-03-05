"""Tests for outs_above_average module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import outs_above_average, outs_above_average_range

SAMPLE_CSV = (
    '"last_name, first_name","player_id","display_team_name","year","primary_pos_formatted",'
    '"fielding_runs_prevented","outs_above_average","outs_above_average_infront",'
    '"outs_above_average_rhh","outs_above_average_lhh",'
    '"actual_success_rate_formatted","adj_estimated_success_rate_formatted","diff_success_rate_formatted"\n'
    '"Kiermaier, Kevin","595281","Blue Jays","2024","CF","10",8,3,5,3,"91%","88%","3%"\n'
    '"Bader, Harrison","664056","Mets","2024","CF","6",5,2,3,2,"89%","87%","2%"\n'
)


def _mock(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestOutsAboveAverage:
    @patch("savant_extras.outs_above_average.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outs_above_average(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.outs_above_average.requests.get")
    def test_oaa_column_present(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outs_above_average(2024)
        assert "outs_above_average" in df.columns

    @patch("savant_extras.outs_above_average.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outs_above_average(2023)
        url = mock_get.call_args[0][0]
        assert "startYear=2023" in url
        assert "endYear=2023" in url

    @patch("savant_extras.outs_above_average.requests.get")
    def test_default_min_q(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outs_above_average(2024)
        url = mock_get.call_args[0][0]
        assert "min=q" in url

    @patch("savant_extras.outs_above_average.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock("")
        df = outs_above_average(2024)
        assert df.empty

    @patch("savant_extras.outs_above_average.requests.get")
    def test_html_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock("<!DOCTYPE html><html></html>")
        df = outs_above_average(2024)
        assert df.empty


class TestOutsAboveAverageRange:
    @patch("savant_extras.outs_above_average.time.sleep")
    @patch("savant_extras.outs_above_average.requests.get")
    def test_returns_dataframe(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outs_above_average_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6  # 3 seasons × 2 rows

    @patch("savant_extras.outs_above_average.time.sleep")
    @patch("savant_extras.outs_above_average.requests.get")
    def test_calls_per_year(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outs_above_average_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.outs_above_average.time.sleep")
    @patch("savant_extras.outs_above_average.requests.get")
    def test_sleep_between_years(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outs_above_average_range(2022, 2024)
        assert mock_sleep.call_count == 2

    @patch("savant_extras.outs_above_average.time.sleep")
    @patch("savant_extras.outs_above_average.requests.get")
    def test_all_empty_returns_empty(self, mock_get, mock_sleep):
        mock_get.return_value = _mock("")
        df = outs_above_average_range(2022, 2024)
        assert df.empty
