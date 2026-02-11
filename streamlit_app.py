"""
MLB Bat Tracking Dashboard — powered by savant-extras
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import matplotlib_fontja  # noqa: F401  — enables Japanese fonts in matplotlib (Python 3.12+ compatible)
from pybaseball import batting_stats, pitching_stats

from savant_extras import bat_tracking, bat_tracking_monthly, bat_tracking_splits
from wbc_rosters import WBC_ROSTERS
from mlb_lineups_2025 import MLB_LINEUPS_2025

st.set_page_config(
    page_title="MLB Bat Tracking Dashboard",
    page_icon="⚾",
    layout="wide",
)

BLUE = "#1f4e79"
RED = "#c0392b"
AVG_COLOR = "#e67e22"   # orange — league average line
PALETTE = plt.cm.tab20.colors

BATTING_METRICS = {
    "avg_bat_speed": "Bat Speed (mph)",
    "attack_angle": "Attack Angle (°)",
    "ideal_attack_angle_rate": "Ideal AA%",
    "swing_tilt": "Swing Tilt (°)",
}
PITCHING_METRICS = {
    "ERA": "ERA (lower=better)",
    "FIP": "FIP (lower=better)",
    "K/9": "K/9",
    "BB/9": "BB/9 (lower=better)",
}

MLB_TEAM_NAMES = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KCR": "Kansas City Royals",
    "LAA": "LA Angels",
    "LAD": "LA Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SDP": "San Diego Padres",
    "SFG": "San Francisco Giants",
    "SEA": "Seattle Mariners",
    "STL": "St. Louis Cardinals",
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSN": "Washington Nationals",
}


def team_label(abbr: str) -> str:
    """Return 'ABB — Full Name' or just abbr if not found."""
    full = MLB_TEAM_NAMES.get(abbr)
    return f"{abbr} — {full}" if full else abbr


# ── Translations ──────────────────────────────────────────────────────────────
T = {
    "en": {
        "sidebar_title": "⚾ Bat Tracking",
        "season": "Season",
        "player_type": "Player type",
        "handedness": "Handedness",
        "hand_all": "All",
        "wbc_label": "🌍 WBC 2026 Country",
        "wbc_all": "All players",
        "team_label": "🏟️ MLB Team",
        "team_all": "All teams",
        "load_btn": "Load Data",
        "reset_btn": "🔄 Reset All",
        "data_caption": "Data: Baseball Savant · Hawk-Eye (2024–)",
        "fetching": "Fetching bat tracking data...",
        "loaded": "{n} players loaded!",
        "filter_label": "Filters:",
        "players": "players",
        "load_first": "← Load data from the sidebar to get started.",
        "welcome_title": "### What can you do here?",
        "card_tab1_title": "🏆 Leaderboard",
        "card_tab1_desc": "Ranking chart for Bat Speed, Attack Angle, and more",
        "card_tab2_title": "👤 Player Comparison",
        "card_tab2_desc": "Radar & bar chart comparing up to 6 players",
        "card_tab3_title": "🌍 WBC Country Strength",
        "card_tab3_desc": "Batting & pitching scores for all 20 WBC 2026 nations",
        "card_tab4_title": "⚾ Team Lineup Builder",
        "card_tab4_desc": "Build a 9-man lineup and see bat tracking metrics",
        "card_tab5_title": "📅 Monthly Trend",
        "card_tab5_desc": "Month-by-month bat speed trend for any player",
        "start_hint": "👈 Set **Season** and **Player type** in the sidebar, then click **Load Data**",
        "no_players": "No players match the current filters.",
        # Tab 1
        "metric": "Metric",
        "top_n": "Top N",
        "filtered": "Filtered",
        "league_avg": "League avg",
        "filter_avg": "Filter avg",
        # Tab 2
        "select_players": "Select players (up to 6)",
        "select_one": "Select at least one player.",
        "search_placeholder": "Type a name to search...",
        "radar_title": "Player Comparison (vs league)",
        "bar_subtitle": "gray dashed = league avg",
        # Tab 3
        "wbc_subheader": "🌍 WBC 2026 Country Strength Comparison",
        "wbc_caption": "Build each country's lineup from their MLB roster players, then compare batting & pitching strength scores.",
        "mode": "Mode",
        "auto_mode": "⚡ Auto (best available)",
        "manual_mode": "✏️ Manual lineup",
        "select_country": "Select country to build lineup",
        "choose_batters": "Choose up to 9 batters for {country}",
        "batters_selected": "{country}: {n} batters selected",
        "overall_ranking": "### Overall Strength Ranking",
        "batting_pitching": "### Batting vs Pitching Balance",
        "radar_top6": "### Top Countries Radar (Batting)",
        "full_table": "📋 Full Score Table",
        "bat_table": "📋 Batting Details by Country",
        "pitch_table": "📋 Pitching Details by Country",
        "col_pitchers": "# Pitchers",
        "col_batter_names": "Batters (bat tracking)",
        "col_era": "Avg ERA",
        "col_fip": "Avg FIP",
        "col_k9": "Avg K/9",
        "col_bb9": "Avg BB/9",
        "no_pitch_data": "No pitching data available.",
        "col_country": "Country",
        "col_batters": "# Batters",
        "col_bat_speed": "Avg Bat Speed",
        "col_bat_score": "Batting Score",
        "col_pit_score": "Pitching Score",
        "col_overall": "Overall Score",
        # Tab 4
        "lineup_subheader": "⚾ MLB Team Lineup Builder",
        "lineup_caption": "Place 9 players into position slots and compare bat tracking metrics. Position matching is not required — any player can fill any slot.",
        "view_mode": "View",
        "build_mode": "🔧 Build single team lineup",
        "compare_mode": "📊 Compare all teams (auto top-9)",
        "select_team": "Select team",
        "lineup_header": "{team} Lineup — {n} players with bat tracking data",
        "pos_caption": "Positions are reference only — place any player in any slot.",
        "no_bat_data": "No bat tracking data for this team.",
        "compare_caption": "Comparing top-9 batters (by wRC+) per team.",
        "cmp_metric": "Comparison metric",
        "vs_league": "{delta:+.2f} vs league",
        # Tab 5
        "monthly_caption": "Fetches month-by-month data (~30 sec). Select players after loading.",
        "load_monthly": "Load Monthly Data",
        "overlay_players": "Overlay players",
        "monthly_loaded": "Loaded: {n} rows.",
        # Glossary
        "glossary_title": "📖 Metric Guide",
        "term_bat_speed": "**Bat Speed (mph)** — Speed of the bat head at the moment of contact. Higher = more power potential.",
        "term_attack_angle": "**Attack Angle (°)** — Bat trajectory angle at impact. Positive = upward swing. ~10–30° is the optimal range for loft and hard contact.",
        "term_ideal_aa": "**Ideal AA%** — Percentage of swings with an attack angle between 10° and 30°. Higher = more consistently ideal swing plane.",
        "term_swing_tilt": "**Swing Tilt (°)** — Tilt of the overall swing plane. Higher value = more uppercut / rotational swing.",
        "term_wrc": "**wRC+** — Weighted Runs Created Plus. Offensive production adjusted for park and league. 100 = league average; 120 = 20% above average.",
        "term_era": "**ERA** — Earned Run Average. Earned runs allowed per 9 innings. Lower = better.",
        "term_fip": "**FIP** — Fielding Independent Pitching. ERA-like stat based only on strikeouts, walks, and home runs — removes defensive influence. Lower = better.",
        "term_k9": "**K/9** — Strikeouts per 9 innings pitched. Higher = better.",
        "term_bb9": "**BB/9** — Walks per 9 innings pitched. Lower = better (better control).",
        # Color legends
        "color_vs_avg": "🔴 Red = above league avg  ·  🔵 Blue = below league avg",
        "color_top3": "🔴 Red = Top 3  ·  🔵 Blue = Others",
        "color_top5": "🔴 Red = Top 5  ·  🔵 Blue = Others",
        "color_vs_lineup": "🔴 Red = above lineup avg  ·  🔵 Blue = below lineup avg",
        # Graph captions
        "cap_ideal_aa": "💡 Ideal AA%: % of swings with attack angle 10–30° (the optimal range for hard contact and loft)",
        "cap_radar_note": "💡 Radar chart is normalized across all players — outer = better. Bat Speed: swing power. Attack Angle: upward tilt at impact. Ideal AA%: % in optimal 10–30° range. Swing Tilt: overall swing plane angle.",
        "cap_bar_note": "💡 Orange dashed line = league average. Bat Speed (mph): higher = more power. Attack Angle (°): ~10–30° is optimal. Ideal AA%: higher = more consistent. Swing Tilt (°): higher = more uppercut swing.",
        "cap_wbc_overall": "💡 Overall Score = average of Batting Score + Pitching Score (0–100, MLB roster players only). Batting score always uses batter data regardless of the Player type setting. ⚠️ Countries with fewer MLB players have less reliable scores — treat as provisional.",
        "cap_wbc_scatter": "💡 Batting Score: Bat Speed + Ideal AA% + Attack Angle. Pitching Score: ERA + FIP + K/9 + BB/9 (all normalized to 0–100)",
        "cap_composite": "💡 Composite Batting Score: Bat Speed + Attack Angle + Ideal AA% combined and normalized to 0–100",
        # Tab names
        "tab1_name": "🏆 Leaderboard",
        "tab2_name": "👤 Player Comparison",
        "tab3_name": "🌍 WBC Country Strength",
        "tab4_name": "⚾ Team Lineup Builder",
        "tab5_name": "📅 Monthly Trend",
        # Graph text
        "graph_strength_score": "Strength Score (0–100)",
        "graph_wbc_overall_title": "WBC 2026 — Overall Strength Score ({year} MLB data)",
        "graph_batting_score": "Batting Score",
        "graph_pitching_score": "Pitching Score",
        "graph_batting_vs_pitching": "Batting vs Pitching Strength",
        "graph_top6_radar": "Top 6 Countries — Batting Radar",
        "graph_lineup_title": "{team} Lineup — Bat Tracking Metrics",
        "graph_avg_bat_speed": "Avg Bat Speed (mph)",
        "graph_attack_angle": "Attack Angle (°)",
        "graph_ideal_aa": "Ideal AA%",
        "graph_swing_tilt": "Swing Tilt (°)",
        "graph_all_teams_metric": "All Teams — Top-9 {metric} ({year})",
        "graph_composite_score": "Composite Batting Score (0–100)",
        "graph_all_teams_strength": "All Teams — Overall Batting Strength Score ({year})",
        "graph_team_overall": "All Teams — Overall Score (Batting + Pitching) ({year})",
        "graph_team_bp_scatter": "Batting vs Pitching Strength by Team",
        "team_bat_table": "📋 Batting Details by Team",
        "team_pitch_table": "📋 Pitching Details by Team",
        "filter_radar_countries": "Select countries for radar (max 8)",
        "filter_radar_teams": "Select teams for radar (max 8)",
        "radar_bat_title": "Batting Radar",
        "radar_pit_title": "Pitching Radar (ERA / FIP / K9 / BB9)",
        "graph_monthly_ylabel": "Avg Bat Speed (mph)",
        "graph_monthly_title": "Monthly Bat Speed — {year}",
        # Pitcher mode
        "pitcher_leaderboard_note": "💡 **Pitcher mode**: Showing ERA / FIP / K/9 / BB/9 for pitchers (min 20 IP — includes starters & relievers). Lower ERA/FIP/BB9 = better. MLB official qualifier = 162 IP (starters only).",
        "pitcher_compare_note": "💡 Radar is normalized so outer = always better (ERA/FIP/BB9 inverted: lower → outer).",
        "tab5_pitcher_note": "📅 Monthly trend uses **bat tracking data** (batter mode). Switch to **Batter** to see monthly bat speed trends.",
        "color_pitcher_lower": "🔴 Red = better than league avg (lower)  ·  🔵 Blue = worse than avg",
        "color_pitcher_higher": "🔴 Red = better than league avg (higher)  ·  🔵 Blue = worse than avg",
        "radar_title_pitcher": "Pitcher Comparison (vs league)",
        # App guide
        "guide_title": "ℹ️ About this app / How to use  ← click to collapse",
        "guide_content": """\
