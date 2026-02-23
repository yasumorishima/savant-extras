"""Tests for batted_ball module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras.batted_ball import batted_ball, batted_ball_range

SAMPLE_CSV = (
    "id,name,bbe,gb_rate,air_rate,fb_rate,ld_rate,pu_rate,"
    "pull_rate,straight_rate,oppo_rate\n"
    '519317,"Stanton, Giancarlo",300,0.35,0.55,0.40,0.20,0.05,0.45,0.30,0.25\n'
    '665833,"Cruz, Oneil",280,0.38,0.52,0.38,0.22,0.04,0.42,0.32,0.26\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestBattedBall:
    @patch("savant_extras.batted_ball.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = batted_ball(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.batted_ball.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        batted_ball(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.batted_ball.requests.get")
    def test_player_type_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        batted_ball(2024, player_type="pitcher")
        url = mock_get.call_args[0][0]
        assert "type=pitcher" in url

    def test_invalid_player_type(self):
        with pytest.raises(ValueError):
            batted_ball(2024, player_type="team")

    @patch("savant_extras.batted_ball.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert batted_ball(2024).empty

    @patch("savant_extras.batted_ball.requests.get")
    def test_html_response(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html>")
        assert batted_ball(2024).empty


class TestBattedBallRange:
    @patch("savant_extras.batted_ball.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = batted_ball_range(2023, 2024)
        assert "year" in df.columns
        assert set(df["year"].unique()) == {2023, 2024}

    @patch("savant_extras.batted_ball.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        batted_ball_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.batted_ball.time.sleep")
    @patch("savant_extras.batted_ball.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        batted_ball_range(2022, 2024)
        assert mock_sleep.call_count == 2
