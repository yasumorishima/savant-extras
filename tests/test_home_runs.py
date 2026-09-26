"""Tests for home_runs module."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

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
    def test_hr_type_not_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        with pytest.warns(DeprecationWarning, match="hr_type"):
            home_runs(2024, hr_type="distance")
        url = mock_get.call_args[0][0]
        assert re.search(r"[?&]type=", url) is None
        assert "distance" not in url
        assert "player_type=Batter" in url and "cat=adj_xhr" in url and "min=0" in url

    @patch("savant_extras.home_runs.requests.get")
    def test_pitcher_category_min_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        home_runs(2024, player_type="pitcher", category="xhr", min_hr=5)
        url = mock_get.call_args[0][0]
        assert "player_type=Pitcher" in url and "cat=xhr" in url and "min=5" in url

    def test_invalid_arguments(self):
        with pytest.raises(ValueError):
            home_runs(2024, player_type="team")
        with pytest.raises(ValueError):
            home_runs(2024, category="distance")

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
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        df = home_runs_range(2023, 2024)
        assert "year" in df.columns
        assert set(df["year"]) == {2023, 2024}

    @patch("savant_extras.home_runs.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        home_runs_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.home_runs.time.sleep")
    @patch("savant_extras.home_runs.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        home_runs_range(2022, 2024)
        assert mock_sleep.call_count == 2
