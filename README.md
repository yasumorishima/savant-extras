# savant-extras

**Baseball Savant leaderboard data with date range support.**

[pybaseball](https://github.com/jldbc/pybaseball) is great for season-level data, but all its leaderboard functions are limited to full seasons. `savant-extras` fills that gap by supporting **arbitrary date ranges** — enabling monthly splits, first/second half comparisons, pre/post trade analysis, and more.

Bat tracking data (Hawk-Eye) is available from the **2024 season onward**.

## Demo App

**[MLB Bat Tracking Dashboard](https://yasumorishima-mlb-bat-tracking.streamlit.app/)** — A Streamlit app built with savant-extras. Source code: [mlb-bat-tracking-dashboard](https://github.com/yasumorishima/mlb-bat-tracking-dashboard)

## Installation

```bash
pip install savant-extras
```

## Quick Start

```python
from savant_extras import bat_tracking, bat_tracking_monthly, bat_tracking_splits

# April 2024 — batter bat tracking
df = bat_tracking("2024-04-01", "2024-04-30")

# Pitcher perspective
df = bat_tracking("2024-04-01", "2024-06-30", player_type="pitcher")

# Full season broken down by month
df = bat_tracking_monthly(2024)
print(df.groupby("month")["avg_bat_speed"].mean())

# First half vs second half
splits = bat_tracking_splits(2024)
first  = splits["first_half"]
second = splits["second_half"]
```

## Functions

### `bat_tracking(start_date, end_date, player_type="batter", min_swings="q")`

Retrieve bat tracking leaderboard for any date range.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_date` | str | — | Start date `YYYY-MM-DD` |
| `end_date` | str | — | End date `YYYY-MM-DD` |
| `player_type` | str | `"batter"` | `"batter"` or `"pitcher"` |
| `min_swings` | int or str | `"q"` | Minimum competitive swings (`"q"` = qualified) |

**Returns**: `pd.DataFrame` with columns including `avg_bat_speed`, `swing_tilt`, `attack_angle`, etc.

---

### `bat_tracking_monthly(year, player_type="batter", min_swings=1)`

Retrieve bat tracking for each month of a season (April–October).
Adds a `month` column to the returned DataFrame.

---

### `bat_tracking_splits(year, player_type="batter", min_swings="q")`

Retrieve first-half / second-half splits. Returns a dict:
```python
{"first_half": pd.DataFrame, "second_half": pd.DataFrame}
```

## Why savant-extras?

| | pybaseball | savant-extras |
|---|---|---|
| Full season data | ✅ | ✅ |
| Monthly splits | ❌ | ✅ |
| First/second half | ❌ | ✅ |
| Custom date range | ❌ | ✅ |
| Pre/post trade splits | ❌ | ✅ |

## License

MIT
