"""
Birim Testleri: İl Grupları (OSB × PM2.5 çeyreklik gruplaması)
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.ai_forecast_page import (
    calculate_quantiles_and_anomalies,
    determine_city_category,
)


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_calculate_quantiles_and_anomalies(master_df):
    q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(master_df)

    assert q1_osb < q3_osb
    assert q1_pm25 < q3_pm25

    # Kategori A kuralları: OSB <= Q1 ve PM2.5 >= Q3
    for _, row in kat_a_df.iterrows():
        assert row["osb_sayisi"] <= q1_osb
        assert row["pm25"] >= q3_pm25

    # Kategori B kuralları: OSB >= Q3 ve PM2.5 >= Q3
    for _, row in kat_b_df.iterrows():
        assert row["osb_sayisi"] >= q3_osb
        assert row["pm25"] >= q3_pm25


def test_determine_city_category_matches_rules(master_df):
    """Her il için kategori, çeyreklik kurallarıyla birebir uyumlu olmalı (tahmin oranı döndürülmez)."""
    q1_osb, q3_osb, q1_pm25, q3_pm25, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(master_df)
    for _, row in master_df.iterrows():
        cat = determine_city_category(row, q1_osb, q3_osb, q1_pm25, q3_pm25)
        assert isinstance(cat, str)
        if row["osb_sayisi"] <= q1_osb and row["pm25"] >= q3_pm25:
            assert cat == "Kategori A"
        elif row["osb_sayisi"] >= q3_osb and row["pm25"] >= q3_pm25:
            assert cat == "Kategori B"
        elif row["pm25"] >= q3_pm25:
            assert cat == "Kategori Dışı (Yüksek Kirlilik / Orta Sanayi)"
        else:
            assert cat == "Normal"
            assert cat == "Kategori Dışı (Orta Segment / Dengeli)"


def test_no_projection_functions_exported():
    """Veri temelli olmayan sabit artış projeksiyonu kaldırıldı."""
    import app_pages.ai_forecast_page as m
    assert not hasattr(m, "build_projection_series")
    assert not hasattr(m, "create_forecast_figure")


def test_ai_forecast_page_apptest_rendering(master_df):
    from streamlit.testing.v1 import AppTest

    def app_forecast():
        from data_sources.local_official_data import build_master_dataset
        from app_pages.ai_forecast_page import render_ai_forecast_page
        render_ai_forecast_page(build_master_dataset())

    at = AppTest.from_function(app_forecast)
    at.run(timeout=30)

    assert not at.exception

    all_markdown = " ".join([m.value for m in at.markdown])
    _, _, _, _, kat_a_df, kat_b_df = calculate_quantiles_and_anomalies(master_df)
    kalan = len(master_df) - len(kat_a_df) - len(kat_b_df)

    assert "81 İl Dağılım Grupları" in all_markdown
    assert "Kategori A: Düşük OSB, Yüksek PM2.5 İlleri" in all_markdown
    assert "Kategori B: Yüksek OSB, Yüksek PM2.5 İlleri" in all_markdown
    assert f"Listelenmeyen {kalan} il" in all_markdown
    assert "gruplama nedensellik göstermez" in all_markdown
    assert "Alt %25 ≤" in all_markdown
    assert "Üst %25 ≥" in all_markdown
    assert "Yapay Zeka" not in all_markdown
    assert "Projeksiyon" not in all_markdown


def test_province_groups_state_sync():
    """Şehir seçiminin session state ve URL ile senkronize olduğunu test eder."""
    from streamlit.testing.v1 import AppTest

    def app_forecast():
        from data_sources.local_official_data import build_master_dataset
        from app_pages.ai_forecast_page import render_ai_forecast_page
        render_ai_forecast_page(build_master_dataset())

    at = AppTest.from_function(app_forecast)
    at.session_state["selected_city"] = "Tokat"
    at.run(timeout=30)
    assert not at.exception

    at.selectbox[0].select("Van").run(timeout=30)
    assert not at.exception
    assert at.session_state["selected_city"] == "Van"
    assert at.query_params["il"] == "Van"
