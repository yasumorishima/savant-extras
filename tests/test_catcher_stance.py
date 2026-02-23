"""Tests for catcher_stance module."""

from __future__ import annotations

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
        assert "year=2024" in url

    @patch("savant_extras.catcher_stance.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert catcher_stance(2024).empty


class TestCatcherStanceRange:
    @patch("savant_extras.catcher_stance.requests.get")
    def test_year_column(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = catcher_stance_range(2023, 2024)
        assert "year" in df.columns

    @patch("savant_extras.catcher_stance.requests.get")
    def test_api_calls(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_stance_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.catcher_stance.time.sleep")
    @patch("savant_extras.catcher_stance.requests.get")
    def test_sleep(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        catcher_stance_range(2022, 2024)
        assert mock_sleep.call_count == 2
