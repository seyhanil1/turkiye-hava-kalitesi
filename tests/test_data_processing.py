"""
Birim Testleri: Veri Temizleme ve Agregasyon
"""

import pytest
import pandas as pd
import numpy as np

from data_processing.cleaner import validate_and_clean_air_data, filter_by_region_and_search
from data_processing.aggregator import aggregate_by_region, get_dso_compliance_stats
from data_sources.local_official_data import build_master_dataset

@pytest.fixture
def master_df():
    return build_master_dataset()

def test_validate_and_clean_air_data(master_df):
    clean_df, report = validate_and_clean_air_data(master_df)
    assert len(clean_df) == 81
    assert report["total_provinces"] == 81
    assert report["data_completeness_pct"] == 100.0

def test_filter_by_region_and_search(master_df):
    marmara_df = filter_by_region_and_search(master_df, region="Marmara")
    assert len(marmara_df) == 11
    assert (marmara_df["bolge"] == "Marmara").all()
    
    search_df = filter_by_region_and_search(master_df, search_query="İzmir")
    assert len(search_df) == 1
    assert search_df.iloc[0]["il"] == "İzmir"

def test_aggregate_by_region(master_df):
    reg_df = aggregate_by_region(master_df, pollutant="pm25")
    assert len(reg_df) == 7
    assert reg_df["il_sayisi"].sum() == 81
    assert (reg_df["ortalama"] > 0).all()

def test_get_dso_compliance_stats(master_df):
    stats = get_dso_compliance_stats(master_df, pollutant="pm25")
    assert stats["total_provinces"] == 81
    assert stats["threshold_ug_m3"] == 5.0
    assert stats["exceeding_count"] + stats["compliant_count"] == 81
    breakdown_sum = sum(stats["risk_breakdown"].values())
    assert breakdown_sum == 81
