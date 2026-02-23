"""Tests for pitch_tempo module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import pitch_tempo, pitch_tempo_range


SAMPLE_CSV = (
    "entity_id,entity_name,entity_code,team_id,total_pitches,"
    "total_pitches_empty,median_seconds_empty,total_pitches_onbase,"
    "freq_hot,freq_warm,freq_cold\n"
    "543037,\"Cole, Gerrit\",NYY,147,3200,2100,15.2,1100,0.45,0.30,0.25\n"
    "608566,\"Wheeler, Zack\",PHI,143,3100,2000,14.8,1100,0.50,0.28,0.22\n"
)


def _mock_response(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestPitchTempo:
    @patch("savant_extras.pitch_tempo.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitch_tempo(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_columns_preserved(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitch_tempo(2024)
        assert "median_seconds_empty" in df.columns
        assert "freq_hot" in df.columns

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_tempo(2024)
        url = mock_get.call_args[0][0]
        assert "season_start=2024" in url
        assert "season_end=2024" in url

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_pitcher_type_maps_to_pit(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_tempo(2024, player_type="pitcher")
        url = mock_get.call_args[0][0]
        assert "type=Pit" in url

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_batter_type_maps_to_bat(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_tempo(2024, player_type="batter")
        url = mock_get.call_args[0][0]
        assert "type=Bat" in url

    def test_invalid_player_type_raises(self):
        with pytest.raises(ValueError, match="player_type must be"):
            pitch_tempo(2024, player_type="team")

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_empty_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("")
        df = pitch_tempo(2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_html_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html><html></html>")
        df = pitch_tempo(2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestPitchTempoRange:
    @patch("savant_extras.pitch_tempo.requests.get")
    def test_returns_dataframe_with_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitch_tempo_range(2023, 2024)
        assert isinstance(df, pd.DataFrame)
        assert "year" in df.columns

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_calls_api_per_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_tempo_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_year_values(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitch_tempo_range(2023, 2024)
        assert set(df["year"].unique()) == {2023, 2024}

    @patch("savant_extras.pitch_tempo.time.sleep")
    @patch("savant_extras.pitch_tempo.requests.get")
    def test_sleep_between_requests(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_tempo_range(2022, 2024)
        assert mock_sleep.call_count == 2

    @patch("savant_extras.pitch_tempo.requests.get")
    def test_all_empty_returns_empty(self, mock_get):
        mock_get.return_value = _mock_response("")
        df = pitch_tempo_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert df.empty
