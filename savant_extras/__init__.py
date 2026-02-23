"""
savant-extras: Baseball Savant leaderboard data — complements pybaseball.

Provides access to Baseball Savant leaderboards that pybaseball does not
support, including bat tracking (date range), pitch tempo, and arm strength.

Available leaderboards
----------------------
- **Bat tracking** (2024+): arbitrary date ranges for custom splits.
- **Pitch tempo** (2010+): pace metrics by pitcher or batter.
- **Arm strength** (2020+): fielder throw speed and accuracy.

Basic usage
-----------
>>> from savant_extras import bat_tracking, pitch_tempo, arm_strength

>>> # April 2024 batter bat tracking
>>> df = bat_tracking("2024-04-01", "2024-04-30")

>>> # 2024 pitcher pitch tempo
>>> df = pitch_tempo(2024)

>>> # 2024 outfielder arm strength
>>> df = arm_strength(2024, position="Outfielder")
"""

from savant_extras.arm_strength import arm_strength, arm_strength_range
from savant_extras.bat_tracking import (
    bat_tracking,
    bat_tracking_monthly,
    bat_tracking_splits,
)
from savant_extras.pitch_tempo import pitch_tempo, pitch_tempo_range

__all__ = [
    "bat_tracking",
    "bat_tracking_monthly",
    "bat_tracking_splits",
    "pitch_tempo",
    "pitch_tempo_range",
    "arm_strength",
    "arm_strength_range",
]

__version__ = "0.2.0"
