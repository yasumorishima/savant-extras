"""Tests for catcher_stance module."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pandas as pd

from savant_extras.catcher_stance import catcher_stance, catcher_stance_range

SAMPLE_CSV = (
    "id,name,year,pitches,knee_down_pct,one_knee_framing_rv,"
    "one_knee_blocking_rv,one_knee_throwing_rv,catching_rv\n"
    '663728,"Realmuto, J.T.",2024,12000,0.65,2.1,1.5,0.8,4.4\n'
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



class TestCatcherStance:
    @patch("savant_extras.catcher_stance.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_stance(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.catcher_stance.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_stance(2024)
        url = mock_get.call_args[0][0]
        assert "seasonStart=2024" in url and "seasonEnd=2024" in url
        assert "type=catcher" in url and "minPitches=" in url
        assert "year=" not in url and "min=" not in url

    @patch("savant_extras.catcher_stance.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert catcher_stance(2024).empty


class TestCatcherStanceRange:
    @patch("savant_extras.catcher_stance.requests.get")
    def test_year_column(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        df = catcher_stance_range(2023, 2024)
        assert "year" in df.columns
        assert set(df["year"]) == {2023, 2024}

    @patch("savant_extras.catcher_stance.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        catcher_stance_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.catcher_stance.time.sleep")
    @patch("savant_extras.catcher_stance.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.side_effect = _per_year(SAMPLE_CSV)
        catcher_stance_range(2022, 2024)
        assert mock_sleep.call_count == 2
