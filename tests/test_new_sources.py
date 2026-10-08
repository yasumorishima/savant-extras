"""Tests for the shared parser, abs_challenges and statcast_minors (mocked)."""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pandas as pd
import json as _json

import pytest

from savant_extras import EmptySavantResponse
from savant_extras._http import parse_savant_csv
from savant_extras.abs_challenges import abs_challenges, abs_challenges_range
from savant_extras.statcast_minors import statcast_minors


def _resp(text):
    mock = MagicMock()
    mock.content = text.encode("utf-8")
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    return mock


# --- parse_savant_csv ----------------------------------------------------

class TestParseSavantCsv:
    def test_rows_do_not_warn(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            df = parse_savant_csv("a,b\n1,2\n", "u")
        assert len(df) == 1

    def test_header_only_warns_and_keeps_columns(self):
        with pytest.warns(EmptySavantResponse, match="no rows"):
            df = parse_savant_csv('﻿"a","b"\n', "http://x")
        assert df.empty
        assert list(df.columns) == ["﻿a", "b"] or list(df.columns) == ["a", "b"]

    @pytest.mark.parametrize("body", ["", "   \n", "<!DOCTYPE html><html>", "<html>"])
    def test_html_or_empty_warns(self, body):
        with pytest.warns(EmptySavantResponse):
            df = parse_savant_csv(body, "http://x")
        assert df.empty and df.columns.empty

    def test_warning_names_the_url(self):
        with pytest.warns(EmptySavantResponse, match="http://savant/abc"):
            parse_savant_csv("a\n", "http://savant/abc")


# --- abs_challenges ------------------------------------------------------

def _page(rows):
    return "<html><script>const absData = " + _json.dumps(rows) + ";\n const x = 1;</script></html>"


def _abs(year=2026, level="MLB", n=2):
    return _page([
        {"id": 600000 + i, "player_name": f"P{i}", "team_abbr": "WSH", "year": year,
         "level": level, "parent_org": "WSH", "n_challenges": i + 1, "n_overturns": i}
        for i in range(n)
    ])


class TestAbsChallenges:
    @patch("requests.get")
    def test_url_carries_every_parameter(self, get):
        get.return_value = _resp(_abs(2025, "AAA"))
        abs_challenges(2025, level="aaa", challenge_type="catcher", game_type="S", min_challenges=0)
        url = get.call_args[0][0]
        for part in ("season%5B%5D=2025", "level=aaa", "challengeType=catcher",
                     "gameType%5B%5D=S", "minChal=0"):
            assert part in url, part

    @patch("requests.get")
    def test_adds_challenge_type_column(self, get):
        get.return_value = _resp(_abs())
        df = abs_challenges(2026, challenge_type="batter")
        assert (df["challenge_type"] == "batter").all()
        assert len(df) == 2

    @patch("requests.get")
    def test_level_mismatch_raises(self, get):
        # Savant ignoring level=aaa would hand back the MLB table
        get.return_value = _resp(_abs(2025, "MLB"))
        with pytest.raises(ValueError, match="level"):
            abs_challenges(2025, level="aaa")

    @patch("requests.get")
    def test_year_mismatch_raises(self, get):
        get.return_value = _resp(_abs(2026, "MLB"))
        with pytest.raises(ValueError, match="year"):
            abs_challenges(2025)

    @patch("requests.get")
    def test_empty_season_warns_and_returns_empty(self, get):
        get.return_value = _resp(_page([]))
        with pytest.warns(EmptySavantResponse):
            df = abs_challenges(2025)
        assert df.empty

    @patch("requests.get")
    def test_page_without_data_raises(self, get):
        get.return_value = _resp("<html>maintenance</html>")
        with pytest.raises(ValueError, match="layout"):
            abs_challenges(2026)

    @patch("requests.get")
    def test_player_id_column_leads(self, get):
        get.return_value = _resp(_abs())
        df = abs_challenges(2026)
        assert list(df.columns[:3]) == ["challenge_type", "player_id", "player_name"]
        assert df["player_id"].tolist() == [600000, 600001]

    @patch("requests.get")
    def test_missing_player_id_raises(self, get):
        get.return_value = _resp(_page([{"id": None, "year": 2026, "level": "MLB"}]))
        with pytest.raises(ValueError, match="player id"):
            abs_challenges(2026)

    @pytest.mark.parametrize("kw", [{"level": "aa"}, {"challenge_type": "umpire"}, {"game_type": "P"}])
    def test_bad_arguments(self, kw):
        with pytest.raises(ValueError):
            abs_challenges(2026, **kw)

    @patch("time.sleep")
    @patch("requests.get")
    def test_range_one_request_per_season_skips_empty(self, get, _sleep):
        get.side_effect = [_resp(_page([])), _resp(_abs(2025, "AAA")), _resp(_abs(2026, "AAA", 3))]
        with pytest.warns(EmptySavantResponse):
            df = abs_challenges_range(2024, 2026, level="aaa")
        assert get.call_count == 3
        assert sorted(df["year"].unique()) == [2025, 2026]
        assert len(df) == 5


# --- statcast_minors -----------------------------------------------------

SC_HEAD = "pitch_type,game_date,game_pk,home_team,away_team,arm_angle\n"


def _sc(day="2025-06-10", home="TOL", away="COL", n=3, pk=780001):
    return SC_HEAD + "".join(f"FF,{day},{pk},{home},{away},40.1\n" for _ in range(n))


class TestStatcastMinors:
    @patch("time.sleep")
    @patch("requests.get")
    def test_one_request_per_day_with_minors_flag(self, get, _sleep):
        get.side_effect = [_resp(_sc(n=2)), _resp(SC_HEAD), _resp(_sc(n=4))]
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # an off day must not warn
            df = statcast_minors("2025-06-10", "2025-06-12")
        assert get.call_count == 3
        assert len(df) == 6
        urls = [c[0][0] for c in get.call_args_list]
        for u in urls:
            assert "minors=true" in u and "hfLevel=AAA%7C" in u and "hfSea=2025%7C" in u
        assert "game_date_gt=2025-06-11&game_date_lt=2025-06-11" in urls[1]

    @patch("requests.get")
    def test_columbus_is_not_a_major_league_game(self, get):
        # COL is Colorado in MLB and Columbus in Triple-A
        get.return_value = _resp(_sc(home="COL", away="TOL"))
        assert len(statcast_minors("2025-06-10", "2025-06-10")) == 3

    @patch("requests.get")
    def test_major_league_game_raises(self, get):
        get.return_value = _resp(_sc(home="COL", away="AZ", pk=777001))
        with pytest.raises(ValueError, match="major-league"):
            statcast_minors("2025-06-10", "2025-06-10")

    @patch("time.sleep")
    @patch("requests.get")
    def test_all_empty_warns_once(self, get, _sleep):
        get.return_value = _resp(SC_HEAD)
        with pytest.warns(EmptySavantResponse, match="no AAA pitches") as rec:
            df = statcast_minors("2025-01-01", "2025-01-03")
        assert df.empty
        assert len(rec) == 1

    @patch("requests.get")
    def test_row_cap_warns(self, get):
        get.return_value = _resp(_sc(n=25000))
        with pytest.warns(UserWarning, match="cap"):
            statcast_minors("2025-06-10", "2025-06-10")

    def test_range_across_seasons_raises(self):
        with pytest.raises(ValueError, match="season"):
            statcast_minors("2024-12-30", "2025-01-02")

    def test_reversed_range_raises(self):
        with pytest.raises(ValueError):
            statcast_minors("2025-06-10", "2025-06-01")

    @pytest.mark.parametrize("kw", [{"level": "AA"}, {"player_type": "team"}])
    def test_bad_arguments(self, kw):
        with pytest.raises(ValueError):
            statcast_minors("2025-06-10", "2025-06-10", **kw)
