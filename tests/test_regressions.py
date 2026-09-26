"""Regression tests for the 0.6 fixes (all requests mocked, no network).

Measured live on 2026-09-27: Savant ignores parameters it does not know and
serves the current season with HTTP 200, so a wrong parameter name looked
like a healthy response. These tests pin the parameter names, the season
check, the empty-response warning and the statcast_minors retry path.
"""

from __future__ import annotations

import importlib
import re
import warnings
from unittest.mock import MagicMock, patch

import pytest
import requests

from savant_extras import EmptySavantResponse
from savant_extras.arm_strength import arm_strength
from savant_extras.home_runs import home_runs
from savant_extras.pitch_movement import pitch_movement
from savant_extras.statcast_minors import statcast_minors


def _resp(text, status=200):
    mock = MagicMock()
    mock.content = text.encode("utf-8")
    mock.status_code = status
    if status >= 400:
        mock.raise_for_status = MagicMock(
            side_effect=requests.HTTPError(f"{status} Server Error")
        )
    else:
        mock.raise_for_status = MagicMock()
    return mock


# name -> positional args for one call asking for season 2024
LEADERBOARDS = {
    "arm_strength": (2024,),
    "baserunning": (2024,),
    "basestealing": (2024,),
    "bat_tracking": ("2024-04-01", "2024-04-30"),
    "batted_ball": (2024,),
    "catcher_blocking": (2024,),
    "catcher_stance": (2024,),
    "catcher_throwing": (2024,),
    "home_runs": (2024,),
    "pitch_movement": (2024,),
    "pitch_tempo": (2024,),
    "pitcher_arm_angle": (2024,),
    "running_game": (2024,),
    "swing_take": (2024,),
    "timer_infractions": (2024,),
    "year_to_year": (2024,),
}

SEASON_CHECKED = sorted(set(LEADERBOARDS) - {"bat_tracking", "year_to_year"})


def _call(name, text, *args, **kwargs):
    fn = getattr(importlib.import_module(f"savant_extras.{name}"), name)
    with patch(f"savant_extras.{name}.requests.get") as get:
        get.return_value = _resp(text)
        out = fn(*(args or LEADERBOARDS[name]), **kwargs)
    return out, get.call_args[0][0]


# (a) header-only and HTML bodies warn ------------------------------------

@pytest.mark.parametrize("name", sorted(LEADERBOARDS))
def test_header_only_warns(name):
    with pytest.warns(EmptySavantResponse, match="header with no rows"):
        df, _ = _call(name, "year,player_id,value\n")
    assert df.empty


@pytest.mark.parametrize("name", sorted(LEADERBOARDS))
def test_html_warns(name):
    with pytest.warns(EmptySavantResponse, match="HTML page"):
        df, _ = _call(name, "<!DOCTYPE html><html></html>")
    assert df.empty


# (b) rows from another season raise --------------------------------------

@pytest.mark.parametrize("name", SEASON_CHECKED)
def test_wrong_season_raises(name):
    with pytest.raises(ValueError, match=r"asked for season 2024 .*\[2026\]"):
        _call(name, "year,player_id\n2026,1\n")


@pytest.mark.parametrize("name", SEASON_CHECKED)
def test_right_season_passes(name):
    # control for the test above: the same body under the asked season
    df, _ = _call(name, "year,player_id\n2024,1\n")
    assert list(df["player_id"]) == [1]


@pytest.mark.parametrize("column", ["year", "start_year", "season"])
def test_every_season_column_is_checked(column):
    with pytest.raises(ValueError, match=repr(column)):
        _call("baserunning", f"{column},player_id\n2026,1\n")


# (c) the dead parameters are gone, the live ones are sent ----------------

