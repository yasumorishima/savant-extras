# savant-extras 次回セッション作業メモ

最終更新: 2026-02-23

---

## 現在の状態

- **v0.3.1 PyPI公開済み** ✅（Known Issues追加のみ、コード変更なし）
- **Kaggle Notebook public化済み** ✅
  - URL: https://www.kaggle.com/code/yasunorim/savant-extras-all-baseball-savant-leaderboards
  - v5: 2024+2025両年取得、グラフはYEAR=2025表示、swing_takeスキップ
- **Kaggle Dataset 作成済み（private）**
  - URL: https://www.kaggle.com/datasets/yasunorim/baseball-savant-leaderboards-2024
  - 15 CSV（`*_2024_2025.csv`）、`year`カラム付き

---

## やること（優先順）

### 1. Dataset カラム説明記入（Kaggle上で手動）

Kaggle Dataset の各ファイルに Column Descriptors を入力する。
WBC Datasetと同じ要領（Settings → Column Descriptions）。

**15ファイル一覧と主なカラム**:

| ファイル | 主なカラム |
|---|---|
| `bat_tracking_2024_2025.csv` | name, avg_bat_speed, attack_angle, swing_tilt, year |
| `batted_ball_2024_2025.csv` | player_name, gb_rate, fb_rate, ld_rate, pull_rate, year |
| `home_runs_2024_2025.csv` | player, hr_total, xhr, avg_dist, no_doubters, year |
| `year_to_year_2024_2025.csv` | player_name, 2024, 2025, delta_2024_2025, query_year |
| `pitch_tempo_2024_2025.csv` | entity_name, median_seconds_empty, median_seconds_on_base, year |
| `pitch_movement_2024_2025.csv` | pitcher_name, pitch_type, pitcher_break_x, pitcher_break_z, year |
| `pitcher_arm_angle_2024_2025.csv` | pitcher_name, ball_angle, year |
| `running_game_2024_2025.csv` | player_name, runs_prevented_on_running_attr, year |
| `timer_infractions_2024_2025.csv` | entity_name, all_violations, pitcher_timer, batter_timer, year |
| `arm_strength_2024_2025.csv` | fielder_name, primary_position, max_arm_strength, arm_overall, year |
| `catcher_blocking_2024_2025.csv` | player_name, blocks_above_average, year |
| `catcher_throwing_2024_2025.csv` | player_name, pop_time, caught_stealing_above_average, year |
| `catcher_stance_2024_2025.csv` | player_name, knee_down_pct, catching_rv, year |
| `baserunning_2024_2025.csv` | entity_name, runner_runs_tot, year |
| `basestealing_2024_2025.csv` | player_name, runs_stolen_on_running_act, year |

### 2. Dataset public化

カラム説明記入後、Kaggle上で Settings → Sharing → Public。

### 3. ブログ記事（全3媒体）

**タイトル案**:
- JA: `pybaseballが未対応のBaseball Savantリーダーボードを全部Python化した`
- EN: `I Built a Python Package for Every Baseball Savant Leaderboard`

**構成**:
1. savant-extrasとは（pybaseballとの違い）
2. v0.2.0: Pitch Tempo + Arm Strength
3. v0.3.0: 全13リーダーボード追加
4. 使い方例（コードスニペット）
5. グラフ例（Kaggle Notebookのスクショ）
6. CSV取得不可だったもの（swing_take等）と理由
7. リンク: PyPI / GitHub / Kaggle Notebook / Kaggle Dataset

**作成ファイル**:
- Zenn: `zenn-content/articles/savant-extras-all-leaderboards.md`
- Qiita: `qiita-content/public/savant-extras-all-leaderboards.md`
- DEV.to: `quarto-blog/devto/savant-extras-all-leaderboards.md`

**注意**:
- 方針11（断定表現避ける）、方針14（Kaggleスコア書かない）、方針18（リンク最大2つ）
- swing_take が空データな件はブログにも一言触れる

### 4. GitHub プロフィール README 更新

- savant-extras セクションを v0.3.1 に更新
- Kaggle Notebook / Dataset URL 追加

### 5. savant-extras README にリンク追加

- Kaggle Notebook URL
- Kaggle Dataset URL
- （方針18: 最大2リンクなのでNotebook + Dataset or PyPI + GitHubのどちらか）

---

## ⚠️ 注意点・ハマりポイント

- **swing_take**: Baseball Savant API壊れ → 全年度で空 → Notebook/Datasetから除外済み。ブログでも触れる
- **Kaggle API v2.0.0**: `.py`ファイル不可、`.ipynb`必須
- **coerce_numeric()**: Baseball Savant CSV の object型カラムを数値変換するヘルパー（Notebookに実装済み）
- **pitch_movement / timer_infractions**: APIに既に`year`カラムあり → `if "year" not in df.columns`で重複防止
- **year_to_year**: カラム名が年度で動的（`2024`, `delta_2024_2025`）→ `query_year`カラムで区別

---

## ローカルパス

- Notebook: `C:\Users\fw_ya\Desktop\Claude_code\kaggle-datasets\savant-extras-showcase\`
- Dataset: `C:\Users\fw_ya\Desktop\Claude_code\kaggle-datasets\savant-extras-dataset\`
- savant-extras: `C:\Users\fw_ya\Desktop\Claude_code\savant-extras\`
