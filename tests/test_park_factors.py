"""Tests for park_factors module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from savant_extras import park_factors, park_factors_range


# Minimal DataFrame that _fetch_one returns after processing
def _make_sample_df(season: int) -> pd.DataFrame:
    return pd.DataFrame({
        "Team": ["Rockies", "Red Sox", "Yankees"],
        "Basic (5yr)": [116, 100, 97],
        "3yr": [115, 99, 96],
        "1yr": [120, 101, 95],
        "HR": [131, 102, 93],
        "1B": [110, 100, 98],
        "2B": [108, 101, 97],
        "3B": [105, 98, 95],
        "SO": [97, 100, 101],
        "BB": [101, 100, 99],
        "FIP": [112, 100, 96],
    })


def _mock_response(html_text: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html_text
    mock.raise_for_status = MagicMock()
    return mock


# Minimal HTML table that pd.read_html can parse
_SAMPLE_HTML = """
<html><body>
<table>
  <tr><th>Team</th><th>Basic (5yr)</th><th>3yr</th><th>1yr</th>
      <th>HR</th><th>1B</th><th>2B</th><th>3B</th><th>SO</th><th>BB</th><th>FIP</th></tr>
  <tr><td>Rockies</td><td>116</td><td>115</td><td>120</td>
      <td>131</td><td>110</td><td>108</td><td>105</td><td>97</td><td>101</td><td>112</td></tr>
  <tr><td>Red Sox</td><td>100</td><td>99</td><td>101</td>
      <td>102</td><td>100</td><td>101</td><td>98</td><td>100</td><td>100</td><td>100</td></tr>
  <tr><td>Yankees</td><td>97</td><td>96</td><td>95</td>
      <td>93</td><td>98</td><td>97</td><td>95</td><td>101</td><td>99</td><td>96</td></tr>
</table>
</body></html>
"""


class TestParkFactors:
    @patch("savant_extras.park_factors.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    @patch("savant_extras.park_factors.requests.get")
    def test_team_column_abbreviation(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        assert "COL" in df["team"].values
        assert "BOS" in df["team"].values
        assert "NYY" in df["team"].values

    @patch("savant_extras.park_factors.requests.get")
    def test_season_column_added(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        assert "season" in df.columns
        assert (df["season"] == 2024).all()

    @patch("savant_extras.park_factors.requests.get")
    def test_pf_columns_present(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        for col in ["pf_5yr", "pf_3yr", "pf_1yr", "pf_hr"]:
            assert col in df.columns, f"{col} not found in columns"

    @patch("savant_extras.park_factors.requests.get")
    def test_col_values_numeric(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        assert df["pf_5yr"].dtype in (float, int) or pd.api.types.is_numeric_dtype(df["pf_5yr"])

    @patch("savant_extras.park_factors.requests.get")
    def test_url_contains_year(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        park_factors(2022)
        url = mock_get.call_args[0][0]
        assert "season=2022" in url

    @patch("savant_extras.park_factors.requests.get")
    def test_col_values_match(self, mock_get):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors(2024)
        col_row = df[df["team"] == "COL"].iloc[0]
        assert col_row["pf_5yr"] == 116
        assert col_row["pf_hr"] == 131

    @patch("savant_extras.park_factors.requests.get")
    def test_no_team_column_raises(self, mock_get):
        no_team_html = "<html><body><table><tr><th>Name</th></tr><tr><td>x</td></tr></table></body></html>"
        mock_get.return_value = _mock_response(no_team_html)
        with pytest.raises(ValueError, match="not found"):
            park_factors(2024)


class TestParkFactorsRange:
    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_returns_dataframe(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors_range(2022, 2024)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 9  # 3 seasons × 3 teams

    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_season_values(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors_range(2022, 2024)
        assert set(df["season"].unique()) == {2022, 2023, 2024}

    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_calls_api_per_year(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        park_factors_range(2022, 2024)
        assert mock_get.call_count == 3

    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_sleep_between_requests(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        park_factors_range(2022, 2024)
        assert mock_sleep.call_count == 2

    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_single_season_range(self, mock_get, mock_sleep):
        mock_get.return_value = _mock_response(_SAMPLE_HTML)
        df = park_factors_range(2024, 2024)
        assert set(df["season"].unique()) == {2024}
        mock_sleep.assert_not_called()

    @patch("savant_extras.park_factors.time.sleep")
    @patch("savant_extras.park_factors.requests.get")
    def test_all_fail_raises(self, mock_get, mock_sleep):
        mock_get.side_effect = Exception("network error")
        with pytest.raises(RuntimeError, match="No park factor data"):
            park_factors_range(2022, 2024)
