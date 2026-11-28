# CLAUDE.md — savant-extras

Working rules for Claude Code (cloud or local). This file is the source of truth for this project; the owner's local notes are not visible to cloud sessions.

## Session protocol (cloud)
This project is worked on in Claude Code cloud. The owner starts a session with just 「続き」/「つづきから」.
1. Start the session in the environment 「クラウド許可1」 (full network access). Read this file, run **Setup**, then continue from the first unfinished item in **Next tasks**.
2. Before ending, record what you did and what comes next **in this file** (update "Next tasks" and add a dated line to "Progress log"). This file is the only memory that survives between cloud sessions.
3. Cloud can push only its session branch: open a PR to `master` and merge it yourself (own repo). Report the merged commit. Wait for the PR's `Tests` and `Live Savant` checks before merging.
4. There is no `gh` CLI in cloud; use the GitHub MCP tools. `workflow_dispatch` returns 403 from cloud, so anything on GitHub Actions must be triggered by a push / PR (both `Tests` and `Live Savant` already run on every PR).
5. Write replies to the owner in Japanese (です/ます). Do not claim anything you did not run in this session; say where every number was measured (cloud / GitHub Actions run id / earlier owner measurement).
6. The owner's PC and Raspberry Pi are not reachable from cloud. Nothing for this repo lives there.

