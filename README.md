# savant-extras

**Baseball Savant leaderboard data — complements pybaseball.**

[pybaseball](https://github.com/jldbc/pybaseball) is great for season-level data, but many Baseball Savant leaderboards are missing or limited to full seasons. `savant-extras` fills that gap with **pitch tempo**, **arm strength**, and **bat tracking with arbitrary date ranges**.

| Leaderboard | Data available | pybaseball | savant-extras |
|---|---|---|---|
| Bat tracking (date range) | 2024+ | Full season only | Custom date ranges |
| Pitch tempo | 2010+ | Not supported | ✅ |
| Arm strength | 2020+ | Not supported | ✅ |

## Demo App

**[MLB Bat Tracking Dashboard](https://yasumorishima-mlb-bat-tracking.streamlit.app/)** — A Streamlit app built with savant-extras. Source code: [mlb-bat-tracking-dashboard](https://github.com/yasumorishima/mlb-bat-tracking-dashboard)

## Installation

```bash
pip install savant-extras
```

## Quick Start

```python
from savant_extras import bat_tracking, pitch_tempo, arm_strength

# April 2024 batter bat tracking
df = bat_tracking("2024-04-01", "2024-04-30")

# 2024 pitcher pitch tempo
df = pitch_tempo(2024)

# 2024 outfielder arm strength
df = arm_strength(2024, position="Outfielder")
```

## Functions

### Bat Tracking

#### `bat_tracking(start_date, end_date, player_type="batter", min_swings="q")`

Retrieve bat tracking leaderboard for any date range.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_date` | str | — | Start date `YYYY-MM-DD` |
| `end_date` | str | — | End date `YYYY-MM-DD` |
| `player_type` | str | `"batter"` | `"batter"` or `"pitcher"` |
| `min_swings` | int or str | `"q"` | Minimum competitive swings (`"q"` = qualified) |

**Returns**: `pd.DataFrame` with columns including `avg_bat_speed`, `swing_tilt`, `attack_angle`, etc.

#### `bat_tracking_monthly(year, player_type="batter", min_swings=1)`

Retrieve bat tracking for each month of a season (April–October). Adds a `month` column.

#### `bat_tracking_splits(year, player_type="batter", min_swings="q")`

Retrieve first-half / second-half splits. Returns `{"first_half": DataFrame, "second_half": DataFrame}`.

---

### Pitch Tempo

#### `pitch_tempo(year, player_type="pitcher", min_pitches="q", game_type="Regular")`

Retrieve pitch tempo leaderboard for a season. Data available from **2010** onward.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `year` | int | — | Season year |
| `player_type` | str | `"pitcher"` | `"pitcher"` or `"batter"` |
| `min_pitches` | int or str | `"q"` | Minimum pitches (`"q"` = qualified) |
| `game_type` | str | `"Regular"` | Game type filter |

**Returns**: `pd.DataFrame` with columns including `median_seconds_empty`, `freq_hot`, `freq_warm`, `freq_cold`, etc.

```python
from savant_extras import pitch_tempo, pitch_tempo_range

# 2024 pitcher tempo
df = pitch_tempo(2024)

# Batter perspective
df = pitch_tempo(2024, player_type="batter")

# Compare pre/post pitch clock (2022 vs 2023)
df = pitch_tempo_range(2022, 2023)
```

#### `pitch_tempo_range(start_year, end_year, player_type="pitcher", min_pitches="q", game_type="Regular")`

Retrieve pitch tempo for multiple seasons. Adds a `year` column.

---

### Arm Strength

#### `arm_strength(year, position="", min_throws=100)`

Retrieve arm strength leaderboard for a season. Data available from **2020** onward.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `year` | int | — | Season year |
| `position` | str | `""` | Position filter (`""`, `"RF"`, `"SS"`, `"Outfielder"`, etc.) |
| `min_throws` | int | `100` | Minimum throws |

**Returns**: `pd.DataFrame` with columns including `max_arm_strength`, `arm_overall`, `total_throws`, etc.

```python
from savant_extras import arm_strength, arm_strength_range

# 2024 all positions
df = arm_strength(2024)

# Right fielders only, lower threshold
df = arm_strength(2024, position="RF", min_throws=50)

# Multi-year comparison
df = arm_strength_range(2020, 2024)
```

#### `arm_strength_range(start_year, end_year, position="", min_throws=100)`

Retrieve arm strength for multiple seasons. Adds a `year` column.

## License

MIT