DEAD = [
    # name, args, kwargs, pattern that must be absent, substrings that must be present
    ("baserunning", (2024,), {}, r"[?&](year|min)=", ["season_start=2024", "season_end=2024", "n=q"]),
    ("basestealing", (2024,), {}, r"[?&](year|min)=", ["season_start=2024", "season_end=2024"]),
    ("catcher_blocking", (2024,), {}, r"[?&](year|min)=", ["season_start=2024", "season_end=2024"]),
    ("catcher_throwing", (2024,), {}, r"[?&](year|min)=", ["season_start=2024", "season_end=2024"]),
    ("running_game", (2024,), {}, r"[?&](year|min)=", ["season_start=2024", "season_end=2024"]),
    ("catcher_stance", (2024,), {}, r"[?&](year|min)=",
     ["type=catcher", "gameType=Regular", "seasonStart=2024", "seasonEnd=2024", "minPitches="]),
    ("pitcher_arm_angle", (2024,), {}, r"[?&]year=", ["season=2024"]),
    ("timer_infractions", (2024,), {}, r"[?&]year=", ["season=2024"]),
    ("pitch_movement", (2024,), {"pitch_type": "SL"}, r"pitchType=", ["pitch_type=SL"]),
    ("home_runs", (2024,), {"player_type": "pitcher"}, r"[?&]type=",
     ["player_type=Pitcher", "cat=adj_xhr", "min=0"]),
    ("year_to_year", (2024,), {"player_type": "pitcher"}, r"[?&]type=pitcher",
     ["group=Pitcher", "type=xwoba"]),
    ("swing_take", (2024,), {"player_type": "pitcher"}, r"[?&]type=", ["group=Pitcher"]),
    ("arm_strength", (2024,), {"position": "SS"}, r"[?&]pos=", ["year=2024", "minThrows=100"]),
]


@pytest.mark.parametrize("name,args,kwargs,dead,live", DEAD, ids=[d[0] for d in DEAD])
def test_dead_parameter_not_sent(name, args, kwargs, dead, live):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", EmptySavantResponse)
        _, url = _call(name, "player_id\n", *args, **kwargs)
    assert re.search(dead, url) is None, url
    for part in live:
        assert part in url, (part, url)


def test_home_runs_hr_type_not_sent():
    with pytest.warns(DeprecationWarning):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EmptySavantResponse)
            _, url = _call("home_runs", "player_id\n", 2024, hr_type="distance")
    assert "distance" not in url and re.search(r"[?&]type=", url) is None


# (d) arm_strength filters by position on the client ----------------------

ARM_CSV = (
    "player_id,year,arm_overall,arm_ss,arm_of\n"
    "1,2024,88.0,90.1,\n"
    "2,2024,85.0,,91.0\n"
    "3,2024,84.0,87.5,\n"
    "4,2024,80.0,,\n"
)


def test_arm_strength_keeps_only_shortstops():
    with patch("savant_extras.arm_strength.requests.get") as get:
        get.return_value = _resp(ARM_CSV)
        df = arm_strength(2024, position="SS")
    assert list(df["player_id"]) == [1, 3]
    assert df["arm_ss"].notna().all()
    assert list(df.index) == [0, 1]


def test_arm_strength_outfielder_maps_to_arm_of():
    with patch("savant_extras.arm_strength.requests.get") as get:
        get.return_value = _resp(ARM_CSV)
        df = arm_strength(2024, position="Outfielder")
    assert list(df["player_id"]) == [2]


def test_arm_strength_no_position_keeps_all():
    with patch("savant_extras.arm_strength.requests.get") as get:
        get.return_value = _resp(ARM_CSV)
        assert len(arm_strength(2024)) == 4


def test_arm_strength_unknown_position_raises_before_request():
    with patch("savant_extras.arm_strength.requests.get") as get:
        with pytest.raises(ValueError, match="position"):
            arm_strength(2024, position="P")
    get.assert_not_called()


def test_arm_strength_missing_column_raises():
    with patch("savant_extras.arm_strength.requests.get") as get:
        get.return_value = _resp(ARM_CSV)
        with pytest.raises(ValueError, match="arm_cf"):
            arm_strength(2024, position="CF")


