"""Real requests to Baseball Savant.

Skipped unless SAVANT_LIVE=1. The unit tests mock every request, which is
how swing_take returned zero rows for every season through 0.5.0 with a
green suite. These check what Savant actually answers.
"""

from __future__ import annotations

import os
import warnings

import pytest

from savant_extras import (
    EmptySavantResponse,
    abs_challenges,
    statcast_minors,
    swing_take,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("SAVANT_LIVE") != "1", reason="set SAVANT_LIVE=1 for live Savant tests"
)


def _no_empty_warning(fn, *a, **kw):
    with warnings.catch_warnings():
        warnings.simplefilter("error", EmptySavantResponse)
        return fn(*a, **kw)


def test_swing_take_returns_batters_and_pitchers():
    bat = _no_empty_warning(swing_take, 2025, player_type="batter")
    pit = _no_empty_warning(swing_take, 2025, player_type="pitcher")
    assert len(bat) > 100 and len(pit) > 100
    assert set(bat["player_id"]) != set(pit["player_id"])
    assert {"runs_heart", "runs_shadow", "runs_chase", "runs_waste"} <= set(bat.columns)


@pytest.mark.parametrize(
    "year,level,ctype,minimum",
    [(2026, "mlb", "batter", 300), (2026, "mlb", "catcher", 50),
     (2025, "aaa", "batter", 300), (2025, "aaa", "catcher", 50)],
)
def test_abs_challenges(year, level, ctype, minimum):
    df = _no_empty_warning(abs_challenges, year, level=level, challenge_type=ctype)
    assert len(df) >= minimum
    assert set(df["level"]) == {level.upper()}
    assert set(df["year"]) == {year}
    assert (df["n_overturns"] + df["n_fails"] == df["n_challenges"]).all()
    assert df["player_id"].notna().all() and df["player_id"].is_unique


def test_abs_challenges_mlb_2025_is_empty():
    # MLB adopted challenges in 2026
    with pytest.warns(EmptySavantResponse):
        assert abs_challenges(2025).empty


def test_statcast_minors_one_day_of_triple_a():
    df = statcast_minors("2025-06-10", "2025-06-10")
    assert len(df) > 1000
    # Triple-A clubs, not major-league ones
    assert {"TOL", "IOW", "DUR"} & set(df["home_team"])
    assert df["arm_angle"].notna().mean() > 0.9
    assert df["bat_speed"].isna().all()
