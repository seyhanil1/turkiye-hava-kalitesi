"""
Birim Testleri: Hipotez Testleri ve Veri Bilimi Yorum Motoru
"""

import pytest
import pandas as pd
import numpy as np

from analytics.hypothesis_tests import run_two_sample_test, run_regional_anova
from analytics.interpreter import generate_data_science_notes
from data_sources.local_official_data import build_master_dataset

@pytest.fixture
def master_df():
    return build_master_dataset()

def test_run_two_sample_test_significant():
    # Belirgin biçimde farklı iki grup
    group_a = [50, 52, 48, 55, 53, 51, 49, 54]
    group_b = [20, 22, 19, 21, 23, 20, 18, 22]
    res = run_two_sample_test(group_a, group_b, label1="Şehir A", label2="Şehir B")
    assert res["success"] is True
    assert res["is_significant"] is True
    assert res["p_value"] < 0.001
    assert "REDDEDİLDİ" in res["decision"]

def test_run_two_sample_test_insignificant():
    # Farksız iki grup
    group_a = [30, 31, 29, 30, 32, 28]
    group_b = [30, 29, 31, 30, 28, 32]
    res = run_two_sample_test(group_a, group_b, label1="Şehir X", label2="Şehir Y")
    assert res["success"] is True
    assert res["is_significant"] is False
    assert res["p_value"] >= 0.05
    assert "REDDEDİLEMEDİ" in res["decision"]

def test_run_regional_anova(master_df):
    res = run_regional_anova(master_df, group_col="bolge", val_col="pm25")
    assert res["success"] is True
    assert res["num_groups"] == 7
    assert "anova_f" in res
    assert "kruskal_h" in res
    assert "interpretation" in res

def test_generate_data_science_notes(master_df):
    notes = generate_data_science_notes(master_df, pollutant="pm25")
    assert isinstance(notes, list)
    assert len(notes) >= 2
    for n in notes:
        assert "title" in n
        assert "content" in n
