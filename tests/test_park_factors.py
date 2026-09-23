"""Tests for park_factors module (Baseball Savant source, 0.5.0+)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest

from savant_extras import park_factors, park_factors_range
from savant_extras import park_factors as _pf_module_probe  # noqa: F401
from savant_extras.park_factors import (
    _COLUMN_ORDER,
    _INDEX_RENAME,
    _NAME_TO_ABB,
    _abbrev,
)

# Both Savant views carry the full index_* key set - measured 2026-09-23,
# the two pages return identical key lists - so both fixtures must too, or
# the "Savant stopped sending this key" guard fires on a shape the real feed
# never produces.
_INDEX_VALUES = {
    "index_hr": "107", "index_1b": "112", "index_2b": "121", "index_3b": "146",
    "index_so": "92", "index_bb": "101", "index_obp": "108", "index_hits": "113",
    "index_woba": "110", "index_wobacon": "116", "index_xwobacon": "104",
    "index_bacon": "113", "index_xbacon": "103", "index_hardhit": "101",
    "index_wobatto": "109",
}
# Distinct values, so a column read from the wrong window changes the result.
_SINGLE_INDEX_VALUES = {k: str(int(v) + 40) for k, v in _INDEX_VALUES.items()}

# Angel Stadium carries the lowest venue_id while LAA sorts third by team,
# so sorting on the wrong column is visible.
_MULTI = [
    dict(_INDEX_VALUES, venue_id=19, venue_name="Coors Field",
         name_display_club="Rockies", main_team_id=115, key_year="2026",
         year_range="2024-2026", n_pa="56243", index_runs="125"),
    dict(_INDEX_VALUES, venue_id=3, venue_name="Fenway Park",
         name_display_club="Red Sox", main_team_id=111, key_year="2026",
         year_range="2024-2026", n_pa="55355", index_runs="106",
         index_hr="88", index_2b="119"),
    dict(_INDEX_VALUES, venue_id=1, venue_name="Angel Stadium",
         name_display_club="Angels", main_team_id=108, key_year="2026",
         year_range="2024-2026", n_pa="54100", index_runs="98",
         index_hr="103"),
]

_SINGLE = [
    dict(_SINGLE_INDEX_VALUES, venue_id=19, venue_name="Coors Field",
         name_display_club="Rockies", main_team_id=115, key_year="2026",
         year_range="2026", n_pa="18700", index_runs="117"),
    dict(_SINGLE_INDEX_VALUES, venue_id=3, venue_name="Fenway Park",
         name_display_club="Red Sox", main_team_id=111, key_year="2026",
         year_range="2026", n_pa="18300", index_runs="101"),
    # A club whose park has no 3-year history: present in the single-season
    # view only. It must still get a row - 2026 OAK at Sutter Health Park is
    # the real case - with the 3-year columns left NaN.
    dict(_SINGLE_INDEX_VALUES, venue_id=1, venue_name="Angel Stadium",
         name_display_club="Angels", main_team_id=108, key_year="2026",
         year_range="2026", n_pa="18050", index_runs="96"),
    dict(_SINGLE_INDEX_VALUES, venue_id=2529, venue_name="Sutter Health Park",
         name_display_club="Athletics", main_team_id=133, key_year="2026",
         year_range="2026", n_pa="17900", index_runs="112"),
    # A venue with a club name this package cannot map: dropped, not emitted
    # with team=None.
    dict(_SINGLE_INDEX_VALUES, venue_id=4999, venue_name="Some Neutral Site",
         name_display_club="Saltines", main_team_id=0, key_year="2026",
         year_range="2026", n_pa="900", index_runs="100"),
]

_CLUBS = {"BOS", "COL", "LAA", "OAK"}


def _page(rows: list[dict]) -> str:
    return ("<html><body><script>\n"
            "var otherThing = [1, 2];\n"
            f"var data = {json.dumps(rows)};\n"
            "</script></body></html>")


def _response(text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


def _relabel(rows: list[dict], year: int) -> list[dict]:
    """Same rows, labelled for another season (park_factors_range calls)."""
    out = []
    for row in rows:
        new = dict(row, key_year=str(year))
        if new.get("year_range") and "-" in str(new["year_range"]):
            new["year_range"] = f"{year - 2}-{year}"
        elif new.get("year_range"):
            new["year_range"] = str(year)
        out.append(new)
    return out


def _fake_get(**overrides):
    """requests.get replacement that answers by the rolling= parameter."""
    multi = overrides.get("multi", _MULTI)
    single = overrides.get("single", _SINGLE)

    def _get(url, **kwargs):
        year = int(parse_qs(urlparse(url).query)["year"][0])
        rolling = parse_qs(urlparse(url).query, keep_blank_values=True)["rolling"][0]
        rows = single if rolling == "1" else multi
        return _response(_page(_relabel(rows, year)))

    return _get


def _patch(**overrides):
    return patch("savant_extras.park_factors.requests.get",
                 side_effect=_fake_get(**overrides))


# ------------------------------------------------------------ the club map


class TestClubMap:
    def test_every_club_maps_to_a_distinct_abbreviation(self):
        """All 30 clubs, not just the three the fixtures happen to use."""
        emitted = [
            "Angels", "Astros", "Athletics", "Blue Jays", "Braves", "Brewers",
            "Cardinals", "Cubs", "D-backs", "Dodgers", "Giants", "Guardians",
            "Mariners", "Marlins", "Mets", "Nationals", "Orioles", "Padres",
            "Phillies", "Pirates", "Rangers", "Rays", "Red Sox", "Reds",
            "Rockies", "Royals", "Tigers", "Twins", "White Sox", "Yankees",
        ]
        assert len(emitted) == 30
        abbs = [_abbrev(name) for name in emitted]
        assert None not in abbs, [n for n, a in zip(emitted, abbs) if a is None]
        assert len(set(abbs)) == 30, "two clubs share an abbreviation"
        expected = {
            "Angels": "LAA", "Astros": "HOU", "Athletics": "OAK",
            "Blue Jays": "TOR", "Braves": "ATL", "Brewers": "MIL",
            "Cardinals": "STL", "Cubs": "CHC", "D-backs": "ARI",
            "Dodgers": "LAD", "Giants": "SF", "Guardians": "CLE",
            "Mariners": "SEA", "Marlins": "MIA", "Mets": "NYM",
            "Nationals": "WAS", "Orioles": "BAL", "Padres": "SD",
            "Phillies": "PHI", "Pirates": "PIT", "Rangers": "TEX",
            "Rays": "TB", "Red Sox": "BOS", "Reds": "CIN", "Rockies": "COL",
            "Royals": "KC", "Tigers": "DET", "Twins": "MIN",
            "White Sox": "CWS", "Yankees": "NYY",
        }
        assert dict(zip(emitted, abbs)) == expected

    def test_red_sox_and_white_sox_do_not_shadow_each_other(self):
        assert _abbrev("White Sox") == "CWS"
        assert _abbrev("Red Sox") == "BOS"

    def test_unmappable_name_returns_none(self):
        assert _abbrev("Saltines") is None

    def test_aliases_resolve_to_the_same_club(self):
        assert _abbrev("Diamondbacks") == _abbrev("D-backs") == "ARI"
        assert _abbrev("Indians") == _abbrev("Guardians") == "CLE"


# ---------------------------------------------------------------- one year


class TestParkFactors:
    def test_returns_one_row_per_nameable_club(self):
        with _patch():
            df = park_factors(2026)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4, "the unmappable venue should be dropped"
        assert set(df["team"]) == _CLUBS
        assert df["team"].notna().all()

    def test_club_missing_from_the_three_year_view_still_gets_a_row(self):
        with _patch():
            df = park_factors(2026)
        assert "OAK" in set(df["team"]), "a club with no 3-year window vanished"
        oak = df[df["team"] == "OAK"].iloc[0]
        assert oak["pf_1yr"] == 112
        assert oak["n_pa_1yr"] == 17900
        assert oak["venue_id"] == 2529
        assert oak["venue_name"] == "Sutter Health Park"
        for col in ("pf_3yr", "pf_hr", "n_pa_3yr", "pf_3yr_years"):
            assert pd.isna(oak[col]), col

    def test_identity_columns_come_from_the_single_season_view(self):
        # The 3-year view has no row for OAK at all, so taking venue_id or
        # venue_name from it would blank them.
        with _patch():
            df = park_factors(2026)
        assert list(df["venue_id"]) == [3, 19, 1, 2529]
        assert list(df["venue_name"]) == [
            "Fenway Park", "Coors Field", "Angel Stadium", "Sutter Health Park"]

    def test_season_column_is_the_year_asked_for(self):
        with _patch():
            df = park_factors(2026)
        assert (df["season"] == 2026).all()

    def test_three_year_and_one_year_come_from_their_own_request(self):
        with _patch():
            df = park_factors(2026)
        col = df[df["team"] == "COL"].iloc[0]
        assert col["pf_3yr"] == 125
        assert col["pf_1yr"] == 117
        assert col["n_pa_3yr"] == 56243
        assert col["n_pa_1yr"] == 18700
        bos = df[df["team"] == "BOS"].iloc[0]
        assert bos["pf_3yr"] == 106
        assert bos["pf_1yr"] == 101

    def test_three_year_values_join_on_venue_id(self):
        # Reverse the 3-year rows: a positional join would put Fenway's 106
        # on COL, a venue_id join keeps 125 there.
        with _patch(multi=list(reversed(_MULTI))):
            df = park_factors(2026)
        assert df[df["team"] == "COL"].iloc[0]["pf_3yr"] == 125
        assert df[df["team"] == "BOS"].iloc[0]["pf_3yr"] == 106

    def test_each_index_column_carries_its_own_metric(self):
        with _patch():
            df = park_factors(2026)
        bos = df[df["team"] == "BOS"].iloc[0]
        assert bos["pf_hr"] == 88, "pf_hr is not index_hr"
        assert bos["pf_2b"] == 119, "pf_2b is not index_2b"
        col = df[df["team"] == "COL"].iloc[0]
        assert col["pf_3b"] == 146
        assert col["pf_so"] == 92
        assert col["pf_hardhit"] == 101

    def test_columns_are_exactly_the_declared_set_in_order(self):
        with _patch():
            df = park_factors(2026)
        assert list(df.columns) == _COLUMN_ORDER
        assert "pf_5yr" not in df.columns, "a FanGraphs-only column came back"
        assert "pf_fip" not in df.columns
        assert "index" not in df.columns, "reset_index leaked a column"

    def test_rows_are_sorted_by_team(self):
        # The documented example cites a positional index, so the order is
        # part of what callers see.
        with _patch():
            df = park_factors(2026)
        assert list(df["team"]) == ["BOS", "COL", "LAA", "OAK"]
        # venue_id order would be LAA, BOS, COL, OAK - a different answer.
        assert list(df["venue_id"]) != sorted(df["venue_id"])
        assert list(df.index) == list(range(len(df)))

    def test_dtypes_do_not_depend_on_whether_a_gap_is_present(self):
        with _patch() as _:
            with_gap = park_factors(2026)
        with _patch(single=_SINGLE[:2]) as _:
            without_gap = park_factors(2026)
        assert "OAK" not in set(without_gap["team"])
        for col in ("pf_3yr", "pf_1yr", "pf_hr", "n_pa_3yr"):
            assert str(with_gap[col].dtype) == "float64", col
            assert str(without_gap[col].dtype) == "float64", col
        assert str(with_gap["season"].dtype) == "int64"
        assert str(with_gap["venue_id"].dtype) == "int64"
        assert str(with_gap["n_pa_1yr"].dtype) == "int64"
        assert with_gap["venue_name"].map(type).eq(str).all()

    def test_window_label_kept(self):
        with _patch():
            df = park_factors(2026)
        labelled = df[df["team"].isin(["COL", "BOS"])]
        assert (labelled["pf_3yr_years"] == "2024-2026").all()

    def test_request_pins_every_query_parameter(self):
        # condition=, batSide= and parks= all change the numbers Savant
        # returns (measured 2026-09-23: condition=Day moves COL index_runs
        # 125 -> 125 with a different table, batSide=R -> 128, parks=all
        # returns 33 rows). A test that only checks year= would let any of
        # them be edited silently.
        with _patch() as mock_get:
            park_factors(2022)
        urls = [call.args[0] for call in mock_get.call_args_list]
        assert len(urls) == 2, "one request per window"
        rollings = set()
        for url in urls:
            parts = urlparse(url)
            assert parts.netloc == "baseballsavant.mlb.com"
            assert parts.path == "/leaderboard/statcast-park-factors"
            q = parse_qs(parts.query, keep_blank_values=True)
            assert q["year"] == ["2022"]
            assert q["type"] == ["year"]
            assert q["batSide"] == [""], "batSide changes the numbers"
            assert q["condition"] == ["All"], "condition changes the numbers"
            assert q["parks"] == ["mlb"], "parks changes the row count"
            assert q["stat"] == ["index_wOBA"]
            rollings.add(q["rolling"][0])
        assert rollings == {"", "1"}, "both windows must be requested"

    def test_honest_user_agent(self):
        # Claiming to be Chrome is what gets a python client challenged.
        from savant_extras.park_factors import _HEADERS

        ua = _HEADERS["User-Agent"]
        assert "savant-extras" in ua
        assert "Mozilla" not in ua and "Chrome" not in ua


class TestParkFactorsFailsLoudly:
    def test_missing_data_block_raises(self):
        with patch("savant_extras.park_factors.requests.get",
                   return_value=_response("<html>no leaderboard here</html>")):
            with pytest.raises(ValueError, match="data block not found"):
                park_factors(2026)

    def test_empty_single_season_table_raises(self):
        with _patch(single=[]):
            with pytest.raises(ValueError, match="empty park factor table"):
                park_factors(2026)

    def test_empty_three_year_table_raises(self):
        # A silently empty 3-year view would NaN out every park factor
        # column while still returning 30 rows.
        with _patch(multi=[]):
            with pytest.raises(ValueError, match="empty park factor table"):
                park_factors(2026)

    def test_page_serving_another_season_raises(self):
        stale = [dict(row, key_year="2019") for row in _SINGLE]
        with patch("savant_extras.park_factors.requests.get",
                   return_value=_response(_page(stale))):
            with pytest.raises(ValueError, match="key_year"):
                park_factors(2026)

    def test_renamed_index_key_raises_instead_of_going_all_nan(self):
        renamed = [{k.replace("index_hardhit", "index_hard_hit"): v
                    for k, v in row.items()} for row in _MULTI]
        with _patch(multi=renamed):
            with pytest.raises(ValueError, match="no longer sends"):
                park_factors(2026)

    def test_row_without_the_join_key_raises(self):
        broken = [dict(row) for row in _SINGLE]
        del broken[0]["venue_id"]
        with _patch(single=broken):
            with pytest.raises(ValueError, match="venue_id"):
                park_factors(2026)

    def test_all_clubs_unmappable_raises(self):
        with _patch(single=[_SINGLE[-1]]):
            with pytest.raises(ValueError, match="could be matched"):
                park_factors(2026)


class TestParkFactorsRange:
    def test_concatenates_seasons(self):
        with _patch():
            df = park_factors_range(2024, 2026, sleep=0)
        assert df["season"].nunique() == 3
        assert len(df) == 12
        assert sorted(df["season"].unique()) == [2024, 2025, 2026]

    def test_one_bad_season_does_not_lose_the_others_but_does_warn(self):
        good = _fake_get()

        def _flaky(url, **kwargs):
            if "year=2025" in url:
                raise RuntimeError("boom")
            return good(url, **kwargs)

        with patch("savant_extras.park_factors.requests.get", side_effect=_flaky):
            with pytest.warns(UserWarning, match="skipped 2025"):
                df = park_factors_range(2024, 2026, sleep=0)
        assert sorted(df["season"].unique()) == [2024, 2026]

    def test_total_failure_warns_and_returns_empty(self):
        with patch("savant_extras.park_factors.requests.get",
                   side_effect=RuntimeError("network down")):
            with pytest.warns(UserWarning, match="no data fetched"):
                df = park_factors_range(2024, 2026, sleep=0)
        assert df.empty


class TestModuleConstants:
    def test_column_order_covers_every_mapped_index(self):
        assert set(_INDEX_RENAME.values()) <= set(_COLUMN_ORDER)
        assert len(_COLUMN_ORDER) == len(set(_COLUMN_ORDER))

    def test_club_map_has_no_duplicate_abbreviation_outside_known_aliases(self):
        counts: dict[str, list[str]] = {}
        for name, abb in _NAME_TO_ABB.items():
            counts.setdefault(abb, []).append(name)
        shared = {abb: names for abb, names in counts.items() if len(names) > 1}
        assert shared == {"ARI": ["D-backs", "Diamondbacks"],
                          "CLE": ["Guardians", "Indians"]}, shared