## Progress log
- 2026-09-07: 0.4.4 — `__version__` had drifted from `pyproject.toml` (0.4.2 vs 0.4.3); `tests/test_version.py` now compares the two files (PR #1, #2).
- 2026-09-23: 0.5.0 — `park_factors()` reads Baseball Savant instead of FanGraphs; FanGraphs kept as `park_factors_fangraphs()` with an honest User-Agent (PR #3).
- 2026-09-27 (JST): 0.6.0 — twelve functions were sending parameters Savant no longer reads and silently got the current season; fixed, season checks added, `abs_challenges()` and `statcast_minors()` added, live tests added (PR #4).
- 2026-10-08: 0.6.1 — CI matrix 3.9–3.14 (tests had failed on 3.9/3.10 because of patch targets), weekly live run, PyPI summary/classifiers (PR #5, #6). Publish run `37796771467` success; PyPI shows 0.6.1.
- 2026-10-12 / 10-19 / 10-26: scheduled `Live Savant` runs on `master` all success.
- 2026-11-01: this file written for cloud work (no code change).
- 2026-11-01 (cloud): `SAVANT_LIVE=1 python -m pytest tests/live -q` 26 passed, 0 failed (113 s); unit tests 296 passed, 26 skipped. Savant / Stats API reachable (section below).
- 2026-11-28 (cloud): measured network vs parse for every public function before deciding on Rust (owner asked, reference: anthropic.com/research/migrating-api-to-rust). **Decision: no Rust.** Parse is ≤0.5% of a call on a cold Savant cache and ≤12% of network on a warm one; even `statcast_minors` 7 days parses in 0.27–0.29 s against 2.2–57 s network + 6 s polite sleep. Table and method in "Rust decision" below; script `benchmarks/measure_split.py` (not run in CI). No library code changed.

## Rust decision (measured 2026-11-28, cloud, Python 3.13, `python benchmarks/measure_split.py --minors-days 7`)
Network = wall time inside `requests.get` (connect + whole body). Sleep = the library's own `time.sleep` between requests. Parse = total − network − sleep (decode, CSV/JSON → DataFrame, `check_season`, rename, concat, MLB-game check). Two runs back to back: run 1 hit a cold Savant cache, run 2 a warm one (same URLs).

| Function (2025 unless noted) | req | network s run1 / run2 | parse s run1 / run2 | rows |
|---|---|---|---|---|
| abs_challenges(2026) | 1 | 0.73 / 0.51 | 0.030 / 0.049 | 526 |
| arm_strength | 1 | 0.52 / 0.36 | 0.004 / 0.003 | 351 |
| baserunning | 1 | 0.96 / 0.35 | 0.005 / 0.004 | 253 |
| basestealing | 1 | 1.07 / 0.38 | 0.005 / 0.004 | 423 |
| bat_tracking (03-27..09-28) | 1 | 1.66 / 0.29 | 0.002 / 0.004 | 226 |
| bat_tracking_monthly | 7 | 10.53 / 2.57 (+6.0 sleep) | 0.026 / 0.033 | 2850 |
| bat_tracking_splits | 2 | 2.52 / 0.63 (+1.0 sleep) | 0.005 / 0.007 | 452 |
| batted_ball | 1 | 1.13 / 0.39 | 0.003 / 0.003 | 316 |
| catcher_blocking | 1 | 1.31 / 0.35 | 0.002 / 0.002 | 65 |
| catcher_stance | 1 | 2.57 / 0.36 | 0.005 / 0.005 | 57 |
| catcher_throwing | 1 | 1.18 / 0.36 | 0.002 / 0.002 | 63 |
| home_runs | 1 | 1.41 / 0.38 | 0.003 / 0.003 | 579 |
| pitch_movement | 1 | 0.63 / 0.37 | 0.004 / 0.004 | 438 |
| pitch_tempo | 1 | 1.60 / 0.38 | 0.004 / 0.003 | 361 |
| pitcher_arm_angle | 1 | 13.81 / 0.35 | 0.002 / 0.002 | 287 |
| running_game | 1 | 2.36 / 0.37 | 0.004 / 0.006 | 504 |
| swing_take | 1 | 0.72 / 0.37 | 0.003 / 0.003 | 300 |
| timer_infractions | 1 | 1.06 / 0.37 | 0.002 / 0.003 | 30 |
| park_factors | 2 | 1.02 / 0.74 | 0.008 / 0.010 | 30 |
| park_factors_fangraphs | 1 | 0.42 / 0.38 | — | 403 (expected, datacenter IP) |
| year_to_year | 1 | 0.45 / 0.12 | 0.003 / 0.002 | 177 |
| statcast_minors (2025-06-10) | 1 | 11.08 / 0.42 | 0.065 / 0.073 | 4,629 (2.9 MB) |
| statcast_minors (06-10..06-16) | 7 | 56.79 / 2.24 (+6.0 sleep) | 0.274 / 0.285 | 27,305 (17.5 MB) |

Inside statcast_minors' parse (one day, 2.9 MB, 119 cols, median of 10, offline): decode 2 ms, `pd.read_csv` (C engine) 33–40 ms, concat of 7 days 4 ms, MLB-game check 1.5 ms. Extrapolated full season (180 copies of one day, 824k rows): concat 0.27 s, MLB check 0.03 s, read_csv ≈ 6–7 s total — against ≈180 s of polite sleep alone plus network.
- **Why no Rust:** the CPU part is already pandas' C CSV parser; the Python-level code around it is milliseconds. Removing parse entirely (Rust's upper bound) saves ≤0.29 s of an 8.5–63 s `statcast_minors` week. Not worth a native build matrix (manylinux/macOS/Windows × 3.9–3.14) for a library whose users install a pure wheel.
- **"Python のまま縮める" check:** `engine="pyarrow"` reads the same day in 14 ms vs 40 ms, but the DataFrame is **not identical** (first difference: column `game_date` dtype — pyarrow parses it as a date, the C engine leaves a string). Would change output; not adopted.
- **If speed matters later, the levers are network-side:** (a) an opt-in on-disk cache of past-season `statcast_minors` days (a finished day never changes; repeat runs went 57 s → 2 s even from Savant's own cache), (b) `*_range`/monthly sleep tuning only with care — the sleeps are there to be polite to Savant; parallel fetching is not recommended for the same reason.
- GHA reference given by owner (not re-measured this session): Tests ≤2 min, Live Savant ≤2 min over the last 30 successful runs.

## Cloud reachability (measured 2026-11-01, cloud session)
| Check | Result | Proof |
|---|---|---|
| `curl --max-time 60 "https://baseballsavant.mlb.com/leaderboard/sprint_speed?year=2025&position=&team=&min=10&csv=true"` | 200, 0.18 s, 36,204 B | 579 CSV lines |
| `curl --max-time 60 "https://statsapi.mlb.com/api/v1/teams?sportId=1"` | 200, 0.20 s | 30 teams |
| `pip install -e ".[dev]"`; `SAVANT_LIVE=1 python -m pytest tests/live -q` (Python 3.13) | **26 passed, 0 failed** in 112.6 s | no FanGraphs test exists in `tests/live`, so the expected FanGraphs 403 was not exercised |
| `python -m pytest tests -q` | 296 passed, 26 skipped | live tests skipped without `SAVANT_LIVE` |

## What this is
Public PyPI library (`pip install savant-extras`, MIT) that wraps Baseball Savant leaderboards pybaseball lacks or gets wrong, each as one function returning a `pandas.DataFrame`, most with a `*_range()` multi-season variant. Package code in `savant_extras/` (one module per leaderboard, shared parsing/season check in `savant_extras/_http.py`), unit tests in `tests/` (every request mocked), live tests in `tests/live/`. User-facing docs: `README.md`; every release is described in `CHANGELOG.md`. Downstream users include the owner's `mlb-data-pipeline` (weekly HF refresh) and Kaggle datasets built from it, so a silent wrong answer here propagates.

## Non-negotiable discipline
1. **Savant ignores parameters it does not recognise and answers HTTP 200 with the current season's table.** This is how twelve functions returned wrong data through 0.5.0. Every function whose table has a season column must pass through `check_season()` (raises `ValueError` on mismatch); a function with no season column (`arm_strength`, `pitch_tempo`, `pitcher_arm_angle`) is guarded only by the live tests. Any new parameter or new function gets a live test proving that changing the argument changes the answer (`tests/live/test_live_filters.py` pattern).
2. **Empty answers warn, never pass silently**: parse through `parse_savant_csv()` so HTML / header-only CSV emits `EmptySavantResponse`.
3. **Minors**: Savant Statcast search needs `minors=true&hfLevel=AAA|` (sent as `hfLevel=AAA%7C`); without `minors=true`, `hfLevel` is ignored and MLB data comes back. `statcast_minors()` also raises if a returned game is MLB vs MLB — keep that.
4. **Do not impersonate a browser.** Send no browser User-Agent (FanGraphs challenges exactly that). The FanGraphs functions are expected to get 403 from datacenter addresses (GitHub runners, and presumably cloud); do not work around it, and do not count that 403 as a library bug.
5. **Unit tests must not hit the network** (patch `requests.get`, `time.sleep`, `pandas.read_html` directly — older patch targets broke 3.9/3.10). Live checks go in `tests/live/` behind `SAVANT_LIVE=1`.
6. **Version lives in two files** (`pyproject.toml` `version =` and `savant_extras/__init__.py` `__version__`); `tests/test_version.py` compares them. Bump both plus a `CHANGELOG.md` section in one PR. Breaking changes are called out in CHANGELOG and README "Known Issues" (users re-fetch data based on it).
7. CI must stay green on every Python `requires-python` allows (3.9–3.14). No paid services.

## Next tasks (in order)
1. **Dead manual workflows.** `.github/workflows/pitcher-quality-integration.yml` imports `pitcher_quality`, removed in 0.4.2; `.github/workflows/park-factors-integration.yml` asserts FanGraphs `pf_5yr` from `park_factors()`, which reads Savant and dropped `pf_5yr` in 0.5.0. Both would fail if dispatched (and cloud cannot dispatch them). Move any still-meaningful check (Savant park factors: 30 clubs per season, COL high) into `tests/live/` and delete both files. Also `.devcontainer/devcontainer.json` is a Streamlit template pointing at a nonexistent `streamlit_app.py` — fix or remove.
2. **`year_to_year` has no season guard** (no `check_season` call). The owner measured on 2026-09-27 that it returned an empty table for 2026, so the guard never fires for the current season. Re-measure live, then add a guard that fits its columns plus a live test.
3. **`swing_take` has no qualifier argument.** Owner's note (2026-09-27, not in the repo): Savant's default is a cap of the top ~300 players by pitches, not a threshold. Find the real parameter live (prove it changes the row count), add it with a live test, release.
4. `LEADERBOARD_RESEARCH.md` (Japanese, last updated 2026-02-23 for v0.3.0) describes old parameters; rewrite against current code or mark it historical.
5. After 1–3: patch/minor release (see "Release").

## Setup (every cloud session)
```bash
pip install -e ".[dev]"
pytest tests/ -q                      # unit tests; tests/live is collected but skipped
SAVANT_LIVE=1 pytest tests/live -v    # real requests to baseballsavant.mlb.com (works from cloud: 26 passed, 2026-11-01)
```
CI: `.github/workflows/test.yml` (push/PR to `master`, Python 3.9–3.14), `.github/workflows/live.yml` (PR to `master` + Mondays 03:17 UTC, Python 3.12, `SAVANT_LIVE=1`).

## Release
- Bump version in both files + CHANGELOG via PR (precedent: PR #6 "chore: release 0.6.1"), merge.
- Publishing: `.github/workflows/publish.yml` runs on **`release: published`** (not on tag push) and uploads to PyPI by OIDC trusted publishing — no token. From the owner's machine: `gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."`.
- **From cloud (unverified; the GitHub MCP tools of the 2026-11-01 session had no create-release tool, only list/get):** publish a GitHub release for tag `vX.Y.Z` on `master` with a GitHub MCP tool if one exists for creating releases. Pushing a tag alone does nothing. If no MCP tool can create a release, stop after the merge and ask the owner to run the `gh release create` line above.
- Verify: the `Publish to PyPI` run is success and `https://pypi.org/pypi/savant-extras/json` reports the new `info.version`; then `pip install -U savant-extras` in a fresh venv and import it.

## Data access
`baseballsavant.mlb.com` (all functions except the two `*_fangraphs`), `www.fangraphs.com` (`park_factors_fangraphs*`, expect 403 from datacenter IPs), `pypi.org` (release check). Keyless. No data is committed to this repo.

## Dependabot / security
No `.github/dependabot.yml`. Vulnerability alerts and automated security fixes are enabled; 0 open Dependabot alerts and 0 open issues/PRs (checked 2026-11-01). Actions are pinned by SHA.
