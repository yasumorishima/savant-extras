"""Live: every season and filter argument must change what Savant returns.

Through 0.5.0, twelve functions sent parameters Savant had stopped reading,
and Savant answered each with the current season's table. The unit tests
mocked every request, so none of it showed. Skipped unless SAVANT_LIVE=1.
"""

from __future__ import annotations

import os
import time
import warnings

import pytest

import savant_extras as sx

pytestmark = pytest.mark.skipif(
    os.environ.get("SAVANT_LIVE") != "1", reason="set SAVANT_LIVE=1 for live Savant tests"
)

CASES = [
    ("arm_strength", dict(year=2024), dict(year=2025)),
    ("baserunning", dict(year=2024), dict(year=2025)),
    ("baserunning", dict(year=2025), dict(year=2025, min_opportunities=1)),
    ("basestealing", dict(year=2024), dict(year=2025)),
    ("batted_ball", dict(year=2024), dict(year=2025)),
    ("catcher_blocking", dict(year=2024), dict(year=2025)),
    ("catcher_stance", dict(year=2024), dict(year=2025)),
    ("catcher_throwing", dict(year=2024), dict(year=2025)),
    ("home_runs", dict(year=2025), dict(year=2025, player_type="pitcher")),
    ("home_runs", dict(year=2025), dict(year=2025, category="xhr")),
    ("pitch_movement", dict(year=2025, pitch_type="SL"), dict(year=2025, pitch_type="CU")),
    ("pitch_tempo", dict(year=2024), dict(year=2025)),
    ("pitcher_arm_angle", dict(year=2024), dict(year=2025)),
    ("running_game", dict(year=2024), dict(year=2025)),
    ("swing_take", dict(year=2024), dict(year=2025)),
    ("timer_infractions", dict(year=2024), dict(year=2025)),
    ("year_to_year", dict(year=2025), dict(year=2025, player_type="pitcher")),
    ("year_to_year", dict(year=2025), dict(year=2025, stat="ba")),
]


@pytest.mark.parametrize("name,a,b", CASES, ids=[f"{c[0]}-{sorted(c[2].items())}" for c in CASES])
def test_argument_changes_the_answer(name, a, b):
    fn = getattr(sx, name)
    with warnings.catch_warnings():
        warnings.simplefilter("error", sx.EmptySavantResponse)
        da = fn(**a)
        time.sleep(1)
        db = fn(**b)
    time.sleep(1)
    assert len(da) > 0 and len(db) > 0
    assert not da.equals(db), f"{name}: {b} returned the same table as {a}"


def test_arm_strength_position_keeps_only_that_position():
    df = sx.arm_strength(2025, position="SS")
    assert len(df) > 0 and df["arm_ss"].notna().all()
    assert len(df) < len(sx.arm_strength(2025))
