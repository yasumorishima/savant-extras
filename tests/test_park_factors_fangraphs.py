"""Tests for the retained FanGraphs park factor source."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import park_factors_fangraphs, park_factors_fangraphs_range

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


def _response() -> MagicMock:
    mock = MagicMock()
    mock.text = "<html/>"
    mock.raise_for_status = MagicMock()
    return mock


def _patch(tables=None):
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        target = "savant_extras.park_factors_fangraphs"
        with patch(f"{target}.requests.get", return_value=_response()) as mg:
            with patch(f"{target}.pd.read_html",
                       return_value=tables or [_SAMPLE_TABLE]) as mh:
                yield mg, mh

    return _ctx()


class TestFangraphsParkFactors:
    def test_keeps_the_columns_savant_cannot_give(self):
        with _patch():
            df = park_factors_fangraphs(2024)
        assert "pf_5yr" in df.columns
        assert "pf_fip" in df.columns
        col = df[df["team"] == "COL"].iloc[0]
        assert col["pf_5yr"] == 116
        assert col["pf_hr"] == 131, "the FanGraphs scale, not the Savant one"

    def test_season_and_team_columns(self):
        with _patch():
            df = park_factors_fangraphs(2022)
        assert (df["season"] == 2022).all()
        assert set(df["team"]) == {"COL", "BOS", "NYY"}

    def test_url_carries_the_season(self):
        with _patch() as (mock_get, _):
            park_factors_fangraphs(2021)
        url = mock_get.call_args[0][0]
        assert "fangraphs.com" in url and "season=2021" in url

    def test_does_not_impersonate_a_browser(self):
        # A Chrome User-Agent is exactly what Cloudflare challenges here;
        # 0.4.4 sent one and got 403 for every season.
        from savant_extras.park_factors_fangraphs import _HEADERS

        ua = _HEADERS["User-Agent"]
        assert "Mozilla" not in ua and "Chrome" not in ua
        assert "savant-extras" in ua

    def test_a_challenge_page_raises_rather_than_returning_nothing(self):
        # A Cloudflare interstitial parses to tables without a Team column.
        with _patch(tables=[pd.DataFrame({"Name": ["just a moment"]})]):
            with pytest.raises(ValueError, match="not found"):
                park_factors_fangraphs(2024)

    def test_total_failure_warns_and_returns_empty(self):
        with patch("savant_extras.park_factors_fangraphs.requests.get",
                   side_effect=RuntimeError("403")):
            with pytest.warns(UserWarning, match="no data fetched"):
                df = park_factors_fangraphs_range(2023, 2024, sleep=0)
        assert df.empty

    def test_partial_failure_warns_but_keeps_the_good_seasons(self):
        real = _response()

        def _flaky(url, **kwargs):
            if "season=2024" in url:
                raise RuntimeError("403")
            return real

        target = "savant_extras.park_factors_fangraphs"
        with patch(f"{target}.requests.get", side_effect=_flaky):
            with patch(f"{target}.pd.read_html", return_value=[_SAMPLE_TABLE]):
                with pytest.warns(UserWarning, match="skipped 2024"):
                    df = park_factors_fangraphs_range(2023, 2024, sleep=0)
        assert sorted(df["season"].unique()) == [2023]
