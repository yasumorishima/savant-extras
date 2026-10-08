# Changelog

## 0.6.1

No change to the library code.

- The PyPI summary is the current one (it still said "16+ leaderboards"; the package wraps 17 Savant leaderboards, plus FanGraphs park factors, ABS challenges and Triple-A Statcast).
- Classifiers list every Python the CI now tests: 3.9 to 3.14.
- Tests patch `requests.get`, `time.sleep` and `pandas.read_html` directly, so they run on 3.9 and 3.10 too (266 tests failed there before, because the old patch targets resolved to same-named re-exports).
- The live Savant tests also run every Monday, not only on pull requests.

## 0.6.0

### Fixed: twelve functions returned the wrong data, silently

Savant ignores a query parameter it does not recognise and answers with
HTTP 200 and the **current season's** table. Measured live on 2026-09-27,
twelve functions were sending parameters Savant no longer reads:

| Function | Was sending | Effect | Now sends |
|---|---|---|---|
| `baserunning`, `basestealing`, `catcher_blocking`, `catcher_throwing`, `running_game` | `year=`, `min=` | every season returned the current one; minimum ignored | `season_start=`/`season_end=`, `n=` |
| `catcher_stance` | `year=`, `min=` | league-summary rows (one per season), not catchers | `type=catcher&seasonStart=`/`seasonEnd=`, `minPitches=` |
| `pitcher_arm_angle`, `timer_infractions` | `year=` | every season returned the current one | `season=` |
| `pitch_movement` | `pitchType=` | always four-seamers | `pitch_type=` (default now `"FF"`) |
| `home_runs` | `type=exit_velocity/distance` | argument had no effect | `player_type=Batter/Pitcher`, `cat=adj_xhr/xhr`, `min=` |
| `year_to_year` | `type=batter/pitcher` | always batters, and not xwOBA | `group=Batter/Pitcher`, `type=<stat>` (default `xwoba`) |
| `arm_strength` | `pos=` | position ignored | filtered locally on the `arm_<pos>` column |
| `swing_take` | `type=batter` | zero rows | `group=Batter/Pitcher` |

**If you saved data with these functions, re-fetch it.** Across seasons the
files will look plausible - the same players, the same columns - and be the
same table repeated under different years.

To stop this recurring silently, eleven functions now compare the season
column Savant returns with the season asked for and raise `ValueError` on a
mismatch, and `pitch_movement` does the same for the pitch type.
`pitcher_arm_angle`, `arm_strength` and `pitch_tempo` return no season
column, so for them only the live tests (which check that 2024 and 2025
differ) guard against a season being ignored.
`home_runs(hr_type=...)` still runs but warns `DeprecationWarning`.

**Breaking for positional callers:** the second positional argument of
`home_runs` is now `player_type`, so `home_runs(2024, "distance")` raises
`ValueError`; pass `hr_type=` by keyword (it is ignored) or drop it.
`arm_strength(position=...)` now raises on values outside
`"", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "Outfielder", "2B/SS/3B"`
instead of passing them to Savant, which ignored them anyway.
`pitch_movement`'s default `pitch_type` is now `"FF"`, which is what an
empty string always returned.

### Fixed: `swing_take()` returned no rows for every season

It sent `type=batter`, which Savant answers with a CSV header and no rows.
The parameter is `group`, and its values are case-sensitive (`Batter` /
`Pitcher`). The README blamed an upstream outage; that was wrong. The unit
tests mocked every request, so nothing ever checked a real answer - see
the live tests below.

### Empty answers warn instead of passing silently

All 16 leaderboard functions now share one parser. An HTML page, an empty
body, or a header-only CSV still returns an empty DataFrame, and now also
emits `EmptySavantResponse` (a `UserWarning`) naming the URL.
The `*_range` functions therefore warn once per empty season (for example
a season before a leaderboard existed); filter `EmptySavantResponse` if that
is expected.

### Added: `abs_challenges()` / `abs_challenges_range()`

The ABS challenge leaderboard: MLB from 2026, Triple-A from 2025, by
batter, pitcher or catcher. It reads the JSON the leaderboard page embeds
rather than its `csv=true` export: same rows, but 86 fields instead of 36,
including the MLBAM `player_id` (the CSV has only a display name) and the
run-value columns. Savant ignores parameters it does not know, so
the function checks that the `year` and `level` it got back are the ones
it asked for and raises otherwise.

