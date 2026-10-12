"""
Birim Testleri: İstatistiksel Analiz Motoru
"""

import pytest
import pandas as pd
import numpy as np

from analytics.descriptive import calculate_descriptive_stats
from analytics.time_series import analyze_time_series_window
from analytics.correlation import calculate_bivariate_correlation, calculate_correlation_matrix
from data_sources.local_official_data import build_master_dataset
from data_sources.openmeteo_connector import get_national_timeseries

@pytest.fixture
def master_df():
    return build_master_dataset()

@pytest.fixture
def timeseries_df():
    return get_national_timeseries(90)

def test_calculate_descriptive_stats():
    data = [10, 20, 30, 40, 50]
    stats = calculate_descriptive_stats(data)
    assert stats["count"] == 5
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["iqr"] == 20.0

def test_analyze_time_series_window(timeseries_df):
    analysis_30 = analyze_time_series_window(timeseries_df, window_days=30, pollutant="pm25")
    assert analysis_30["window_days"] == 30
    assert "current_mean" in analysis_30
    assert "delta_pct" in analysis_30
    assert "trend_direction" in analysis_30

def test_calculate_bivariate_correlation(master_df):
    corr = calculate_bivariate_correlation(master_df["pm25"], master_df["pm10"])
    assert corr["n"] == 81
    assert corr["pearson_r"] > 0.8
    assert corr["pearson_p"] < 0.001
    assert 0.0 <= corr["r_squared"] <= 1.0

def test_calculate_correlation_matrix(master_df):
    cols = ["pm25", "pm10", "no2", "toplam_osb"]
    corr_mat, pval_mat = calculate_correlation_matrix(master_df, columns=cols)
    assert corr_mat.shape == (4, 4)
    assert (np.diag(corr_mat.values) == 1.0).all()
