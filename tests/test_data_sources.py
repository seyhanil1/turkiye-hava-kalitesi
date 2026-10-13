"""
Birim Testleri: Veri Kaynakları ve Ayrıştırıcılar
"""

import pytest
import pandas as pd
import numpy as np

from data_sources.constants import PLAKA_ILLER, BOLGELER, NUFUSLAR
from data_sources.local_official_data import (
    parse_kara_rapor,
    parse_tuik_saglik,
    parse_sanayi_osb,
    build_master_dataset
)
from data_sources.openmeteo_connector import get_national_timeseries
from data_sources.openaq_connector import OpenAQConnector

def test_constants_integrity():
    assert len(PLAKA_ILLER) == 81
    assert len(NUFUSLAR) == 81
    total_in_regions = sum(len(iller) for iller in BOLGELER.values())
    assert total_in_regions == 81

def test_parse_kara_rapor():
    df = parse_kara_rapor("data/hava_kirliligi.xlsx")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 81
    assert "il" in df.columns and "pm25" in df.columns
    assert df["pm25"].isna().sum() == 0
    assert (df["pm25"] > 0).all()

def test_parse_tuik_saglik():
    df = parse_tuik_saglik("data/tuik_saglik.xlsx")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 81
    assert "solunum_olum" in df.columns
    assert (df["solunum_olum"] > 0).all()

def test_parse_sanayi_osb():
    df = parse_sanayi_osb("data/sanayi.txt")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 81
    assert "toplam_osb" in df.columns
    assert "toplam_parsel" in df.columns
    assert (df["toplam_osb"] >= 0).all()

def test_build_master_dataset():
    df = build_master_dataset()
    assert len(df) == 81
    expected_cols = [
        "il", "plaka", "bolge", "lat", "lon", "nufus", 
        "pm25", "toplam_osb", "faal_osb", 
        "solunum_olum_100k", "dso_risk"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Eksik sütun: {col}"
    assert df["plaka"].nunique() == 81
    assert df["solunum_olum_100k"].isna().sum() == 0

def test_timeseries_dataset():
    df_ts = get_national_timeseries(90)
    assert isinstance(df_ts, pd.DataFrame)
    assert len(df_ts) >= 30
    assert "pm25" in df_ts.columns
    assert "date" in df_ts.columns

def test_openaq_connector_status():
    connector = OpenAQConnector()
    status = connector.check_connection()
    assert isinstance(status, dict)
    assert "status" in status
