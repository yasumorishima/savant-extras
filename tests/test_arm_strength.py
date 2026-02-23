"""Tests for arm_strength module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import arm_strength, arm_strength_range


SAMPLE_CSV = (
    "fielder_name,player_id,team_name,primary_position,primary_position_name,"
    "total_throws,max_arm_strength,arm_overall\n"
    "\"Betts, Mookie\",605141,LAD,RF,Right Field,250,92.3,88.5\n"
    "\"Soto, Juan\",665742,NYY,RF,Right Field,180,89.1,85.2\n"
)


def _mock_response(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestArmStrength:
    @patch("savant_extras.arm_strength.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = arm_strength(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.arm_strength.requests.get")
    def test_columns_preserved(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = arm_strength(2024)
        assert "max_arm_strength" in df.columns
        assert "arm_overall" in df.columns

    @patch("savant_extras.arm_strength.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.arm_strength.requests.get")
    def test_position_filter(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength(2024, position="RF")
        url = mock_get.call_args[0][0]
        assert "pos=RF" in url

    @patch("savant_extras.arm_strength.requests.get")
    def test_default_position_empty(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength(2024)
        url = mock_get.call_args[0][0]
        assert "pos=&" in url or "pos=" in url

    @patch("savant_extras.arm_strength.requests.get")
    def test_min_throws_passed(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength(2024, min_throws=50)
        url = mock_get.call_args[0][0]
        assert "minThrows=50" in url

    @patch("savant_extras.arm_strength.requests.get")
    def test_empty_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("")
        df = arm_strength(2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    @patch("savant_extras.arm_strength.requests.get")
    def test_html_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html><html></html>")
        df = arm_strength(2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestArmStrengthRange:
    @patch("savant_extras.arm_strength.requests.get")
    def test_returns_dataframe_with_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = arm_strength_range(2023, 2024)
        assert isinstance(df, pd.DataFrame)
        assert "year" in df.columns

    @patch("savant_extras.arm_strength.requests.get")
    def test_calls_api_per_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.arm_strength.requests.get")
    def test_year_values(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = arm_strength_range(2023, 2024)
        assert set(df["year"].unique()) == {2023, 2024}

    @patch("savant_extras.arm_strength.time.sleep")
    @patch("savant_extras.arm_strength.requests.get")
    def test_sleep_between_requests(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        arm_strength_range(2022, 2024)
        assert mock_sleep.call_count == 2

    @patch("savant_extras.arm_strength.requests.get")
    def test_all_empty_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("")
        df = arm_strength_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty
