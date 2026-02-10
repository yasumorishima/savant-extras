"""
savant-extras: Baseball Savant leaderboard data with date range support.

Extends pybaseball with arbitrary date ranges for custom splits
(monthly, first/second half, pre/post trade, etc.).

Bat tracking data is available from the 2024 season onward (Hawk-Eye).

Basic usage
-----------
>>> from savant_extras import bat_tracking, bat_tracking_monthly, bat_tracking_splits

>>> # April 2024 batter bat tracking
>>> df = bat_tracking("2024-04-01", "2024-04-30")

>>> # Monthly splits for full season
>>> df = bat_tracking_monthly(2024)

>>> # First half / second half comparison
>>> splits = bat_tracking_splits(2024)
"""

from savant_extras.bat_tracking import (
    bat_tracking,
    bat_tracking_monthly,
    bat_tracking_splits,
)

__all__ = [
    "bat_tracking",
    "bat_tracking_monthly",
    "bat_tracking_splits",
]

__version__ = "0.1.0"
