"""
savant-extras: Baseball Savant leaderboard data — complements pybaseball.

Provides access to Baseball Savant leaderboards that pybaseball does not
support, covering batting, pitching, catching, baserunning, and fielding.

Available leaderboards
----------------------
- **Bat tracking** (2024+): arbitrary date ranges for custom splits.
- **Pitch tempo** (2010+): pace metrics by pitcher or batter.
- **Arm strength** (2020+): fielder throw speed and accuracy.
- **Batted ball** profile: GB/FB/LD rates, pull/oppo splits.
- **Home runs**: HR totals, xHR, no-doubters, trot time; hit or allowed.
- **Pitch movement**: horizontal/vertical break by pitch type.
- **Swing & take**: run values by zone (heart/shadow/chase/waste).
- **Year-to-year**: xwOBA changes across seasons.
- **Pitcher arm angle**: release point angles.
- **Running game** (pitcher): pickoffs, CS above average.
- **Catcher blocking**: blocks above average, PB/WP prevention.
- **Catcher throwing**: pop time, CS rate, arm strength.
- **Catcher stance**: one-knee vs traditional metrics.
- **Baserunning run value**: total baserunning value.
- **Basestealing run value**: stolen base run value.
- **Timer infractions** (2023+): pitch clock violations.
- **ABS challenges** (MLB 2026+, Triple-A 2025+): challenge results
  against an expected overturn rate, by batter, pitcher or catcher.
- **Minor-league Statcast** (Triple-A 2023+): pitch-level search with
  ``minors=true``, which pybaseball's ``statcast()`` cannot send.
- **Park factors** (2015+): Statcast ballpark run factors, 1-year and 3-year
  windows. The FanGraphs table is still available as ``park_factors_fangraphs``.

Basic usage
-----------
>>> from savant_extras import bat_tracking, pitch_tempo, arm_strength
>>> df = bat_tracking("2024-04-01", "2024-04-30")
>>> df = pitch_tempo(2024)
>>> df = arm_strength(2024, position="Outfielder")
"""

from savant_extras._http import EmptySavantResponse
from savant_extras.abs_challenges import abs_challenges, abs_challenges_range
from savant_extras.arm_strength import arm_strength, arm_strength_range
from savant_extras.baserunning import baserunning, baserunning_range
from savant_extras.basestealing import basestealing, basestealing_range
from savant_extras.bat_tracking import (
    bat_tracking,
    bat_tracking_monthly,
    bat_tracking_splits,
)
from savant_extras.batted_ball import batted_ball, batted_ball_range
from savant_extras.catcher_blocking import catcher_blocking, catcher_blocking_range
from savant_extras.catcher_stance import catcher_stance, catcher_stance_range
from savant_extras.catcher_throwing import catcher_throwing, catcher_throwing_range
from savant_extras.home_runs import home_runs, home_runs_range
from savant_extras.pitch_movement import pitch_movement, pitch_movement_range
from savant_extras.pitch_tempo import pitch_tempo, pitch_tempo_range
from savant_extras.pitcher_arm_angle import pitcher_arm_angle, pitcher_arm_angle_range
from savant_extras.running_game import running_game, running_game_range
from savant_extras.swing_take import swing_take, swing_take_range
from savant_extras.timer_infractions import timer_infractions, timer_infractions_range
from savant_extras.park_factors import park_factors, park_factors_range
from savant_extras.park_factors_fangraphs import (
    park_factors_fangraphs,
    park_factors_fangraphs_range,
)
from savant_extras.statcast_minors import statcast_minors
from savant_extras.year_to_year import year_to_year

__all__ = [
    "EmptySavantResponse",
    "abs_challenges",
    "abs_challenges_range",
    "arm_strength",
    "arm_strength_range",
    "baserunning",
    "baserunning_range",
    "basestealing",
    "basestealing_range",
    "bat_tracking",
    "bat_tracking_monthly",
    "bat_tracking_splits",
    "batted_ball",
    "batted_ball_range",
    "catcher_blocking",
    "catcher_blocking_range",
    "catcher_stance",
    "catcher_stance_range",
    "catcher_throwing",
    "catcher_throwing_range",
    "home_runs",
    "home_runs_range",
    "pitch_movement",
    "pitch_movement_range",
    "pitch_tempo",
    "pitch_tempo_range",
    "pitcher_arm_angle",
    "pitcher_arm_angle_range",
    "running_game",
    "running_game_range",
    "swing_take",
    "swing_take_range",
    "timer_infractions",
    "timer_infractions_range",
    "park_factors",
    "park_factors_range",
    "park_factors_fangraphs",
    "park_factors_fangraphs_range",
    "statcast_minors",
    "year_to_year",
]

__version__ = "0.6.1"
