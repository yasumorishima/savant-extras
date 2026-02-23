"""Tests for year_to_year module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras.year_to_year import year_to_year

SAMPLE_CSV = (
    "name,entity_id,2023,2024,delta_2023_2024\n"
    '"Soto, Juan",665742,0.410,0.425,0.015\n'
)


def _mock_response(csv_text):
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestYearToYear:
    @patch("savant_extras.year_to_year.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        df = year_to_year(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    @patch("savant_extras.year_to_year.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        year_to_year(2024)
        url = mock_get.call_args[0][0]
        assert "year=2024" in url

    @patch("savant_extras.year_to_year.requests.get")
    def test_player_type_in_url(self, mock_get):
        mock_get.return_value = _mock_response(SAMPLE_CSV)
        year_to_year(2024, player_type="pitcher")
        url = mock_get.call_args[0][0]
        assert "type=pitcher" in url

    def test_invalid_player_type(self):
        with pytest.raises(ValueError):
            year_to_year(2024, player_type="team")

    @patch("savant_extras.year_to_year.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock_response("")
        assert year_to_year(2024).empty
