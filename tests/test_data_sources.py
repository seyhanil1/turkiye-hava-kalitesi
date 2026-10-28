"""
Birim Testleri: Veri Kaynakları ve Ayrıştırıcılar
"""

import pytest
import pandas as pd
import numpy as np

from data_sources.constants import PLAKA_ILLER, BOLGELER, NUFUSLAR
from data_sources.local_official_data import (
    parse_kara_rapor_istasyon,
    parse_cams_annual,
    atfedilen_olum_orani,
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

def test_parse_cams_annual_integrity():
    """CAMS yıllık dosyası: 81 il, tam veri, fiziksel olarak makul aralık, PM2.5 <= PM10."""
    df = parse_cams_annual()
    assert len(df) == 81
    assert set(df["il"]) == set(PLAKA_ILLER.values())
    assert df["pm25_cams"].notna().all() and df["pm10_cams"].notna().all()
    assert df["pm25_cams"].between(1, 100).all()
    assert (df["pm25_cams"] <= df["pm10_cams"]).all()


def test_parse_kara_rapor_istasyon():
    """Kara Rapor 2025 istasyon değerleri: yayımlanan en yüksek değer Iğdır 46,81 µg/m³."""
    df = parse_kara_rapor_istasyon()
    assert set(df["il"]) <= set(PLAKA_ILLER.values())
    assert df["pm25_istasyon_max_2024"].max() == pytest.approx(46.81)
    assert df.set_index("il").loc["Iğdır", "pm25_istasyon_max_2024"] == pytest.approx(46.81)


def test_atfedilen_olum_orani():
    """AirQ+ log-lineer modeli: 5 µg/m³ ve altında pay 0, 15 µg/m³'te 1 - 1/1,08."""
    paf = atfedilen_olum_orani(pd.Series([3.0, 5.0, 15.0, 25.0]))
    assert paf.iloc[0] == 0 and paf.iloc[1] == 0
    assert paf.iloc[2] == pytest.approx(1 - 1 / 1.08)
    assert paf.iloc[3] == pytest.approx(1 - 1 / 1.08 ** 2)

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
    # PM2.5 kaynağı açıkça işaretlenmeli ve CAMS sütunuyla aynı olmalı
    assert (df["pm25_kaynak"].str.startswith("CAMS")).all()
    assert (df["pm25"] == df["pm25_cams"]).all()
    # Kademe etiketleri tek merkezi tanımdan gelmeli
    from data_sources.constants import KIRLILIK_KADEMELERI
    assert set(df["dso_risk"]) <= {k["etiket"] for k in KIRLILIK_KADEMELERI["pm25"]}
    assert df["solunum_olum_payi"].between(0, 100).all()
    assert (df["atfedilen_olum_tahmini"] <= df["toplam_olum"]).all()

def test_timeseries_dataset():
    df_ts = get_national_timeseries(90)
    assert isinstance(df_ts, pd.DataFrame)
    assert len(df_ts) >= 30
    assert "pm25" in df_ts.columns
    assert "date" in df_ts.columns
    # Nüfus ağırlıklı ortalama, günlük il min/max aralığında kalmalı
    assert (df_ts["pm25"] >= df_ts["pm25_min"]).all()
    assert (df_ts["pm25"] <= df_ts["pm25_max"]).all()


def test_timeseries_no_synthetic_fallback(monkeypatch, tmp_path):
    """Günlük veri dosyası yoksa sentetik seri üretilmemeli, boş tablo dönmeli."""
    import data_sources.openmeteo_connector as om
    monkeypatch.setattr(om.os.path, "exists", lambda p: False)
    df_ts = om.get_national_timeseries(90)
    assert df_ts.empty

def test_openaq_connector_status():
    connector = OpenAQConnector()
    status = connector.check_connection()
    assert isinstance(status, dict)
    assert "status" in status