# (e) pitch_movement refuses a table of the wrong pitch type --------------

PM_CSV = "year,pitcher_id,pitch_type,pitcher_break_z\n2024,1,FF,14.2\n2024,2,FF,13.0\n"


def test_pitch_movement_mismatched_type_raises():
    with patch("savant_extras.pitch_movement.requests.get") as get:
        get.return_value = _resp(PM_CSV)
        with pytest.raises(ValueError, match="pitch_type=CU"):
            pitch_movement(2024, pitch_type="CU")


def test_pitch_movement_matching_type_passes():
    with patch("savant_extras.pitch_movement.requests.get") as get:
        get.return_value = _resp(PM_CSV.replace(",FF,", ",CU,"))
        assert len(pitch_movement(2024, pitch_type="CU")) == 2


# (f) home_runs(hr_type=...) is deprecated --------------------------------

def test_home_runs_hr_type_deprecated():
    with patch("savant_extras.home_runs.requests.get") as get:
        get.return_value = _resp("year,player_id\n2024,1\n")
        with pytest.warns(DeprecationWarning, match="hr_type"):
            home_runs(2024, hr_type="exit_velocity")


def test_home_runs_without_hr_type_does_not_warn():
    with patch("savant_extras.home_runs.requests.get") as get:
        get.return_value = _resp("year,player_id\n2024,1\n")
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            home_runs(2024)


# (g) statcast_minors: bad days and retries --------------------------------

SC_HEAD = "pitch_type,game_date,game_pk,home_team,away_team\n"


def _sc(day, n):
    return SC_HEAD + "".join(f"FF,{day},780001,TOL,COL\n" for _ in range(n))


@patch("savant_extras.statcast_minors.time.sleep")
@patch("savant_extras.statcast_minors.requests.get")
def test_minors_html_day_warns_once_and_keeps_other_days(get, _sleep):
    get.side_effect = [
        _resp(_sc("2025-06-10", 2)),
        _resp("<html><body>error</body></html>"),
        _resp(_sc("2025-06-12", 3)),
    ]
    with pytest.warns(EmptySavantResponse) as rec:
        df = statcast_minors("2025-06-10", "2025-06-12")
    assert len(rec) == 1
    assert "2025-06-11" in str(rec[0].message) and "HTML" in str(rec[0].message)
    assert len(df) == 5
    assert sorted(df["game_date"].unique()) == ["2025-06-10", "2025-06-12"]


@patch("savant_extras.statcast_minors.time.sleep")
@patch("savant_extras.statcast_minors.requests.get")
def test_minors_retries_503_then_succeeds(get, sleep):
    get.side_effect = [_resp("", status=503), _resp(_sc("2025-06-10", 4))]
    df = statcast_minors("2025-06-10", "2025-06-10")
    assert len(df) == 4
    assert get.call_count == 2
    assert sleep.call_count == 1


@patch("savant_extras.statcast_minors.time.sleep")
@patch("savant_extras.statcast_minors.requests.get")
def test_minors_retries_connection_error(get, _sleep):
    get.side_effect = [requests.ConnectionError("reset"), _resp(_sc("2025-06-10", 1))]
    assert len(statcast_minors("2025-06-10", "2025-06-10")) == 1


@patch("savant_extras.statcast_minors.time.sleep")
@patch("savant_extras.statcast_minors.requests.get")
def test_minors_persistent_503_raises(get, _sleep):
    get.return_value = _resp("", status=503)
    with pytest.raises(requests.HTTPError):
        statcast_minors("2025-06-10", "2025-06-10")
    assert get.call_count == 3


@patch("savant_extras.statcast_minors.time.sleep")
@patch("savant_extras.statcast_minors.requests.get")
def test_minors_4xx_is_not_retried(get, _sleep):
    get.return_value = _resp("", status=404)
    with pytest.raises(requests.HTTPError):
        statcast_minors("2025-06-10", "2025-06-10")
    assert get.call_count == 1
