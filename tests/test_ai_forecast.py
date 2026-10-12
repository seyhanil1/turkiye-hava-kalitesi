"""
Birim Testleri: Yapay Zeka İçgörü & Tahmin Motoru
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.ai_forecast_page import (
    calculate_quantiles_and_anomalies,
    determine_city_category,
    build_projection_series,
    create_forecast_figure
)


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_calculate_quantiles_and_anomalies(master_df):
    q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(master_df)

    assert q1_osb < q3_osb
    assert q1_pm25 < q3_pm25
    assert len(kat_a_df) > 0
    assert len(kat_b_df) > 0

    # Kategori A kuralları: OSB <= Q1 ve PM2.5 >= Q3
    for _, row in kat_a_df.iterrows():
        assert row["osb_sayisi"] <= q1_osb
        assert row["pm25"] >= q3_pm25

    # Kategori B kuralları: OSB >= Q3 ve PM2.5 >= Q3
    for _, row in kat_b_df.iterrows():
        assert row["osb_sayisi"] >= q3_osb
        assert row["pm25"] >= q3_pm25


def test_determine_city_category(master_df):
    q1_osb, q3_osb, q1_pm25, q3_pm25, _, _ = calculate_quantiles_and_anomalies(master_df)

    # Iğdır Kategori A olmalı (düşük OSB, yüksek PM2.5)
    igdir_row = master_df[master_df["il"] == "Iğdır"].iloc[0]
    cat_igdir, rate_igdir = determine_city_category(igdir_row, q1_osb, q3_osb, q1_pm25, q3_pm25)
    assert cat_igdir == "Kategori A"
    assert rate_igdir == 0.03

    # Bursa Kategori B olmalı (yüksek OSB, yüksek PM2.5)
    bursa_row = master_df[master_df["il"] == "Bursa"].iloc[0]
    cat_bursa, rate_bursa = determine_city_category(bursa_row, q1_osb, q3_osb, q1_pm25, q3_pm25)
    assert cat_bursa == "Kategori B"
    assert rate_bursa == 0.05

    # Tunceli Normal olmalı (düşük kirlilik)
    tunceli_row = master_df[master_df["il"] == "Tunceli"].iloc[0]
    cat_tunceli, rate_tunceli = determine_city_category(tunceli_row, q1_osb, q3_osb, q1_pm25, q3_pm25)
    assert cat_tunceli == "Normal"
    assert rate_tunceli == 0.01


def test_build_projection_series():
    years, vals_a = build_projection_series(100.0, 0.03)
    assert years == [2026, 2027, 2028, 2029, 2030, 2031]
    assert vals_a[0] == 100.0
    assert vals_a[1] == 103.0
    assert round(vals_a[5], 2) == round(100.0 * (1.03 ** 5), 2)

    years, vals_b = build_projection_series(100.0, 0.05)
    assert vals_b[0] == 100.0
    assert vals_b[1] == 105.0
    assert round(vals_b[5], 2) == round(100.0 * (1.05 ** 5), 2)


def test_create_forecast_figure():
    years = [2026, 2027, 2028, 2029, 2030, 2031]
    vals = [50.0, 52.5, 55.1, 57.9, 60.8, 63.8]
    fig = create_forecast_figure("Bursa", "Kategori B", years, vals, 0.05)
    assert fig is not None
    assert len(fig.data) >= 1
    # Çizginin dash=dash olduğunu doğrula
    assert fig.data[0].line.dash == "dash"
    # Başlıktaki kırık parantez düzeltmesini doğrula
    assert "[Kategori B (Ağır Sanayi Baskısı) — Yıllık +%5 Artış Trendi]" in fig.layout.title.text
    # Çizgi etiketlerinin yshift ve yanchor='bottom' ile kaydırıldığını doğrula
    assert fig.layout.annotations[0].yshift == 8
    assert fig.layout.annotations[1].yshift == 8
    assert fig.layout.annotations[0].yanchor == "bottom"
    assert fig.layout.annotations[1].yanchor == "bottom"
    # Başlık fontunun kesilmeyecek boyutta olduğunu doğrula
    assert fig.layout.title.font.size <= 13


def test_ai_forecast_page_apptest_rendering():
    from streamlit.testing.v1 import AppTest

    def app_forecast():
        import streamlit as st
        from data_sources.local_official_data import build_master_dataset
        from app_pages.ai_forecast_page import render_ai_forecast_page
        df = build_master_dataset()
        render_ai_forecast_page(df)

    at = AppTest.from_function(app_forecast)
    at.run()

    assert not at.exception

    all_markdown = " ".join([m.value for m in at.markdown])

    # 1. Başlıklar ve kod sızıntısı temizliği
    assert "📋 81 İl İstatistiksel Risk ve Anomali Grupları" in all_markdown
    assert "(Pandas Filtreleme)" not in all_markdown
    assert "İstatistiksel Risk ve Anomali Analizi" in all_markdown

    # 2. İstatistiksel kartlar ve dilim bilgisi (Türkçe virgüllü)
    assert "Alt %25 ≤" in all_markdown
    assert "Üst %25 ≥" in all_markdown

    # 3. Şehir rozetlerinde birimler (µg/m³, Adet)
    assert "µg/m³, OSB:" in all_markdown
    assert "Adet)" in all_markdown

    # 4. Metin temizliği (Yapay Zeka Analizi kalktı)
    assert "Yapay Zeka Analizi:" not in all_markdown