### Added: `statcast_minors()`

Pitch-level Statcast for Triple-A (and the Class-A clubs Savant serves),
one request per day. It always sends `minors=true` - without it `hfLevel`
is ignored - and raises if a returned game is between two major-league
clubs. Bat tracking columns are empty in the minors; `arm_angle` is filled
from 2023.

### Corrected claims about pybaseball

The README and two module docstrings said pybaseball does not read the
pitch movement and swing & take leaderboards. It does
(`statcast_pitcher_pitch_movement`, `statcast_batter_run_value`,
`statcast_pitcher_run_value`). Catcher throwing is noted as overlapping
with `statcast_catcher_poptime` for pop time.

### Live tests

`tests/live/` makes real requests to Savant and is skipped unless
`SAVANT_LIVE=1`. It checks, for every function, that changing the season
or filter argument changes the answer. The `Live Savant` workflow runs it on pull requests and
on demand.

## 0.5.0

### Park factors moved from FanGraphs to Baseball Savant

`park_factors()` and `park_factors_range()` now read Baseball Savant's
Statcast Park Factors leaderboard. Through 0.4.4 they scraped FanGraphs
Guts! — in a package whose every other function reads Savant.

**Breaking, and quiet if you do not read this:** several columns kept their
names and changed their meaning. `pf_hr`, `pf_1b`, `pf_2b`, `pf_3b`,
`pf_so`, `pf_bb` and the runs factor now come from Savant's index, and the
two scales disagree — COL 2024 is `pf_hr` 109 on the new scale and 131 on
the old one. Pin `savant-extras<0.5` or call the FanGraphs functions below
if you need the old numbers.

- Removed: `pf_5yr` (Savant publishes 1-year and 3-year windows, not 5) and
  `pf_fip`. Both raise `KeyError` now instead of returning a substitute.
- Renamed: the runs factor is `pf_1yr` (single season) and `pf_3yr` (3-year
  window ending at `season`).
- Added: `venue_id`, `venue_name`, `n_pa_1yr`, `n_pa_3yr`, `pf_3yr_years`,
  and the wOBA-family indices `pf_obp`, `pf_hits`, `pf_woba`, `pf_wobacon`,
  `pf_xwobacon`, `pf_bacon`, `pf_xbacon`, `pf_hardhit`, `pf_wobatto`.
- All 30 clubs now appear in every season. The frame is built from the
  single-season view; the 3-year view is joined on `venue_id` and leaves
  NaN where a park has no three-year history (8 rows of 360 for 2015-2026).
  `pf_xwobacon`, `pf_xbacon` and `pf_hardhit` are additionally NaN for all
  of 2015 and 2016, whose windows predate Statcast.
- Every factor column is float64 in every season, so `astype(int)` no longer
  works on one season and raises on another.
- Fails loudly where it used to go quiet: a page serving a different season,
  a renamed Savant key, a row with no `venue_id`, and an empty table each
  raise `ValueError`. A partial failure in `park_factors_range()` now warns
  with the seasons it skipped instead of only printing.

### Added: `park_factors_fangraphs()` / `park_factors_fangraphs_range()`

The FanGraphs table, kept, because it is the only source here for `pf_5yr`
and `pf_fip`.

It also gets the fix that 0.4.4 needed: **it no longer claims to be a
browser.** Measured 2026-09-23 from a residential line, `fangraphs.com`
answers a `Chrome/140` or `Chrome/120` User-Agent with 403 and
`cf-mitigated: challenge`, and answers `curl`, no User-Agent, or this
package's own UA with 200 and the real page. 0.4.4 sent a Chrome UA and was
challenged every time, which is why it returned an empty frame for every
season.

That fixes the User-Agent half only. Datacenter addresses are blocked
separately: on a GitHub runner (2026-09-21), pybaseball — which sets no
User-Agent, so it sends the honest default — still got 403 for all 12
seasons. Expect these two functions to work from a home connection and not
from a cloud runner.

### Also

- `park_factors` and `park_factors_fangraphs` identify themselves in the
  `User-Agent` header rather than impersonating Chrome.
- Fixed a duplicated line in the package docstring.
