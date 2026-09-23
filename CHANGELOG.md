# Changelog

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