**MLB Bat Tracking Dashboard** visualizes swing metrics captured by Hawk-Eye sensors (2024–), \
powered by [savant-extras](https://github.com/yasumorishima/savant-extras).

**🚀 Getting started**
1. Choose **Season**, **Player type** (batter / pitcher), and optional filters in the sidebar
2. Click **Load Data** — data loads in ~5 seconds
3. Switch between tabs to explore

**📊 Tabs**
| Tab | Description |
|---|---|
| 🏆 Leaderboard | Top-N ranking bar chart for any batting metric |
| 👤 Player Comparison | Radar chart + bar chart comparing up to 6 players |
| 🌍 WBC Country Strength | Batting & pitching strength scores for all 20 WBC 2026 nations |
| ⚾ Team Lineup Builder | Build a 9-man lineup and compare bat tracking metrics |
| 📅 Monthly Trend | Month-by-month bat speed trend for selected players |
""",
    },
    "ja": {
        "sidebar_title": "⚾ バットトラッキング",
        "season": "シーズン",
        "player_type": "選手タイプ",
        "handedness": "打席",
        "hand_all": "全体",
        "wbc_label": "🌍 WBC 2026 国",
        "wbc_all": "全選手",
        "team_label": "🏟️ MLBチーム",
        "team_all": "全チーム",
        "load_btn": "データ読み込み",
        "reset_btn": "🔄 リセット",
        "data_caption": "データ: Baseball Savant · Hawk-Eye（2024年以降）",
        "fetching": "バットトラッキングデータを取得中...",
        "loaded": "{n}人の選手データを読み込みました！",
        "filter_label": "フィルタ:",
        "players": "選手",
        "load_first": "← サイドバーからデータを読み込んでください。",
        "welcome_title": "### このアプリでできること",
        "card_tab1_title": "🏆 リーダーボード",
        "card_tab1_desc": "バットスピード・アタックアングルなどのランキング表示",
        "card_tab2_title": "👤 選手比較",
        "card_tab2_desc": "最大6選手をレーダー＆棒グラフで比較",
        "card_tab3_title": "🌍 WBC国別戦力",
        "card_tab3_desc": "WBC 2026全20カ国の打撃・投球スコア比較",
        "card_tab4_title": "⚾ チームラインナップ",
        "card_tab4_desc": "9人のラインナップを組んでバット指標を確認",
        "card_tab5_title": "📅 月次トレンド",
        "card_tab5_desc": "選手ごとの月別バットスピード推移を表示",
        "start_hint": "👈 サイドバーで **シーズン** と **選手タイプ** を選んで **データ読み込み** をクリック",
        "no_players": "条件に一致する選手がいません。",
        # Tab 1
        "metric": "指標",
        "top_n": "上位 N 人",
        "filtered": "対象選手",
        "league_avg": "リーグ平均",
        "filter_avg": "フィルタ平均",
        # Tab 2
        "select_players": "選手を選択（最大6人）",
        "select_one": "選手を1人以上選んでください。",
        "search_placeholder": "名前を入力して検索...",
        "radar_title": "選手比較（リーグ全体で正規化）",
        "bar_subtitle": "灰色点線 = リーグ平均",
        # Tab 3
        "wbc_subheader": "🌍 WBC 2026 国別戦力比較",
        "wbc_caption": "各国のMLB所属選手データから打撃・投球スコアを算出して比較します。",
        "mode": "モード",
        "auto_mode": "⚡ 自動（上位選手）",
        "manual_mode": "✏️ 手動選択",
        "select_country": "ラインナップを組む国を選択",
        "choose_batters": "{country} の打者を最大9人選択",
        "batters_selected": "{country}: {n}人の打者を選択中",
        "overall_ranking": "### 総合ランキング",
        "batting_pitching": "### 打撃 vs 投球 バランス",
        "radar_top6": "### 上位国 レーダーチャート（打撃）",
        "full_table": "📋 スコア一覧",
        "bat_table": "📋 国別打球詳細",
        "pitch_table": "📋 国別投球詳細",
        "col_pitchers": "投手数",
        "col_batter_names": "打者（バットトラッキング）",
        "col_era": "平均ERA",
        "col_fip": "平均FIP",
        "col_k9": "平均K/9",
        "col_bb9": "平均BB/9",
        "no_pitch_data": "投球データがありません。",
        "col_country": "国",
        "col_batters": "打者数",
        "col_bat_speed": "平均バットスピード",
        "col_bat_score": "打撃スコア",
        "col_pit_score": "投球スコア",
        "col_overall": "総合スコア",
        # Tab 4
        "lineup_subheader": "⚾ MLBチーム ラインナップビルダー",
        "lineup_caption": "9つのポジションスロットに選手を配置してバット指標を比較。ポジション厳密マッチ不要 — 好きな選手を好きなスロットに。",
        "view_mode": "表示モード",
        "build_mode": "🔧 チームラインナップを組む",
        "compare_mode": "📊 全チーム比較（自動top-9）",
        "select_team": "チームを選択",
        "lineup_header": "{team} ラインナップ — バットトラッキングデータあり: {n}人",
        "pos_caption": "ポジションは参考枠。どのスロットにどの選手を置いてもOK。",
        "no_bat_data": "このチームのバットトラッキングデータがありません。",
        "compare_caption": "各チームのwRC+上位9打者の平均値で比較。",
        "cmp_metric": "比較指標",
        "vs_league": "vs リーグ平均 {delta:+.2f}",
        # Tab 5
        "monthly_caption": "月次データを取得します（約30秒）。読み込み後に選手を選択してください。",
        "load_monthly": "月次データを読み込む",
        "overlay_players": "選手を重ねて表示",
        "monthly_loaded": "{n}行のデータを読み込みました。",
        # Glossary
        "glossary_title": "📖 指標解説",
        "term_bat_speed": "**Bat Speed（バットスピード, mph）** — インパクト時のバットヘッドの速度。高いほどパワーポテンシャルが大きい。",
        "term_attack_angle": "**Attack Angle（アタックアングル, °）** — インパクト時のバット軌道の角度。正値 = 上向きスイング。10〜30°がフライボール打球に最適とされる。",
        "term_ideal_aa": "**Ideal AA%（理想アタックアングル率）** — アタックアングルが10〜30°（理想範囲）に入るスイングの割合。高いほど安定して好条件の打球を生みやすい。",
        "term_swing_tilt": "**Swing Tilt（スイング傾斜, °）** — スイング面の傾き角度。値が大きいほどアッパースイング・回転スイング傾向。",
        "term_wrc": "**wRC+（加重得点創出力）** — 球場・リーグ補正済みの打撃貢献指標。100 = リーグ平均。120 = 平均より20%優秀。",
        "term_era": "**ERA（防御率）** — 9イニングあたりの自責点。低いほど優秀。",
        "term_fip": "**FIP（守備無関係防御率）** — 三振・四球・本塁打のみで算出するERA類似指標。守備の影響を排除して投手の実力を測る。低いほど優秀。",
        "term_k9": "**K/9（奪三振率）** — 9イニングあたりの奪三振数。高いほど優秀。",
        "term_bb9": "**BB/9（与四球率）** — 9イニングあたりの与四球数。低いほど制球力が高い。",
        # Color legends
        "color_vs_avg": "🔴 赤 = リーグ平均以上  ·  🔵 青 = リーグ平均未満",
        "color_top3": "🔴 赤 = 上位3カ国  ·  🔵 青 = それ以外",
        "color_top5": "🔴 赤 = 上位5チーム  ·  🔵 青 = それ以外",
        "color_vs_lineup": "🔴 赤 = ラインナップ平均以上  ·  🔵 青 = 平均未満",
        # Graph captions
        "cap_ideal_aa": "💡 理想AA%（Ideal AA%）: アタックアングルが10〜30°（強い打球・フライが生まれやすい理想範囲）に入るスイングの割合",
        "cap_radar_note": "💡 レーダーチャートは全選手で正規化済み — 外側ほど優秀。バットスピード: スイングの力強さ。アタックアングル: インパクト時の上向き角度。理想AA%: 10〜30°（最適範囲）に入る割合。スイング傾斜: スイング面の傾き角度。",
        "cap_bar_note": "💡 オレンジ点線 = リーグ平均。バットスピード（mph）: 高いほどパワー大。アタックアングル（°）: 10〜30°が最適。理想AA%: 高いほど安定。スイング傾斜（°）: 高いほどアッパースイング傾向。",
        "cap_wbc_overall": "💡 総合スコア = 打撃スコア + 投球スコアの平均（各0〜100、MLB所属選手のみ）。打撃スコアは選手タイプの設定に関係なく常に打者データを使用。⚠️ MLB在籍選手が少ない国はスコアの信頼性が低く、暫定値として参考程度に。",
        "cap_wbc_scatter": "💡 打撃スコア: バットスピード + 理想AA% + アタックアングルを正規化。投球スコア: ERA + FIP + K/9 + BB/9を正規化（各0〜100）",
        "cap_composite": "💡 複合打撃スコア: バットスピード + アタックアングル + 理想AA%を組み合わせて0〜100に正規化",
        # Tab names
        "tab1_name": "🏆 リーダーボード",
        "tab2_name": "👤 選手比較",
        "tab3_name": "🌍 WBC国別戦力",
        "tab4_name": "⚾ チームラインナップ",
        "tab5_name": "📅 月次トレンド",
        # Graph text
        "graph_strength_score": "戦力スコア（0〜100）",
        "graph_wbc_overall_title": "WBC 2026 — 総合戦力スコア（{year}年 MLBデータ）",
        "graph_batting_score": "打撃スコア",
        "graph_pitching_score": "投球スコア",
        "graph_batting_vs_pitching": "打撃 vs 投球 バランス",
        "graph_top6_radar": "上位6カ国 — 打撃レーダーチャート",
        "graph_lineup_title": "{team} ラインナップ — バットトラッキング指標",
        "graph_avg_bat_speed": "平均バットスピード（mph）",
        "graph_attack_angle": "アタックアングル（°）",
        "graph_ideal_aa": "理想AA%",
        "graph_swing_tilt": "スイング傾斜（°）",
        "graph_all_teams_metric": "全チーム — Top-9 {metric}（{year}年）",
        "graph_composite_score": "複合打撃スコア（0〜100）",
        "graph_all_teams_strength": "全チーム — 総合打撃スコア（{year}年）",
        "graph_team_overall": "全チーム — 総合スコア（打撃＋投球）（{year}年）",
        "graph_team_bp_scatter": "チーム別 打撃 vs 投球 バランス",
        "team_bat_table": "📋 チーム別打撃詳細",
        "team_pitch_table": "📋 チーム別投球詳細",
        "filter_radar_countries": "レーダーに表示する国を選択（最大8）",
        "filter_radar_teams": "レーダーに表示するチームを選択（最大8）",
        "radar_bat_title": "打撃レーダーチャート",
        "radar_pit_title": "投球レーダーチャート（ERA / FIP / K9 / BB9）",
        "graph_monthly_ylabel": "平均バットスピード（mph）",
        "graph_monthly_title": "月次バットスピード — {year}年",
        # Pitcher mode
        "pitcher_leaderboard_note": "💡 **投手モード**: ERA / FIP / K/9 / BB/9 を表示（20投球回以上 — 先発・リリーバー含む）。ERA・FIP・BB/9 は低いほど優秀。MLB公式規定投球回は162IP（先発のみ対象）。",
        "pitcher_compare_note": "💡 レーダーは正規化済み（外側 = 常に優秀）。ERA・FIP・BB/9 は反転（低い = 外側）。",
        "tab5_pitcher_note": "📅 月次トレンドは **バットトラッキングデータ**（打者モード）専用です。月次推移を見るには **打者（Batter）** に切り替えてください。",
        "color_pitcher_lower": "🔴 赤 = リーグ平均より優秀（低い）  ·  🔵 青 = 平均より劣る",
        "color_pitcher_higher": "🔴 赤 = リーグ平均より優秀（高い）  ·  🔵 青 = 平均より劣る",
        "radar_title_pitcher": "投手比較（リーグ全体で正規化）",
        # App guide
        "guide_title": "ℹ️ このアプリについて / 使い方  ← クリックで折りたたむ",
        "guide_content": """\
**MLB Bat Tracking Dashboard** は、Hawk-Eyeセンサーで計測したスイング指標（2024年〜）を可視化するダッシュボードです。\
データは [savant-extras](https://github.com/yasumorishima/savant-extras) 経由で Baseball Savant から取得しています。

**🚀 使い方**
1. サイドバーで **シーズン**・**選手タイプ**（打者 / 投手）・フィルタを設定
2. **データ読み込み** ボタンをクリック（約5秒で読み込み完了）
3. タブを切り替えて分析・比較

**📊 タブ一覧**
| タブ | 内容 |
|---|---|
| 🏆 Leaderboard | 任意の指標でTop-Nランキングを棒グラフ表示 |
| 👤 Player Comparison | 最大6選手をレーダーチャート・棒グラフで比較 |
| 🌍 WBC Country Strength | WBC 2026全20カ国の打撃・投球スコアを比較 |
| ⚾ Team Lineup Builder | 9人のラインナップを組んでバット指標を比較 |
| 📅 Monthly Trend | 選手ごとの月別バットスピード推移を表示 |
""",
    },
}


# ── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_bat_data(year: int, player_type: str) -> pd.DataFrame:
    df = bat_tracking(f"{year}-03-01", f"{year}-11-01",
                      player_type=player_type, min_swings=50)
    return df


@st.cache_data(show_spinner=False)
def load_team_lookup(year: int) -> dict[str, str]:
    try:
        bs = batting_stats(year, qual=10)[["Name", "Team"]]
        ps = pitching_stats(year, qual=1)[["Name", "Team"]]
        combined = pd.concat([bs, ps]).drop_duplicates("Name")
        return dict(zip(combined["Name"], combined["Team"]))
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def load_pitching_data(year: int) -> pd.DataFrame:
    try:
        df = pitching_stats(year, qual=20)[
            ["Name", "Team", "ERA", "FIP", "K/9", "BB/9", "IP", "W", "L", "SV"]
        ].copy()
        df["name_lf"] = df["Name"].apply(
            lambda n: f"{n.split()[-1]}, {' '.join(n.split()[:-1])}"
        )
        return df
    except Exception:
        return pd.DataFrame()


def normalize_name(last_first: str) -> str:
    if ", " in last_first:
        parts = last_first.split(", ", 1)
        return f"{parts[1]} {parts[0]}"
    return last_first


def compute_batting_score(df_players: pd.DataFrame, df_all: pd.DataFrame) -> float:
    scores = []
    for col in ["avg_bat_speed", "ideal_attack_angle_rate", "attack_angle"]:
        if col not in df_players.columns or df_players[col].isna().all():
            continue
        mn, mx = df_all[col].min(), df_all[col].max()
        if mx == mn:
            continue
        score = (df_players[col].mean() - mn) / (mx - mn) * 100
        scores.append(score)
    return np.mean(scores) if scores else 0.0


def compute_pitching_score(df_players: pd.DataFrame, df_all: pd.DataFrame) -> float:
    scores = []
    for col, invert in [("ERA", True), ("FIP", True), ("K/9", False), ("BB/9", True)]:
        if col not in df_players.columns or df_players[col].isna().all():
            continue
        mn, mx = df_all[col].min(), df_all[col].max()
        if mx == mn:
            continue
        raw = (df_players[col].mean() - mn) / (mx - mn)
        score = (1 - raw) * 100 if invert else raw * 100
        scores.append(score)
    return np.mean(scores) if scores else 0.0


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    _col_lang, _col_theme = st.columns([3, 1])
    with _col_lang:
        _lang_sel = st.radio(
            "Language / 言語",
            ["🇺🇸 English", "🇯🇵 日本語"],
            horizontal=True,
            label_visibility="collapsed",
        )
    with _col_theme:
        dark_mode = st.toggle("🌙", key="dark_mode_toggle")
    lang = "ja" if "日本語" in _lang_sel else "en"
    t = T[lang]

    st.title(t["sidebar_title"])
    st.caption("Powered by [savant-extras](https://github.com/yasumorishima/savant-extras)")
    st.divider()

    year = st.selectbox(t["season"], [2025, 2024])
    player_type = st.selectbox(t["player_type"], ["batter", "pitcher"])
    load_btn = st.button(t["load_btn"], type="primary", use_container_width=True)
    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.caption(t["data_caption"])

    st.divider()

    side_options = [t["hand_all"], "R", "L"]
    side_filter = st.selectbox(t["handedness"], side_options)

    wbc_options = [t["wbc_all"]] + list(WBC_ROSTERS.keys())
    wbc_filter = st.selectbox(t["wbc_label"], wbc_options)

    team_placeholder = st.empty()


# ── Theme CSS injection ───────────────────────────────────────────────────────
if dark_mode:
    st.markdown("""
<style>
.stApp { background-color: #0e1117 !important; }
.stApp p, .stApp span, .stApp li,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp label, .stApp div, .stMarkdown,
[data-testid="stText"], [data-testid="stMarkdownContainer"] { color: #e0e0e0 !important; }
section[data-testid="stSidebar"] { background-color: #1a1d24 !important; }
section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stAlert"] { background-color: #1e2130 !important; }
[data-testid="stAlert"] * { color: #e0e0e0 !important; }
[data-testid="stExpander"] { background-color: #1e2130 !important; }
[data-testid="stExpander"] * { color: #e0e0e0 !important; }
.stTabs [data-baseweb="tab-list"] { background-color: #1a1d24 !important; }
.stTabs [data-baseweb="tab"] { color: #e0e0e0 !important; }
.stTabs [data-baseweb="tab-panel"] { background-color: #0e1117 !important; }
div[data-testid="stMetric"] { background-color: #1e2130 !important; border-radius: 8px; padding: 8px; }
div[data-testid="stMetric"] * { color: #e0e0e0 !important; }
div[data-baseweb="select"] > div { background-color: #1e2130 !important; color: #e0e0e0 !important; }
div[data-baseweb="select"] input { color: #e0e0e0 !important; caret-color: #e0e0e0 !important; }
div[data-baseweb="select"] [data-baseweb="tag"] { background-color: #2a2d3e !important; color: #e0e0e0 !important; }
div[data-baseweb="popover"] li { background-color: #1e2130 !important; color: #e0e0e0 !important; }
div[data-baseweb="popover"] li:hover { background-color: #2a2d3e !important; }
.stButton button { background-color: #1e2130 !important; color: #e0e0e0 !important; border: 1px solid #444 !important; }
.stButton button:hover { background-color: #2a2d3e !important; border-color: #888 !important; }
.stButton button[kind="primary"] { background-color: #c0392b !important; color: #ffffff !important; border: none !important; }
.stButton button[kind="primary"]:hover { background-color: #e74c3c !important; }
[data-testid="stElementToolbarButtonIcon"] {
    fill: #e0e0e0 !important;
    color: #e0e0e0 !important;
}
[data-testid="stElementToolbarButton"],
button[data-testid="stElementToolbarButton"] {
    background-color: rgba(80,80,80,0.85) !important;
    border-radius: 4px !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
if load_btn:
    with st.spinner(t["fetching"]):
        try:
            df_raw = load_bat_data(year, player_type)
            df_raw["name_normal"] = df_raw["name"].apply(normalize_name)
            team_lookup = load_team_lookup(year)
            df_raw["team"] = df_raw["name_normal"].map(team_lookup).fillna("—")
            st.session_state["df_raw"] = df_raw
            st.session_state["df_pitch"] = load_pitching_data(year)
            st.session_state["year"] = year
            # Always store batter data for WBC/Team tabs (independent of player_type)
            df_batter = load_bat_data(year, "batter")  # cache hit if player_type=="batter"
            df_batter["name_normal"] = df_batter["name"].apply(normalize_name)
            df_batter["team"] = df_batter["name_normal"].map(team_lookup).fillna("—")
            st.session_state["df_batter"] = df_batter
            st.sidebar.success(f"✅ " + t["loaded"].format(n=len(df_raw)))
        except Exception as e:
            st.sidebar.error(f"Error: {e}")


# ── Apply filters ────────────────────────────────────────────────────────────
if "df_raw" in st.session_state:
    df_raw = st.session_state["df_raw"]
    df_pitch = st.session_state.get("df_pitch", pd.DataFrame())
    df_batter = st.session_state.get("df_batter", df_raw)  # batter-only for WBC/Team
    teams = sorted([t_ for t_ in df_batter["team"].unique() if t_ != "—"])
    with team_placeholder:
        team_filter = st.selectbox(
            t["team_label"],
            [t["team_all"]] + teams,
            key="team_sel",
        )

    df = df_raw.copy()
    if side_filter != t["hand_all"]:
        df = df[df["side"] == side_filter]
    if wbc_filter != t["wbc_all"]:
        df = df[df["name"].isin(WBC_ROSTERS[wbc_filter])]
    if st.session_state.get("team_sel", t["team_all"]) != t["team_all"]:
        df = df[df["team"] == st.session_state["team_sel"]]
    player_count = len(df)
else:
    df = None
    df_raw = None
    df_batter = None
    player_count = 0
    df_pitch = pd.DataFrame()

if df is not None:
    badges = []
    if side_filter != t["hand_all"]:
        badges.append(f"✋ {side_filter}")
    if wbc_filter != t["wbc_all"]:
        badges.append(f"🌍 {wbc_filter}")
    if st.session_state.get("team_sel", t["team_all"]) != t["team_all"]:
        badges.append(f"🏟️ {st.session_state['team_sel']}")
    if badges:
        st.info(f"{t['filter_label']} {' · '.join(badges)} — **{player_count} {t['players']}**")


# ── Welcome cards (shown only before data is loaded) ─────────────────────────
def _welcome_card(col, title_key: str, desc_key: str, color: str = "#1f4e79") -> None:
    col.markdown(
        f"""<div style="border:1px solid {color}; border-radius:10px; padding:14px 16px; height:90px;">
  <p style="font-size:1.05rem; font-weight:700; margin:0 0 4px 0;">{t[title_key]}</p>
  <p style="font-size:0.85rem; margin:0; opacity:0.8;">{t[desc_key]}</p>
</div>""",
        unsafe_allow_html=True,
    )

if df is None:
    st.markdown(t["welcome_title"])
    c1, c2, c3 = st.columns(3)
    _welcome_card(c1, "card_tab1_title", "card_tab1_desc")
    _welcome_card(c2, "card_tab2_title", "card_tab2_desc")
    _welcome_card(c3, "card_tab3_title", "card_tab3_desc")
    st.write("")
    c1b, c2b, _ = st.columns(3)
    _welcome_card(c1b, "card_tab4_title", "card_tab4_desc")
    _welcome_card(c2b, "card_tab5_title", "card_tab5_desc", color="#27ae60")
    st.caption(t["start_hint"])
    st.divider()

# ── App Guide ────────────────────────────────────────────────────────────────
with st.expander(t["guide_title"], expanded=False):
    st.markdown(t["guide_content"])

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t["tab1_name"],
    t["tab2_name"],
    t["tab3_name"],
    t["tab4_name"],
    t["tab5_name"],
])


# ── Tab 1: Leaderboard ───────────────────────────────────────────────────────
with tab1:
    if df is None:
        st.info(t["load_first"])
    elif player_type == "pitcher":
        # ── Pitcher Leaderboard ───────────────────────────────────────────────
        if df_pitch.empty:
            st.warning(t["no_pitch_data"])
        else:
            with st.expander(t["glossary_title"]):
                st.markdown(t["term_era"])
                st.markdown(t["term_fip"])
                st.markdown(t["term_k9"])
                st.markdown(t["term_bb9"])

            st.caption(t["pitcher_leaderboard_note"])

            # Apply team / WBC filters to df_pitch
            dp = df_pitch.copy()
            if st.session_state.get("team_sel", t["team_all"]) != t["team_all"]:
                dp = dp[dp["Team"] == st.session_state["team_sel"]]
            if wbc_filter != t["wbc_all"]:
                dp = dp[dp["name_lf"].isin(WBC_ROSTERS[wbc_filter])]

            p_metric = st.selectbox(
                t["metric"],
                list(PITCHING_METRICS.keys()),
                format_func=lambda x: PITCHING_METRICS[x],
                index=list(PITCHING_METRICS.keys()).index("BB/9"),
                key="tab1_p_metric",
            )
            lower_is_better = {"ERA": True, "FIP": True, "K/9": False, "BB/9": True}
            lib = lower_is_better[p_metric]

            n_max_p = min(50, len(dp))
            top_n_p = st.slider(t["top_n"], 5, n_max_p, min(20, n_max_p), step=5,
                                key="tab1_p_topn") if n_max_p >= 5 else n_max_p

            top_p = dp.nsmallest(top_n_p, p_metric) if lib else dp.nlargest(top_n_p, p_metric)
            top_p = top_p.sort_values(p_metric, ascending=not lib)
            league_avg_p = df_pitch[p_metric].mean()

            fig, ax = plt.subplots(figsize=(9, top_n_p * 0.40 + 1.2))
            colors_p = [RED if (v <= league_avg_p if lib else v >= league_avg_p) else BLUE
                        for v in top_p[p_metric]]
            bars_p = ax.barh(top_p["Name"], top_p[p_metric], color=colors_p)
            ax.bar_label(bars_p, fmt="%.2f", padding=4, fontsize=8)
            ax.axvline(league_avg_p, color=AVG_COLOR, linestyle="--", linewidth=2.0,
                       label=f"{t['league_avg']}: {league_avg_p:.2f}")
            ax.set_title(f"Top {top_n_p} — {PITCHING_METRICS[p_metric]} ({year})",
                         fontsize=13, fontweight="bold")
            ax.legend(fontsize=9)
            ax.grid(axis="x", alpha=0.3)
            p_vals = top_p[p_metric].values
            p_pad = (p_vals.max() - p_vals.min()) * 0.15 + 0.1
            ax.set_xlim(left=p_vals.min() - p_pad * 0.3, right=p_vals.max() + p_pad)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.caption(t["color_pitcher_lower"] if lib else t["color_pitcher_higher"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t["filtered"], len(dp))
            c2.metric(t["league_avg"], f"{league_avg_p:.2f}")
            best_row = top_p.iloc[-1]  # last row = top of chart = best
            c3.metric("#1", best_row["Name"], f"{best_row[p_metric]:.2f}")
            c4.metric(t["filter_avg"], f"{dp[p_metric].mean():.2f}")

    elif df.empty:
        st.warning(t["no_players"])
    else:
        # ── Batter Leaderboard ────────────────────────────────────────────────
        with st.expander(t["glossary_title"]):
            st.markdown(t["term_bat_speed"])
            st.markdown(t["term_attack_angle"])
            st.markdown(t["term_ideal_aa"])
            st.markdown(t["term_swing_tilt"])

        col_left, col_right = st.columns([3, 1])
        with col_left:
            metric = st.selectbox(
                t["metric"],
                list(BATTING_METRICS.keys()),
                format_func=lambda x: BATTING_METRICS[x],
            )
        with col_right:
            n_max = min(50, len(df))
        top_n = st.slider(t["top_n"], 5, n_max, min(20, n_max), step=5) if n_max >= 5 else n_max

        top = df.nlargest(top_n, metric).sort_values(metric)
        league_avg = df_raw[metric].mean()

        fig, ax = plt.subplots(figsize=(9, top_n * 0.40 + 1.2))
        colors = [RED if v >= league_avg else BLUE for v in top[metric]]
        bars = ax.barh(top["name"], top[metric], color=colors)
        ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=8)
        ax.axvline(league_avg, color=AVG_COLOR, linestyle="--", linewidth=2.0,
                   label=f"{t['league_avg']}: {league_avg:.1f}")
        title = f"Top {top_n} — {BATTING_METRICS[metric]} ({year})"
        if wbc_filter != t["wbc_all"]:
            title += f"  [{wbc_filter.split(' ', 1)[-1]}]"
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(axis="x", alpha=0.3)
        vals = top[metric].values
        pad = (vals.max() - vals.min()) * 0.15 + 0.5
        ax.set_xlim(left=vals.min() - pad * 0.3, right=vals.max() + pad)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(t["color_vs_avg"])
        if metric == "ideal_attack_angle_rate":
            st.caption(t["cap_ideal_aa"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t["filtered"], player_count)
        c2.metric(t["league_avg"], f"{league_avg:.2f}")
        c3.metric("#1", top.iloc[-1]["name"], f"{top.iloc[-1][metric]:.2f}")
        c4.metric(t["filter_avg"], f"{df[metric].mean():.2f}")


# ── Tab 2: Player Comparison ─────────────────────────────────────────────────
with tab2:
    if df is None:
        st.info(t["load_first"])
    elif player_type == "pitcher":
        # ── Pitcher Comparison ────────────────────────────────────────────────
        if df_pitch.empty:
            st.warning(t["no_pitch_data"])
        else:
            with st.expander(t["glossary_title"]):
                st.markdown(t["term_era"])
                st.markdown(t["term_fip"])
                st.markdown(t["term_k9"])
                st.markdown(t["term_bb9"])

            p_metrics = list(PITCHING_METRICS.keys())   # ["ERA","FIP","K/9","BB/9"]
            p_labels = list(PITCHING_METRICS.values())
            p_invert = [True, True, False, True]        # lower=better → invert for radar

            pitcher_list = sorted(df_pitch["Name"].tolist())
            sel_p = st.multiselect(
                t["select_players"],
                options=pitcher_list,
                default=[],
                max_selections=6,
                placeholder=t["search_placeholder"],
                key="tab2_p_sel",
            )
            if not sel_p:
                st.warning(t["select_one"])
            else:
                sub_p = df_pitch[df_pitch["Name"].isin(sel_p)].set_index("Name")
                norm_p = {m: (df_pitch[m].max() - df_pitch[m].min()) or 1 for m in p_metrics}

                N_p = len(p_metrics)
                angles_p = np.linspace(0, 2 * np.pi, N_p, endpoint=False).tolist() + [0]
                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

                for i, name in enumerate(sel_p):
                    if name not in sub_p.index:
                        continue
                    radar_vals = []
                    for m, inv in zip(p_metrics, p_invert):
                        normalized = (sub_p.loc[name, m] - df_pitch[m].min()) / norm_p[m]
                        radar_vals.append(1 - normalized if inv else normalized)
                    radar_vals += radar_vals[:1]
                    ax.plot(angles_p, radar_vals, color=PALETTE[i], linewidth=2, label=name)
                    ax.fill(angles_p, radar_vals, color=PALETTE[i], alpha=0.08)

                ax.set_xticks(angles_p[:-1])
                ax.set_xticklabels([lb.split(" ")[0] for lb in p_labels], fontsize=11)
                ax.set_yticklabels([])
                ax.set_title(t["radar_title_pitcher"], fontsize=12, fontweight="bold", pad=20)
                ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)
                st.pyplot(fig)
                plt.close(fig)
                st.caption(t["pitcher_compare_note"])

                fig2, axes2 = plt.subplots(1, N_p, figsize=(4 * N_p, 4.5))
                for ax2, m, label in zip(axes2, p_metrics, p_labels):
                    vals2 = [sub_p.loc[n, m] if n in sub_p.index else np.nan for n in sel_p]
                    bars2 = ax2.bar(range(len(sel_p)), vals2, color=PALETTE[:len(sel_p)])
                    ax2.bar_label(bars2, fmt="%.2f", padding=2, fontsize=8)
                    ax2.set_xticks(range(len(sel_p)))
                    ax2.set_xticklabels([n.split(" ")[-1] for n in sel_p],
                                        rotation=30, ha="right", fontsize=9)
                    ax2.set_title(label, fontsize=10, fontweight="bold")
                    avg_p = df_pitch[m].mean()
                    ax2.axhline(avg_p, color=AVG_COLOR, linestyle="--", linewidth=2.0,
                                label=f"avg {avg_p:.2f}")
                    ax2.legend(fontsize=7)
                    ax2.grid(axis="y", alpha=0.3)
                    valid2 = [v for v in vals2 if not np.isnan(v)]
                    if valid2:
                        v_pad2 = (max(valid2) - min(valid2)) * 0.2 + 0.1
                        ax2.set_ylim(bottom=min(valid2) - v_pad2 * 0.3,
                                     top=max(valid2) + v_pad2)
                fig2.suptitle(f"Metric Comparison  ({t['bar_subtitle']})", fontsize=11)
                fig2.tight_layout()
                st.pyplot(fig2)
                plt.close(fig2)
                st.caption(t["cap_bar_note"])

    elif df.empty:
        st.warning(t["no_players"])
    else:
        # ── Batter Comparison ─────────────────────────────────────────────────
        with st.expander(t["glossary_title"]):
            st.markdown(t["term_bat_speed"])
            st.markdown(t["term_attack_angle"])
            st.markdown(t["term_ideal_aa"])
            st.markdown(t["term_swing_tilt"])

        player_list = sorted(df["name"].tolist())
        selected = st.multiselect(
            t["select_players"],
            options=player_list,
            default=[],
            max_selections=6,
            placeholder=t["search_placeholder"],
        )
        if not selected:
            st.warning(t["select_one"])
        else:
            metrics = list(BATTING_METRICS.keys())
            labels = list(BATTING_METRICS.values())
            sub = df[df["name"].isin(selected)].set_index("name")

            N = len(metrics)
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist() + [0]
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            norm = {m: (df_raw[m].max() - df_raw[m].min()) or 1 for m in metrics}

            for i, name in enumerate(selected):
                if name not in sub.index:
                    continue
                vals = [(sub.loc[name, m] - df_raw[m].min()) / norm[m] for m in metrics]
                vals += vals[:1]
                ax.plot(angles, vals, color=PALETTE[i], linewidth=2, label=name)
                ax.fill(angles, vals, color=PALETTE[i], alpha=0.08)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([l.split(" ")[0] for l in labels], fontsize=11)
            ax.set_yticklabels([])
            ax.set_title(t["radar_title"], fontsize=12, fontweight="bold", pad=20)
            ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=9)
            st.pyplot(fig)
            plt.close(fig)
            st.caption(t["cap_radar_note"])

            fig2, axes = plt.subplots(1, N, figsize=(4 * N, 4.5))
            for ax2, m, label in zip(axes, metrics, labels):
                vals = [sub.loc[n, m] if n in sub.index else np.nan for n in selected]
                bars2 = ax2.bar(range(len(selected)), vals, color=PALETTE[:len(selected)])
                ax2.bar_label(bars2, fmt="%.1f", padding=2, fontsize=8)
                ax2.set_xticks(range(len(selected)))
                ax2.set_xticklabels([n.split(",")[0] for n in selected],
                                    rotation=30, ha="right", fontsize=9)
                ax2.set_title(label, fontsize=10, fontweight="bold")
                avg_val = df_raw[m].mean()
                ax2.axhline(avg_val, color=AVG_COLOR, linestyle="--", linewidth=2.0,
                            label=f"avg {avg_val:.1f}")
                ax2.legend(fontsize=7)
                ax2.grid(axis="y", alpha=0.3)
                valid_vals = [v for v in vals if not np.isnan(v)]
                if valid_vals:
                    v_pad = (max(valid_vals) - min(valid_vals)) * 0.2 + 0.5
                    ax2.set_ylim(bottom=min(valid_vals) - v_pad * 0.3,
                                 top=max(valid_vals) + v_pad)
            fig2.suptitle(f"Metric Comparison  ({t['bar_subtitle']})", fontsize=11)
            fig2.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
            st.caption(t["cap_bar_note"])


# ── Tab 3: WBC Country Strength ──────────────────────────────────────────────
with tab3:
    if df_batter is None:
        st.info(t["load_first"])
    else:
        st.subheader(t["wbc_subheader"])
        st.caption(t["wbc_caption"])

        with st.expander(t["glossary_title"]):
            st.markdown("**Batting metrics**" if lang == "en" else "**打撃指標**")
            st.markdown(t["term_bat_speed"])
            st.markdown(t["term_attack_angle"])
            st.markdown(t["term_ideal_aa"])
            st.markdown("**Pitching metrics**" if lang == "en" else "**投球指標**")
            st.markdown(t["term_era"])
            st.markdown(t["term_fip"])
            st.markdown(t["term_k9"])
            st.markdown(t["term_bb9"])

        mode = st.radio(t["mode"], [t["auto_mode"], t["manual_mode"]], horizontal=True)

        country_batting: dict[str, pd.DataFrame] = {}
        country_pitching: dict[str, pd.DataFrame] = {}

        for country, roster in WBC_ROSTERS.items():
            bat = df_batter[df_batter["name"].isin(roster)]
            country_batting[country] = bat
            if not df_pitch.empty:
                pit = df_pitch[df_pitch["name_lf"].isin(roster)]
                country_pitching[country] = pit

        if mode == t["manual_mode"]:
            st.markdown("---")
            sel_country = st.selectbox(
                t["select_country"],
                [c for c in WBC_ROSTERS if not country_batting[c].empty],
            )
            available = sorted(country_batting[sel_country]["name"].tolist())
            lineup = st.multiselect(
                t["choose_batters"].format(country=sel_country),
                options=available,
                default=available[:min(9, len(available))],
                max_selections=9,
                key="lineup_sel",
            )
            if lineup:
                sub_bat = country_batting[sel_country][
                    country_batting[sel_country]["name"].isin(lineup)
                ]
                country_batting[sel_country] = sub_bat
                st.success(t["batters_selected"].format(country=sel_country, n=len(lineup)))

        rows = []
        for country in WBC_ROSTERS:
            bat = country_batting.get(country, pd.DataFrame())
            pit = country_pitching.get(country, pd.DataFrame())
            b_score = compute_batting_score(bat, df_batter) if not bat.empty else None
            p_score = compute_pitching_score(pit, df_pitch) if not pit.empty and not df_pitch.empty else None
            bat_speed = bat["avg_bat_speed"].mean() if not bat.empty else None
            bat_n = len(bat)
            pit_n = len(pit)
            batter_names = ", ".join(bat["name"].apply(normalize_name).tolist()) if not bat.empty else "—"
            rows.append({
                "country": country,
                "batting_score": b_score,
                "pitching_score": p_score,
                "avg_bat_speed": bat_speed,
                "n_batters": bat_n,
                "n_pitchers": pit_n,
                "batter_names": batter_names,
            })

        df_scores = pd.DataFrame(rows).dropna(subset=["batting_score"])
        df_scores["overall_score"] = df_scores[["batting_score", "pitching_score"]].mean(axis=1)
        df_scores = df_scores.sort_values("overall_score", ascending=False)
        # Strip flag emoji for matplotlib (emojis are not renderable in standard fonts)
        df_scores["country_label"] = df_scores["country"].str.split(" ", n=1).str[-1]

        with st.expander(t["full_table"], expanded=True):
            display = df_scores[["country", "n_batters", "n_pitchers", "avg_bat_speed",
                                  "batting_score", "pitching_score", "overall_score",
                                  "batter_names"]].copy()
            display.columns = [
                t["col_country"], t["col_batters"], t["col_pitchers"], t["col_bat_speed"],
                t["col_bat_score"], t["col_pit_score"], t["col_overall"],
                t["col_batter_names"],
            ]
            display = display.set_index(t["col_country"])
            st.dataframe(display.style.format({
                t["col_bat_speed"]: "{:.1f}",
                t["col_bat_score"]: "{:.1f}",
                t["col_pit_score"]: lambda x: f"{x:.1f}" if pd.notna(x) else "—",
                t["col_overall"]: "{:.1f}",
            }), use_container_width=True)
            st.caption(t["cap_wbc_overall"])

        df_both = df_scores.dropna(subset=["batting_score", "pitching_score"])
        if not df_both.empty:
            st.markdown(t["batting_pitching"])
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.scatter(df_both["batting_score"], df_both["pitching_score"],
                        s=120, color=BLUE, alpha=0.8)
            for _, row in df_both.iterrows():
                ax2.annotate(row["country_label"],
                             (row["batting_score"], row["pitching_score"]),
                             fontsize=8, ha="left", va="bottom",
                             xytext=(4, 4), textcoords="offset points")
            ax2.axvline(df_both["batting_score"].mean(), color="gray",
                        linestyle="--", linewidth=1, alpha=0.5)
            ax2.axhline(df_both["pitching_score"].mean(), color="gray",
                        linestyle="--", linewidth=1, alpha=0.5)
            ax2.set_xlabel(t["graph_batting_score"])
            ax2.set_ylabel(t["graph_pitching_score"])
            ax2.set_title(t["graph_batting_vs_pitching"], fontsize=12, fontweight="bold")
            fig2.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
            st.caption(t["cap_wbc_scatter"])

        # ── Radar section ──
        st.markdown("---")
        radar_options = [c for c in df_scores["country"].tolist()
                         if not country_batting[c].empty]
        top6_default = radar_options[:min(6, len(radar_options))]
        sel_radar = st.multiselect(
            t["filter_radar_countries"],
            options=radar_options,
            default=top6_default,
            max_selections=8,
            key="wbc_radar_sel",
        )
        bat_r_metrics = ["avg_bat_speed", "ideal_attack_angle_rate", "attack_angle"]
        bat_r_labels  = ["Bat Speed", "Ideal AA%", "Attack Angle"]
        pit_r_metrics = ["ERA", "FIP", "K/9", "BB/9"]
        pit_r_labels  = ["ERA", "FIP", "K/9", "BB/9"]
        pit_r_invert  = [True, True, False, True]  # lower=better → invert for radar

        if len(sel_radar) >= 2:
            rc1, rc2 = st.columns(2)

            # Batting radar
            valid_bat = [c for c in sel_radar
                         if all(m in country_batting[c].columns for m in bat_r_metrics)]
            if len(valid_bat) >= 2:
                N = len(bat_r_metrics)
                angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist() + [0]
                norm_bat = {m: (df_batter[m].max() - df_batter[m].min()) or 1 for m in bat_r_metrics}
                fig_rb, ax_rb = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                for i, country in enumerate(valid_bat):
                    bat = country_batting[country]
                    vals = [(bat[m].mean() - df_batter[m].min()) / norm_bat[m] for m in bat_r_metrics]
                    vals += vals[:1]
                    ax_rb.plot(angles, vals, color=PALETTE[i], linewidth=2,
                               label=country.split(" ", 1)[-1])
                    ax_rb.fill(angles, vals, color=PALETTE[i], alpha=0.07)
                ax_rb.set_xticks(angles[:-1])
                ax_rb.set_xticklabels(bat_r_labels, fontsize=10)
                ax_rb.set_yticklabels([])
                ax_rb.set_title(t["radar_bat_title"], fontsize=12, fontweight="bold", pad=20)
                ax_rb.legend(loc="upper right", bbox_to_anchor=(1.45, 1.15), fontsize=8)
                fig_rb.tight_layout()
                rc1.pyplot(fig_rb)
                plt.close(fig_rb)

            # Pitching radar
            if not df_pitch.empty:
                valid_pit = [c for c in sel_radar if not country_pitching.get(c, pd.DataFrame()).empty]
                if len(valid_pit) >= 2:
                    N = len(pit_r_metrics)
                    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist() + [0]
                    norm_pit = {}
                    for m in pit_r_metrics:
                        mn, mx = df_pitch[m].min(), df_pitch[m].max()
                        norm_pit[m] = (mn, mx, (mx - mn) or 1)
                    fig_rp, ax_rp = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                    for i, country in enumerate(valid_pit):
                        pit = country_pitching[country]
                        vals = []
                        for m, inv in zip(pit_r_metrics, pit_r_invert):
                            mn, mx, rng = norm_pit[m]
                            v = (pit[m].mean() - mn) / rng
                            vals.append(1 - v if inv else v)
                        vals += vals[:1]
                        ax_rp.plot(angles, vals, color=PALETTE[i], linewidth=2,
                                   label=country.split(" ", 1)[-1])
                        ax_rp.fill(angles, vals, color=PALETTE[i], alpha=0.07)
                    ax_rp.set_xticks(angles[:-1])
                    ax_rp.set_xticklabels(pit_r_labels, fontsize=10)
                    ax_rp.set_yticklabels([])
                    ax_rp.set_title(t["radar_pit_title"], fontsize=12, fontweight="bold", pad=20)
                    ax_rp.legend(loc="upper right", bbox_to_anchor=(1.45, 1.15), fontsize=8)
                    fig_rp.tight_layout()
                    rc2.pyplot(fig_rp)
                    plt.close(fig_rp)

        with st.expander(t["bat_table"]):
            bat_rows = []
            for country in WBC_ROSTERS:
                bat = country_batting.get(country, pd.DataFrame())
                if bat.empty:
                    continue
                bat_rows.append({
                    t["col_country"]: country,
                    t["col_batters"]: len(bat),
                    t["col_bat_speed"]: bat["avg_bat_speed"].mean(),
                    t["graph_attack_angle"]: bat["attack_angle"].mean(),
                    t["graph_ideal_aa"]: bat["ideal_attack_angle_rate"].mean(),
                    t["graph_swing_tilt"]: bat["swing_tilt"].mean(),
                    t["col_bat_score"]: compute_batting_score(bat, df_batter),
                })
            if bat_rows:
                df_bat_display = pd.DataFrame(bat_rows).sort_values(
                    t["col_bat_score"], ascending=False
                ).set_index(t["col_country"])
                st.dataframe(df_bat_display.style.format("{:.2f}", subset=[
                    t["col_bat_speed"], t["graph_attack_angle"],
                    t["graph_ideal_aa"], t["graph_swing_tilt"], t["col_bat_score"],
                ]), use_container_width=True)

        with st.expander(t["pitch_table"]):
            pit_rows = []
            for country in WBC_ROSTERS:
                pit = country_pitching.get(country, pd.DataFrame())
                if pit.empty:
                    continue
                pit_rows.append({
                    t["col_country"]: country,
                    t["col_pitchers"]: len(pit),
                    t["col_era"]: pit["ERA"].mean(),
                    t["col_fip"]: pit["FIP"].mean(),
                    t["col_k9"]: pit["K/9"].mean(),
                    t["col_bb9"]: pit["BB/9"].mean(),
                    t["col_pit_score"]: compute_pitching_score(pit, df_pitch),
                })
            if pit_rows:
                df_pit_display = pd.DataFrame(pit_rows).sort_values(
                    t["col_pit_score"], ascending=False
                ).set_index(t["col_country"])
                st.dataframe(df_pit_display.style.format({
                    t["col_era"]: "{:.2f}",
                    t["col_fip"]: "{:.2f}",
                    t["col_k9"]: "{:.2f}",
                    t["col_bb9"]: "{:.2f}",
                    t["col_pit_score"]: "{:.1f}",
                }), use_container_width=True)
            else:
                st.info(t["no_pitch_data"])


# ── Tab 4: Team Lineup Builder ───────────────────────────────────────────────
POSITIONS = ["C", "1B", "2B", "SS", "3B", "LF", "CF", "RF", "DH"]
POS_ORDER = ["DH", "1B", "RF", "LF", "CF", "3B", "2B", "SS", "C"]

with tab4:
    if df_batter is None:
        st.info(t["load_first"])
    else:
        st.subheader(t["lineup_subheader"])
        st.caption(t["lineup_caption"])

        with st.expander(t["glossary_title"]):
            st.markdown(t["term_bat_speed"])
            st.markdown(t["term_attack_angle"])
            st.markdown(t["term_ideal_aa"])
            st.markdown(t["term_swing_tilt"])
            st.markdown(t["term_wrc"])

        @st.cache_data(show_spinner=False)
        def build_team_roster(year: int) -> pd.DataFrame:
            bt = load_bat_data(year, "batter")
            bt["name_normal"] = bt["name"].apply(normalize_name)
            try:
                bs = batting_stats(year, qual=10)[["Name", "Team", "wRC+"]]
                merged = bt.merge(bs, left_on="name_normal", right_on="Name", how="inner")
                merged = merged[merged["Team"] != "- - -"]
                return merged
            except Exception:
                return bt

        roster_df = build_team_roster(year)
        all_teams = sorted(roster_df["Team"].unique().tolist())

        view_mode = st.radio(
            t["view_mode"],
            [t["compare_mode"], t["build_mode"]],
            horizontal=True,
        )

        if view_mode == t["build_mode"]:
            sel_team = st.selectbox(t["select_team"], all_teams)
            team_players = roster_df[roster_df["Team"] == sel_team].sort_values(
                "wRC+", ascending=False
            )
            player_opts = team_players["name"].tolist()

            if not player_opts:
                st.warning(t["no_bat_data"])
            else:
                st.markdown(f"**{t['lineup_header'].format(team=sel_team, n=len(player_opts))}**")
                st.caption(t["pos_caption"])

                lineup_selections = {}
                cols = st.columns(3)
                hardcoded_lineup = MLB_LINEUPS_2025.get(sel_team, {})
                for i, pos in enumerate(POSITIONS):
                    hardcoded_name = hardcoded_lineup.get(pos)
                    if hardcoded_name and hardcoded_name in player_opts:
                        default_player = hardcoded_name
                    else:
                        default_idx = POS_ORDER.index(pos) if pos in POS_ORDER else i
                        default_player = (
                            player_opts[default_idx]
                            if default_idx < len(player_opts)
                            else player_opts[0]
                        )
                    with cols[i % 3]:
                        lineup_selections[pos] = st.selectbox(
                            f"**{pos}**",
                            options=player_opts,
                            index=player_opts.index(default_player),
                            key=f"lineup_{pos}",
                        )

                lineup_names = list(lineup_selections.values())
                lineup_data = team_players[team_players["name"].isin(lineup_names)]
                lineup_data = lineup_data.drop_duplicates("name")

                st.markdown("---")
                metrics_show = ["avg_bat_speed", "attack_angle",
                                "ideal_attack_angle_rate", "swing_tilt"]
                labels_show = ["Bat Speed", "Attack Angle", "Ideal AA%", "Swing Tilt"]

                c1, c2, c3, c4 = st.columns(4)
                for col, m, label in zip([c1, c2, c3, c4], metrics_show, labels_show):
                    lineup_val = lineup_data[m].mean() if m in lineup_data else 0
                    league_val = roster_df[m].mean() if m in roster_df else 0
                    delta = lineup_val - league_val
                    col.metric(label, f"{lineup_val:.2f}",
                               t["vs_league"].format(delta=delta))

                fig, axes = plt.subplots(1, 4, figsize=(16, 5))
                for ax_i, (m, label) in enumerate(zip(metrics_show, labels_show)):
                    ax = axes[ax_i]
                    sorted_ld = lineup_data.sort_values(m, ascending=True)
                    avg_val = roster_df[m].mean()
                    colors = [RED if v >= avg_val else BLUE for v in sorted_ld[m]]
                    bars = ax.barh(sorted_ld["name"], sorted_ld[m], color=colors)
                    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=8)
                    ax.axvline(avg_val, color=AVG_COLOR, linestyle="--",
                               linewidth=2.0, label=f"{t['league_avg']} {avg_val:.1f}")
                    ax.set_title(label, fontsize=10, fontweight="bold")
                    ax.legend(fontsize=7)
                    ax.grid(axis="x", alpha=0.3)
                    vals = sorted_ld[m].values
                    pad = (vals.max() - vals.min()) * 0.15 + 0.5
                    ax.set_xlim(left=vals.min() - pad * 0.3, right=vals.max() + pad)
                fig.suptitle(t["graph_lineup_title"].format(team=sel_team), fontsize=12,
                             fontweight="bold")
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
                st.caption(t["color_vs_lineup"])

        else:
            st.caption(t["compare_caption"])
            metric_cmp = st.selectbox(
                t["cmp_metric"],
                ["avg_bat_speed", "attack_angle", "ideal_attack_angle_rate", "swing_tilt"],
                format_func=lambda x: {
                    "avg_bat_speed": "Avg Bat Speed (mph)",
                    "attack_angle": "Attack Angle (°)",
                    "ideal_attack_angle_rate": "Ideal AA%",
                    "swing_tilt": "Swing Tilt (°)",
                }.get(x, x),
                key="team_cmp_metric",
            )

            team_scores = []
            for team in all_teams:
                tp = roster_df[roster_df["Team"] == team].sort_values(
                    "wRC+", ascending=False
                ).head(9)
                if len(tp) == 0:
                    continue
                pit_team = df_pitch[df_pitch["Team"] == team] if not df_pitch.empty else pd.DataFrame()
                p_score = compute_pitching_score(pit_team, df_pitch) if not pit_team.empty else None
                b_score = compute_batting_score(tp, roster_df)
                team_scores.append({
                    "team": team,
                    "value": tp[metric_cmp].mean(),
                    "n": len(tp),
                    "bat_score": b_score,
                    "pit_score": p_score,
                    "overall_score": np.mean([s for s in [b_score, p_score] if s is not None]),
                    "avg_bat_speed": tp["avg_bat_speed"].mean() if "avg_bat_speed" in tp.columns else None,
                    "attack_angle": tp["attack_angle"].mean() if "attack_angle" in tp.columns else None,
                    "ideal_aa": tp["ideal_attack_angle_rate"].mean() if "ideal_attack_angle_rate" in tp.columns else None,
                    "swing_tilt": tp["swing_tilt"].mean() if "swing_tilt" in tp.columns else None,
                    "n_pitchers": len(pit_team),
                    "era": pit_team["ERA"].mean() if not pit_team.empty else None,
                    "fip": pit_team["FIP"].mean() if not pit_team.empty else None,
                    "k9": pit_team["K/9"].mean() if not pit_team.empty else None,
                    "bb9": pit_team["BB/9"].mean() if not pit_team.empty else None,
                })

            df_team_scores = pd.DataFrame(team_scores).sort_values("value", ascending=True)
            league_avg = roster_df[metric_cmp].mean()

            fig, ax = plt.subplots(figsize=(9, len(df_team_scores) * 0.42 + 1.5))
            colors = [RED if v >= league_avg else BLUE for v in df_team_scores["value"]]
            bars = ax.barh(df_team_scores["team"], df_team_scores["value"], color=colors)
            ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
            ax.axvline(league_avg, color=AVG_COLOR, linestyle="--", linewidth=2.0,
                       label=f"{t['league_avg']}: {league_avg:.2f}")
            ax.set_xlabel({
                "avg_bat_speed": t["graph_avg_bat_speed"],
                "attack_angle": t["graph_attack_angle"],
                "ideal_attack_angle_rate": t["graph_ideal_aa"],
                "swing_tilt": t["graph_swing_tilt"],
            }.get(metric_cmp, metric_cmp))
            ax.set_title(t["graph_all_teams_metric"].format(
                metric=metric_cmp.replace("_", " ").title(), year=year),
                         fontsize=13, fontweight="bold")
            ax.legend(fontsize=9)
            ax.grid(axis="x", alpha=0.3)
            vals = df_team_scores["value"].values
            pad = (vals.max() - vals.min()) * 0.15 + 0.5
            ax.set_xlim(left=vals.min() - pad * 0.3, right=vals.max() + pad)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.caption(t["color_vs_avg"])

            df_team_scores_sorted = pd.DataFrame(team_scores).sort_values(
                "bat_score", ascending=True
            )
            fig2, ax2 = plt.subplots(figsize=(9, len(df_team_scores_sorted) * 0.42 + 1.5))
            colors2 = [RED if i >= len(df_team_scores_sorted) - 5 else BLUE
                       for i in range(len(df_team_scores_sorted))]
            ax2.barh(df_team_scores_sorted["team"], df_team_scores_sorted["bat_score"],
                     color=colors2)
            ax2.set_xlabel(t["graph_composite_score"])
            ax2.set_title(t["graph_all_teams_strength"].format(year=year),
                          fontsize=13, fontweight="bold")
            fig2.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)
            st.caption(t["color_top5"] + "  ·  " + t["cap_composite"])

            # Overall score (batting + pitching)
            df_overall = pd.DataFrame(team_scores).dropna(subset=["pit_score"]).sort_values(
                "overall_score", ascending=True
            )
            if not df_overall.empty:
                fig3, ax3 = plt.subplots(figsize=(9, len(df_overall) * 0.42 + 1.5))
                colors3 = [RED if i >= len(df_overall) - 5 else BLUE for i in range(len(df_overall))]
                bars3 = ax3.barh(df_overall["team"], df_overall["overall_score"], color=colors3)
                ax3.bar_label(bars3, fmt="%.1f", padding=3, fontsize=8)
                ax3.set_xlabel(t["graph_strength_score"])
                ax3.set_title(t["graph_team_overall"].format(year=year), fontsize=13, fontweight="bold")
                ax3.grid(axis="x", alpha=0.3)
                fig3.tight_layout()
                st.pyplot(fig3)
                plt.close(fig3)
                st.caption(t["color_top5"] + "  ·  " + t["cap_wbc_overall"])

                fig4, ax4 = plt.subplots(figsize=(9, 6))
                ax4.scatter(df_overall["bat_score"], df_overall["pit_score"],
                            s=120, color=BLUE, alpha=0.8)
                for _, row in df_overall.iterrows():
                    ax4.annotate(row["team"], (row["bat_score"], row["pit_score"]),
                                 fontsize=7, ha="left", va="bottom",
                                 xytext=(4, 4), textcoords="offset points")
                ax4.axvline(df_overall["bat_score"].mean(), color="gray", linestyle="--", linewidth=1, alpha=0.5)
                ax4.axhline(df_overall["pit_score"].mean(), color="gray", linestyle="--", linewidth=1, alpha=0.5)
                ax4.set_xlabel(t["graph_batting_score"])
                ax4.set_ylabel(t["graph_pitching_score"])
                ax4.set_title(t["graph_team_bp_scatter"], fontsize=12, fontweight="bold")
                fig4.tight_layout()
                st.pyplot(fig4)
                plt.close(fig4)
                st.caption(t["cap_wbc_scatter"])

            # Radar charts with team filter
            st.markdown("---")
            all_team_list = [r["team"] for r in team_scores]
            default_teams = all_team_list[:min(6, len(all_team_list))]
            sel_radar_teams = st.multiselect(
                t["filter_radar_teams"],
                options=all_team_list,
                default=default_teams,
                max_selections=8,
                key="team_radar_sel",
                format_func=team_label,
            )
            if len(sel_radar_teams) >= 2:
                tr1, tr2 = st.columns(2)
                bat_r_metrics = ["avg_bat_speed", "ideal_attack_angle_rate", "attack_angle", "swing_tilt"]
                bat_r_labels  = ["Bat Speed", "Ideal AA%", "Attack Angle", "Swing Tilt"]
                pit_r_metrics_t = ["ERA", "FIP", "K/9", "BB/9"]
                pit_r_invert_t  = [True, True, False, True]

                # Batting radar
                N = len(bat_r_metrics)
                angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist() + [0]
                norm_b = {m: (roster_df[m].max() - roster_df[m].min()) or 1
                          for m in bat_r_metrics if m in roster_df.columns}
                fig_tr, ax_tr = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                for i, team in enumerate(sel_radar_teams):
                    row = next((r for r in team_scores if r["team"] == team), None)
                    if row is None:
                        continue
                    vals = []
                    for m in bat_r_metrics:
                        v = row.get(m.replace("ideal_attack_angle_rate", "ideal_aa")
                                      .replace("avg_bat_speed", "avg_bat_speed")
                                      .replace("attack_angle", "attack_angle")
                                      .replace("swing_tilt", "swing_tilt"))
                        mn = roster_df[m].min() if m in roster_df.columns else 0
                        rng = norm_b.get(m, 1)
                        vals.append(((v or 0) - mn) / rng if v is not None else 0)
                    vals += vals[:1]
                    ax_tr.plot(angles, vals, color=PALETTE[i], linewidth=2, label=team_label(team))
                    ax_tr.fill(angles, vals, color=PALETTE[i], alpha=0.07)
                ax_tr.set_xticks(angles[:-1])
                ax_tr.set_xticklabels(bat_r_labels, fontsize=9)
                ax_tr.set_yticklabels([])
                ax_tr.set_title(t["radar_bat_title"], fontsize=12, fontweight="bold", pad=20)
                ax_tr.legend(loc="upper right", bbox_to_anchor=(1.5, 1.15), fontsize=7)
                fig_tr.tight_layout()
                tr1.pyplot(fig_tr)
                plt.close(fig_tr)

                # Pitching radar
                if not df_pitch.empty:
                    norm_p = {}
                    for m in pit_r_metrics_t:
                        mn, mx = df_pitch[m].min(), df_pitch[m].max()
                        norm_p[m] = (mn, mx, (mx - mn) or 1)
                    fig_tp, ax_tp = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                    drawn = 0
                    for i, team in enumerate(sel_radar_teams):
                        row = next((r for r in team_scores if r["team"] == team), None)
                        if row is None or row.get("pit_score") is None:
                            continue
                        vals = []
                        for m, inv in zip(pit_r_metrics_t, pit_r_invert_t):
                            key = {"ERA": "era", "FIP": "fip", "K/9": "k9", "BB/9": "bb9"}[m]
                            v = row.get(key) or norm_p[m][0]
                            mn, mx, rng = norm_p[m]
                            nv = (v - mn) / rng
                            vals.append(1 - nv if inv else nv)
                        vals += vals[:1]
                        ax_tp.plot(angles, vals, color=PALETTE[i], linewidth=2, label=team_label(team))
                        ax_tp.fill(angles, vals, color=PALETTE[i], alpha=0.07)
                        drawn += 1
                    if drawn >= 2:
                        ax_tp.set_xticks(angles[:-1])
                        ax_tp.set_xticklabels(pit_r_metrics_t, fontsize=10)
                        ax_tp.set_yticklabels([])
                        ax_tp.set_title(t["radar_pit_title"], fontsize=12, fontweight="bold", pad=20)
                        ax_tp.legend(loc="upper right", bbox_to_anchor=(1.5, 1.15), fontsize=7)
                        fig_tp.tight_layout()
                        tr2.pyplot(fig_tp)
                    plt.close(fig_tp)

            # Batting details table
            with st.expander(t["team_bat_table"]):
                bat_cols = {
                    t["col_batters"]: "n",
                    t["col_bat_speed"]: "avg_bat_speed",
                    t["graph_attack_angle"]: "attack_angle",
                    t["graph_ideal_aa"]: "ideal_aa",
                    t["graph_swing_tilt"]: "swing_tilt",
                    t["col_bat_score"]: "bat_score",
                }
                df_bt = pd.DataFrame(team_scores).set_index("team")[list(bat_cols.values())].copy()
                df_bt.index.name = t["col_country"] if lang == "en" else "チーム"
                df_bt.columns = list(bat_cols.keys())
                df_bt = df_bt.sort_values(t["col_bat_score"], ascending=False)
                st.dataframe(df_bt.style.format("{:.2f}", subset=[
                    c for c in df_bt.columns if c != t["col_batters"]
                ]), use_container_width=True)

            # Pitching details table
            with st.expander(t["team_pitch_table"]):
                df_pt = pd.DataFrame(team_scores).dropna(subset=["pit_score"]).set_index("team")[[
                    "n_pitchers", "era", "fip", "k9", "bb9", "pit_score"
                ]].copy()
                df_pt.index.name = t["col_country"] if lang == "en" else "チーム"
                df_pt.columns = [
                    t["col_pitchers"], t["col_era"], t["col_fip"],
                    t["col_k9"], t["col_bb9"], t["col_pit_score"],
                ]
                df_pt = df_pt.sort_values(t["col_pit_score"], ascending=False)
                st.dataframe(df_pt.style.format({
                    t["col_era"]: "{:.2f}", t["col_fip"]: "{:.2f}",
                    t["col_k9"]: "{:.2f}", t["col_bb9"]: "{:.2f}",
                    t["col_pit_score"]: "{:.1f}",
                }), use_container_width=True)


# ── Tab 5: Monthly Trend ─────────────────────────────────────────────────────
with tab5:
    if df is None:
        st.info(t["load_first"])
    elif player_type == "pitcher":
        st.info(t["tab5_pitcher_note"])
    else:
        st.caption(t["monthly_caption"])

        if st.button(t["load_monthly"], key="mt_btn"):
            with st.spinner(t["fetching"]):
                try:
                    df_m = bat_tracking_monthly(year, player_type=player_type)
                    st.session_state["df_monthly"] = df_m
                    st.success(t["monthly_loaded"].format(n=len(df_m)))
                except Exception as e:
                    st.error(f"Error: {e}")

        if "df_monthly" in st.session_state:
            df_m = st.session_state["df_monthly"]
            month_labels = {4: "Apr", 5: "May", 6: "Jun", 7: "Jul",
                            8: "Aug", 9: "Sep", 10: "Oct"}

            avg_trend = df_m.groupby("month")["avg_bat_speed"].mean()
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot([month_labels[m] for m in avg_trend.index], avg_trend.values,
                    color=AVG_COLOR, linestyle="--", linewidth=2.5, label=t["league_avg"], zorder=1)

            default_monthly = []
            if wbc_filter != t["wbc_all"] and df is not None:
                default_monthly = [n for n in df["name"].tolist()
                                   if n in df_m["name"].values][:6]

            player_list_m = sorted(df_m["name"].unique().tolist())
            selected_m = st.multiselect(
                t["overlay_players"], options=player_list_m,
                default=default_monthly, key="mt_players", max_selections=6,
            )
            for i, name in enumerate(selected_m):
                sub = df_m[df_m["name"] == name].sort_values("month")
                ax.plot([month_labels[m] for m in sub["month"]],
                        sub["avg_bat_speed"],
                        marker="o", linewidth=2, color=PALETTE[i], label=name, zorder=2)

            ax.set_ylabel(t["graph_monthly_ylabel"])
            ax.set_title(t["graph_monthly_title"].format(year=year), fontsize=13, fontweight="bold")
            ax.legend(fontsize=9)
            ax.grid(axis="y", alpha=0.3)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
