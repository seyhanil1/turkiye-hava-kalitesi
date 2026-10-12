"""
analytics paketi
HavaAtlası - Türkiye Hava Kalitesi ve Bölgesel Veri Analizi Platformu
"""

from analytics.descriptive import calculate_descriptive_stats
from analytics.time_series import analyze_time_series_window
from analytics.correlation import calculate_bivariate_correlation, calculate_correlation_matrix
from analytics.hypothesis_tests import run_two_sample_test, run_regional_anova
from analytics.interpreter import generate_data_science_notes

__all__ = [
    "calculate_descriptive_stats",
    "analyze_time_series_window",
    "calculate_bivariate_correlation",
    "calculate_correlation_matrix",
    "run_two_sample_test",
    "run_regional_anova",
    "generate_data_science_notes"
]
