"""Tests for outfield_jump module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import outfield_jump, outfield_jump_range

SAMPLE_CSV = (
    '"last_name, first_name","resp_fielder_id","year","outs_above_average","outs_per_play",'
    '"rel_league_burst_distance","rel_league_reaction_distance","rel_league_routing_distance",'
    '"rel_league_bootup_distance","f_bootup_distance","n","n_outs"\n'
    '"Kiermaier, Kevin","595281","2024","6","61.1","0","0.6","0.2","0.8","34.9","54","33"\n'
    '"Adell, Jo","666176","2024","0","56","-0.2","-1.3","-0.1","-1.6","31.7","50","28"\n'
)


def _mock(csv_text: str) -> MagicMock:
    mock = MagicMock()
    mock.content = csv_text.encode("utf-8")
    mock.raise_for_status = MagicMock()
    return mock


class TestOutfieldJump:
    @patch("savant_extras.outfield_jump.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outfield_jump(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    @patch("savant_extras.outfield_jump.requests.get")
    def test_jump_columns_present(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outfield_jump(2024)
        assert "rel_league_bootup_distance" in df.columns
        assert "rel_league_reaction_distance" in df.columns

    @patch("savant_extras.outfield_jump.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outfield_jump(2023)
        url = mock_get.call_args[0][0]
        assert "year=2023" in url

    @patch("savant_extras.outfield_jump.requests.get")
    def test_empty_response(self, mock_get):
        mock_get.return_value = _mock("")
        df = outfield_jump(2024)
        assert df.empty

    @patch("savant_extras.outfield_jump.requests.get")
    def test_html_response_returns_empty(self, mock_get):
        mock_get.return_value = _mock("<!DOCTYPE html><html></html>")
        df = outfield_jump(2024)
        assert df.empty


class TestOutfieldJumpRange:
    @patch("savant_extras.outfield_jump.time.sleep")
    @patch("savant_extras.outfield_jump.requests.get")
    def test_returns_dataframe(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        df = outfield_jump_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6

    @patch("savant_extras.outfield_jump.time.sleep")
    @patch("savant_extras.outfield_jump.requests.get")
    def test_calls_per_year(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outfield_jump_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.outfield_jump.time.sleep")
    @patch("savant_extras.outfield_jump.requests.get")
    def test_sleep_between_years(self, mock_get, mock_sleep):
        mock_get.return_value = _mock(SAMPLE_CSV)
        outfield_jump_range(2022, 2024)
        assert mock_sleep.call_count == 2
