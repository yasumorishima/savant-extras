"""Tests for bat_tracking module."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import bat_tracking, bat_tracking_monthly, bat_tracking_splits


SAMPLE_CSV = (
    "id,name,side,avg_bat_speed,swing_tilt,attack_angle,"
    "attack_direction,ideal_attack_angle_rate,"
    "avg_intercept_y_vs_plate,avg_intercept_y_vs_batter,"
    "avg_batter_y_position,avg_batter_x_position,competitive_swings\n"
    "519317,\"Stanton, Giancarlo\",R,81.2,26.2,8.7,-2.7,0.60,2.3,27.2,24.9,33.0,714\n"
    "665833,\"Cruz, Oneil\",L,78.5,32.9,8.4,-6.7,0.42,9.1,35.3,26.2,28.3,879\n"
)


def _mock_response(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestBatTracking:
    @patch("savant_extras.bat_tracking.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = bat_tracking("2024-04-01", "2024-04-30")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.bat_tracking.requests.get")
    def test_columns_preserved(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = bat_tracking("2024-04-01", "2024-04-30")
        assert "avg_bat_speed" in df.columns
        assert "attack_angle" in df.columns

    @patch("savant_extras.bat_tracking.requests.get")
    def test_url_contains_dates(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking("2024-04-01", "2024-04-30")
        url = mock_get.call_args[0][0]
        assert "dateStart=2024-04-01" in url
        assert "dateEnd=2024-04-30" in url

    @patch("savant_extras.bat_tracking.requests.get")
    def test_pitcher_type(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking("2024-04-01", "2024-04-30", player_type="pitcher")
        url = mock_get.call_args[0][0]
        assert "type=pitcher" in url

    @patch("savant_extras.bat_tracking.requests.get")
    def test_batter_type_default(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking("2024-04-01", "2024-04-30")
        url = mock_get.call_args[0][0]
        assert "type=batter" in url

    def test_invalid_player_type_raises(self):
        with pytest.raises(ValueError, match="player_type must be"):
            bat_tracking("2024-04-01", "2024-04-30", player_type="team")

    @patch("savant_extras.bat_tracking.requests.get")
    def test_min_swings_passed(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking("2024-04-01", "2024-04-30", min_swings=50)
        url = mock_get.call_args[0][0]
        assert "minSwings=50" in url

    @patch("savant_extras.bat_tracking.requests.get")
    def test_pre_2024_warns(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bat_tracking("2023-04-01", "2023-04-30")
            assert len(w) == 1
            assert "2024" in str(w[0].message)
            assert "Hawk-Eye" in str(w[0].message)

    @patch("savant_extras.bat_tracking.requests.get")
    def test_html_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html><html></html>")
        df = bat_tracking("2024-04-01", "2024-04-30")
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    @patch("savant_extras.bat_tracking.requests.get")
    def test_empty_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("")
        df = bat_tracking("2024-04-01", "2024-04-30")
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    @patch("savant_extras.bat_tracking.requests.get")
    def test_2024_no_warning(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bat_tracking("2024-04-01", "2024-04-30")
            hawk_warnings = [x for x in w if "Hawk-Eye" in str(x.message)]
            assert len(hawk_warnings) == 0


class TestBatTrackingMonthly:
    @patch("savant_extras.bat_tracking.requests.get")
    def test_returns_dataframe_with_month_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = bat_tracking_monthly(2024)
        assert isinstance(df, pd.DataFrame)
        assert "month" in df.columns

    @patch("savant_extras.bat_tracking.requests.get")
    def test_calls_all_months(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking_monthly(2024)
        # April(4) through October(10) = 7 months
        assert mock_get.call_count == 7

    @patch("savant_extras.bat_tracking.requests.get")
    def test_month_values_in_range(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = bat_tracking_monthly(2024)
        assert df["month"].min() == 4
        assert df["month"].max() == 10

    @patch("savant_extras.bat_tracking.requests.get")
    def test_empty_response_handled(self, mock_get):
        empty_csv = "id,name,side,avg_bat_speed\n"
        mock_get.return_value = _mock_response(empty_csv)
        df = bat_tracking_monthly(2024)
        assert isinstance(df, pd.DataFrame)

    @patch("savant_extras.bat_tracking.requests.get")
    def test_pre_2024_warns(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bat_tracking_monthly(2023)
            hawk_warnings = [x for x in w if "Hawk-Eye" in str(x.message)]
            assert len(hawk_warnings) >= 1

    @patch("savant_extras.bat_tracking.time.sleep")
    @patch("savant_extras.bat_tracking.requests.get")
    def test_sleep_between_requests(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking_monthly(2024)
        # 7 months, sleep between each (6 sleeps)
        assert mock_sleep.call_count == 6


class TestBatTrackingSplits:
    @patch("savant_extras.bat_tracking.requests.get")
    def test_returns_dict_with_two_keys(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        splits = bat_tracking_splits(2024)
        assert "first_half" in splits
        assert "second_half" in splits

    @patch("savant_extras.bat_tracking.requests.get")
    def test_both_halves_are_dataframes(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        splits = bat_tracking_splits(2024)
        assert isinstance(splits["first_half"], pd.DataFrame)
        assert isinstance(splits["second_half"], pd.DataFrame)

    @patch("savant_extras.bat_tracking.requests.get")
    def test_calls_api_twice(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking_splits(2024)
        assert mock_get.call_count == 2

    @patch("savant_extras.bat_tracking.requests.get")
    def test_first_half_date_range(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking_splits(2024)
        first_url = mock_get.call_args_list[0][0][0]
        assert "dateStart=2024-03-01" in first_url
        assert "dateEnd=2024-07-13" in first_url

    @patch("savant_extras.bat_tracking.requests.get")
    def test_second_half_date_range(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        bat_tracking_splits(2024)
        second_url = mock_get.call_args_list[1][0][0]
        assert "dateStart=2024-07-14" in second_url
        assert "dateEnd=2024-11-01" in second_url

    @patch("savant_extras.bat_tracking.requests.get")
    def test_pre_2024_warns(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            bat_tracking_splits(2023)
            hawk_warnings = [x for x in w if "Hawk-Eye" in str(x.message)]
            assert len(hawk_warnings) >= 1
