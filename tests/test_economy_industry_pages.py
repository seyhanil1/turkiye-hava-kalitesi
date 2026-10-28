"""
Birim Testleri: Sanayi Profili Sayfası & Dashboard Entegrasyonu
"""

import pytest
import pandas as pd
from data_sources.local_official_data import build_master_dataset
from app_pages.industry_page import render_industry_page
from visualization.pixel_perfect_dashboard import generate_pixel_perfect_dashboard_html


@pytest.fixture
def master_df():
    return build_master_dataset()


def test_industry_page_data_integrity(master_df):
    """OSBÜK kayıtlı 419 OSB ve 143.267 Hektar verilerinin korunduğunu test eder."""
    total_osb = master_df["toplam_osb"].sum()
    total_area = master_df["osb_alani_hektar"].sum()

    assert total_osb == 419
    assert round(total_area) == 143267

    # Fonksiyonun çalışma hatası vermediğini doğrula
    render_industry_page(master_df)


def test_pixel_perfect_dashboard_modules_content(master_df):
    """Ulaşılamayan eski dashboard modülleri (sabit istatistikler içeren) HTML'den kaldırılmış olmalı."""
    html = generate_pixel_perfect_dashboard_html(master_df)

    for eski in ["industryBarChart", "view-korelasyon", "view-duello", "view-ai_tahmin",
                 "SANAYİ SİCİLİ", "Bakanlık siciline", "r = +0,48", "t = 8,42", "Projeksiyon"]:
        assert eski not in html, eski
    assert "view-genel_bakis" in html


def test_industry_page_kpi_cards_and_parsel_removal():
    """Sanayi Profili sayfasında spekülatif parsel ve hektar verilerinin kaldırıldığını ve Faal OSB oranını test eder."""
    with open("app_pages/industry_page.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Hektar ve parsel verilerinin sayfadan tamamen kaldırıldığını doğrula
    assert "Toplam OSB Sanayi Alanı" not in content
    assert "Hektar" not in content
    assert "hektar" not in content
    assert "parsel" not in content.lower()

    # Yeni resmi Faal OSB KPI kartını doğrula
    assert "OSBÜK • FAAL ORANI" in content
    assert "BAKANLIK" not in content
    assert "AKTİF ÜRETİMDEKİ OSB" in content
    assert "Tescilli 419 OSB'nin 304'ü fiilen işletme ve üretim aşamasındadır (OSBÜK Ekim 2026)." in content
    assert "planlama/altyapı aşamasında organize sanayi bölgesi" in content

    # Marmara kartı veriden hesaplanmalı
    assert "Marmara bölgesi genelinde {marmara_osb} OSB ({marmara_faal} faal üretimde)" in content
    assert "faal üretim kapasitesi" in content


def test_industry_page_barchart_descending_and_formatting():
    """Bölgesel OSB çubuk grafiğinde büyükten küçüğe sıralama ve Türkçe format kontrolü."""
    with open("app_pages/industry_page.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Bölge verisi sabit liste yerine master tablodan hesaplanmalı ve OSB'ye göre azalan sıralanmalı
    assert '"bolge": "Marmara", "osb": 100' not in content
    assert 'df.groupby("bolge").agg(osb=("toplam_osb", "sum")' in content
    assert 'reg.sort_values("osb", ascending=False)' in content

    # Doğu Anadolu metin ezilmesini önlemek için textposition="auto" olduğunu doğrula
    assert 'textposition="auto"' in content
    assert 'textposition="inside"' not in content

    # Keyfi kırmızı (#ef4444) ve neon açık turkuaz (#00f2fe) renklerinin kaldırıldığını doğrula
    fig_bar_code = content.split("fig_bar = go.Figure")[1].split("st.plotly_chart")[0]
    assert "#ef4444" not in fig_bar_code
    assert "#00f2fe" not in fig_bar_code
    assert 'color="#0369a1"' in fig_bar_code
    assert 'margin=dict(l=140, r=40, t=20, b=40)' in fig_bar_code
    assert 'weight="bold"' in fig_bar_code

    # PM2.5 virgül formatlama kodunun varlığını doğrula
    assert 'pm_str = f"{r[\'pm25\']:.1f}".replace(".", ",")' in content


def test_industry_page_table_faal_oran_and_formatting(master_df):
    """81 il tablosunda Parsel sütununun olmadığını, Faal Oran (%) sütununun eklendiğini doğrular."""
    with open("app_pages/industry_page.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Tablo kodunda Parsel veya Alan (Hektar) olmadığını doğrula
    assert "Alan (Hektar)" not in content
    assert '"toplam_parsel"' not in content
    assert '"Parsel"' not in content

    # Faal Oran (%) sütununun ve hesaplama fonksiyonunun varlığını doğrula
    assert '"faal_oran": "Faal Oran (%)"' in content
    assert "calc_faal_oran" in content

    # PM2.5 virgüllü ve tek ondalık formatlamasını doğrula
    assert 'table_df["pm25"] = table_df["pm25"].apply(lambda v: f"{float(v):.1f}".replace(".", ","))' in content


def test_industry_page_apptest_no_city_selector():
    """Sanayi Profili sayfasında üst bar münferit il seçicisinin gizlendiğini AppTest ile doğrular."""
    import os
    from streamlit.testing.v1 import AppTest

    app_path = os.path.abspath("app/app.py")
    at = AppTest.from_file(app_path, default_timeout=30)
    at.query_params["sayfa"] = "Sanayi Profili"
    at.session_state["active_category"] = "Analiz"
    at.run()

    assert not at.exception
    # Şehir seçicinin Sanayi Profili sayfasında gizlendiğini doğrula (show_city=False)
    city_selectboxes = [sb for sb in at.selectbox if "İl Seçimi" in getattr(sb, "label", "")]
    assert len(city_selectboxes) == 0
