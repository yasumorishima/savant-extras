"""Tests for pitch_movement module."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.pitch_movement import pitch_movement, pitch_movement_range

SAMPLE_CSV = (
    "year,\"last_name, first_name\",pitcher_id,team_name,team_name_abbrev,"
    "pitch_hand,avg_speed,pitches_thrown,total_pitches,pitches_per_game,"
    "pitch_per,pitch_type,pitch_type_name,pitcher_break_z,league_break_z,"
    "diff_z,rise,pitcher_break_z_induced,pitcher_break_x,league_break_x,"
    "diff_x,tail,percent_rank_diff_z,percent_rank_diff_x\n"
    '2024,"Cole, Gerrit",543037,Yankees,NYY,R,97.5,500,3200,100,15.6,'
    "FF,4-Seam Fastball,14.2,13.5,0.7,1,15.8,-6.2,-5.0,-1.2,1,75,80\n"
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock

_YEAR_IN_URL = re.compile(r"[?&](?:season_start|seasonStart|season|year)=(\d{4})")


def _per_year(csv_text):
    """Serve the fixture under the season the URL asked for.

    Every season-keyed function raises when the rows belong to a different
    season than requested, so a range test must not return the 2024 fixture
    for 2022 and 2023.
    """
    def _serve(url, *args, **kwargs):
        year = _YEAR_IN_URL.search(url).group(1)
        return _mock_response(csv_text.replace("2024", year))
    return _serve



class TestPitchMovement:
    @patch("savant_extras.pitch_movement.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = pitch_movement(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.pitch_movement.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_movement(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.pitch_movement.requests.get")
    def test_pitch_type_filter(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV.replace(",FF,", ",SL,"))
        df = pitch_movement(2024, pitch_type="SL")
        url = mock_get.call_args[0][0]
        assert "pitch_type=SL" in url
        assert "pitchType" not in url
        assert set(df["pitch_type"]) == {"SL"}

    @patch("savant_extras.pitch_movement.requests.get")
    def test_default_pitch_type_is_ff(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        pitch_movement(2024)
        assert "pitch_type=FF" in mock_get.call_args[0][0]

    @patch("savant_extras.pitch_movement.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert pitch_movement(2024).empty

    @patch("savant_extras.pitch_movement.requests.get")
    def test_html_response(self, mock_get):
        mock_get.return_value = _mock_response("<!DOCTYPE html>")
        assert pitch_movement(2024).empty


class TestPitchMovementRange:
    @patch("savant_extras.pitch_movement.requests.get")
    def test_concatenates(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        df = pitch_movement_range(2023, 2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.pitch_movement.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        pitch_movement_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.pitch_movement.time.sleep")
    @patch("savant_extras.pitch_movement.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        pitch_movement_range(2022, 2024)
        assert mock_sleep.call_count == 2
