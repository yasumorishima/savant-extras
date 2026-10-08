"""Tests for running_game module."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.running_game import running_game, running_game_range

SAMPLE_CSV = (
    "player_id,player_name,team_name,start_year,end_year,"
    "key_target_base,runs_prevented_on_running_attr,"
    "n_pitcher_cs_aa,n_init,rate_sbx,n_sb,n_cs,n_pk,n_bk\n"
    '543037,"Cole, Gerrit",Yankees,2024,2024,2B,-1.5,3,150,0.72,15,5,2,0\n'
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



class TestRunningGame:
    @patch("requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = running_game(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        running_game(2024)
        url = mock_get.call_args[0][0]
        assert "season_start=2024" in url and "season_end=2024" in url
        assert "game_type=Regular" in url
        assert "year=" not in url and "min=" not in url

    @patch("requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert running_game(2024).empty


class TestRunningGameRange:
    @patch("requests.get")
    def test_year_column(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        df = running_game_range(2023, 2024)
        assert "year" in df.columns
        assert set(df["year"]) == {2023, 2024}

    @patch("requests.get")
    def test_api_calls(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        running_game_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("time.sleep")
    @patch("requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        running_game_range(2022, 2024)
        assert mock_sleep.call_count == 2
