# savant-extras

**Baseball Savant leaderboard data — complements pybaseball.**

[pybaseball](https://github.com/jldbc/pybaseball) is great but many Baseball Savant leaderboards are missing or limited. `savant-extras` fills that gap with **15+ leaderboards** covering batting, pitching, catching, baserunning, and fielding — all as simple one-line function calls returning DataFrames.

## Installation

```bash
pip install savant-extras
```

## Quick Start

```python
from savant_extras import (
    bat_tracking, pitch_tempo, arm_strength,
    pitch_movement, swing_take, catcher_throwing,
)

# Bat tracking with custom date range (2024+)
df = bat_tracking("2024-04-01", "2024-04-30")

# Pitcher pitch tempo
df = pitch_tempo(2024)

# Outfielder arm strength
df = arm_strength(2024, position="Outfielder")

# Slider movement
df = pitch_movement(2024, pitch_type="SL")

# Batter plate discipline
df = swing_take(2024)

# Catcher pop time & CS rate
df = catcher_throwing(2024)
```

## All Functions

Every leaderboard function returns a `pd.DataFrame`. Most have a `_range()` variant for multi-season queries (adds a `year` column).

### Batting

| Function | Data from | Description |
|---|---|---|
| `bat_tracking(start_date, end_date)` | 2024+ | Bat speed, attack angle, swing tilt (custom date range) |
| `bat_tracking_monthly(year)` | 2024+ | Monthly bat tracking (Apr–Oct) |
| `bat_tracking_splits(year)` | 2024+ | First-half / second-half splits |
| `batted_ball(year)` | — | GB/FB/LD rates, pull/oppo splits |
| `home_runs(year)` | — | HR distance, exit velocity, xHR, no-doubters |
| `swing_take(year)` | — | Run values by zone (heart/shadow/chase/waste) |
| `year_to_year(year)` | — | xwOBA changes across seasons |

### Pitching

| Function | Data from | Description |
|---|---|---|
| `pitch_tempo(year)` | 2010+ | Pace metrics (median seconds, hot/warm/cold) |
| `pitch_movement(year)` | — | Horizontal/vertical break by pitch type |
| `pitcher_arm_angle(year)` | — | Release point angles and positions |
| `running_game(year)` | — | Pitcher running game (pickoffs, CS above avg) |
| `timer_infractions(year)` | 2023+ | Pitch clock violations |

### Catching

| Function | Data from | Description |
|---|---|---|
| `catcher_blocking(year)` | — | Blocks above average, PB/WP prevention |
| `catcher_throwing(year)` | — | Pop time, exchange time, CS rate, arm strength |
| `catcher_stance(year)` | — | One-knee vs traditional: framing, blocking, throwing |

### Baserunning & Fielding

| Function | Data from | Description |
|---|---|---|
| `arm_strength(year)` | 2020+ | Fielder throw speed by position |
| `baserunning(year)` | — | Total baserunning run value (XB + SB) |
| `basestealing(year)` | — | Stolen base run value, lead distances |

### Common Parameters

| Parameter | Type | Description |
|---|---|---|
| `player_type` | str | `"batter"` or `"pitcher"` (where applicable) |
| `min_*` | int or str | Minimum threshold; `"q"` = qualified |
| `position` | str | Position filter (arm_strength): `""`, `"RF"`, `"SS"`, etc. |
| `pitch_type` | str | Pitch type filter (pitch_movement): `"FF"`, `"SL"`, etc. |

### Multi-Season Queries

Most functions have a `_range(start_year, end_year)` variant:

```python
from savant_extras import pitch_tempo_range, arm_strength_range

# Compare pitch tempo pre/post pitch clock
df = pitch_tempo_range(2022, 2024)

# 5 years of arm strength
df = arm_strength_range(2020, 2024)
```

## Demo App

**[MLB Bat Tracking Dashboard](https://yasumorishima-mlb-bat-tracking.streamlit.app/)** — built with savant-extras ([source](https://github.com/yasumorishima/mlb-bat-tracking-dashboard))

## Why savant-extras?

| Leaderboard | pybaseball | savant-extras |
|---|---|---|
| Bat tracking (date range) | Full season only | Custom date ranges |
| Pitch tempo | Not supported | ✅ |
| Arm strength | Not supported | ✅ |
| Batted ball profile | Not supported | ✅ |
| Home runs | Not supported | ✅ |
| Pitch movement | Not supported | ✅ |
| Swing & take | Not supported | ✅ |
| Year-to-year changes | Not supported | ✅ |
| Pitcher arm angle | Not supported | ✅ |
| Running game (pitcher) | Not supported | ✅ |
| Catcher blocking | Not supported | ✅ |
| Catcher throwing | Not supported | ✅ |
| Catcher stance | Not supported | ✅ |
| Baserunning run value | Not supported | ✅ |
| Basestealing run value | Not supported | ✅ |
| Timer infractions | Not supported | ✅ |

## Known Issues

- **`swing_take()`**: Baseball Savant's CSV endpoint for the Swing & Take leaderboard currently returns header-only data (no rows) for all years. The function is included and will work when the upstream API is restored, but currently returns an empty DataFrame.

## License

MIT
