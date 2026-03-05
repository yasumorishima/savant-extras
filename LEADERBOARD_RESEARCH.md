# Baseball Savant Leaderboard CSV API 調査結果

最終更新: 2026-02-23（v0.3.0公開後）

---

## 実装済み（v0.3.0 — 16リーダーボード、33関数）

### 打撃系
| リーダーボード | モジュール | 関数 | データ開始 |
|---|---|---|---|
| Bat Tracking | `bat_tracking` | `bat_tracking` / `bat_tracking_monthly` / `bat_tracking_splits` | 2024+（Hawk-Eye） |
| Batted Ball Profile | `batted_ball` | `batted_ball` / `batted_ball_range` | — |
| Home Runs | `home_runs` | `home_runs` / `home_runs_range` | — |
| Swing & Take Run Value | `swing_take` | `swing_take` / `swing_take_range` | — |
| Year to Year Changes | `year_to_year` | `year_to_year` | — |

### 投球系
| リーダーボード | モジュール | 関数 | データ開始 |
|---|---|---|---|
| Pitch Tempo | `pitch_tempo` | `pitch_tempo` / `pitch_tempo_range` | 2010+ |
| Pitch Movement | `pitch_movement` | `pitch_movement` / `pitch_movement_range` | — |
| Pitcher Arm Angle | `pitcher_arm_angle` | `pitcher_arm_angle` / `pitcher_arm_angle_range` | — |
| Running Game (Pitcher) | `running_game` | `running_game` / `running_game_range` | — |
| Timer Infractions | `timer_infractions` | `timer_infractions` / `timer_infractions_range` | 2023+ |

### 捕手系
| リーダーボード | モジュール | 関数 | データ開始 |
|---|---|---|---|
| Catcher Blocking | `catcher_blocking` | `catcher_blocking` / `catcher_blocking_range` | — |
| Catcher Throwing | `catcher_throwing` | `catcher_throwing` / `catcher_throwing_range` | — |
| Catcher Stance | `catcher_stance` | `catcher_stance` / `catcher_stance_range` | — |

### 走塁・守備系
| リーダーボード | モジュール | 関数 | データ開始 |
|---|---|---|---|
| Arm Strength | `arm_strength` | `arm_strength` / `arm_strength_range` | 2020+ |
| Baserunning Run Value | `baserunning` | `baserunning` / `baserunning_range` | — |
| Basestealing Run Value | `basestealing` | `basestealing` / `basestealing_range` | — |

---

## CSV取得不可（HTMLのみ返却）— 未実装

| リーダーボード | URLパス | 不可の理由 |
|---|---|---|
| Rolling Windows | `/leaderboard/rolling` | 200返すがHTML（CSVパラメータ無効） |
| Statcast Park Factors | `/leaderboard/statcast-park-factors` | JSON埋め込み型ページ |
| Hot Stove | `/leaderboard/hot-stove` | HTML返却 |
| Enhanced Game Scores | `/leaderboard/weighted-score` | HTML返却 |
| Custom Leaderboard | `/leaderboard/custom` | CSV返るがカラム3列のみ（実用外） |

将来対応する場合はHTMLパース or JavaScript実行 or JSON抽出が必要。

---

## pybaseball対応済み（savant-extrasでは未実装）

| リーダーボード | pybaseball関数 |
|---|---|
| Expected Statistics | `statcast_batter_expected_stats()` / `statcast_pitcher_expected_stats()` |
| Percentile Rankings | `statcast_batter_percentile_ranks()` / `statcast_pitcher_percentile_ranks()` |
| Sprint Speed | `statcast_sprint_speed()` |
| Catcher Framing | `statcast_catcher_framing()` — ただし高度フィルタ未対応 |

---

## 共通仕様メモ

- 全リーダーボードは `&csv=true` パラメータでCSVデータを返す（認証不要）
- **dateStart/dateEnd（日付範囲指定）はBat Trackingのみ**。他は全てシーズン単位
- パラメータ名はリーダーボード間で不統一（year / season_start / seasonStart）
- BOM付きUTF-8（`\ufeff`）の場合あり → `pd.read_csv` は自動処理
- レート制限あり: 全 `_range` 関数で1秒sleepを入れている

## 個別パラメータ詳細

### Pitch Tempo
```
https://baseballsavant.mlb.com/leaderboard/pitch-tempo?type=Pit&season_start=2024&season_end=2024&n=q&game_type=Regular&team=&split=no&with_team_only=1&csv=true
```
- type: Pit / Bat（savant-extrasでは pitcher→Pit, batter→Bat に変換）
- n: q / 1 / 10 / 50 / 100 / 250 / 500 / 1000 / 2000 / 5000

### Arm Strength
```
https://baseballsavant.mlb.com/leaderboard/arm-strength?type=player&year=2024&pos=&team=&minThrows=100&csv=true
```
- pos: 空 / 2B/SS/3B / Outfielder / 1B / 2B / 3B / SS / LF / CF / RF

### Batted Ball
```
https://baseballsavant.mlb.com/leaderboard/batted-ball?year=2024&type=batter&min=q&csv=true
```

### Home Runs
```
https://baseballsavant.mlb.com/leaderboard/home-runs?year=2024&type=exit_velocity&min=0&csv=true
```
- type: exit_velocity / adj_xhr / distance

### Pitch Movement
```
https://baseballsavant.mlb.com/leaderboard/pitch-movement?year=2024&team=&pitchType=&csv=true
```
- pitchType: FF / SL / CU / CH / SI / FC / ST / SV / KN 等

### Swing & Take
```
https://baseballsavant.mlb.com/leaderboard/swing-take?year=2024&type=batter&csv=true
```

### Year to Year
```
https://baseballsavant.mlb.com/leaderboard/statcast-year-to-year?year=2024&type=batter&csv=true
```
- カラム名が年度で動的（`2023`, `delta_2023_2024` 等）

### Pitcher Arm Angle
```
https://baseballsavant.mlb.com/leaderboard/pitcher-arm-angles?year=2024&team=&csv=true
```

### Running Game
```
https://baseballsavant.mlb.com/leaderboard/pitcher-running-game?year=2024&min=q&csv=true
```

### Catcher Blocking
```
https://baseballsavant.mlb.com/leaderboard/catcher-blocking?year=2024&min=q&csv=true
```

### Catcher Throwing
```
https://baseballsavant.mlb.com/leaderboard/catcher-throwing?year=2024&min=q&csv=true
```

### Catcher Stance
```
https://baseballsavant.mlb.com/leaderboard/catcher-stance?year=2024&min=q&csv=true
```

### Baserunning Run Value
```
https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?year=2024&min=q&csv=true
```

### Basestealing Run Value
```
https://baseballsavant.mlb.com/leaderboard/basestealing-run-value?year=2024&min=q&csv=true
```

### Timer Infractions
```
https://baseballsavant.mlb.com/leaderboard/pitch-timer-infractions?year=2024&csv=true
```
