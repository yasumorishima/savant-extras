"""Split one call of each public function into network time and parse time.

Real requests to Baseball Savant (run by hand, never in CI):

    python benchmarks/measure_split.py [--minors-days N] [--json out.json]

``requests.get`` is wrapped: its wall time (connect + full body download,
since nothing here streams) counts as network. ``time.sleep`` calls made by
the library are slept for real (politeness) but counted separately.
parse = total - network - sleep: everything after the bytes arrive
(decode, CSV/JSON -> DataFrame, season check, renaming, concat).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
import warnings

import requests

import savant_extras as se

_real_get = requests.get
_real_sleep = time.sleep
_acc = {"net": 0.0, "net_cpu": 0.0, "sleep": 0.0, "bytes": 0, "requests": 0}


def _timed_get(*a, **kw):
    t0, c0 = time.perf_counter(), time.process_time()
    try:
        r = _real_get(*a, **kw)
        _acc["bytes"] += len(r.content)
        return r
    finally:
        _acc["net"] += time.perf_counter() - t0
        _acc["net_cpu"] += time.process_time() - c0
        _acc["requests"] += 1


def _timed_sleep(s):
    t0 = time.perf_counter()
    _real_sleep(s)
    _acc["sleep"] += time.perf_counter() - t0


requests.get = _timed_get
time.sleep = _timed_sleep


def measure(name, fn, *a, **kw):
    for k in _acc:
        _acc[k] = 0 if k in ("bytes", "requests") else 0.0
    t0, c0 = time.perf_counter(), time.process_time()
    err = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            out = fn(*a, **kw)
        except Exception as e:  # keep going; record the failure
            out, err = None, f"{type(e).__name__}: {e}"[:120]
    total = time.perf_counter() - t0
    cpu = time.process_time() - c0
    if isinstance(out, dict):
        rows = sum(len(v) for v in out.values())
    else:
        rows = None if out is None else len(out)
    rec = {
        "function": name,
        "requests": _acc["requests"],
        "bytes": _acc["bytes"],
        "total_s": round(total, 3),
        "network_s": round(_acc["net"], 3),
        "sleep_s": round(_acc["sleep"], 3),
        "parse_s": round(total - _acc["net"] - _acc["sleep"], 3),
        "parse_cpu_s": round(cpu - _acc["net_cpu"], 3),
        "rows": rows,
        "error": err,
    }
    print(json.dumps(rec), flush=True)
    _real_sleep(1.0)  # be polite between functions
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minors-days", type=int, default=7)
    ap.add_argument("--json")
    args = ap.parse_args()
    y = 2025
    start = dt.date(2025, 6, 10)
    end = start + dt.timedelta(days=args.minors_days - 1)
    calls = [
        ("abs_challenges(2026)", se.abs_challenges, 2026),
        ("arm_strength(2025)", se.arm_strength, y),
        ("baserunning(2025)", se.baserunning, y),
        ("basestealing(2025)", se.basestealing, y),
        ("bat_tracking(2025 season)", se.bat_tracking, "2025-03-27", "2025-09-28"),
        ("bat_tracking_monthly(2025)", se.bat_tracking_monthly, y),
        ("bat_tracking_splits(2025)", se.bat_tracking_splits, y),
        ("batted_ball(2025)", se.batted_ball, y),
        ("catcher_blocking(2025)", se.catcher_blocking, y),
        ("catcher_stance(2025)", se.catcher_stance, y),
        ("catcher_throwing(2025)", se.catcher_throwing, y),
        ("home_runs(2025)", se.home_runs, y),
        ("pitch_movement(2025)", se.pitch_movement, y),
        ("pitch_tempo(2025)", se.pitch_tempo, y),
        ("pitcher_arm_angle(2025)", se.pitcher_arm_angle, y),
        ("running_game(2025)", se.running_game, y),
        ("swing_take(2025)", se.swing_take, y),
        ("timer_infractions(2025)", se.timer_infractions, y),
        ("park_factors(2025)", se.park_factors, y),
        ("park_factors_fangraphs(2025)", se.park_factors_fangraphs, y),
        ("year_to_year(2025)", se.year_to_year, y),
        ("statcast_minors(1 day)", se.statcast_minors, "2025-06-10", "2025-06-10"),
        (f"statcast_minors({args.minors_days} days)", se.statcast_minors,
         start.isoformat(), end.isoformat()),
    ]
    recs = [measure(n, f, *a) for n, f, *a in calls]
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(recs, fh, indent=1)


if __name__ == "__main__":
    main()
