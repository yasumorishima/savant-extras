"""Tests for park_factors module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import park_factors, park_factors_range


# Sample DataFrame that represents what pd.read_html returns from FanGraphs
_SAMPLE_TABLE = pd.DataFrame({
    "Team": ["Rockies", "Red Sox", "Yankees"],
    "Basic (5yr)": [116, 100, 97],
    "3yr": [115, 99, 96],
    "1yr": [120, 101, 95],
    "HR": [131, 102, 93],
    "1B": [110, 100, 98],
    "2B": [108, 101, 97],
    "3B": [105, 98, 95],
    "SO": [97, 100, 101],
    "BB": [101, 100, 99],
    "FIP": [112, 100, 96],
})


def _mock_response() -> MagicMock:
    mock = MagicMock()
    mock.text = "<html/>"
    mock.raise_for_status = MagicMock()
    return mock


# Patch both requests.get and pd.read_html so lxml is not required in CI
def _patch_fetch(monkeypatch_or_patch=None):
    """Return context managers for mocking the HTTP fetch + HTML parse."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("savant_extras.park_factors.requests.get", return_value=_mock_response()) as mg:
            with patch("savant_extras.park_factors.pd.read_html", return_value=[_SAMPLE_TABLE]) as mh:
                yield mg, mh

    return _ctx()


class TestParkFactors:
    def test_returns_dataframe(self):
        with _patch_fetch():
            df = park_factors(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_team_column_abbreviation(self):
        with _patch_fetch():
            df = park_factors(2024)
        assert "COL" in df["team"].values
        assert "BOS" in df["team"].values
        assert "NYY" in df["team"].values

    def test_season_column_added(self):
        with _patch_fetch():
            df = park_factors(2024)
        assert "season" in df.columns
        assert (df["season"] == 2024).all()

    def test_pf_columns_present(self):
        with _patch_fetch():
            df = park_factors(2024)
        for col in ["pf_5yr", "pf_3yr", "pf_1yr", "pf_hr"]:
            assert col in df.columns, f"{col} not found in columns"

    def test_col_values_numeric(self):
        with _patch_fetch():
            df = park_factors(2024)
        assert pd.api.types.is_numeric_dtype(df["pf_5yr"])

    def test_url_contains_year(self):
        with _patch_fetch() as (mock_get, _):
            park_factors(2022)
        url = mock_get.call_args[0][0]
        assert "season=2022" in url

    def test_col_values_match(self):
        with _patch_fetch():
            df = park_factors(2024)
        col_row = df[df["team"] == "COL"].iloc[0]
        assert col_row["pf_5yr"] == 116
        assert col_row["pf_hr"] == 131

    def test_no_team_table_raises(self):
        no_team_table = pd.DataFrame({"Name": ["x"]})
        with patch("savant_extras.park_factors.requests.get", return_value=_mock_response()):
            with patch("savant_extras.park_factors.pd.read_html", return_value=[no_team_table]):
                with pytest.raises(ValueError, match="not found"):
                    park_factors(2024)

    def test_no_table_at_all_raises(self):
        with patch("savant_extras.park_factors.requests.get", return_value=_mock_response()):
            with patch("savant_extras.park_factors.pd.read_html", return_value=[]):
                with pytest.raises(ValueError, match="not found"):
                    park_factors(2024)


class TestParkFactorsRange:
    def test_returns_dataframe(self):
        with patch("savant_extras.park_factors.time.sleep"):
            with _patch_fetch():
                df = park_factors_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 9  # 3 seasons × 3 teams

    def test_season_values(self):
        with patch("savant_extras.park_factors.time.sleep"):
            with _patch_fetch():
                df = park_factors_range(2022, 2024)
        assert set(df["season"].unique()) == {2022, 2023, 2024}

    def test_calls_api_per_year(self):
        with patch("savant_extras.park_factors.time.sleep"):
            with _patch_fetch() as (mock_get, _):
                park_factors_range(2022, 2024)
        assert mock_get.call_count == 3

    def test_sleep_between_requests(self):
        with patch("savant_extras.park_factors.time.sleep") as mock_sleep:
            with _patch_fetch():
                park_factors_range(2022, 2024)
        assert mock_sleep.call_count == 2

    def test_single_season_range(self):
        with patch("savant_extras.park_factors.time.sleep") as mock_sleep:
            with _patch_fetch():
                df = park_factors_range(2024, 2024)
        assert set(df["season"].unique()) == {2024}
        mock_sleep.assert_not_called()

    def test_all_fail_returns_empty(self):
        with patch("savant_extras.park_factors.time.sleep"):
            with patch("savant_extras.park_factors.requests.get", side_effect=Exception("network error")):
                import warnings
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    df = park_factors_range(2022, 2024)
                assert df.empty
                assert any("no data fetched" in str(warning.message).lower() for warning in w)
