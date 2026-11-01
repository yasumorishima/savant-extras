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
SAVANT_LIVE=1 pytest tests/live -v    # real requests to baseballsavant.mlb.com (unverified from cloud so far)
```
CI: `.github/workflows/test.yml` (push/PR to `master`, Python 3.9–3.14), `.github/workflows/live.yml` (PR to `master` + Mondays 03:17 UTC, Python 3.12, `SAVANT_LIVE=1`).

## Release
- Bump version in both files + CHANGELOG via PR (precedent: PR #6 "chore: release 0.6.1"), merge.
- Publishing: `.github/workflows/publish.yml` runs on **`release: published`** (not on tag push) and uploads to PyPI by OIDC trusted publishing — no token. From the owner's machine: `gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."`.
- **From cloud (unverified):** publish a GitHub release for tag `vX.Y.Z` on `master` with a GitHub MCP tool if one exists for creating releases. Pushing a tag alone does nothing. If no MCP tool can create a release, stop after the merge and ask the owner to run the `gh release create` line above.
- Verify: the `Publish to PyPI` run is success and `https://pypi.org/pypi/savant-extras/json` reports the new `info.version`; then `pip install -U savant-extras` in a fresh venv and import it.

## Data access
`baseballsavant.mlb.com` (all functions except the two `*_fangraphs`), `www.fangraphs.com` (`park_factors_fangraphs*`, expect 403 from datacenter IPs), `pypi.org` (release check). Keyless. No data is committed to this repo.

## Dependabot / security
No `.github/dependabot.yml`. Vulnerability alerts and automated security fixes are enabled; 0 open Dependabot alerts and 0 open issues/PRs (checked 2026-11-01). Actions are pinned by SHA.
